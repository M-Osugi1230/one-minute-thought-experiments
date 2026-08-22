"""Write human-editable and machine-readable Phase 1 artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from .errors import ConfigurationError
from .models import BrandConfig, Experiment, GeneratedPackage
from .quality import ValidationReport
from .timeline import TimelineScene


ARTIFACT_NAMES = (
    "script.json",
    "script.md",
    "narration.txt",
    "scenes.json",
    "timeline.json",
    "subtitles.srt",
    "caption.txt",
    "pinned_comment.txt",
    "manifest.json",
)


def source_digest(
    experiment: Experiment,
    brand: BrandConfig,
    prompt_version: str,
) -> str:
    payload = {
        "experiment": experiment.model_dump(mode="json"),
        "brand": brand.model_dump(mode="json"),
        "prompt_version": prompt_version,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_artifacts(
    output_dir: Path,
    package: GeneratedPackage,
    experiment: Experiment,
    timeline: list[TimelineScene],
    srt_text: str,
    report: ValidationReport,
    provider_name: str,
    model_name: str,
    prompt_version: str,
    digest: str,
    overwrite: bool = False,
) -> list[Path]:
    existing = [output_dir / name for name in ARTIFACT_NAMES if (output_dir / name).exists()]
    if existing and not overwrite:
        raise ConfigurationError(
            f"出力先に既存ファイルがあります: {output_dir}。再生成には --overwrite を指定してください。"
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    scenes_payload = [
        {
            **scene.model_dump(mode="json"),
            "timing": timing.as_dict(),
        }
        for scene, timing in zip(package.scenes, timeline, strict=True)
    ]
    narration = "\n\n".join(scene.narration for scene in package.scenes) + "\n"
    caption = package.caption.rstrip() + "\n\n" + " ".join(
        f"#{tag}" for tag in package.hashtags
    ) + "\n"

    _json(output_dir / "script.json", package.model_dump(mode="json"))
    (output_dir / "script.md").write_text(
        _script_markdown(package, timeline), encoding="utf-8"
    )
    (output_dir / "narration.txt").write_text(narration, encoding="utf-8")
    _json(output_dir / "scenes.json", scenes_payload)
    _json(output_dir / "timeline.json", [item.as_dict() for item in timeline])
    (output_dir / "subtitles.srt").write_text(srt_text, encoding="utf-8")
    (output_dir / "caption.txt").write_text(caption, encoding="utf-8")
    (output_dir / "pinned_comment.txt").write_text(
        package.pinned_comment.rstrip() + "\n", encoding="utf-8"
    )
    _json(
        output_dir / "manifest.json",
        {
            "schema_version": "1.0",
            "experiment_id": experiment.id,
            "slug": experiment.slug,
            "created_at": datetime.now(UTC).isoformat(),
            "generation": {
                "provider": provider_name,
                "model": model_name,
                "prompt_version": prompt_version,
            },
            "source_sha256": digest,
            "planned_duration_seconds": package.planned_duration_seconds,
            "timing_basis": "planned_scene_durations",
            "quality": report.as_dict(),
            "artifacts": list(ARTIFACT_NAMES),
        },
    )
    return [output_dir / name for name in ARTIFACT_NAMES]


def _json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _script_markdown(
    package: GeneratedPackage,
    timeline: list[TimelineScene],
) -> str:
    lines = [
        f"# {package.working_title}",
        "",
        f"- 思考実験: {package.experiment_title} (#{package.experiment_id})",
        f"- 予定尺: {package.planned_duration_seconds:.1f}秒",
        f"- 採用Hook: {package.selected_hook_index + 1}/3",
        "",
        "## Hook候補",
        "",
    ]
    for index, hook in enumerate(package.hook_options, start=1):
        marker = "（採用）" if index - 1 == package.selected_hook_index else ""
        lines.append(f"{index}. {hook.narration}{marker}")

    lines.extend(["", "## シーン", ""])
    for scene, timing in zip(package.scenes, timeline, strict=True):
        lines.extend(
            [
                f"### {scene.id}. {scene.purpose.value} "
                f"({timing.start_seconds:.1f}–{timing.pause_end_seconds:.1f}秒)",
                "",
                f"- ナレーション: {scene.narration}",
                f"- 画面テキスト: {scene.screen_text}",
                f"- 映像: {scene.visual_description}",
                f"- テンプレート: `{scene.visual_template}`",
                f"- 後の間: {scene.pause_after_seconds:.1f}秒",
                "",
            ]
        )
    lines.extend(
        [
            "## 投稿文",
            "",
            package.caption,
            "",
            "## 固定コメント",
            "",
            package.pinned_comment,
            "",
        ]
    )
    return "\n".join(lines)
