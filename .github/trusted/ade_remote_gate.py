from __future__ import annotations

import base64
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ADE_REPOSITORY = "M-Osugi1230/autonomous-development-engine"
ADE_API_BASE = f"https://api.github.com/repos/{ADE_REPOSITORY}"
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


def _request_json(
    url: str,
    *,
    method: str = "GET",
    token: str | None = None,
    payload: dict[str, Any] | None = None,
) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ADE-Remote-PR-Gate/1.1",
        "Cache-Control": "no-cache",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        headers["Content-Type"] = "application/json"

    request = Request(url, data=body, headers=headers, method=method)
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
    return _request_json(
        "https://api.github.com" + path,
        method=method,
        token=token,
        payload=payload,
    )


def _ade_head_sha() -> str:
    payload = _request_json(f"{ADE_API_BASE}/commits/main")
    if not isinstance(payload, dict):
        raise GateError("ADE main commit response must be an object")
    sha = payload.get("sha")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise GateError("ADE main commit SHA is invalid")
    return sha


def _ade_json(relative_path: str, *, ref: str) -> dict[str, Any]:
    path = relative_path.lstrip("/")
    payload = _request_json(f"{ADE_API_BASE}/contents/{path}?ref={ref}")
    if not isinstance(payload, dict):
        raise GateError(f"ADE contract {relative_path} response must be an object")
    encoded = payload.get("content")
    if not isinstance(encoded, str):
        raise GateError(f"ADE contract {relative_path} has no content")
    try:
        raw = base64.b64decode(encoded.replace("\n", ""))
        decoded = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError(f"ADE contract {relative_path} is invalid JSON") from exc
    if not isinstance(decoded, dict):
        raise GateError(f"ADE contract {relative_path} must be a JSON object")
    return decoded


def _github_list_pr_files(
    repository: str,
    pr_number: int,
    *,
    page_size: int = 100,
    max_pages: int = 20,
) -> list[dict[str, Any]]:
    if type(pr_number) is not int or pr_number < 1:
        raise GateError("pull request number must be positive")
    if type(page_size) is not int or not 1 <= page_size <= 100:
        raise GateError("page_size must be between 1 and 100")
    if type(max_pages) is not int or max_pages < 1:
        raise GateError("max_pages must be positive")

    result: list[dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        payload = _github_request(
            "GET",
            f"/repos/{repository}/pulls/{pr_number}/files"
            f"?per_page={page_size}&page={page}",
        )
        if not isinstance(payload, list):
            raise GateError("pull request files response must be a list")
        items = [item for item in payload if isinstance(item, dict)]
        result.extend(items)
        if len(payload) < page_size:
            return result
    raise GateError("pull request files pagination exceeded trusted page budget")


def _validate_remote_receipt(
    receipt: dict[str, Any],
    *,
    repository: str,
    task_id: str,
    pr_number: int,
) -> None:
    if receipt.get("schema_version") != 1:
        raise GateError("ADE remote receipt schema_version is invalid")
    if receipt.get("status") != "PR_CREATED":
        raise GateError("ADE remote receipt is not PR_CREATED")
    if receipt.get("task_id") != task_id:
        raise GateError("ADE remote receipt task_id does not match current task")
    if receipt.get("target_repository") != repository:
        raise GateError("ADE remote receipt target_repository does not match this repository")
    expected_url = f"https://github.com/{repository}/pull/{pr_number}"
    if receipt.get("pull_request_url") != expected_url:
        raise GateError("ADE remote receipt does not bind this pull request")


def _current_contract(
    *,
    pr_number: int,
) -> tuple[str, tuple[str, ...], str, str]:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    ade_ref = _ade_head_sha()
    state = _ade_json(".autodev/state.json", ref=ade_ref)
    accepted = _ade_json(".autodev/accepted-plan.json", ref=ade_ref)
    campaign = _ade_json(".autodev/campaign.json", ref=ade_ref)
    graph = _ade_json(".autodev/task-graph.json", ref=ade_ref)
    receipt = _ade_json(".autodev/runtime/remote-execution.json", ref=ade_ref)

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
        if (
            value.startswith("/")
            or ".." in value.split("/")
            or value.startswith((".github/", ".autodev/"))
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

    _validate_remote_receipt(
        receipt,
        repository=repository,
        task_id=task_id,
        pr_number=pr_number,
    )

    base_branch = metadata.get("target_base_branch", "main")
    if not isinstance(base_branch, str) or not base_branch.strip():
        raise GateError("ADE target base branch is invalid")
    return task_id, tuple(allowed_paths), base_branch, ade_ref


def _validate_pr(
    pr: dict[str, Any],
    files: list[dict[str, Any]],
    *,
    allowed_paths: tuple[str, ...],
    base_branch: str,
    ci_head_sha: str,
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
    head_sha = head.get("sha")
    if not isinstance(head_sha, str) or not head_sha:
        raise GateError("pull request head SHA is missing")
    if head_sha != ci_head_sha:
        raise GateError("pull request head SHA does not match the SHA that passed CI")

    base = pr.get("base")
    if not isinstance(base, dict) or base.get("ref") != base_branch:
        raise GateError("pull request base branch does not match ADE contract")

    # Editable PR text is only supplemental evidence. The authoritative
    # task/PR binding comes from ADE's trusted remote-execution receipt.
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

        ci_head_sha = workflow_run.get("head_sha")
        if not isinstance(ci_head_sha, str) or not re.fullmatch(
            r"[0-9a-f]{40}", ci_head_sha
        ):
            raise GateError("workflow_run head_sha is invalid")

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
        files = _github_list_pr_files(repository, pr_number)

        task_id, allowed_paths, base_branch, ade_ref = _current_contract(
            pr_number=pr_number
        )
        _validate_pr(
            pr,
            files,
            allowed_paths=allowed_paths,
            base_branch=base_branch,
            ci_head_sha=ci_head_sha,
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
            f"ade_ref={ade_ref}; scope={list(allowed_paths)}"
        )
        return 0
    except (GateError, ValueError, KeyError, json.JSONDecodeError, OSError) as exc:
        print(f"HUMAN_WAIT: ADE remote PR gate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
