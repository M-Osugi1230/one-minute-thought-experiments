"""Orchestrate a single validated Phase 1 generation run."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .artifacts import source_digest, write_artifacts
from .errors import QualityValidationError
from .prompting import BuiltPrompt, build_prompt
from .providers import ScriptProvider
from .quality import ValidationReport, validate_generated_package
from .repository import ProjectRepository
from .timeline import build_srt, build_timeline


@dataclass(frozen=True)
class PipelineResult:
    output_dir: Path
    planned_duration_seconds: float
    report: ValidationReport
    artifacts: list[Path]


class Pipeline:
    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    def prompt(self, experiment_id: str) -> BuiltPrompt:
        return build_prompt(
            self.repository.prompts(),
            self.repository.brand(),
            self.repository.experiment(experiment_id),
        )

    def run(
        self,
        experiment_id: str,
        provider: ScriptProvider,
        output_root: Path,
        overwrite: bool = False,
    ) -> PipelineResult:
        experiment = self.repository.experiment(experiment_id)
        brand = self.repository.brand()
        llm = self.repository.llm()
        video = self.repository.video()
        prompt = build_prompt(self.repository.prompts(), brand, experiment)

        package = provider.generate(experiment.id, prompt)
        report = validate_generated_package(package, experiment, brand)
        if not report.is_valid:
            detail = "\n".join(
                f"- [{issue.code}] {issue.path}: {issue.message}" for issue in report.errors
            )
            raise QualityValidationError(f"生成結果が品質チェックに失敗しました:\n{detail}")

        timeline = build_timeline(package, video)
        srt_text = build_srt(package, timeline, video)
        output_dir = output_root / f"{experiment.id}_{experiment.slug}"
        artifacts = write_artifacts(
            output_dir=output_dir,
            package=package,
            experiment=experiment,
            timeline=timeline,
            srt_text=srt_text,
            report=report,
            provider_name=provider.name,
            model_name=provider.model,
            prompt_version=llm.prompt_version,
            digest=source_digest(experiment, brand, llm.prompt_version),
            overwrite=overwrite,
        )
        return PipelineResult(
            output_dir=output_dir,
            planned_duration_seconds=package.planned_duration_seconds,
            report=report,
            artifacts=artifacts,
        )
