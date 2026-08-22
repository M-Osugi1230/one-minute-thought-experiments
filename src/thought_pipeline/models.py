"""Strict schemas shared by content files, LLM output, and later phases."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DurationRange(StrictModel):
    min_seconds: float = Field(ge=1)
    ideal_seconds: float = Field(ge=1)
    max_seconds: float = Field(ge=1)

    @model_validator(mode="after")
    def ordered(self) -> "DurationRange":
        if not self.min_seconds <= self.ideal_seconds <= self.max_seconds:
            raise ValueError("duration must satisfy min <= ideal <= max")
        return self


class Choice(StrictModel):
    label: str = Field(min_length=1, max_length=4)
    action: str = Field(min_length=1, max_length=100)
    consequence: str = Field(min_length=1, max_length=160)


class Scenario(StrictModel):
    viewer_role: str = Field(min_length=1)
    initial_state: str = Field(min_length=1)
    available_action: str = Field(min_length=1)
    action_result: str = Field(min_length=1)
    inaction_result: str = Field(min_length=1)
    constraints: list[str] = Field(min_length=1)


class PhilosophicalFocus(StrictModel):
    primary: str = Field(min_length=1)
    avoid_overclaiming: list[str] = Field(min_length=1)


class Source(StrictModel):
    author: str = Field(min_length=1)
    title: str = Field(min_length=1)
    year: int = Field(ge=1500, le=2100)
    kind: Literal["primary", "secondary"]
    locator: str = Field(min_length=1)
    url: HttpUrl | None = None


class ContentRules(StrictModel):
    must_include: list[str] = Field(min_length=1)
    must_not_include: list[str] = Field(min_length=1)


class Experiment(StrictModel):
    id: str = Field(pattern=r"^\d{3}$")
    slug: str = Field(pattern=r"^[a-z0-9_]+$")
    title: str = Field(min_length=1)
    category: str = Field(min_length=1)
    status: Literal["draft", "ready", "archived"]
    template: Literal["pov", "binary_choice", "mystery"]
    one_line_summary: str = Field(min_length=1)
    core_question: str = Field(min_length=1)
    target_duration: DurationRange
    scenario: Scenario
    choices: list[Choice] = Field(min_length=2, max_length=3)
    variation_question: str = Field(min_length=1)
    philosophical_focus: PhilosophicalFocus
    facts: list[str] = Field(min_length=1)
    sources: list[Source] = Field(min_length=1)
    content_rules: ContentRules


class BrandDuration(StrictModel):
    min_seconds: float = Field(ge=1)
    ideal_seconds: float = Field(ge=1)
    max_seconds: float = Field(ge=1)


class BrandConfig(StrictModel):
    brand_name: str
    language: str
    audience: str
    tone: str
    principles: list[str] = Field(min_length=1)
    duration: BrandDuration
    required_scene_purposes: list[str] = Field(min_length=1)
    forbidden_hook_terms: list[str]


class LLMConfig(StrictModel):
    provider: Literal["openai"]
    model_env: str
    default_model: str
    max_output_tokens: int = Field(ge=1000, le=100000)
    store: bool
    prompt_version: str


class PromptConfig(StrictModel):
    system: str = Field(min_length=1)
    task: str = Field(min_length=1)


class CanvasConfig(StrictModel):
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    fps: int = Field(ge=1, le=120)


class SafeAreaConfig(StrictModel):
    top: int = Field(ge=0)
    right: int = Field(ge=0)
    bottom: int = Field(ge=0)
    left: int = Field(ge=0)


class SubtitleConfig(StrictModel):
    max_chars_per_line: int = Field(ge=1, le=100)
    max_lines: int = Field(ge=1, le=4)
    position_y: int = Field(ge=0)
    font_size: int = Field(ge=1)


class TimelineConfig(StrictModel):
    default_gap_seconds: float = Field(ge=0)
    subtitle_lead_in_seconds: float = Field(ge=0)
    subtitle_tail_seconds: float = Field(ge=0)


class VideoConfig(StrictModel):
    canvas: CanvasConfig
    safe_area: SafeAreaConfig
    subtitle: SubtitleConfig
    timeline: TimelineConfig


class VoiceNormalization(StrictModel):
    target_lufs: float
    true_peak_db: float


class VoiceConfig(StrictModel):
    provider: str
    model: str
    voice: str
    format: Literal["wav", "mp3", "aac", "flac", "opus", "pcm"]
    speed: float = Field(gt=0, le=4)
    instructions: str
    normalization: VoiceNormalization


class ScenePurpose(str, Enum):
    hook = "hook"
    scenario = "scenario"
    setup = "setup"
    consequence = "consequence"
    choice = "choice"
    reveal = "reveal"
    insight = "insight"
    second_question = "second_question"
    cta = "cta"


class HookOption(StrictModel):
    narration: str = Field(min_length=1, max_length=100)
    screen_text: str = Field(min_length=1, max_length=60)
    angle: str = Field(min_length=1, max_length=80)


class Scene(StrictModel):
    id: int = Field(ge=1)
    purpose: ScenePurpose
    narration: str = Field(min_length=1, max_length=300)
    screen_text: str = Field(min_length=1, max_length=100)
    visual_description: str = Field(min_length=1, max_length=300)
    visual_template: str = Field(min_length=1, max_length=80)
    emphasis_words: list[str] = Field(max_length=6)
    duration_seconds: float = Field(ge=0.5, le=15)
    pause_after_seconds: float = Field(ge=0, le=5)


class GeneratedPackage(StrictModel):
    schema_version: Literal["1.0"]
    experiment_id: str = Field(pattern=r"^\d{3}$")
    experiment_title: str = Field(min_length=1)
    working_title: str = Field(min_length=1, max_length=100)
    hook_options: list[HookOption] = Field(min_length=3, max_length=3)
    selected_hook_index: int = Field(ge=0, le=2)
    scenes: list[Scene] = Field(min_length=7, max_length=14)
    caption: str = Field(min_length=1, max_length=600)
    pinned_comment: str = Field(min_length=1, max_length=300)
    hashtags: list[str] = Field(min_length=1, max_length=5)
    editorial_notes: list[str] = Field(max_length=8)

    @model_validator(mode="after")
    def scene_ids_are_contiguous(self) -> "GeneratedPackage":
        ids = [scene.id for scene in self.scenes]
        if ids != list(range(1, len(ids) + 1)):
            raise ValueError("scene ids must be contiguous and start at 1")
        return self

    @property
    def planned_duration_seconds(self) -> float:
        return round(
            sum(scene.duration_seconds + scene.pause_after_seconds for scene in self.scenes),
            3,
        )
