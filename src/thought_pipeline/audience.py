"""Utility for validating and normalizing experiment audience labels."""

from dataclasses import dataclass
from typing import Any

import pytest


@dataclass(frozen=True)
class AudienceLabelSummary:
    """Structured summary containing the normalized display label and stable key."""

    display_label: str
    key: str


def normalize_audience_label(label: Any) -> AudienceLabelSummary:
    """Validate and normalize a non-empty experiment audience label.

    - Rejects non-string inputs with TypeError.
    - Rejects empty or whitespace-only inputs with ValueError.
    - Display label collapses surrounding and internal whitespace, preserving letter case.
    - Key uses Unicode case folding and replaces spaces with hyphens.
    """
    if not isinstance(label, str):
        raise TypeError(f"Audience label must be a string, got {type(label).__name__}")

    words = label.split()
    if not words:
        raise ValueError("Audience label cannot be empty or whitespace-only")

    display_label = " ".join(words)
    key = display_label.casefold().replace(" ", "-")

    return AudienceLabelSummary(display_label=display_label, key=key)


# Focused unit tests


def test_normalize_audience_label_rejects_non_string():
    invalid_inputs = [123, None, ["General"], {"audience": "Tech"}, 4.5, True]
    for val in invalid_inputs:
        with pytest.raises(TypeError, match="Audience label must be a string"):
            normalize_audience_label(val)


def test_normalize_audience_label_rejects_empty_or_whitespace():
    empty_inputs = ["", "   ", "\t\n\r  ", "  \n  "]
    for val in empty_inputs:
        with pytest.raises(ValueError, match="Audience label cannot be empty or whitespace-only"):
            normalize_audience_label(val)


def test_normalize_audience_label_valid():
    summary = normalize_audience_label("  General   Audience  ")
    assert summary.display_label == "General Audience"
    assert summary.key == "general-audience"


def test_normalize_audience_label_preserves_case_in_display_label():
    summary = normalize_audience_label("\tAI &  Data Science   Enthusiasts \n")
    assert summary.display_label == "AI & Data Science Enthusiasts"
    assert summary.key == "ai-&-data-science-enthusiasts"


def test_normalize_audience_label_unicode_case_folding():
    summary = normalize_audience_label("  GROßE   STRAßE  ")
    assert summary.display_label == "GROßE STRAßE"
    assert summary.key == "grosse-strasse"
