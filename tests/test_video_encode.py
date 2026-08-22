from __future__ import annotations

from pathlib import Path

from PIL import Image
from imageio_ffmpeg import count_frames_and_secs

from thought_pipeline.audio import VoiceTrackResult, write_silence_wav
from thought_pipeline.render import encode_video
from thought_pipeline.visuals import VisualResult


def test_ffmpeg_encodes_vertical_mp4_with_audio(tmp_path) -> None:
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    Image.new("RGB", (180, 320), "#08090D").save(first)
    Image.new("RGB", (180, 320), "#D4AF37").save(second)
    concat = tmp_path / "frames.ffconcat"
    concat.write_text(
        "\n".join(
            [
                "ffconcat version 1.0",
                f"file '{first.resolve()}'",
                "duration 0.5",
                f"file '{second.resolve()}'",
                "duration 0.5",
                f"file '{second.resolve()}'",
                "",
            ]
        ),
        encoding="utf-8",
    )
    voice = tmp_path / "voice.wav"
    write_silence_wav(voice, 1.0, 24000, 1)
    visual = VisualResult(
        width=180,
        height=320,
        fps=10,
        frame_paths=[first, second],
        frame_durations=[0.5, 0.5],
        concat_path=concat,
        storyboard_path=Path("unused.jpg"),
        font_path=Path("unused.ttf"),
    )
    track = VoiceTrackResult(
        provider_name="silent-planned",
        voice_path=voice,
        scene_paths=[],
        narration_durations={},
        total_duration_seconds=1.0,
        manifest_path=Path("unused.json"),
    )
    target = tmp_path / "draft.mp4"

    encode_video(visual, track, target, 1.0, "libx264", "96k")
    frames, seconds = count_frames_and_secs(str(target))

    assert target.stat().st_size > 1000
    assert frames == 10
    assert seconds == 1.0
