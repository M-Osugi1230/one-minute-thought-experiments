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
        "base": {"ref": "main", "sha": "c" * 40},
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

def _v17_review_payloads() -> dict[str, dict]:
    repository = "M-Osugi1230/one-minute-thought-experiments"
    task_id = "v17proof-001"
    accepted_fp = "1" * 64
    base_sha = "a" * 40
    head_sha = "b" * 40
    implementer = {
        "schema_version": 1,
        "assignment_id": "implementer",
        "role": "IMPLEMENTER",
        "provider_id": "jules",
        "repository": repository,
        "source_sha": base_sha,
        "campaign_id": "campaign-001",
        "task_id": task_id,
        "accepted_plan_fingerprint": accepted_fp,
        "objective": "Implement frozen scope.",
        "evidence_paths": [".autodev/accepted-plan.json"],
        "evidence_fingerprints": ["2" * 64],
        "execution_authority": False,
        "auto_dispatch": False,
        "merge_authority": False,
        "acceptance_authority": False,
        "may_expand_scope": False,
    }
    reviewer = {
        **implementer,
        "assignment_id": "reviewer",
        "role": "REVIEWER",
        "objective": "Review frozen scope.",
    }
    plan = {
        "schema_version": 1,
        "plan_id": "multi-agent-plan-001",
        "repository": repository,
        "source_sha": base_sha,
        "campaign_id": "campaign-001",
        "task_id": task_id,
        "accepted_plan_fingerprint": accepted_fp,
        "assignments": [implementer, reviewer],
        "provider_ids": ["jules"],
        "execution_authority": False,
        "auto_dispatch": False,
        "merge_authority": False,
        "acceptance_authority": False,
        "may_expand_scope": False,
    }
    plan_fp = gate._canonical_fingerprint(plan)
    reviewer_fp = gate._canonical_fingerprint(reviewer)
    session = {
        "schema_version": 1,
        "plan_fingerprint": plan_fp,
        "assignment_fingerprint": reviewer_fp,
        "assignment_id": "reviewer",
        "role": "REVIEWER",
        "provider_id": "jules",
        "repository": repository,
        "source_sha": base_sha,
        "campaign_id": "campaign-001",
        "task_id": task_id,
        "accepted_plan_fingerprint": accepted_fp,
        "state": "COMPLETED",
        "provider_session_id": "review-session-001",
        "attempt": 1,
        "resume_after": None,
        "execution_authority": False,
        "merge_authority": False,
        "acceptance_authority": False,
        "may_expand_scope": False,
    }
    contribution = {
        "schema_version": 1,
        "contribution_id": "contribution-001",
        "kind": "REVIEW",
        "verdict": "CLEAR",
        "repository": repository,
        "source_sha": base_sha,
        "campaign_id": "campaign-001",
        "task_id": task_id,
        "accepted_plan_fingerprint": accepted_fp,
        "multi_agent_plan_fingerprint": plan_fp,
        "assignment_id": "reviewer",
        "assignment_fingerprint": reviewer_fp,
        "role": "REVIEWER",
        "provider_id": "jules",
        "summary": "Independent review is clear.",
        "evidence_paths": [".autodev/multi-agent/reviewer-observation.json"],
        "evidence_fingerprints": ["3" * 64],
        "advisory_only": True,
        "execution_authority": False,
        "code_mutation_authority": False,
        "campaign_state_authority": False,
        "acceptance_authority": False,
        "merge_authority": False,
        "runtime_verification_authority": False,
        "auto_dispatch": False,
        "may_expand_scope": False,
    }
    contribution_fp = gate._canonical_fingerprint(contribution)
    reconciliation = {
        "schema_version": 1,
        "repository": repository,
        "source_sha": base_sha,
        "campaign_id": "campaign-001",
        "task_id": task_id,
        "accepted_plan_fingerprint": accepted_fp,
        "multi_agent_plan_fingerprint": plan_fp,
        "contribution_fingerprints": [contribution_fp],
        "disposition": "CLEAR",
        "reason": "ALL_CLEAR",
        "policy_fingerprint": "4" * 64,
        "human_decision_id": None,
        "majority_voting": False,
        "execution_authority": False,
        "merge_authority": False,
        "acceptance_authority": False,
        "runtime_verification_authority": False,
    }
    session_fp = gate._canonical_fingerprint(session)
    reconciliation_fp = gate._canonical_fingerprint(reconciliation)
    clearance = {
        "schema_version": 1,
        "clearance_id": "review-clearance-001",
        "task_id": task_id,
        "target_repository": repository,
        "plan_source_sha": base_sha,
        "reviewed_head_sha": head_sha,
        "pull_request_number": 21,
        "accepted_plan_fingerprint": accepted_fp,
        "multi_agent_plan_fingerprint": plan_fp,
        "reviewer_assignment_id": "reviewer",
        "reviewer_assignment_fingerprint": reviewer_fp,
        "reviewer_role_session_fingerprint": session_fp,
        "contribution_fingerprint": contribution_fp,
        "reconciliation_fingerprint": reconciliation_fp,
        "reviewer_provider_id": "jules",
        "verdict": "CLEAR",
        "advisory_evidence_only": True,
        "execution_authority": False,
        "code_mutation_authority": False,
        "campaign_state_authority": False,
        "merge_authority": False,
        "acceptance_authority": False,
        "runtime_verification_authority": False,
        "auto_dispatch": False,
        "may_expand_scope": False,
    }
    checkpoint = {
        "task_id": task_id,
        "state": "COMPLETED",
        "provider_session_id": "implement-session-001",
    }
    return {
        "plan": plan,
        "session": session,
        "contribution": contribution,
        "reconciliation": reconciliation,
        "clearance": clearance,
        "checkpoint": checkpoint,
        "accepted_fp": accepted_fp,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "task_id": task_id,
        "repository": repository,
    }


