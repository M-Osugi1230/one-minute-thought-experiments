"""Script-generation providers: OpenAI Structured Outputs and offline fixture."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Protocol

from pydantic import ValidationError

from .errors import ConfigurationError, GenerationError
from .models import GeneratedPackage, LLMConfig
from .prompting import BuiltPrompt


class ScriptProvider(Protocol):
    name: str
    model: str

    def generate(self, experiment_id: str, prompt: BuiltPrompt) -> GeneratedPackage:
        ...


class OfflineGoldenProvider:
    """Deterministic provider used for setup checks, tests, and editorial baselines."""

    name = "offline-golden"
    model = "golden-sample-v1"

    def __init__(self, project_root: Path, variant: str | None = None) -> None:
        self.project_root = project_root
        self.variant = variant
        if variant:
            self.model = f"golden-sample-v1:{variant}"

    def generate(self, experiment_id: str, prompt: BuiltPrompt) -> GeneratedPackage:
        del prompt
        root = self.project_root / "content" / "golden"
        if self.variant:
            root = root / "variants" / self.variant
        path = root / f"{experiment_id}.json"
        if not path.is_file():
            raise GenerationError(f"オフラインサンプルがありません: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return GeneratedPackage.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise GenerationError(f"オフラインサンプルが不正です: {path}\n{exc}") from exc


class OpenAIStructuredProvider:
    """Use Responses API parsing so malformed JSON never enters the pipeline."""

    name = "openai-responses"

    def __init__(self, config: LLMConfig) -> None:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY が未設定です。.env を設定するか --offline を使用してください。"
            )
        self.config = config
        self.api_key = api_key
        self.model = os.getenv(config.model_env, config.default_model).strip()
        if not self.model:
            self.model = config.default_model

    def generate(self, experiment_id: str, prompt: BuiltPrompt) -> GeneratedPackage:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": prompt.system},
                    {"role": "user", "content": prompt.user},
                ],
                text_format=GeneratedPackage,
                max_output_tokens=self.config.max_output_tokens,
                store=self.config.store,
            )
        except Exception as exc:  # SDK errors vary by version and HTTP failure type.
            raise GenerationError(f"OpenAI APIで台本を生成できませんでした: {exc}") from exc

        parsed = response.output_parsed
        if parsed is None:
            refusal = _find_refusal(response)
            detail = f" 拒否理由: {refusal}" if refusal else ""
            raise GenerationError(f"構造化された台本が返りませんでした。{detail}".strip())
        if parsed.experiment_id != experiment_id:
            raise GenerationError(
                f"生成結果のexperiment_idが不一致です: {parsed.experiment_id} != {experiment_id}"
            )
        return parsed


def _find_refusal(response: object) -> str | None:
    for output in getattr(response, "output", []) or []:
        for item in getattr(output, "content", []) or []:
            if getattr(item, "type", None) == "refusal":
                return str(getattr(item, "refusal", ""))
    return None
