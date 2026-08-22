"""Editorial and timing checks that are stricter than the JSON schema."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .models import BrandConfig, Experiment, GeneratedPackage, ScenePurpose


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    path: str
    severity: str = "error"


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "errors": [issue.__dict__ for issue in self.errors],
            "warnings": [issue.__dict__ for issue in self.warnings],
        }


def _normalized(text: str) -> str:
    return re.sub(r"[\s、。！？!?「」『』・—―]+", "", text).casefold()


def validate_generated_package(
    package: GeneratedPackage,
    experiment: Experiment,
    brand: BrandConfig,
) -> ValidationReport:
    report = ValidationReport()

    def add(code: str, message: str, path: str, severity: str = "error") -> None:
        report.issues.append(ValidationIssue(code, message, path, severity))

    if package.experiment_id != experiment.id:
        add("experiment_id_mismatch", "Fact PackのIDと一致しません", "experiment_id")
    if package.experiment_title != experiment.title:
        add("experiment_title_mismatch", "Fact Packのタイトルと一致しません", "experiment_title")

    min_duration = max(brand.duration.min_seconds, experiment.target_duration.min_seconds)
    max_duration = min(brand.duration.max_seconds, experiment.target_duration.max_seconds)
    duration = package.planned_duration_seconds
    if not min_duration <= duration <= max_duration:
        add(
            "duration_out_of_range",
            f"予定尺 {duration:.1f}秒 は許容範囲 {min_duration:.1f}〜{max_duration:.1f}秒外です",
            "scenes",
        )

    purposes = [scene.purpose.value for scene in package.scenes]
    for required in brand.required_scene_purposes:
        if required not in purposes:
            add("missing_scene_purpose", f"{required} シーンがありません", "scenes")

    if package.scenes[0].purpose is not ScenePurpose.hook:
        add("first_scene_not_hook", "最初のシーンはhookである必要があります", "scenes.0.purpose")

    selected = package.hook_options[package.selected_hook_index]
    if _normalized(selected.narration) != _normalized(package.scenes[0].narration):
        add(
            "selected_hook_mismatch",
            "選択したHookと最初のナレーションが一致しません",
            "selected_hook_index",
        )
    if _normalized(selected.screen_text) != _normalized(package.scenes[0].screen_text):
        add(
            "selected_hook_screen_mismatch",
            "選択したHookと最初の画面テキストが一致しません",
            "selected_hook_index",
        )

    normalized_hooks = [_normalized(hook.narration) for hook in package.hook_options]
    if len(normalized_hooks) != len(set(normalized_hooks)):
        add("duplicate_hooks", "Hook 3案に重複があります", "hook_options")

    for index, hook in enumerate(package.hook_options):
        hook_text = f"{hook.narration} {hook.screen_text}"
        if experiment.title in hook_text:
            add("title_in_hook", "冒頭Hookで思考実験名を公開しています", f"hook_options.{index}")
        for term in brand.forbidden_hook_terms:
            if term in hook_text:
                add(
                    "forbidden_hook_term",
                    f"冒頭Hookに禁止語「{term}」が含まれます",
                    f"hook_options.{index}",
                )

    first_text = f"{package.scenes[0].narration} {package.scenes[0].screen_text}"
    if "あなた" not in first_text:
        add("viewer_not_addressed", "冒頭で視聴者を当事者化できていません", "scenes.0")
    if experiment.title in first_text:
        add("title_in_first_scene", "最初のシーンで思考実験名を公開しています", "scenes.0")
    for term in brand.forbidden_hook_terms:
        if term in first_text:
            add(
                "forbidden_term_in_first_scene",
                f"最初のシーンに禁止語「{term}」が含まれます",
                "scenes.0",
            )

    indices = {purpose: purposes.index(purpose) for purpose in set(purposes)}
    expected_order = brand.required_scene_purposes
    if all(purpose in indices for purpose in expected_order):
        positions = [indices[purpose] for purpose in expected_order]
        if positions != sorted(positions):
            add(
                "scene_order_invalid",
                "必須シーンの順序がブランド構成と一致しません",
                "scenes",
            )
    if "choice" in indices and "reveal" in indices and indices["reveal"] <= indices["choice"]:
        add("reveal_before_choice", "名称公開は選択の後に置いてください", "scenes")
    if (
        "second_question" in indices
        and "cta" in indices
        and indices["cta"] <= indices["second_question"]
    ):
        add("cta_before_second_question", "CTAは第二の問いの後に置いてください", "scenes")

    reveal_text = " ".join(
        f"{scene.narration} {scene.screen_text}"
        for scene in package.scenes
        if scene.purpose is ScenePurpose.reveal
    )
    if experiment.title not in reveal_text:
        add("missing_title_reveal", "revealで思考実験名を公開していません", "scenes")

    choice_text = " ".join(
        f"{scene.narration} {scene.screen_text}"
        for scene in package.scenes
        if scene.purpose is ScenePurpose.choice
    )
    if not ("A" in choice_text and "B" in choice_text):
        add("missing_ab_choice", "choiceでA/Bを明示していません", "scenes")
    choice_pause = sum(
        scene.pause_after_seconds
        for scene in package.scenes
        if scene.purpose is ScenePurpose.choice
    )
    if choice_pause < 1.5:
        add(
            "choice_pause_too_short",
            "視聴者が回答する間は1.5秒以上必要です",
            "scenes",
        )

    second_question_text = " ".join(
        f"{scene.narration} {scene.screen_text}"
        for scene in package.scenes
        if scene.purpose is ScenePurpose.second_question
    )
    important_terms = [
        term
        for term in ("家族", "子ども", "親友", "犯罪者", "AI")
        if term in experiment.variation_question
    ]
    for term in important_terms:
        if term not in second_question_text:
            add(
                "variation_missing",
                f"第二の問いに条件語「{term}」がありません",
                "scenes",
            )

    cta_text = " ".join(
        f"{scene.narration} {scene.screen_text}"
        for scene in package.scenes
        if scene.purpose is ScenePurpose.cta
    )
    if not ("A" in cta_text and "B" in cta_text):
        add("cta_missing_ab", "CTAでA/Bを再掲していません", "scenes")
    if not any(term in cta_text for term in ("理由", "なぜ", "一言")):
        add("cta_missing_reason", "CTAで短い理由を求めていません", "scenes")
    if not any(term in cta_text for term in ("変わ", "最初", "矢印", "→")):
        add(
            "cta_missing_answer_change",
            "CTAで最初と条件変更後の回答変化を回収していません",
            "scenes",
            severity="warning",
        )

    planned_cursor = 0.0
    second_question_start = None
    for index, scene in enumerate(package.scenes):
        if scene.purpose is ScenePurpose.reveal and scene.duration_seconds > 3.0:
            add(
                "reveal_too_long",
                "名称公開が3秒を超えています。論点と並行して短く表示してください",
                f"scenes.{index}.duration_seconds",
                severity="warning",
            )
        chars_per_second = len(_normalized(scene.narration)) / scene.duration_seconds
        if chars_per_second > 7.0:
            add(
                "planned_speech_too_dense",
                f"予定読み上げ密度が高すぎます（{chars_per_second:.1f}文字/秒）",
                f"scenes.{index}.duration_seconds",
                severity="warning",
            )
        if scene.purpose is ScenePurpose.second_question:
            second_question_start = planned_cursor
        planned_cursor += scene.duration_seconds + scene.pause_after_seconds
    if (
        second_question_start is not None
        and duration > 0
        and second_question_start / duration > 0.72
    ):
        add(
            "second_question_too_late",
            "条件変更が動画の72%より後です。独自の見せ場を前倒ししてください",
            "scenes",
            severity="warning",
        )

    for index, hashtag in enumerate(package.hashtags):
        if hashtag.startswith("#"):
            add(
                "hashtag_contains_hash",
                "hashtagsには#を含めず保存してください",
                f"hashtags.{index}",
            )
    normalized_hashtags = [_normalized(tag) for tag in package.hashtags]
    if len(normalized_hashtags) != len(set(normalized_hashtags)):
        add("duplicate_hashtags", "hashtagsに重複があります", "hashtags")

    if duration < brand.duration.ideal_seconds - 8:
        add(
            "duration_short_of_ideal",
            "予定尺がブランド理想尺よりかなり短めです",
            "scenes",
            severity="warning",
        )

    return report
