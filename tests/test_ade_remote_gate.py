from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import types

import pytest


MODULE_PATH = Path(".github/trusted/ade_remote_gate.py")
SPEC = importlib.util.spec_from_file_location("ade_remote_gate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def _pr(head_sha: str = "a" * 40) -> dict:
    return {
        "state": "open",
        "draft": False,
        "body": (
            "Implemented change\n\n"
            "*PR created automatically by Jules for task "
            "[123](https://jules.google.com/task/123) started by @M-Osugi1230*"
        ),
        "head": {
            "ref": "jules-123",
            "sha": head_sha,
            "repo": {"full_name": "M-Osugi1230/one-minute-thought-experiments"},
        },
        "base": {"ref": "main"},
    }


def test_validate_pr_requires_exact_ci_head_sha(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "GITHUB_REPOSITORY",
        "M-Osugi1230/one-minute-thought-experiments",
    )
    with pytest.raises(gate.GateError, match="SHA that passed CI"):
        gate._validate_pr(
            _pr("b" * 40),
            [{"filename": "src/thought_pipeline/labels.py", "status": "added"}],
            allowed_paths=("src/thought_pipeline/labels.py",),
            base_branch="main",
            ci_head_sha="a" * 40,
        )


def test_validate_pr_accepts_only_exact_allowed_files(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "GITHUB_REPOSITORY",
        "M-Osugi1230/one-minute-thought-experiments",
    )
    gate._validate_pr(
        _pr(),
        [{"filename": "src/thought_pipeline/labels.py", "status": "added"}],
        allowed_paths=("src/thought_pipeline/labels.py",),
        base_branch="main",
        ci_head_sha="a" * 40,
    )

    with pytest.raises(gate.GateError, match="outside ADE allowed_paths"):
        gate._validate_pr(
            _pr(),
            [{"filename": "src/thought_pipeline/__init__.py", "status": "modified"}],
            allowed_paths=("src/thought_pipeline/labels.py",),
            base_branch="main",
            ci_head_sha="a" * 40,
        )


def test_remote_receipt_is_authoritative_task_pr_binding() -> None:
    receipt = {
        "schema_version": 1,
        "status": "PR_CREATED",
        "task_id": "v12ext-001",
        "target_repository": "M-Osugi1230/one-minute-thought-experiments",
        "pull_request_url": (
            "https://github.com/M-Osugi1230/one-minute-thought-experiments/pull/5"
        ),
    }
    gate._validate_remote_receipt(
        receipt,
        repository="M-Osugi1230/one-minute-thought-experiments",
        task_id="v12ext-001",
        pr_number=5,
    )

    tampered = dict(receipt)
    tampered["pull_request_url"] = (
        "https://github.com/M-Osugi1230/one-minute-thought-experiments/pull/6"
    )
    with pytest.raises(gate.GateError, match="does not bind"):
        gate._validate_remote_receipt(
            tampered,
            repository="M-Osugi1230/one-minute-thought-experiments",
            task_id="v12ext-001",
            pr_number=5,
        )


def test_pr_file_listing_fetches_all_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_request(method: str, path: str, payload=None):
        assert method == "GET"
        calls.append(path)
        if path.endswith("&page=1"):
            return [
                {"filename": f"tests/test_{index}.py", "status": "added"}
                for index in range(100)
            ]
        if path.endswith("&page=2"):
            return [{"filename": "tests/test_last.py", "status": "added"}]
        raise AssertionError(path)

    monkeypatch.setattr(gate, "_github_request", fake_request)
    files = gate._github_list_pr_files(
        "M-Osugi1230/one-minute-thought-experiments",
        5,
        page_size=100,
    )

    assert len(files) == 101
    assert len(calls) == 2
    assert calls[0].endswith("&page=1")
    assert calls[1].endswith("&page=2")
