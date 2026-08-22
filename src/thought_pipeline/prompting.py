"""Build a reviewable, versioned prompt from repository data."""

from __future__ import annotations

from dataclasses import dataclass

import yaml

from .models import BrandConfig, Experiment, PromptConfig


@dataclass(frozen=True)
class BuiltPrompt:
    system: str
    user: str


def _yaml_text(data: dict) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip()


def build_prompt(
    prompts: PromptConfig,
    brand: BrandConfig,
    experiment: Experiment,
) -> BuiltPrompt:
    """Render only trusted repository data into the prompt template."""
    user = prompts.task.format(
        brand_yaml=_yaml_text(brand.model_dump(mode="json")),
        experiment_yaml=_yaml_text(experiment.model_dump(mode="json")),
    )
    return BuiltPrompt(system=prompts.system, user=user)
