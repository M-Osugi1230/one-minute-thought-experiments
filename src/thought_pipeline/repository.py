"""Load and validate repository-owned YAML data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from .errors import ConfigurationError, ContentNotFoundError
from .models import (
    BrandConfig,
    Experiment,
    LLMConfig,
    PromptConfig,
    VideoConfig,
    VoiceConfig,
)


ModelT = TypeVar("ModelT", bound=BaseModel)


@dataclass(frozen=True)
class ExperimentRecord:
    id: str
    slug: str
    title: str
    path: Path
    template: str
    status: str


class ProjectRepository:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or Path(__file__).resolve().parents[2]).resolve()

    def _yaml(self, relative_path: str | Path) -> Any:
        path = self.root / relative_path
        if not path.is_file():
            raise ContentNotFoundError(f"ファイルが見つかりません: {path}")
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ConfigurationError(f"YAMLを解析できません: {path}: {exc}") from exc

    def _model(self, relative_path: str, model: type[ModelT]) -> ModelT:
        try:
            return model.model_validate(self._yaml(relative_path))
        except ValidationError as exc:
            raise ConfigurationError(f"設定の形式が不正です: {relative_path}\n{exc}") from exc

    def brand(self) -> BrandConfig:
        return self._model("config/brand.yaml", BrandConfig)

    def llm(self) -> LLMConfig:
        return self._model("config/llm.yaml", LLMConfig)

    def prompts(self) -> PromptConfig:
        return self._model("config/prompts.yaml", PromptConfig)

    def video(self) -> VideoConfig:
        return self._model("config/video.yaml", VideoConfig)

    def voice(self) -> VoiceConfig:
        return self._model("config/voice.yaml", VoiceConfig)

    def experiment_records(self) -> list[ExperimentRecord]:
        data = self._yaml("content/experiments.yaml")
        if not isinstance(data, dict) or not isinstance(data.get("experiments"), list):
            raise ConfigurationError("content/experiments.yaml に experiments 配列が必要です")

        records: list[ExperimentRecord] = []
        for raw in data["experiments"]:
            try:
                records.append(
                    ExperimentRecord(
                        id=str(raw["id"]),
                        slug=str(raw["slug"]),
                        title=str(raw["title"]),
                        path=Path(str(raw["path"])),
                        template=str(raw["template"]),
                        status=str(raw["status"]),
                    )
                )
            except (KeyError, TypeError) as exc:
                raise ConfigurationError(f"思考実験インデックスが不正です: {raw}") from exc

        ids = [record.id for record in records]
        if len(ids) != len(set(ids)):
            raise ConfigurationError("思考実験IDが重複しています")
        return records

    def experiment(self, experiment_id: str) -> Experiment:
        normalized = experiment_id.zfill(3)
        record = next(
            (item for item in self.experiment_records() if item.id == normalized),
            None,
        )
        if record is None:
            raise ContentNotFoundError(f"思考実験ID {normalized} は登録されていません")
        try:
            experiment = Experiment.model_validate(self._yaml(record.path))
        except ValidationError as exc:
            raise ConfigurationError(f"Fact Packが不正です: {record.path}\n{exc}") from exc
        if experiment.id != record.id or experiment.slug != record.slug:
            raise ConfigurationError(
                f"インデックスとFact PackのID/slugが一致しません: {record.path}"
            )
        return experiment

    def validate_all(self) -> list[Experiment]:
        self.brand()
        self.llm()
        self.prompts()
        self.video()
        self.voice()
        return [self.experiment(record.id) for record in self.experiment_records()]
