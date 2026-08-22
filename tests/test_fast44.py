from __future__ import annotations

import wave

from thought_pipeline.providers import OfflineGoldenProvider
from thought_pipeline.quality import validate_generated_package
from thought_pipeline.repository import ProjectRepository
from thought_pipeline.soundbed import build_soundbed
from thought_pipeline.timeline import build_subtitle_cues, build_timeline
from thought_pipeline.visuals import render_visuals


def test_fast44_variant_is_valid_and_moves_twist_forward() -> None:
    repository = ProjectRepository()
    package = OfflineGoldenProvider(repository.root, "fast44").generate("001", object())
    report = validate_generated_package(
        package,
        repository.experiment("001"),
        repository.brand(),
    )
    timeline = build_timeline(package, repository.video())
    second_question = next(item for item in timeline if item.purpose == "second_question")

    assert report.is_valid
    assert package.planned_duration_seconds == 40.1
    assert second_question.start_seconds / package.planned_duration_seconds < 0.70
    assert "最初" in package.scenes[-1].screen_text


def test_kinetic_profile_adds_motion_frames_and_neutral_storyboard(tmp_path) -> None:
    repository = ProjectRepository()
    package = OfflineGoldenProvider(repository.root, "fast44").generate("001", object())
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
        edit_profile="kinetic",
    )

    assert len(result.frame_paths) > len(package.scenes) * 4
    assert result.storyboard_path.is_file()


def test_soundbed_matches_timeline_and_ducks_choice_pauses(tmp_path) -> None:
    repository = ProjectRepository()
    package = OfflineGoldenProvider(repository.root, "fast44").generate("001", object())
    timeline = build_timeline(package, repository.video())
    voice = repository.voice()

    result = build_soundbed(
        timeline,
        tmp_path / "soundbed.wav",
        voice.sample_rate_hz,
        voice.channels,
    )

    with wave.open(str(result.path), "rb") as audio:
        duration = audio.getnframes() / audio.getframerate()
    assert round(duration, 3) == timeline[-1].pause_end_seconds
    assert {cue.kind for cue in result.cues} >= {"rumble", "lever", "heartbeat", "impact"}
    assert result.manifest_path.is_file()
