"""Phase 2 orchestration: measured TTS, deterministic visuals, and MP4 output."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from .audio import VoiceTrackResult, build_voice_track, select_voice_provider
from .errors import ConfigurationError, GenerationError, QualityValidationError
from .media import ffmpeg_executable, run_media_command
from .models import GeneratedPackage
from .quality import validate_generated_package
from .repository import ProjectRepository
from .timeline import (
    build_srt,
    build_subtitle_cues,
    build_timeline_from_durations,
)
from .visuals import VisualResult, render_visuals


PHASE2_ARTIFACT_NAMES = (
    "voice.wav",
    "audio_manifest.json",
    "timeline_actual.json",
    "subtitles_actual.srt",
    "storyboard.jpg",
    "publish_caption.txt",
    "render_manifest.json",
)


@dataclass(frozen=True)
class RenderResult:
    output_dir: Path
    video_path: Path
    voice_path: Path
    storyboard_path: Path
    provider_name: str
    actual_duration_seconds: float
    duration_in_target_range: bool
    width: int
    height: int
    fps: int


def render_phase2(
    repository: ProjectRepository,
    experiment_id: str,
    output_root: Path,
    voice_mode: str = "auto",
    preview: bool = False,
    overwrite: bool = False,
) -> RenderResult:
    experiment = repository.experiment(experiment_id)
    output_dir = output_root / f"{experiment.id}_{experiment.slug}"
    script_path = output_dir / "script.json"
    if not script_path.is_file():
        raise ConfigurationError(
            f"Phase 1のscript.jsonがありません: {script_path}。先に台本を生成してください。"
        )

    video_name = "draft_preview.mp4" if preview else "draft.mp4"
    known_paths = [output_dir / name for name in PHASE2_ARTIFACT_NAMES]
    known_paths.append(output_dir / video_name)
    existing = [path for path in known_paths if path.exists()]
    if existing and not overwrite:
        raise ConfigurationError(
            f"Phase 2の既存成果物があります: {output_dir}。再生成には --overwrite を指定してください。"
        )

    try:
        package = GeneratedPackage.model_validate_json(
            script_path.read_text(encoding="utf-8")
        )
    except (OSError, ValidationError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"script.jsonが不正です: {script_path}\n{exc}") from exc

    report = validate_generated_package(package, experiment, repository.brand())
    if not report.is_valid:
        detail = "\n".join(
            f"- [{issue.code}] {issue.path}: {issue.message}" for issue in report.errors
        )
        raise QualityValidationError(
            f"動画化前の品質チェックに失敗しました:\n{detail}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    voice_config = repository.voice()
    video_config = repository.video()
    provider = select_voice_provider(voice_mode, voice_config)
    track = build_voice_track(package, output_dir, provider, voice_config)

    timeline = build_timeline_from_durations(
        package,
        track.narration_durations,
        video_config,
    )
    actual_duration = timeline[-1].pause_end_seconds
    duration_in_target_range = (
        experiment.target_duration.min_seconds
        <= actual_duration
        <= experiment.target_duration.max_seconds
    )
    _json(
        output_dir / "timeline_actual.json",
        [item.as_dict() for item in timeline],
    )
    (output_dir / "subtitles_actual.srt").write_text(
        build_srt(package, timeline, video_config),
        encoding="utf-8",
    )

    cues = build_subtitle_cues(package, timeline, video_config)
    visual = render_visuals(
        package=package,
        experiment=experiment,
        timeline=timeline,
        cues=cues,
        video=video_config,
        voice=voice_config,
        output_dir=output_dir,
        project_root=repository.root,
        preview=preview,
    )
    video_path = output_dir / video_name
    encode_video(
        visual=visual,
        track=track,
        target=video_path,
        total_duration_seconds=actual_duration,
        video_codec=video_config.render.video_codec,
        audio_bitrate=video_config.render.audio_bitrate,
    )

    _write_publish_caption(
        output_dir / "caption.txt",
        output_dir / "publish_caption.txt",
        voice_config.disclosure_text,
    )
    _json(
        output_dir / "render_manifest.json",
        {
            "schema_version": "1.0",
            "experiment_id": experiment.id,
            "created_at": datetime.now(UTC).isoformat(),
            "timing_basis": "measured_scene_audio",
            "voice_provider": track.provider_name,
            "actual_duration_seconds": round(actual_duration, 3),
            "duration_in_target_range": duration_in_target_range,
            "preview": preview,
            "video": {
                "path": video_path.name,
                "width": visual.width,
                "height": visual.height,
                "fps": visual.fps,
                "codec": video_config.render.video_codec,
            },
            "font": str(visual.font_path),
            "artifacts": [
                *PHASE2_ARTIFACT_NAMES,
                video_path.name,
                "visuals/",
                "audio/scenes/",
            ],
        },
    )
    return RenderResult(
        output_dir=output_dir,
        video_path=video_path,
        voice_path=track.voice_path,
        storyboard_path=visual.storyboard_path,
        provider_name=track.provider_name,
        actual_duration_seconds=round(actual_duration, 3),
        duration_in_target_range=duration_in_target_range,
        width=visual.width,
        height=visual.height,
        fps=visual.fps,
    )


def encode_video(
    visual: VisualResult,
    track: VoiceTrackResult,
    target: Path,
    total_duration_seconds: float,
    video_codec: str,
    audio_bitrate: str,
) -> None:
    if total_duration_seconds <= 0:
        raise GenerationError("動画尺が0秒以下です")
    run_media_command(
        [
            ffmpeg_executable(),
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(visual.concat_path),
            "-i",
            str(track.voice_path),
            "-vf",
            f"fps={visual.fps}",
            "-af",
            "apad",
            "-t",
            f"{total_duration_seconds:.3f}",
            "-c:v",
            video_codec,
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            audio_bitrate,
            "-movflags",
            "+faststart",
            str(target),
        ]
    )


def _write_publish_caption(source: Path, target: Path, disclosure: str) -> None:
    caption = source.read_text(encoding="utf-8").strip()
    if disclosure not in caption:
        caption = f"{caption}\n\n{disclosure}"
    target.write_text(caption + "\n", encoding="utf-8")


def _json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
