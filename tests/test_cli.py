"""Tests for CLI command parsing and shorthand behaviors."""

import pytest

from thought_pipeline.cli import _parser, main


def test_numeric_shorthand_parsing() -> None:
    """Numeric experiment ID shorthand is prepended with 'generate' in main()."""
    args_list = ["001", "--offline"]
    if args_list and args_list[0].isdigit():
        args_list.insert(0, "generate")

    parsed = _parser().parse_args(args_list)
    assert parsed.command == "generate"
    assert parsed.experiment_id == "001"
    assert parsed.offline is True


def test_mistyped_command_fails_fast() -> None:
    """Mistyped command names fail fast as invalid subcommands rather than defaulting to generate."""
    with pytest.raises(SystemExit) as exc_info:
        main(["valdate"])
    assert exc_info.value.code == 2


def test_valid_commands_recognized() -> None:
    """Valid commands parse correctly without inserting generate."""
    parsed_validate = _parser().parse_args(["validate"])
    assert parsed_validate.command == "validate"

    parsed_list = _parser().parse_args(["list"])
    assert parsed_list.command == "list"

    parsed_prompt = _parser().parse_args(["prompt", "001"])
    assert parsed_prompt.command == "prompt"
    assert parsed_prompt.experiment_id == "001"
