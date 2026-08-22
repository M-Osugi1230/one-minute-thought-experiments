"""Planned timing and draft subtitles; actual TTS timing replaces this in Phase 2."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from .models import GeneratedPackage, VideoConfig


@dataclass(frozen=True)
class TimelineScene:
    scene_id: int
    purpose: str
    start_seconds: float
    narration_end_seconds: float
    pause_end_seconds: float
    duration_seconds: float
    pause_after_seconds: float

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SubtitleCue:
    start_seconds: float
    end_seconds: float
    text: str


def build_timeline(
    package: GeneratedPackage,
    video: VideoConfig,
) -> list[TimelineScene]:
    durations = {scene.id: scene.duration_seconds for scene in package.scenes}
    return build_timeline_from_durations(package, durations, video)


def build_timeline_from_durations(
    package: GeneratedPackage,
    narration_durations: dict[int, float],
    video: VideoConfig,
) -> list[TimelineScene]:
    cursor = 0.0
    result: list[TimelineScene] = []
    for scene in package.scenes:
        if scene.id not in narration_durations:
            raise ValueError(f"missing narration duration for scene {scene.id}")
        duration = narration_durations[scene.id]
        if duration <= 0:
            raise ValueError(f"narration duration must be positive for scene {scene.id}")
        start = cursor
        narration_end = start + duration
        pause_end = narration_end + scene.pause_after_seconds
        result.append(
            TimelineScene(
                scene_id=scene.id,
                purpose=scene.purpose.value,
                start_seconds=round(start, 3),
                narration_end_seconds=round(narration_end, 3),
                pause_end_seconds=round(pause_end, 3),
                duration_seconds=round(duration, 3),
                pause_after_seconds=scene.pause_after_seconds,
            )
        )
        cursor = pause_end + video.timeline.default_gap_seconds
    return result


def build_srt(
    package: GeneratedPackage,
    timeline: list[TimelineScene],
    video: VideoConfig,
) -> str:
    cues = build_subtitle_cues(package, timeline, video)

    blocks = []
    for index, cue in enumerate(cues, start=1):
        blocks.append(
            f"{index}\n{_srt_time(cue.start_seconds)} --> {_srt_time(cue.end_seconds)}\n{cue.text}"
        )
    return "\n\n".join(blocks) + "\n"


def build_subtitle_cues(
    package: GeneratedPackage,
    timeline: list[TimelineScene],
    video: VideoConfig,
) -> list[SubtitleCue]:
    cues: list[SubtitleCue] = []
    chars_per_cue = (
        video.subtitle.max_chars_per_line * video.subtitle.max_lines
    )
    for scene, timing in zip(package.scenes, timeline, strict=True):
        chunks = _subtitle_chunks(scene.narration, chars_per_cue)
        total_chars = sum(max(1, len(_compact(chunk))) for chunk in chunks)
        cursor = timing.start_seconds + video.timeline.subtitle_lead_in_seconds
        available_end = max(
            cursor + 0.1,
            timing.narration_end_seconds - video.timeline.subtitle_tail_seconds,
        )
        available = available_end - cursor
        for index, chunk in enumerate(chunks):
            weight = max(1, len(_compact(chunk))) / total_chars
            end = available_end if index == len(chunks) - 1 else cursor + available * weight
            cues.append(
                SubtitleCue(
                    start_seconds=round(cursor, 3),
                    end_seconds=round(end, 3),
                    text=_wrap_lines(chunk, video.subtitle.max_chars_per_line),
                )
            )
            cursor = end
    return cues


def _compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _subtitle_chunks(text: str, limit: int) -> list[str]:
    normalized = re.sub(r"\s+", "", text.strip())
    if len(normalized) <= limit:
        return [normalized]

    chunks: list[str] = []
    remaining = normalized
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        window = remaining[:limit]
        split_at = max(window.rfind(mark) for mark in ("。", "？", "！", "、"))
        if split_at < max(6, limit // 3):
            split_at = limit - 1
        chunks.append(remaining[: split_at + 1])
        remaining = remaining[split_at + 1 :]
    return chunks


def _wrap_lines(text: str, width: int) -> str:
    compact = _compact(text)
    lines: list[str] = []
    while compact:
        if len(compact) <= width:
            lines.append(compact)
            break
        cut = width
        preferred_cuts = [
            index + 1
            for index, char in enumerate(compact[:width])
            if char in "、。！？!?」』）はがをにでともへ"
        ]
        if preferred_cuts and preferred_cuts[-1] >= max(4, int(width * 0.5)):
            cut = preferred_cuts[-1]
        tail_length = len(compact) - cut
        minimum_tail = max(4, width // 4)
        if 0 < tail_length < minimum_tail:
            cut = max(1, cut - (minimum_tail - tail_length))
        # Do not leave Japanese punctuation stranded at the start of a line.
        while cut < len(compact) and compact[cut] in "、。！？!?」』）":
            cut += 1
        lines.append(compact[:cut])
        compact = compact[cut:]
    return "\n".join(lines)


def _srt_time(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
