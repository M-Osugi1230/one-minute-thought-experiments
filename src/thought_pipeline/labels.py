"""Deterministic utility for experiment label normalization."""

from __future__ import annotations

import re
from typing import Any


def normalize_experiment_label(label: str) -> dict[str, Any]:
    """Normalize a non-empty experiment label string by collapsing surrounding and internal whitespace.

    Args:
        label: The raw experiment label to normalize. Must be a non-empty string.

    Returns:
        A structured summary dictionary containing normalization details.

    Raises:
        ValueError: If label is not a string, or is empty / whitespace-only.
    """
    if not isinstance(label, str):
        raise ValueError("Experiment label must be a string.")

    raw = label
    normalized = re.sub(r"\s+", " ", raw).strip()

    if not normalized:
        raise ValueError("Experiment label must not be empty or whitespace-only.")

    return {
        "raw_label": raw,
        "normalized_label": normalized,
        "is_changed": raw != normalized,
        "char_count": len(normalized),
        "word_count": len(normalized.split(" ")),
    }
