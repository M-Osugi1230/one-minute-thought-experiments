"""Utility for validating and normalizing experiment audience labels."""

from dataclasses import dataclass
from typing import Any


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
