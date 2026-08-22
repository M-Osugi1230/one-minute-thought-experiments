"""Scene-level TTS, WAV normalization, and measured voice-track assembly."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .errors import ConfigurationError, GenerationError
from .media import ffmpeg_executable, run_media_command
from .models import GeneratedPackage, Scene, VoiceConfig


class VoiceProvider(Protocol):
    name: str

    def synthesize(self, scene: Scene, target: Path) -> None:
        ...


@dataclass(frozen=True)
class VoiceTrackResult:
    provider_name: str
    voice_path: Path
    scene_paths: list[Path]
    narration_durations: dict[int, float]
    total_duration_seconds: float
    manifest_path: Path


class SilentVoiceProvider:
    """Portable fallback used in CI and environments without a speech engine."""

    name = "silent-planned"

    def __init__(self, config: VoiceConfig) -> None:
        self.config = config

    def synthesize(self, scene: Scene, target: Path) -> None:
        write_silence_wav(
            target,
            scene.duration_seconds,
            self.config.sample_rate_hz,
            self.config.channels,
        )


class MacOSSystemVoiceProvider:
    """No-key local preview voice using macOS `say`."""

    name = "macos-system-tts"

    def __init__(self, config: VoiceConfig) -> None:
        if platform.system() != "Darwin" or not shutil.which("say"):
            raise ConfigurationError("macOSのsayコマンドを利用できません")
        self.config = config
        self.ffmpeg = ffmpeg_executable()

    def synthesize(self, scene: Scene, target: Path) -> None:
        raw_path = target.with_suffix(".aiff")
        last_error = "音声データが空でした"
        for _ in range(3):
            raw_path.unlink(missing_ok=True)
            target.unlink(missing_ok=True)
            completed = subprocess.run(
                [
                    shutil.which("say") or "/usr/bin/say",
                    "-v",
                    self.config.system_voice,
                    "-r",
                    str(self.config.system_rate),
                    "-o",
                    str(raw_path),
                    scene.narration,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                last_error = completed.stderr.strip() or f"終了コード {completed.returncode}"
                continue
            # macOS `say` can occasionally return a valid header with no samples.
            if raw_path.is_file() and raw_path.stat().st_size > 4096:
                normalize_wav(raw_path, target, self.config, self.ffmpeg)
                if target.is_file() and wav_duration(target) > 0.05:
                    raw_path.unlink(missing_ok=True)
                    return
            last_error = "音声データが空でした"
        raw_path.unlink(missing_ok=True)
        raise GenerationError(
            f"macOS音声の生成に3回失敗しました（scene {scene.id}）: {last_error}"
        )


class OpenAIVoiceProvider:
    """OpenAI Speech API provider following the official streaming-file pattern."""

    name = "openai-tts"

    def __init__(self, config: VoiceConfig) -> None:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY が未設定です。systemまたはsilent音声を使用してください。"
            )
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.config = config
        self.ffmpeg = ffmpeg_executable()

    def synthesize(self, scene: Scene, target: Path) -> None:
        raw_path = target.with_name(f"{target.stem}.raw.wav")
        raw_path.unlink(missing_ok=True)
        try:
            with self.client.audio.speech.with_streaming_response.create(
                model=self.config.model,
                voice=self.config.voice,
                input=scene.narration,
                instructions=self.config.instructions,
                response_format="wav",
                speed=self.config.speed,
            ) as response:
                response.stream_to_file(raw_path)
        except Exception as exc:
            raw_path.unlink(missing_ok=True)
            raise GenerationError(
                f"OpenAI音声の生成に失敗しました（scene {scene.id}）: {exc}"
            ) from exc
        try:
            normalize_wav(raw_path, target, self.config, self.ffmpeg)
        finally:
            raw_path.unlink(missing_ok=True)


def select_voice_provider(mode: str, config: VoiceConfig) -> VoiceProvider:
    if mode == "openai":
        return OpenAIVoiceProvider(config)
    if mode == "system":
        return MacOSSystemVoiceProvider(config)
    if mode == "silent":
        return SilentVoiceProvider(config)
    if mode != "auto":
        raise ConfigurationError(f"不明な音声モードです: {mode}")

    if os.getenv("OPENAI_API_KEY", "").strip():
        return OpenAIVoiceProvider(config)
    if platform.system() == "Darwin" and shutil.which("say"):
        return MacOSSystemVoiceProvider(config)
    return SilentVoiceProvider(config)


def build_voice_track(
    package: GeneratedPackage,
    output_dir: Path,
    provider: VoiceProvider,
    config: VoiceConfig,
) -> VoiceTrackResult:
    audio_dir = output_dir / "audio"
    scenes_dir = audio_dir / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)

    durations: dict[int, float] = {}
    scene_paths: list[Path] = []
    cache_hits: list[int] = []
    for scene in package.scenes:
        scene_path = scenes_dir / f"{scene.id:02d}_{scene.purpose.value}.wav"
        cache_path = scene_path.with_suffix(".cache.json")
        cache_key = _audio_cache_key(scene, provider.name, config)
        if _is_cached_audio_valid(scene_path, cache_path, cache_key):
            cache_hits.append(scene.id)
        else:
            provider.synthesize(scene, scene_path)
            duration = wav_duration(scene_path)
            if duration <= 0.05:
                raise GenerationError(f"生成音声が空です: scene {scene.id}")
            cache_path.write_text(
                json.dumps({"cache_key": cache_key}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        durations[scene.id] = wav_duration(scene_path)
        scene_paths.append(scene_path)

    voice_path = output_dir / "voice.wav"
    total = concatenate_scene_wavs(
        package,
        scene_paths,
        voice_path,
        config.sample_rate_hz,
        config.channels,
    )
    manifest_path = output_dir / "audio_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "provider": provider.name,
                "model": config.model if provider.name == "openai-tts" else None,
                "voice": (
                    config.voice
                    if provider.name == "openai-tts"
                    else config.system_voice if provider.name == "macos-system-tts" else None
                ),
                "sample_rate_hz": config.sample_rate_hz,
                "channels": config.channels,
                "narration_durations": {
                    str(scene_id): round(duration, 3)
                    for scene_id, duration in durations.items()
                },
                "cache_hit_scene_ids": cache_hits,
                "total_duration_seconds": round(total, 3),
                "disclosure_text": config.disclosure_text,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return VoiceTrackResult(
        provider_name=provider.name,
        voice_path=voice_path,
        scene_paths=scene_paths,
        narration_durations=durations,
        total_duration_seconds=round(total, 3),
        manifest_path=manifest_path,
    )


def _audio_cache_key(scene: Scene, provider_name: str, config: VoiceConfig) -> str:
    payload = {
        "provider": provider_name,
        "scene_id": scene.id,
        "narration": scene.narration,
        "voice_config": config.model_dump(mode="json"),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _is_cached_audio_valid(path: Path, cache_path: Path, expected_key: str) -> bool:
    if not path.is_file() or not cache_path.is_file():
        return False
    try:
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        return cached.get("cache_key") == expected_key and wav_duration(path) > 0.05
    except (OSError, json.JSONDecodeError, wave.Error):
        return False


def normalize_wav(
    source: Path,
    target: Path,
    config: VoiceConfig,
    ffmpeg: str | None = None,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    run_media_command(
        [
            ffmpeg or ffmpeg_executable(),
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-vn",
            "-af",
            (
                f"loudnorm=I={config.normalization.target_lufs}:"
                f"TP={config.normalization.true_peak_db}:LRA=11"
            ),
            "-ac",
            str(config.channels),
            "-ar",
            str(config.sample_rate_hz),
            "-c:a",
            "pcm_s16le",
            str(target),
        ]
    )


def write_silence_wav(
    path: Path,
    duration_seconds: float,
    sample_rate_hz: int,
    channels: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = round(duration_seconds * sample_rate_hz)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(channels)
        output.setsampwidth(2)
        output.setframerate(sample_rate_hz)
        output.writeframes(b"\x00" * frames * channels * 2)


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def concatenate_scene_wavs(
    package: GeneratedPackage,
    scene_paths: list[Path],
    target: Path,
    sample_rate_hz: int,
    channels: int,
) -> float:
    if len(scene_paths) != len(package.scenes):
        raise GenerationError("シーン数と音声ファイル数が一致しません")
    total_frames = 0
    with wave.open(str(target), "wb") as output:
        output.setnchannels(channels)
        output.setsampwidth(2)
        output.setframerate(sample_rate_hz)
        for scene, scene_path in zip(package.scenes, scene_paths, strict=True):
            with wave.open(str(scene_path), "rb") as source:
                if (
                    source.getnchannels() != channels
                    or source.getsampwidth() != 2
                    or source.getframerate() != sample_rate_hz
                ):
                    raise GenerationError(f"音声形式が統一されていません: {scene_path}")
                frames = source.readframes(source.getnframes())
                output.writeframes(frames)
                total_frames += source.getnframes()
            pause_frames = round(scene.pause_after_seconds * sample_rate_hz)
            output.writeframes(b"\x00" * pause_frames * channels * 2)
            total_frames += pause_frames
    return total_frames / sample_rate_hz
