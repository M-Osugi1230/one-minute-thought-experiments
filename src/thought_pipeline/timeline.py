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


def build_timeline(
    package: GeneratedPackage,
    video: VideoConfig,
) -> list[TimelineScene]:
    cursor = 0.0
    result: list[TimelineScene] = []
    for scene in package.scenes:
        start = cursor
        narration_end = start + scene.duration_seconds
        pause_end = narration_end + scene.pause_after_seconds
        result.append(
            TimelineScene(
                scene_id=scene.id,
                purpose=scene.purpose.value,
                start_seconds=round(start, 3),
                narration_end_seconds=round(narration_end, 3),
                pause_end_seconds=round(pause_end, 3),
                duration_seconds=scene.duration_seconds,
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
    cues: list[tuple[float, float, str]] = []
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
                (
                    cursor,
                    end,
                    _wrap_lines(chunk, video.subtitle.max_chars_per_line),
                )
            )
            cursor = end

    blocks = []
    for index, (start, end, text) in enumerate(cues, start=1):
        blocks.append(f"{index}\n{_srt_time(start)} --> {_srt_time(end)}\n{text}")
    return "\n\n".join(blocks) + "\n"


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
        punctuation_cuts = [
            index + 1
            for index, char in enumerate(compact[:width])
            if char in "、。！？!?」』）"
        ]
        if punctuation_cuts and punctuation_cuts[-1] >= max(4, int(width * 0.55)):
            cut = punctuation_cuts[-1]
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
