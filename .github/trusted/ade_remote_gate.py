from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ADE_RAW_BASE = (
    "https://raw.githubusercontent.com/"
    "M-Osugi1230/autonomous-development-engine/main"
)
JULES_PROVENANCE_MARKER = "PR created automatically by Jules for task"
JULES_TASK_URL = re.compile(r"https://jules\.google\.com/task/\d+")


class GateError(RuntimeError):
    pass


def _load_event() -> dict[str, Any]:
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        raise GateError("GITHUB_EVENT_PATH is required")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise GateError("workflow event must be a JSON object")
    return payload


def _github_request(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    token = os.environ.get("GITHUB_TOKEN", "")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    if not token:
        raise GateError("GITHUB_TOKEN is required")
    if "/" not in repository:
        raise GateError("GITHUB_REPOSITORY must be owner/name")

    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ADE-Remote-PR-Gate/1.0",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"

    request = Request(
        "https://api.github.com" + path,
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GateError(f"GitHub HTTP {exc.code}: {detail[:800]}") from exc
    except URLError as exc:
        raise GateError(f"GitHub network error: {exc.reason}") from exc

    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise GateError("GitHub returned invalid JSON") from exc


def _ade_json(relative_path: str) -> dict[str, Any]:
    url = ADE_RAW_BASE + "/" + relative_path.lstrip("/")
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "User-Agent": "ADE-Remote-PR-Gate/1.0",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GateError(f"ADE contract HTTP {exc.code}: {detail[:500]}") from exc
    except URLError as exc:
        raise GateError(f"ADE contract network error: {exc.reason}") from exc
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise GateError(f"ADE contract {relative_path} is invalid JSON") from exc
    if not isinstance(payload, dict):
        raise GateError(f"ADE contract {relative_path} must be a JSON object")
    return payload


def _current_contract() -> tuple[str, tuple[str, ...], str]:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    state = _ade_json(".autodev/state.json")
    accepted = _ade_json(".autodev/accepted-plan.json")
    campaign = _ade_json(".autodev/campaign.json")
    graph = _ade_json(".autodev/task-graph.json")

    metadata = state.get("metadata")
    if not isinstance(metadata, dict):
        raise GateError("ADE state metadata is invalid")
    if metadata.get("target_repository") != repository:
        raise GateError("ADE current target_repository does not match this repository")

    task_id = state.get("current_task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        raise GateError("ADE has no current external task")
    if state.get("status") not in {"READY", "RUNNING"}:
        raise GateError(f"ADE project state is not executable: {state.get('status')}")

    accepted_fingerprint = accepted.get("fingerprint")
    if accepted.get("status") != "ACCEPTED" or not isinstance(
        accepted_fingerprint, str
    ):
        raise GateError("ADE AcceptedPlan is not accepted")
    if metadata.get("accepted_plan_fingerprint") != accepted_fingerprint:
        raise GateError("ADE state and AcceptedPlan fingerprint do not reconcile")

    plan = accepted.get("plan")
    if not isinstance(plan, dict):
        raise GateError("ADE AcceptedPlan plan is invalid")
    tasks = plan.get("tasks")
    if not isinstance(tasks, list):
        raise GateError("ADE AcceptedPlan tasks are invalid")

    task: dict[str, Any] | None = None
    for candidate in tasks:
        if isinstance(candidate, dict) and candidate.get("task_id") == task_id:
            task = candidate
            break
    if task is None:
        raise GateError("ADE current task is absent from AcceptedPlan")

    allowed = task.get("allowed_paths")
    if not isinstance(allowed, list) or not allowed:
        raise GateError("ADE current task has no allowed_paths")
    allowed_paths: list[str] = []
    for value in allowed:
        if not isinstance(value, str) or not value.strip():
            raise GateError("ADE allowed_paths contains an invalid value")
        if value.startswith("/") or ".." in value.split("/") or value.startswith(
            (".github/", ".autodev/")
        ):
            raise GateError(f"ADE allowed path is unsafe: {value}")
        allowed_paths.append(value)

    campaign_id = metadata.get("campaign_id")
    if campaign.get("campaign_id") != campaign_id:
        raise GateError("ADE Campaign id does not reconcile with project state")
    if campaign.get("status") != "RUNNING":
        raise GateError("ADE Campaign is not RUNNING")
    campaign_tasks = campaign.get("task_ids")
    completed = campaign.get("completed_task_ids")
    if not isinstance(campaign_tasks, list) or task_id not in campaign_tasks:
        raise GateError("ADE current task is absent from Campaign")
    if isinstance(completed, list) and task_id in completed:
        raise GateError("ADE current task is already completed")

    graph_tasks = graph.get("tasks")
    if not isinstance(graph_tasks, list):
        raise GateError("ADE task graph is invalid")
    graph_node: dict[str, Any] | None = None
    for node in graph_tasks:
        if not isinstance(node, dict):
            continue
        raw_task = node.get("task")
        if isinstance(raw_task, dict) and raw_task.get("task_id") == task_id:
            graph_node = node
            break
    if graph_node is None or graph_node.get("status") != "RUNNING":
        raise GateError("ADE current task is not RUNNING in Task DAG")

    base_branch = metadata.get("target_base_branch", "main")
    if not isinstance(base_branch, str) or not base_branch.strip():
        raise GateError("ADE target base branch is invalid")
    return task_id, tuple(allowed_paths), base_branch


def _validate_pr(
    pr: dict[str, Any],
    files: list[dict[str, Any]],
    *,
    allowed_paths: tuple[str, ...],
    base_branch: str,
) -> None:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    if pr.get("state") != "open":
        raise GateError("pull request is not open")
    if pr.get("draft") is True:
        raise GateError("draft pull request cannot be auto-merged")

    head = pr.get("head")
    if not isinstance(head, dict):
        raise GateError("pull request head is missing")
    head_repo = head.get("repo")
    if not isinstance(head_repo, dict) or head_repo.get("full_name") != repository:
        raise GateError("pull request head repository does not match target repository")
    head_ref = head.get("ref")
    if not isinstance(head_ref, str) or head_ref in {"main", "master"}:
        raise GateError("pull request head branch is invalid")

    base = pr.get("base")
    if not isinstance(base, dict) or base.get("ref") != base_branch:
        raise GateError("pull request base branch does not match ADE contract")

    body = pr.get("body")
    if not isinstance(body, str):
        raise GateError("Jules provenance marker is missing")
    if JULES_PROVENANCE_MARKER not in body or JULES_TASK_URL.search(body) is None:
        raise GateError("Jules provenance marker or task URL is missing")

    if not files:
        raise GateError("pull request changes no files")
    allowed = set(allowed_paths)
    for changed in files:
        filename = changed.get("filename")
        status = changed.get("status")
        if not isinstance(filename, str):
            raise GateError("changed file has no filename")
        if status not in {"added", "modified"}:
            raise GateError(f"remote gate forbids file status {status}: {filename}")
        if filename not in allowed:
            raise GateError(f"file is outside ADE allowed_paths: {filename}")


def main() -> int:
    try:
        event = _load_event()
        workflow_run = event.get("workflow_run")
        if not isinstance(workflow_run, dict):
            print("SKIP: no workflow_run payload")
            return 0
        if workflow_run.get("event") != "pull_request":
            print("SKIP: target CI was not triggered by a pull request")
            return 0
        if workflow_run.get("conclusion") != "success":
            print("WAIT: target CI is not green")
            return 0

        pull_requests = workflow_run.get("pull_requests")
        if not isinstance(pull_requests, list) or len(pull_requests) != 1:
            print("SKIP: expected exactly one associated pull request")
            return 0
        pr_number = pull_requests[0].get("number")
        if not isinstance(pr_number, int):
            raise GateError("associated pull request number is missing")

        repository = os.environ.get("GITHUB_REPOSITORY", "")
        pr = _github_request("GET", f"/repos/{repository}/pulls/{pr_number}")
        if not isinstance(pr, dict):
            raise GateError("pull request response must be an object")
        files_payload = _github_request(
            "GET",
            f"/repos/{repository}/pulls/{pr_number}/files?per_page=100",
        )
        if not isinstance(files_payload, list):
            raise GateError("pull request files response must be a list")
        files = [item for item in files_payload if isinstance(item, dict)]

        task_id, allowed_paths, base_branch = _current_contract()
        _validate_pr(
            pr,
            files,
            allowed_paths=allowed_paths,
            base_branch=base_branch,
        )

        head = pr.get("head")
        expected_sha = head.get("sha") if isinstance(head, dict) else None
        if not isinstance(expected_sha, str) or not expected_sha:
            raise GateError("pull request head SHA is missing")

        merge = _github_request(
            "PUT",
            f"/repos/{repository}/pulls/{pr_number}/merge",
            {
                "sha": expected_sha,
                "merge_method": "squash",
                "commit_title": f"ADE remote autonomous merge: PR #{pr_number}",
            },
        )
        if not isinstance(merge, dict) or merge.get("merged") is not True:
            raise GateError(f"GitHub did not merge PR #{pr_number}: {merge}")

        print(
            f"MERGED: ADE remote task {task_id} via target PR #{pr_number}; "
            f"scope={list(allowed_paths)}"
        )
        return 0
    except (GateError, ValueError, KeyError, json.JSONDecodeError, OSError) as exc:
        print(f"HUMAN_WAIT: ADE remote PR gate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
