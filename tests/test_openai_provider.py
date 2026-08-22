from __future__ import annotations

from types import SimpleNamespace

import openai
import pytest

from thought_pipeline.errors import ConfigurationError
from thought_pipeline.models import GeneratedPackage
from thought_pipeline.prompting import BuiltPrompt
from thought_pipeline.providers import OfflineGoldenProvider, OpenAIStructuredProvider
from thought_pipeline.repository import ProjectRepository


def test_openai_provider_uses_responses_structured_parse(monkeypatch) -> None:
    repository = ProjectRepository()
    golden = OfflineGoldenProvider(repository.root).generate("001", object())
    captured: dict = {}

    class FakeResponses:
        def parse(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_parsed=golden, output=[])

    class FakeClient:
        def __init__(self, **kwargs):
            captured["client_kwargs"] = kwargs
            self.responses = FakeResponses()

    monkeypatch.setattr(openai, "OpenAI", FakeClient)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    provider = OpenAIStructuredProvider(repository.llm())
    result = provider.generate("001", BuiltPrompt(system="system", user="user"))

    assert result.experiment_id == "001"
    assert captured["model"] == "gpt-5.4-mini"
    assert captured["text_format"] is GeneratedPackage
    assert captured["store"] is False
    assert [item["role"] for item in captured["input"]] == ["system", "user"]


def test_openai_provider_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        OpenAIStructuredProvider(ProjectRepository().llm())
