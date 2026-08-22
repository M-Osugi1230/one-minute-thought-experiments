from __future__ import annotations

from PIL import Image

from thought_pipeline.providers import OfflineGoldenProvider
from thought_pipeline.repository import ProjectRepository
from thought_pipeline.timeline import build_subtitle_cues, build_timeline
from thought_pipeline.visuals import render_visuals


def test_preview_visuals_include_scene_cards_subtitles_and_storyboard(tmp_path) -> None:
    repository = ProjectRepository()
    package = OfflineGoldenProvider(repository.root).generate("001", object())
    video = repository.video()
    timeline = build_timeline(package, video)

    result = render_visuals(
        package=package,
        experiment=repository.experiment("001"),
        timeline=timeline,
        cues=build_subtitle_cues(package, timeline, video),
        video=video,
        voice=repository.voice(),
        output_dir=tmp_path,
        project_root=repository.root,
        preview=True,
    )

    assert (result.width, result.height, result.fps) == (540, 960, 15)
    assert len(result.frame_paths) >= len(package.scenes)
    assert result.concat_path.is_file()
    assert result.storyboard_path.is_file()
    with Image.open(result.frame_paths[0]) as frame:
        assert frame.size == (540, 960)
