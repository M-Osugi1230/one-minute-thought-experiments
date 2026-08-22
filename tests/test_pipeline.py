from __future__ import annotations

import json

from thought_pipeline.core import Pipeline
from thought_pipeline.providers import OfflineGoldenProvider
from thought_pipeline.repository import ProjectRepository
from thought_pipeline.timeline import build_srt, build_timeline


def test_offline_pipeline_writes_complete_artifact_set(tmp_path) -> None:
    repository = ProjectRepository()
    provider = OfflineGoldenProvider(repository.root)

    result = Pipeline(repository).run(
        "001",
        provider,
        output_root=tmp_path,
    )

    names = {path.name for path in result.artifacts}
    assert names == {
        "script.json",
        "script.md",
        "narration.txt",
        "scenes.json",
        "timeline.json",
        "subtitles.srt",
        "caption.txt",
        "pinned_comment.txt",
        "manifest.json",
    }
    manifest = json.loads((result.output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["quality"]["is_valid"] is True
    assert manifest["planned_duration_seconds"] == 50.0
    assert manifest["generation"]["provider"] == "offline-golden"


def test_planned_timeline_and_srt_end_at_fifty_seconds() -> None:
    repository = ProjectRepository()
    package = OfflineGoldenProvider(repository.root).generate("001", object())
    video = repository.video()
    timeline = build_timeline(package, video)
    srt = build_srt(package, timeline, video)

    assert timeline[-1].pause_end_seconds == 50.0
    assert "00:00:50,000" in srt
    assert "\n。" not in srt
    assert "変え\nます" not in srt
