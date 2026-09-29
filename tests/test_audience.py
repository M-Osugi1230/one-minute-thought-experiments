from __future__ import annotations

import pytest

from thought_pipeline.audience import normalize_audience_label


@pytest.mark.parametrize(
    "value",
    [123, None, ["General"], {"audience": "Tech"}, 4.5, True],
)
def test_normalize_audience_label_rejects_non_string(value: object) -> None:
    with pytest.raises(TypeError, match="Audience label must be a string"):
        normalize_audience_label(value)


@pytest.mark.parametrize("value", ["", "   ", "\t\n\r  ", "  \n  "])
def test_normalize_audience_label_rejects_empty_or_whitespace(value: str) -> None:
    with pytest.raises(ValueError, match="Audience label cannot be empty or whitespace-only"):
        normalize_audience_label(value)


def test_normalize_audience_label_collapses_whitespace_and_preserves_display_case() -> None:
    summary = normalize_audience_label("\tAI &  Data Science   Enthusiasts \n")
    assert summary.display_label == "AI & Data Science Enthusiasts"
    assert summary.key == "ai-&-data-science-enthusiasts"


def test_normalize_audience_label_uses_unicode_case_folding_for_key() -> None:
    summary = normalize_audience_label("  GROßE   STRAßE  ")
    assert summary.display_label == "GROßE STRAßE"
    assert summary.key == "grosse-strasse"
