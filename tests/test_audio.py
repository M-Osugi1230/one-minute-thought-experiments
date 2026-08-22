from __future__ import annotations

import json
import shutil
from types import SimpleNamespace

import openai

from thought_pipeline.audio import (
    OpenAIVoiceProvider,
    SilentVoiceProvider,
    build_voice_track,
    wav_duration,
    write_silence_wav,
)
from thought_pipeline.providers import OfflineGoldenProvider
from thought_pipeline.repository import ProjectRepository
from thought_pipeline.timeline import build_timeline_from_durations


def test_silent_provider_builds_measurable_scene_track(tmp_path) -> None:
    repository = ProjectRepository()
    package = OfflineGoldenProvider(repository.root).generate("001", object())
    voice = repository.voice()

    result = build_voice_track(
        package,
        tmp_path,
        SilentVoiceProvider(voice),
        voice,
    )
    timeline = build_timeline_from_durations(
        package,
        result.narration_durations,
        repository.video(),
    )
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert len(result.scene_paths) == len(package.scenes)
    assert wav_duration(result.voice_path) == 50.0
    assert timeline[-1].pause_end_seconds == 50.0
    assert manifest["provider"] == "silent-planned"
    assert manifest["narration_durations"]["1"] == 3.8

    build_voice_track(package, tmp_path, SilentVoiceProvider(voice), voice)
    cached_manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert cached_manifest["cache_hit_scene_ids"] == list(range(1, 10))


def test_openai_voice_uses_streaming_wav_and_voice_instructions(
    tmp_path, monkeypatch
) -> None:
    repository = ProjectRepository()
    scene = OfflineGoldenProvider(repository.root).generate("001", object()).scenes[0]
    captured: dict = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def stream_to_file(self, path) -> None:
            write_silence_wav(path, 0.25, 24000, 1)

    class FakeStreaming:
        def create(self, **kwargs):
            captured.update(kwargs)
            return FakeResponse()

    class FakeClient:
        def __init__(self, **kwargs):
            captured["client_kwargs"] = kwargs
            self.audio = SimpleNamespace(
                speech=SimpleNamespace(
                    with_streaming_response=FakeStreaming(),
                )
            )

    monkeypatch.setattr(openai, "OpenAI", FakeClient)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        "thought_pipeline.audio.normalize_wav",
        lambda source, target, config, ffmpeg: shutil.copyfile(source, target),
    )
    monkeypatch.setattr("thought_pipeline.audio.ffmpeg_executable", lambda: "ffmpeg")
    provider = OpenAIVoiceProvider(repository.voice())
    target = tmp_path / "scene.wav"

    provider.synthesize(scene, target)

    assert target.is_file()
    assert captured["model"] == "gpt-4o-mini-tts"
    assert captured["voice"] == "cedar"
    assert captured["response_format"] == "wav"
    assert captured["instructions"] == repository.voice().instructions
