"""Deterministic 9:16 scene cards and timed subtitle frames."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .errors import ConfigurationError
from .models import Experiment, GeneratedPackage, Scene, VideoConfig, VoiceConfig
from .timeline import SubtitleCue, TimelineScene


@dataclass(frozen=True)
class VisualResult:
    width: int
    height: int
    fps: int
    frame_paths: list[Path]
    frame_durations: list[float]
    concat_path: Path
    storyboard_path: Path
    font_path: Path


@dataclass(frozen=True)
class FontSet:
    small: ImageFont.FreeTypeFont
    label: ImageFont.FreeTypeFont
    body: ImageFont.FreeTypeFont
    title: ImageFont.FreeTypeFont
    huge: ImageFont.FreeTypeFont


def resolve_font_path(project_root: Path) -> Path:
    configured = os.getenv("THOUGHT_PIPELINE_FONT", "").strip()
    candidates = [
        Path(configured) if configured else None,
        project_root / "assets" / "fonts" / "NotoSansJP-Bold.ttf",
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    raise ConfigurationError(
        "日本語表示用フォントが見つかりません。THOUGHT_PIPELINE_FONTを設定してください。"
    )


def render_visuals(
    package: GeneratedPackage,
    experiment: Experiment,
    timeline: list[TimelineScene],
    cues: list[SubtitleCue],
    video: VideoConfig,
    voice: VoiceConfig,
    output_dir: Path,
    project_root: Path,
    preview: bool,
) -> VisualResult:
    scale = video.render.preview_scale if preview else 1.0
    width = round(video.canvas.width * scale)
    height = round(video.canvas.height * scale)
    fps = video.render.preview_fps if preview else video.canvas.fps
    font_path = resolve_font_path(project_root)
    fonts = _fonts(font_path, scale)

    visuals_dir = output_dir / "visuals"
    scenes_dir = visuals_dir / "scenes"
    frames_dir = visuals_dir / "frames"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    base_images: dict[int, Image.Image] = {}
    scene_paths: list[Path] = []
    for scene in package.scenes:
        image = _scene_card(
            scene,
            experiment,
            package,
            video,
            voice,
            fonts,
            width,
            height,
            scale,
        )
        path = scenes_dir / f"{scene.id:02d}_{scene.purpose.value}.png"
        image.save(path, format="PNG", optimize=True)
        base_images[scene.id] = image
        scene_paths.append(path)

    boundaries = {0.0, timeline[-1].pause_end_seconds}
    for item in timeline:
        boundaries.update((item.start_seconds, item.pause_end_seconds))
    for cue in cues:
        boundaries.update((cue.start_seconds, cue.end_seconds))
    ordered = sorted(boundaries)

    frame_paths: list[Path] = []
    frame_durations: list[float] = []
    for index, (start, end) in enumerate(zip(ordered, ordered[1:]), start=1):
        duration = end - start
        if duration < 0.01:
            continue
        midpoint = start + duration / 2
        active_timing = next(
            (item for item in timeline if item.start_seconds <= midpoint < item.pause_end_seconds),
            timeline[-1],
        )
        active_cue = next(
            (cue for cue in cues if cue.start_seconds <= midpoint < cue.end_seconds),
            None,
        )
        frame = base_images[active_timing.scene_id].copy()
        if active_cue:
            _draw_subtitle(frame, active_cue.text, fonts, video, scale)
        frame_path = frames_dir / f"frame_{index:03d}.png"
        frame.save(frame_path, format="PNG", optimize=True)
        frame_paths.append(frame_path)
        frame_durations.append(round(duration, 6))

    concat_path = visuals_dir / "frames.ffconcat"
    _write_concat(concat_path, frame_paths, frame_durations)
    storyboard_path = output_dir / "storyboard.jpg"
    _storyboard(scene_paths, storyboard_path)
    return VisualResult(
        width=width,
        height=height,
        fps=fps,
        frame_paths=frame_paths,
        frame_durations=frame_durations,
        concat_path=concat_path,
        storyboard_path=storyboard_path,
        font_path=font_path,
    )


def _fonts(path: Path, scale: float) -> FontSet:
    def font(size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(path), max(12, round(size * scale)))

    return FontSet(
        small=font(25),
        label=font(34),
        body=font(58),
        title=font(76),
        huge=font(150),
    )


def _scene_card(
    scene: Scene,
    experiment: Experiment,
    package: GeneratedPackage,
    video: VideoConfig,
    voice: VoiceConfig,
    fonts: FontSet,
    width: int,
    height: int,
    scale: float,
) -> Image.Image:
    palette = video.palette
    image = Image.new("RGB", (width, height), palette.background)
    draw = ImageDraw.Draw(image, "RGBA")
    _background(draw, width, height, palette.background_alt, palette.accent, scale)

    margin = round(72 * scale)
    draw.text(
        (margin, round(78 * scale)),
        f"THOUGHT EXPERIMENT  #{experiment.id}",
        font=fonts.label,
        fill=palette.accent,
    )
    purpose_label = scene.purpose.value.upper().replace("_", " ")
    bbox = draw.textbbox((0, 0), purpose_label, font=fonts.small)
    draw.text(
        (width - margin - (bbox[2] - bbox[0]), round(88 * scale)),
        purpose_label,
        font=fonts.small,
        fill=palette.muted,
    )

    max_text_width = width - margin * 2
    display_text = _wrap_pixels(draw, scene.screen_text, fonts.title, max_text_width)
    _center_text(
        draw,
        display_text,
        fonts.title,
        width // 2,
        round(250 * scale),
        palette.foreground,
        spacing=round(18 * scale),
        stroke=round(2 * scale),
    )

    _template_art(
        draw,
        scene.visual_template,
        width,
        height,
        scale,
        palette.foreground,
        palette.muted,
        palette.accent,
        palette.danger,
        fonts,
        experiment,
        package,
    )
    disclosure = "AI生成音声" if voice.disclosure_text else ""
    bbox = draw.textbbox((0, 0), disclosure, font=fonts.small)
    draw.rounded_rectangle(
        (
            width - margin - (bbox[2] - bbox[0]) - round(30 * scale),
            height - round(88 * scale),
            width - margin,
            height - round(38 * scale),
        ),
        radius=round(12 * scale),
        fill=(*_rgb(palette.background_alt), 205),
    )
    draw.text(
        (width - margin - (bbox[2] - bbox[0]) - round(15 * scale), height - round(82 * scale)),
        disclosure,
        font=fonts.small,
        fill=palette.muted,
    )
    return image


def _background(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    alt: str,
    accent: str,
    scale: float,
) -> None:
    draw.ellipse(
        (
            -round(220 * scale),
            round(420 * scale),
            width + round(300 * scale),
            round(1500 * scale),
        ),
        outline=(*_rgb(alt), 190),
        width=max(1, round(4 * scale)),
    )
    for offset, alpha in ((0, 70), (70, 40), (140, 20)):
        draw.line(
            (
                round((80 + offset) * scale),
                height,
                round((430 + offset) * scale),
                round(500 * scale),
            ),
            fill=(*_rgb(accent), alpha),
            width=max(1, round(3 * scale)),
        )


def _template_art(
    draw: ImageDraw.ImageDraw,
    template: str,
    width: int,
    height: int,
    scale: float,
    foreground: str,
    muted: str,
    accent: str,
    danger: str,
    fonts: FontSet,
    experiment: Experiment,
    package: GeneratedPackage,
) -> None:
    cx = width // 2
    y_top = round(650 * scale)
    y_bottom = round(1305 * scale)

    if template in {"dramatic_question", "track_overview", "lever_switch"}:
        split_y = round(920 * scale)
        _track(draw, cx, y_top, cx, split_y, foreground, scale)
        _track(draw, cx, split_y, round(245 * scale), y_bottom, foreground, scale)
        _track(draw, cx, split_y, width - round(245 * scale), y_bottom, foreground, scale)
        _trolley(draw, cx, round(760 * scale), accent, foreground, scale)
        if template != "dramatic_question":
            for index in range(5):
                _person(
                    draw,
                    round((660 + (index % 3) * 90) * scale),
                    round((1090 + (index // 3) * 110) * scale),
                    foreground,
                    scale,
                )
        if template == "lever_switch":
            _lever(draw, round(250 * scale), round(950 * scale), accent, foreground, scale)
    elif template == "single_person_focus":
        draw.ellipse(
            (round(210 * scale), y_top, width - round(210 * scale), y_bottom),
            outline=(*_rgb(danger), 135),
            width=max(2, round(6 * scale)),
        )
        _person(draw, cx, round(930 * scale), foreground, scale, large=True)
    elif template == "binary_choice_split":
        _choice_panel(draw, round(80 * scale), round(680 * scale), round(500 * scale), y_bottom, "A", "引く", accent, fonts, scale)
        _choice_panel(draw, round(580 * scale), round(680 * scale), width - round(80 * scale), y_bottom, "B", "引かない", muted, fonts, scale)
    elif template == "title_reveal":
        radius = round(250 * scale)
        draw.ellipse((cx - radius, round(730 * scale), cx + radius, round(1230 * scale)), outline=accent, width=max(2, round(8 * scale)))
        _center_text(draw, experiment.id, fonts.huge, cx, round(825 * scale), accent)
        _center_text(draw, experiment.title, fonts.body, cx, round(1080 * scale), foreground)
    elif template == "action_vs_inaction":
        _lever(draw, round(270 * scale), round(970 * scale), accent, foreground, scale)
        draw.line((cx, round(720 * scale), cx, y_bottom), fill=(*_rgb(muted), 120), width=max(1, round(3 * scale)))
        _center_text(draw, "行為", fonts.body, round(270 * scale), round(1190 * scale), accent)
        _center_text(draw, "不作為", fonts.body, width - round(270 * scale), round(1190 * scale), muted)
        _person(draw, width - round(270 * scale), round(900 * scale), foreground, scale, large=True)
    elif template == "condition_twist":
        positions = [(cx, 880, True), (cx - round(220 * scale), 1030, False), (cx + round(220 * scale), 1030, False)]
        for px, py, large in positions:
            _person(draw, px, round(py * scale) if isinstance(py, int) else py, accent if large else foreground, scale, large=large)
        draw.arc((round(160 * scale), round(700 * scale), width - round(160 * scale), y_bottom), 205, 335, fill=(*_rgb(accent), 150), width=max(2, round(6 * scale)))
    elif template == "comment_cta":
        _choice_panel(draw, round(100 * scale), round(720 * scale), round(490 * scale), round(1160 * scale), "A", "引く", accent, fonts, scale)
        _choice_panel(draw, round(590 * scale), round(720 * scale), width - round(100 * scale), round(1160 * scale), "B", "引かない", muted, fonts, scale)
        bubble = (round(280 * scale), round(1210 * scale), width - round(280 * scale), round(1350 * scale))
        draw.rounded_rectangle(bubble, radius=round(50 * scale), outline=foreground, width=max(2, round(4 * scale)))
        _center_text(draw, "理由をコメント", fonts.label, cx, round(1250 * scale), foreground)
    else:
        draw.rounded_rectangle((round(160 * scale), y_top, width - round(160 * scale), y_bottom), radius=round(40 * scale), outline=accent, width=max(2, round(5 * scale)))
        _center_text(draw, package.working_title, fonts.body, cx, round(900 * scale), foreground)


def _track(draw, x1, y1, x2, y2, color, scale) -> None:
    offset = round(34 * scale)
    width = max(2, round(6 * scale))
    draw.line((x1 - offset, y1, x2 - offset, y2), fill=color, width=width)
    draw.line((x1 + offset, y1, x2 + offset, y2), fill=color, width=width)


def _trolley(draw, x, y, accent, foreground, scale) -> None:
    w, h = round(180 * scale), round(125 * scale)
    draw.rounded_rectangle((x - w // 2, y - h // 2, x + w // 2, y + h // 2), radius=round(18 * scale), fill=(*_rgb(accent), 220), outline=foreground, width=max(2, round(5 * scale)))
    for dx in (-55, 55):
        draw.ellipse((x + round(dx * scale) - round(18 * scale), y + h // 2 - round(4 * scale), x + round(dx * scale) + round(18 * scale), y + h // 2 + round(32 * scale)), fill=foreground)


def _person(draw, x, y, color, scale, large=False) -> None:
    factor = 1.45 if large else 1.0
    r = round(30 * scale * factor)
    draw.ellipse((x - r, y - r * 2, x + r, y), fill=color)
    body_w = round(52 * scale * factor)
    body_h = round(105 * scale * factor)
    draw.rounded_rectangle((x - body_w // 2, y + round(8 * scale), x + body_w // 2, y + body_h), radius=round(20 * scale), fill=color)


def _lever(draw, x, y, accent, foreground, scale) -> None:
    draw.rounded_rectangle((x - round(95 * scale), y + round(80 * scale), x + round(95 * scale), y + round(150 * scale)), radius=round(18 * scale), fill=foreground)
    draw.line((x, y + round(90 * scale), x + round(90 * scale), y - round(120 * scale)), fill=accent, width=max(3, round(18 * scale)))
    draw.ellipse((x + round(55 * scale), y - round(155 * scale), x + round(125 * scale), y - round(85 * scale)), fill=accent)


def _choice_panel(draw, left, top, right, bottom, label, text, color, fonts, scale) -> None:
    draw.rounded_rectangle((left, top, right, bottom), radius=round(42 * scale), fill=(*_rgb(color), 35), outline=color, width=max(2, round(5 * scale)))
    cx = (left + right) // 2
    _center_text(draw, label, fonts.huge, cx, top + round(80 * scale), color)
    _center_text(draw, text, fonts.body, cx, bottom - round(150 * scale), color)


def _draw_subtitle(
    image: Image.Image,
    text: str,
    fonts: FontSet,
    video: VideoConfig,
    scale: float,
) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, _ = image.size
    y = round(video.subtitle.position_y * scale)
    bbox = draw.multiline_textbbox((0, 0), text, font=fonts.body, spacing=round(12 * scale), align="center", stroke_width=max(1, round(2 * scale)))
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pad_x, pad_y = round(45 * scale), round(28 * scale)
    draw.rounded_rectangle(
        (width // 2 - text_w // 2 - pad_x, y - pad_y, width // 2 + text_w // 2 + pad_x, y + text_h + pad_y),
        radius=round(24 * scale),
        fill=(0, 0, 0, video.render.subtitle_box_opacity),
    )
    draw.multiline_text(
        (width // 2, y),
        text,
        font=fonts.body,
        fill=video.palette.foreground,
        anchor="ma",
        align="center",
        spacing=round(12 * scale),
        stroke_width=max(1, round(2 * scale)),
        stroke_fill="#000000",
    )
    image.paste(overlay, (0, 0), overlay)


def _center_text(draw, text, font, x, y, fill, spacing=8, stroke=0) -> None:
    draw.multiline_text((x, y), text, font=font, fill=fill, anchor="ma", align="center", spacing=spacing, stroke_width=stroke, stroke_fill="#000000")


def _wrap_pixels(draw, text: str, font, max_width: int) -> str:
    lines: list[str] = []
    for source_line in text.splitlines() or [text]:
        current = ""
        for char in source_line:
            candidate = current + char
            if current and draw.textlength(candidate, font=font) > max_width:
                lines.append(current)
                current = char
            else:
                current = candidate
        if current:
            lines.append(current)
    return "\n".join(lines)


def _write_concat(path: Path, frames: list[Path], durations: list[float]) -> None:
    lines = ["ffconcat version 1.0"]
    for frame, duration in zip(frames, durations, strict=True):
        lines.append(f"file '{frame.resolve()}'")
        lines.append(f"duration {duration:.6f}")
    if frames:
        lines.append(f"file '{frames[-1].resolve()}'")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _storyboard(scene_paths: list[Path], target: Path) -> None:
    thumb_w, thumb_h = 270, 480
    columns = 3
    rows = (len(scene_paths) + columns - 1) // columns
    sheet = Image.new("RGB", (thumb_w * columns, thumb_h * rows), "#08090D")
    for index, path in enumerate(scene_paths):
        with Image.open(path) as source:
            image = source.convert("RGB")
            image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            x = (index % columns) * thumb_w + (thumb_w - image.width) // 2
            y = (index // columns) * thumb_h + (thumb_h - image.height) // 2
            sheet.paste(image, (x, y))
    sheet.save(target, format="JPEG", quality=88, optimize=True)


def _rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))
