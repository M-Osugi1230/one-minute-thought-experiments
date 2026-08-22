"""Deterministic, license-free ambience and editorial sound cues."""

from __future__ import annotations

import json
import math
import wave
from array import array
from dataclasses import dataclass
from pathlib import Path

from .timeline import TimelineScene


@dataclass(frozen=True)
class SoundCue:
    seconds: float
    kind: str
    purpose: str


@dataclass(frozen=True)
class SoundbedResult:
    path: Path
    manifest_path: Path
    cues: list[SoundCue]


def build_soundbed(
    timeline: list[TimelineScene],
    target: Path,
    sample_rate_hz: int,
    channels: int,
) -> SoundbedResult:
    """Create a quiet cinematic bed without external music or licensed assets."""

    total_seconds = timeline[-1].pause_end_seconds
    cues = _editorial_cues(timeline)
    pauses = [
        (item.narration_end_seconds, item.pause_end_seconds)
        for item in timeline
        if item.pause_end_seconds > item.narration_end_seconds
    ]

    frame_count = round(total_seconds * sample_rate_hz)
    samples = array("h")
    for frame in range(frame_count):
        time_seconds = frame / sample_rate_hz
        # A restrained two-note drone supplies continuity without sounding like a song.
        ambient = (
            0.011 * math.sin(math.tau * 46.0 * time_seconds)
            + 0.004 * math.sin(math.tau * 92.0 * time_seconds + 0.7)
            + 0.002 * math.sin(math.tau * 137.0 * time_seconds + 1.4)
        )
        if any(start <= time_seconds < end for start, end in pauses):
            ambient *= 0.08

        effect = sum(
            _effect_sample(cue.kind, time_seconds - cue.seconds)
            for cue in cues
            if 0 <= time_seconds - cue.seconds <= 1.2
        )
        value = max(-0.32, min(0.32, ambient + effect))
        encoded = round(value * 32767)
        for _ in range(channels):
            samples.append(encoded)

    target.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(target), "wb") as output:
        output.setnchannels(channels)
        output.setsampwidth(2)
        output.setframerate(sample_rate_hz)
        output.writeframes(samples.tobytes())

    manifest_path = target.with_name("soundbed_manifest.json")
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "generator": "deterministic-cinematic-v1",
                "duration_seconds": round(total_seconds, 3),
                "sample_rate_hz": sample_rate_hz,
                "channels": channels,
                "cues": [cue.__dict__ for cue in cues],
                "license": "generated-in-repository",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return SoundbedResult(target, manifest_path, cues)


def _editorial_cues(timeline: list[TimelineScene]) -> list[SoundCue]:
    by_purpose = {item.purpose: item for item in timeline}
    cues: list[SoundCue] = [SoundCue(0.0, "rumble", "hook")]

    def add(purpose: str, offset: float, kind: str) -> None:
        item = by_purpose.get(purpose)
        if item:
            cues.append(
                SoundCue(round(item.start_seconds + offset, 3), kind, purpose)
            )

    add("scenario", 0.35, "rail")
    if "setup" in by_purpose:
        add("setup", 0.45, "lever")
    else:
        add("scenario", 1.25, "lever")
    add("consequence", 0.25, "heartbeat")
    add("reveal", 0.0, "impact")
    add("second_question", 0.0, "impact")
    add("second_question", 0.65, "heartbeat")
    add("cta", 0.0, "tick")
    total = timeline[-1].pause_end_seconds
    cues.append(SoundCue(max(0.0, round(total - 0.7, 3)), "rumble", "loop"))
    return cues


def _effect_sample(kind: str, local_time: float) -> float:
    if local_time < 0:
        return 0.0
    if kind == "rumble" and local_time <= 1.2:
        fade = min(1.0, local_time / 0.2) * max(0.0, 1.0 - local_time / 1.2)
        return fade * (
            0.025 * math.sin(math.tau * 34.0 * local_time)
            + 0.012 * math.sin(math.tau * 51.0 * local_time + 0.4)
        )
    if kind == "rail" and local_time <= 0.16:
        return 0.07 * math.exp(-24.0 * local_time) * (
            math.sin(math.tau * 760.0 * local_time)
            + 0.45 * math.sin(math.tau * 1130.0 * local_time)
        )
    if kind == "lever" and local_time <= 0.22:
        return 0.09 * math.exp(-18.0 * local_time) * math.sin(
            math.tau * 520.0 * local_time
        )
    if kind == "impact" and local_time <= 0.75:
        return 0.075 * math.exp(-4.8 * local_time) * math.sin(
            math.tau * (62.0 - 18.0 * local_time) * local_time
        )
    if kind == "heartbeat" and local_time <= 0.72:
        first = _pulse(local_time, 0.0, 0.105)
        second = _pulse(local_time, 0.28, 0.075)
        return first + second
    if kind == "tick" and local_time <= 0.12:
        return 0.055 * math.exp(-35.0 * local_time) * math.sin(
            math.tau * 980.0 * local_time
        )
    return 0.0


def _pulse(time_seconds: float, start: float, amplitude: float) -> float:
    local = time_seconds - start
    if not 0 <= local <= 0.16:
        return 0.0
    return amplitude * math.sin(math.pi * local / 0.16) * math.sin(
        math.tau * 64.0 * local
    )
