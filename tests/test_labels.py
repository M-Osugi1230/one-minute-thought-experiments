"""Unit tests for experiment label normalization utility."""

from __future__ import annotations

import pytest

from thought_pipeline import normalize_experiment_label
from thought_pipeline.labels import normalize_experiment_label as direct_normalize_experiment_label


def test_normalize_already_clean_label() -> None:
    result = normalize_experiment_label("trolley_problem")
    assert result == {
        "raw_label": "trolley_problem",
        "normalized_label": "trolley_problem",
        "is_changed": False,
        "char_count": 15,
        "word_count": 1,
    }


def test_normalize_surrounding_whitespace() -> None:
    result = normalize_experiment_label("   001_trolley_problem   ")
    assert result == {
        "raw_label": "   001_trolley_problem   ",
        "normalized_label": "001_trolley_problem",
        "is_changed": True,
        "char_count": 19,
        "word_count": 1,
    }


def test_normalize_internal_whitespace_and_newlines() -> None:
    raw = "  001 \t  trolley \n\n  problem  "
    result = normalize_experiment_label(raw)
    assert result["normalized_label"] == "001 trolley problem"
    assert result["is_changed"] is True
    assert result["char_count"] == 19
    assert result["word_count"] == 3
    assert result["raw_label"] == raw


def test_normalize_unicode_japanese_text() -> None:
    raw = "  思考実験   トロッコ  問題  "
    result = normalize_experiment_label(raw)
    assert result["normalized_label"] == "思考実験 トロッコ 問題"
    assert result["is_changed"] is True
    assert result["word_count"] == 3


def test_empty_label_raises_value_error() -> None:
    with pytest.raises(ValueError, match="must not be empty or whitespace-only"):
        normalize_experiment_label("")


def test_whitespace_only_label_raises_value_error() -> None:
    with pytest.raises(ValueError, match="must not be empty or whitespace-only"):
        normalize_experiment_label("   \t \n  ")


@pytest.mark.parametrize("invalid_input", [None, 123, 45.6, [], {"label": "test"}])
def test_non_string_input_raises_value_error(invalid_input: object) -> None:
    with pytest.raises(ValueError, match="must be a string"):
        normalize_experiment_label(invalid_input)  # type: ignore[arg-type]


def test_deterministic_behavior() -> None:
    raw = "  test   label  123 "
    first = normalize_experiment_label(raw)
    second = direct_normalize_experiment_label(raw)
    assert first == second
