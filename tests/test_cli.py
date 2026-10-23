from __future__ import annotations

import pytest

from thought_pipeline.cli import main


def test_numeric_experiment_id_shorthand(tmp_path) -> None:
    code = main(["001", "--offline", "--output-root", str(tmp_path)])
    assert code == 0
    output_dir = tmp_path / "001_trolley_problem"
    assert (output_dir / "script.json").is_file()


def test_explicit_valid_commands(tmp_path) -> None:
    assert main(["validate"]) == 0
    assert main(["list"]) == 0
    assert main(["generate", "001", "--offline", "--output-root", str(tmp_path), "--overwrite"]) == 0


def test_mistyped_command_fails_fast() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["valdate"])
    assert exc_info.value.code == 2

    with pytest.raises(SystemExit) as exc_info:
        main(["genrate", "001"])
    assert exc_info.value.code == 2