def _install_v17_review_payloads(
    monkeypatch: pytest.MonkeyPatch,
    values: dict[str, dict],
) -> None:
    mapping = {
        ".autodev/multi-agent/plan.json": values["plan"],
        ".autodev/multi-agent/reviewer-session.json": values["session"],
        ".autodev/multi-agent/reviewer-contribution.json": values["contribution"],
        ".autodev/multi-agent/reconciliation.json": values["reconciliation"],
        ".autodev/runtime/checkpoint.json": values["checkpoint"],
    }
    monkeypatch.setattr(
        gate,
        "_ade_optional_json",
        lambda path, ref: (
            values["clearance"]
            if path == ".autodev/multi-agent/review-clearance.json"
            else None
        ),
    )
    monkeypatch.setattr(gate, "_ade_json", lambda path, ref: mapping[path])


def test_v17_review_chain_requires_exact_clear_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    values = _v17_review_payloads()
    _install_v17_review_payloads(monkeypatch, values)
    assert gate._validate_v1_7_review_chain(
        ade_ref="f" * 40,
        repository=values["repository"],
        task_id=values["task_id"],
        accepted_fingerprint=values["accepted_fp"],
        pr_number=21,
        pr_head_sha=values["head_sha"],
        pr_base_sha=values["base_sha"],
    )


def test_v17_review_chain_waits_when_clearance_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(gate, "_ade_optional_json", lambda path, ref: None)
    assert (
        gate._validate_v1_7_review_chain(
            ade_ref="f" * 40,
            repository="M-Osugi1230/one-minute-thought-experiments",
            task_id="v17proof-001",
            accepted_fingerprint="1" * 64,
            pr_number=21,
            pr_head_sha="b" * 40,
            pr_base_sha="a" * 40,
        )
        is False
    )


def test_v17_review_chain_rejects_stale_head_and_shared_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    values = _v17_review_payloads()
    _install_v17_review_payloads(monkeypatch, values)
    with pytest.raises(gate.GateError, match="does not bind"):
        gate._validate_v1_7_review_chain(
            ade_ref="f" * 40,
            repository=values["repository"],
            task_id=values["task_id"],
            accepted_fingerprint=values["accepted_fp"],
            pr_number=21,
            pr_head_sha="e" * 40,
            pr_base_sha=values["base_sha"],
        )

    values["checkpoint"] = {
        **values["checkpoint"],
        "provider_session_id": "review-session-001",
    }
    _install_v17_review_payloads(monkeypatch, values)
    with pytest.raises(gate.GateError, match="independent provider session"):
        gate._validate_v1_7_review_chain(
            ade_ref="f" * 40,
            repository=values["repository"],
            task_id=values["task_id"],
            accepted_fingerprint=values["accepted_fp"],
            pr_number=21,
            pr_head_sha=values["head_sha"],
            pr_base_sha=values["base_sha"],
        )


def test_v17_review_chain_rejects_authority_escalation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    values = _v17_review_payloads()
    values["contribution"] = {
        **values["contribution"],
        "merge_authority": True,
    }
    _install_v17_review_payloads(monkeypatch, values)
    with pytest.raises(gate.GateError, match="merge_authority"):
        gate._validate_v1_7_review_chain(
            ade_ref="f" * 40,
            repository=values["repository"],
            task_id=values["task_id"],
            accepted_fingerprint=values["accepted_fp"],
            pr_number=21,
            pr_head_sha=values["head_sha"],
            pr_base_sha=values["base_sha"],
        )

