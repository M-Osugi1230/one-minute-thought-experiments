#!/usr/bin/env python3
"""Collect TikTok Display API analytics into versioned JSON/CSV snapshots.

This module intentionally keeps the public analytics history in Git while storing the
rotating TikTok refresh token as an authenticated-encrypted Fernet blob. The Fernet
key and TikTok client secret must stay outside the repository (for example GitHub
Actions secrets).

Commands:
    python scripts/tiktok_analytics.py authorize
    python scripts/tiktok_analytics.py collect
    python scripts/tiktok_analytics.py inspect
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import secrets
import string
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterable

from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
ANALYTICS_ROOT = ROOT / "analytics"
PRIVATE_ROOT = ANALYTICS_ROOT / "private"
SNAPSHOT_ROOT = ANALYTICS_ROOT / "snapshots"
HISTORY_ROOT = ANALYTICS_ROOT / "history"
TOKEN_PATH = PRIVATE_ROOT / "tiktok_refresh_token.fernet"
TOKEN_META_PATH = PRIVATE_ROOT / "token_metadata.json"
LATEST_PATH = ANALYTICS_ROOT / "latest.json"
POST_HISTORY_PATH = HISTORY_ROOT / "post_snapshots.csv"
ACCOUNT_HISTORY_PATH = HISTORY_ROOT / "account_snapshots.csv"

TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_USER_URL = "https://open.tiktokapis.com/v2/user/info/"
TIKTOK_VIDEO_LIST_URL = "https://open.tiktokapis.com/v2/video/list/"

DEFAULT_REDIRECT_URI = "http://127.0.0.1:8765/callback/"
DEFAULT_SCOPES = "user.info.basic,video.list,user.info.stats,user.info.profile"
DEFAULT_ACCOUNT_KEY = "1minshiko"
VIDEO_FIELDS = (
    "id,create_time,share_url,video_description,title,duration,"
    "like_count,comment_count,share_count,view_count,is_aigc"
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime | None = None) -> str:
    target = value or utc_now()
    return target.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} is required.")
    return value


def optional_env(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return default if value is None else value.strip()


def json_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
    form_body: dict[str, str] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    payload: bytes | None = None
    final_headers = {"Accept": "application/json"}
    if headers:
        final_headers.update(headers)

    if json_body is not None:
        payload = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        final_headers["Content-Type"] = "application/json"
    elif form_body is not None:
        payload = urllib.parse.urlencode(form_body).encode("utf-8")
        final_headers["Content-Type"] = "application/x-www-form-urlencoded"

    request = urllib.request.Request(url, data=payload, headers=final_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from TikTok: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach TikTok API: {exc}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"TikTok returned non-JSON content: {raw[:500]}") from exc


def ensure_tiktok_ok(payload: dict[str, Any], operation: str) -> dict[str, Any]:
    error = payload.get("error")
    if isinstance(error, dict):
        code = error.get("code")
        if code not in (None, "", "ok"):
            raise RuntimeError(
                f"TikTok {operation} failed: {code}: {error.get('message', '')} "
                f"(log_id={error.get('log_id', '')})"
            )
    elif isinstance(error, str) and error:
        raise RuntimeError(
            f"TikTok {operation} failed: {error}: {payload.get('error_description', '')}"
        )
    return payload


def fernet_from_env() -> Fernet:
    raw = require_env("TIKTOK_TOKEN_ENCRYPTION_KEY")
    try:
        return Fernet(raw.encode("ascii"))
    except (ValueError, TypeError) as exc:
        raise RuntimeError(
            "TIKTOK_TOKEN_ENCRYPTION_KEY must be a valid Fernet key. "
            "Generate one with: python scripts/tiktok_analytics.py keygen"
        ) from exc


def save_refresh_token(refresh_token: str, metadata: dict[str, Any]) -> None:
    PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
    encrypted = fernet_from_env().encrypt(refresh_token.encode("utf-8"))
    TOKEN_PATH.write_bytes(encrypted + b"\n")
    safe_metadata = {
        "updated_at": iso_utc(),
        "open_id": metadata.get("open_id"),
        "scope": metadata.get("scope"),
        "refresh_expires_in": metadata.get("refresh_expires_in"),
    }
    TOKEN_META_PATH.write_text(
        json.dumps(safe_metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_refresh_token() -> str:
    if TOKEN_PATH.is_file():
        encrypted = TOKEN_PATH.read_bytes().strip()
        try:
            return fernet_from_env().decrypt(encrypted).decode("utf-8")
        except InvalidToken as exc:
            raise RuntimeError(
                "The encrypted TikTok token could not be decrypted. "
                "Check TIKTOK_TOKEN_ENCRYPTION_KEY."
            ) from exc

    bootstrap = optional_env("TIKTOK_REFRESH_TOKEN")
    if bootstrap:
        return bootstrap
    raise RuntimeError(
        "No TikTok refresh token is available. Run the authorize command locally first, "
        "or provide TIKTOK_REFRESH_TOKEN once for bootstrap."
    )


def token_exchange(
    *,
    grant_type: str,
    code: str | None = None,
    code_verifier: str | None = None,
    refresh_token: str | None = None,
) -> dict[str, Any]:
    body = {
        "client_key": require_env("TIKTOK_CLIENT_KEY"),
        "client_secret": require_env("TIKTOK_CLIENT_SECRET"),
        "grant_type": grant_type,
    }
    if grant_type == "authorization_code":
        if not code:
            raise RuntimeError("Authorization code is missing.")
        body["code"] = code
        body["redirect_uri"] = optional_env("TIKTOK_REDIRECT_URI", DEFAULT_REDIRECT_URI)
        if code_verifier:
            body["code_verifier"] = code_verifier
    elif grant_type == "refresh_token":
        if not refresh_token:
            raise RuntimeError("Refresh token is missing.")
        body["refresh_token"] = refresh_token
    else:
        raise RuntimeError(f"Unsupported grant type: {grant_type}")

    payload = json_request("POST", TIKTOK_TOKEN_URL, form_body=body)
    ensure_tiktok_ok(payload, "token exchange")
    if not payload.get("access_token") or not payload.get("refresh_token"):
        raise RuntimeError(f"TikTok token response is missing tokens: {payload}")
    return payload


def refresh_access() -> dict[str, Any]:
    current = load_refresh_token()
    token = token_exchange(grant_type="refresh_token", refresh_token=current)
    save_refresh_token(str(token["refresh_token"]), token)
    return token


def scopes_from_token(token: dict[str, Any]) -> set[str]:
    return {item.strip() for item in str(token.get("scope", "")).split(",") if item.strip()}


def user_fields(scopes: set[str]) -> list[str]:
    fields = ["open_id", "union_id", "avatar_url", "display_name"]
    if "user.info.profile" in scopes:
        fields.extend(["profile_deep_link", "bio_description", "is_verified"])
    if "user.info.stats" in scopes:
        fields.extend(["follower_count", "following_count", "likes_count", "video_count"])
    return fields


def fetch_user(access_token: str, scopes: set[str]) -> dict[str, Any]:
    fields = ",".join(user_fields(scopes))
    url = f"{TIKTOK_USER_URL}?{urllib.parse.urlencode({'fields': fields})}"
    payload = json_request(
        "GET",
        url,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    ensure_tiktok_ok(payload, "user info")
    user = payload.get("data", {}).get("user")
    if not isinstance(user, dict):
        raise RuntimeError(f"TikTok user response did not include a user object: {payload}")
    return user


def fetch_videos(access_token: str, max_posts: int) -> list[dict[str, Any]]:
    if max_posts <= 0:
        return []
    url = f"{TIKTOK_VIDEO_LIST_URL}?{urllib.parse.urlencode({'fields': VIDEO_FIELDS})}"
    videos: list[dict[str, Any]] = []
    cursor: int | None = None

    while len(videos) < max_posts:
        body: dict[str, Any] = {"max_count": min(20, max_posts - len(videos))}
        if cursor is not None:
            body["cursor"] = cursor
        payload = json_request(
            "POST",
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            json_body=body,
        )
        ensure_tiktok_ok(payload, "video list")
        data = payload.get("data", {})
        page = data.get("videos", [])
        if not isinstance(page, list):
            raise RuntimeError(f"TikTok video response did not include a video list: {payload}")
        videos.extend(item for item in page if isinstance(item, dict))
        if not data.get("has_more") or not page:
            break
        next_cursor = data.get("cursor")
        if next_cursor is None or next_cursor == cursor:
            break
        cursor = int(next_cursor)

    return videos[:max_posts]


def safe_rate(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 6)


def int_value(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_video(video: dict[str, Any], collected_at: str) -> dict[str, Any]:
    views = int_value(video.get("view_count")) or 0
    likes = int_value(video.get("like_count")) or 0
    comments = int_value(video.get("comment_count")) or 0
    shares = int_value(video.get("share_count")) or 0
    create_time = int_value(video.get("create_time"))
    created_at = (
        datetime.fromtimestamp(create_time, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        if create_time is not None
        else None
    )
    age_hours: float | None = None
    if create_time is not None:
        age_hours = round(max(0.0, (utc_now().timestamp() - create_time) / 3600.0), 3)

    return {
        "id": str(video.get("id", "")),
        "created_at": created_at,
        "title": video.get("title") or "",
        "description": video.get("video_description") or "",
        "share_url": video.get("share_url") or "",
        "duration": int_value(video.get("duration")),
        "is_aigc": bool(video.get("is_aigc", False)),
        "view_count": views,
        "like_count": likes,
        "comment_count": comments,
        "share_count": shares,
        "like_rate": safe_rate(likes, views),
        "comment_rate": safe_rate(comments, views),
        "share_rate": safe_rate(shares, views),
        "engagement_rate": safe_rate(likes + comments + shares, views),
        "age_hours": age_hours,
        "views_per_age_hour": round(views / age_hours, 3) if age_hours and age_hours > 0 else None,
        "collected_at": collected_at,
    }


def load_previous_latest() -> dict[str, Any] | None:
    if not LATEST_PATH.is_file():
        return None
    try:
        data = json.loads(LATEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def add_deltas(current: list[dict[str, Any]], previous: dict[str, Any] | None) -> None:
    previous_posts = {}
    if previous:
        previous_posts = {
            str(item.get("id")): item
            for item in previous.get("posts", [])
            if isinstance(item, dict) and item.get("id")
        }
    for post in current:
        old = previous_posts.get(str(post.get("id")))
        for field in ("view_count", "like_count", "comment_count", "share_count"):
            previous_value = int_value(old.get(field)) if old else None
            current_value = int_value(post.get(field))
            post[f"delta_{field}"] = (
                current_value - previous_value
                if current_value is not None and previous_value is not None
                else None
            )


def account_snapshot(user: dict[str, Any], collected_at: str, previous: dict[str, Any] | None) -> dict[str, Any]:
    result = {
        "collected_at": collected_at,
        "account_key": optional_env("TIKTOK_ACCOUNT_KEY", DEFAULT_ACCOUNT_KEY),
        "open_id": user.get("open_id"),
        "display_name": user.get("display_name"),
        "profile_deep_link": user.get("profile_deep_link"),
        "bio_description": user.get("bio_description"),
        "is_verified": user.get("is_verified"),
        "follower_count": int_value(user.get("follower_count")),
        "following_count": int_value(user.get("following_count")),
        "likes_count": int_value(user.get("likes_count")),
        "video_count": int_value(user.get("video_count")),
    }
    previous_account = previous.get("account", {}) if previous else {}
    for field in ("follower_count", "following_count", "likes_count", "video_count"):
        current_value = int_value(result.get(field))
        previous_value = int_value(previous_account.get(field)) if isinstance(previous_account, dict) else None
        result[f"delta_{field}"] = (
            current_value - previous_value
            if current_value is not None and previous_value is not None
            else None
        )
    return result


def post_csv_row(post: dict[str, Any]) -> dict[str, Any]:
    fields = [
        "collected_at",
        "id",
        "created_at",
        "title",
        "view_count",
        "like_count",
        "comment_count",
        "share_count",
        "like_rate",
        "comment_rate",
        "share_rate",
        "engagement_rate",
        "age_hours",
        "views_per_age_hour",
        "delta_view_count",
        "delta_like_count",
        "delta_comment_count",
        "delta_share_count",
        "share_url",
    ]
    return {field: post.get(field) for field in fields}


def account_csv_row(account: dict[str, Any]) -> dict[str, Any]:
    fields = [
        "collected_at",
        "account_key",
        "display_name",
        "follower_count",
        "following_count",
        "likes_count",
        "video_count",
        "delta_follower_count",
        "delta_following_count",
        "delta_likes_count",
        "delta_video_count",
    ]
    return {field: account.get(field) for field in fields}


def append_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    exists = path.is_file() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def write_snapshot(snapshot: dict[str, Any]) -> Path:
    collected = datetime.fromisoformat(str(snapshot["collected_at"]).replace("Z", "+00:00"))
    relative = Path(
        f"{collected.year:04d}",
        f"{collected.month:02d}",
        f"{collected.day:02d}",
        collected.strftime("%Y%m%dT%H%M%SZ") + ".json",
    )
    target = SNAPSHOT_ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    target.write_text(serialized, encoding="utf-8")
    ANALYTICS_ROOT.mkdir(parents=True, exist_ok=True)
    LATEST_PATH.write_text(serialized, encoding="utf-8")
    append_csv(POST_HISTORY_PATH, (post_csv_row(post) for post in snapshot.get("posts", [])))
    append_csv(ACCOUNT_HISTORY_PATH, [account_csv_row(snapshot.get("account", {}))])
    return target


def collect() -> int:
    previous = load_previous_latest()
    token = refresh_access()
    scopes = scopes_from_token(token)
    if "video.list" not in scopes:
        raise RuntimeError(
            "The authorized TikTok token does not include video.list. "
            "Re-authorize after the scope is approved in TikTok Developer Portal."
        )

    collected_at = iso_utc()
    access_token = str(token["access_token"])
    user = fetch_user(access_token, scopes)
    max_posts = int(optional_env("TIKTOK_MAX_POSTS", "100") or "100")
    raw_videos = fetch_videos(access_token, max_posts=max_posts)
    posts = [normalize_video(item, collected_at) for item in raw_videos]
    add_deltas(posts, previous)
    account = account_snapshot(user, collected_at, previous)

    posts.sort(key=lambda item: (item.get("created_at") or "", item.get("id") or ""), reverse=True)
    snapshot = {
        "schema_version": 1,
        "collected_at": collected_at,
        "source": "TikTok Display API v2",
        "account": account,
        "authorized_scopes": sorted(scopes),
        "posts": posts,
        "diagnostics": {
            "post_count_returned": len(posts),
            "max_posts_requested": max_posts,
            "photo_post_support_unverified": True,
            "note": (
                "TikTok documents this endpoint as public video posts. The collector records whatever "
                "the authorized /v2/video/list/ endpoint returns; verify that photo carousel posts appear."
            ),
        },
    }
    target = write_snapshot(snapshot)
    print(
        json.dumps(
            {
                "ok": True,
                "collected_at": collected_at,
                "snapshot": str(target.relative_to(ROOT)),
                "posts": len(posts),
                "followers": account.get("follower_count"),
                "scopes": sorted(scopes),
            },
            ensure_ascii=False,
        )
    )
    return 0


@dataclass
class OAuthResult:
    code: str | None = None
    state: str | None = None
    error: str | None = None
    error_description: str | None = None


class OAuthCallbackState:
    def __init__(self) -> None:
        self.event = threading.Event()
        self.result = OAuthResult()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    state_holder: OAuthCallbackState

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        self.state_holder.result = OAuthResult(
            code=(params.get("code") or [None])[0],
            state=(params.get("state") or [None])[0],
            error=(params.get("error") or [None])[0],
            error_description=(params.get("error_description") or [None])[0],
        )
        self.state_holder.event.set()
        body = (
            "<!doctype html><meta charset='utf-8'><title>TikTok authorization</title>"
            "<style>body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:640px;"
            "margin:80px auto;padding:24px;line-height:1.6}</style>"
            "<h1>認証を受け取りました</h1><p>このタブを閉じてターミナルに戻ってください。</p>"
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def generate_code_verifier(length: int = 64) -> str:
    alphabet = string.ascii_letters + string.digits + "-._~"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def authorize(timeout_seconds: int) -> int:
    require_env("TIKTOK_CLIENT_KEY")
    require_env("TIKTOK_CLIENT_SECRET")
    fernet_from_env()

    redirect_uri = optional_env("TIKTOK_REDIRECT_URI", DEFAULT_REDIRECT_URI)
    parsed = urllib.parse.urlparse(redirect_uri)
    if parsed.hostname not in {"127.0.0.1", "localhost"} or not parsed.port:
        raise RuntimeError(
            "The authorize helper uses TikTok Desktop Login Kit and requires a localhost redirect URI "
            "with a port, for example http://127.0.0.1:8765/callback/."
        )

    scopes = optional_env("TIKTOK_SCOPES", DEFAULT_SCOPES)
    state = secrets.token_urlsafe(32)
    verifier = generate_code_verifier(64)
    challenge = hashlib.sha256(verifier.encode("ascii")).hexdigest()
    query = urllib.parse.urlencode(
        {
            "client_key": require_env("TIKTOK_CLIENT_KEY"),
            "response_type": "code",
            "scope": scopes,
            "redirect_uri": redirect_uri,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    auth_url = f"{TIKTOK_AUTH_URL}?{query}"

    holder = OAuthCallbackState()
    handler = type("BoundOAuthHandler", (OAuthCallbackHandler,), {"state_holder": holder})
    server = ThreadingHTTPServer((parsed.hostname, parsed.port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print("TikTok認証ページを開きます。開かない場合は次のURLをブラウザで開いてください。")
    print(auth_url)
    webbrowser.open(auth_url)
    try:
        if not holder.event.wait(timeout_seconds):
            raise RuntimeError(f"Timed out after {timeout_seconds} seconds waiting for TikTok OAuth callback.")
    finally:
        server.shutdown()
        server.server_close()

    result = holder.result
    if result.error:
        raise RuntimeError(f"TikTok authorization failed: {result.error}: {result.error_description or ''}")
    if result.state != state:
        raise RuntimeError("OAuth state mismatch. Authorization was aborted for safety.")
    if not result.code:
        raise RuntimeError("TikTok callback did not contain an authorization code.")

    token = token_exchange(
        grant_type="authorization_code",
        code=urllib.parse.unquote(result.code),
        code_verifier=verifier,
    )
    save_refresh_token(str(token["refresh_token"]), token)
    print("TikTok認証に成功し、refresh tokenを暗号化して保存しました。")
    print(f"保存先: {TOKEN_PATH.relative_to(ROOT)}")
    print(f"Scopes: {token.get('scope', '')}")
    print("次に `python scripts/tiktok_analytics.py collect` を実行して取得確認してください。")
    return 0


def inspect_latest() -> int:
    if not LATEST_PATH.is_file():
        print("analytics/latest.json はまだありません。collect を先に実行してください。")
        return 1
    data = json.loads(LATEST_PATH.read_text(encoding="utf-8"))
    posts = [item for item in data.get("posts", []) if isinstance(item, dict)]
    posts.sort(key=lambda item: int_value(item.get("view_count")) or 0, reverse=True)
    output = {
        "collected_at": data.get("collected_at"),
        "account": data.get("account"),
        "top_posts": [
            {
                "id": post.get("id"),
                "title": post.get("title") or post.get("description"),
                "views": post.get("view_count"),
                "likes": post.get("like_count"),
                "comments": post.get("comment_count"),
                "shares": post.get("share_count"),
                "delta_views": post.get("delta_view_count"),
                "engagement_rate": post.get("engagement_rate"),
            }
            for post in posts[:10]
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def keygen() -> int:
    print(Fernet.generate_key().decode("ascii"))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="TikTok analytics automation for 1分思考実験")
    sub = result.add_subparsers(dest="command", required=True)
    auth = sub.add_parser("authorize", help="Desktop Login Kitで初回OAuth認証しtokenを暗号化保存")
    auth.add_argument("--timeout", type=int, default=300, help="OAuth callback待ち時間（秒）")
    sub.add_parser("collect", help="Display APIから現在値を取得しJSON/CSVへ追記")
    sub.add_parser("inspect", help="latest.jsonの要約を表示")
    sub.add_parser("keygen", help="TIKTOK_TOKEN_ENCRYPTION_KEY用のFernet keyを生成")
    return result


def main(argv: list[str] | None = None) -> int:
    load_dotenv(ROOT / ".env")
    args = parser().parse_args(argv)
    try:
        if args.command == "authorize":
            return authorize(args.timeout)
        if args.command == "collect":
            return collect()
        if args.command == "inspect":
            return inspect_latest()
        if args.command == "keygen":
            return keygen()
    except (RuntimeError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
