from dataclasses import FrozenInstanceError

import pytest

from thought_pipeline.models import (
    ExperimentSeriesLabelSummary,
    ExperimentVariantLabelSummary,
    normalize_experiment_series_label,
    normalize_experiment_variant_label,
)


def test_normalize_experiment_series_label_valid_inputs() -> None:
    res = normalize_experiment_series_label("  Thought   Series  ")
    assert res.display_label == "Thought Series"
    assert res.key == "thought-series"

    res_tab_newline = normalize_experiment_series_label("  \t  Thought\n  Series \r ")
    assert res_tab_newline.display_label == "Thought Series"
    assert res_tab_newline.key == "thought-series"

    res_casefold = normalize_experiment_series_label("ß-Series")
    assert res_casefold.display_label == "ß-Series"
    assert res_casefold.key == "ss-series"

    res_unicode = normalize_experiment_series_label("ÉLÉPHANT   TROLLEY")
    assert res_unicode.display_label == "ÉLÉPHANT TROLLEY"
    assert res_unicode.key == "éléphant-trolley"

    res_single = normalize_experiment_series_label("  Single  ")
    assert res_single.display_label == "Single"
    assert res_single.key == "single"


def test_normalize_experiment_series_label_returns_frozen_summary() -> None:
    res = normalize_experiment_series_label("  Thought   Series  ")
    assert isinstance(res, ExperimentSeriesLabelSummary)
    assert res.display_label == "Thought Series"
    assert res.key == "thought-series"

    with pytest.raises((FrozenInstanceError, AttributeError)):
        res.display_label = "Other Series"  # type: ignore[misc]

    with pytest.raises((FrozenInstanceError, AttributeError)):
        res.key = "other-series"  # type: ignore[misc]


@pytest.mark.parametrize(
    "invalid_input",
    [
        None,
        123,
        12.34,
        True,
        ["Thought Series"],
        {"label": "Thought Series"},
    ],
)
def test_normalize_experiment_series_label_rejects_non_string_input(
    invalid_input: object,
) -> None:
    with pytest.raises(TypeError, match="label must be a string"):
        normalize_experiment_series_label(invalid_input)


@pytest.mark.parametrize(
    "empty_input",
    [
        "",
        "   ",
        "\t\n\r",
        "     \n  \t ",
    ],
)
def test_normalize_experiment_series_label_rejects_empty_or_whitespace_input(
    empty_input: str,
) -> None:
    with pytest.raises(ValueError, match="label cannot be empty or whitespace-only"):
        normalize_experiment_series_label(empty_input)


def test_normalize_experiment_variant_label_valid_inputs() -> None:
    res = normalize_experiment_variant_label("  Variant   A  ")
    assert res.display_label == "Variant A"
    assert res.key == "variant-a"

    res_tab_newline = normalize_experiment_variant_label("  \t  Variant\n  A \r ")
    assert res_tab_newline.display_label == "Variant A"
    assert res_tab_newline.key == "variant-a"

    res_casefold = normalize_experiment_variant_label("ß-Variant")
    assert res_casefold.display_label == "ß-Variant"
    assert res_casefold.key == "ss-variant"

    res_unicode = normalize_experiment_variant_label("ÉLÉPHANT   VARIANT")
    assert res_unicode.display_label == "ÉLÉPHANT VARIANT"
    assert res_unicode.key == "éléphant-variant"

    res_unicode_whitespace = normalize_experiment_variant_label("  \u00a0 Variant \u2003 A \u00a0 ")
    assert res_unicode_whitespace.display_label == "Variant A"
    assert res_unicode_whitespace.key == "variant-a"

    res_ideographic_thin_space = normalize_experiment_variant_label(" \u3000 Variant \u2009 A \u3000 ")
    assert res_ideographic_thin_space.display_label == "Variant A"
    assert res_ideographic_thin_space.key == "variant-a"

    res_narrow_nobreak_medium_math = normalize_experiment_variant_label(" \u202f Variant \u205f A \u202f ")
    assert res_narrow_nobreak_medium_math.display_label == "Variant A"
    assert res_narrow_nobreak_medium_math.key == "variant-a"

    res_ogham_figure_space = normalize_experiment_variant_label(" \u1680 Variant \u2007 A \u1680 ")
    assert res_ogham_figure_space.display_label == "Variant A"
    assert res_ogham_figure_space.key == "variant-a"

    res_en_hair_space = normalize_experiment_variant_label(" \u2002 Variant \u200a A \u2002 ")
    assert res_en_hair_space.display_label == "Variant A"
    assert res_en_hair_space.key == "variant-a"

    res_three_six_per_em_space = normalize_experiment_variant_label(" \u2004 Variant \u2006 A \u2004 ")
    assert res_three_six_per_em_space.display_label == "Variant A"
    assert res_three_six_per_em_space.key == "variant-a"

    res_single = normalize_experiment_variant_label("  Variant  ")
    assert res_single.display_label == "Variant"
    assert res_single.key == "variant"


def test_normalize_experiment_variant_label_returns_frozen_summary() -> None:
    res = normalize_experiment_variant_label("  Variant   A  ")
    assert isinstance(res, ExperimentVariantLabelSummary)
    assert res.display_label == "Variant A"
    assert res.key == "variant-a"

    with pytest.raises((FrozenInstanceError, AttributeError)):
        res.display_label = "Other Variant"  # type: ignore[misc]

    with pytest.raises((FrozenInstanceError, AttributeError)):
        res.key = "other-variant"  # type: ignore[misc]


@pytest.mark.parametrize(
    "invalid_input",
    [
        None,
        123,
        12.34,
        True,
        ["Variant A"],
        {"label": "Variant A"},
    ],
)
def test_normalize_experiment_variant_label_rejects_non_string_input(
    invalid_input: object,
) -> None:
    with pytest.raises(TypeError, match="label must be a string"):
        normalize_experiment_variant_label(invalid_input)


@pytest.mark.parametrize(
    "empty_input",
    [
        "",
        "   ",
        "\t\n\r",
        "     \n  \t ",
    ],
)
def test_normalize_experiment_variant_label_rejects_empty_or_whitespace_input(
    empty_input: str,
) -> None:
    with pytest.raises(ValueError, match="label cannot be empty or whitespace-only"):
        normalize_experiment_variant_label(empty_input)
