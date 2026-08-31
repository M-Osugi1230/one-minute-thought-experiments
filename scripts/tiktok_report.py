#!/usr/bin/env python3
"""Generate a compact Markdown health report from TikTok analytics snapshots."""

from __future__ import annotations

import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ANALYTICS_ROOT = ROOT / "analytics"
LATEST_PATH = ANALYTICS_ROOT / "latest.json"
MANUAL_BASELINE = ANALYTICS_ROOT / "manual" / "2026-08-31-baseline.json"
REPORT_PATH = ANALYTICS_ROOT / "report.md"


def number(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def pct(value: Any) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "—"


def load_source() -> tuple[dict[str, Any], str]:
    if LATEST_PATH.is_file():
        return json.loads(LATEST_PATH.read_text(encoding="utf-8")), "TikTok Display API"
    if MANUAL_BASELINE.is_file():
        manual = json.loads(MANUAL_BASELINE.read_text(encoding="utf-8"))
        posts = []
        for item in manual.get("posts", []):
            views = number(item.get("views"))
            likes = number(item.get("likes"))
            comments = number(item.get("comments_total_including_creator"))
            shares = number(item.get("shares"))
            posts.append(
                {
                    "id": item.get("label"),
                    "title": item.get("label"),
                    "description": item.get("hook"),
                    "view_count": views,
                    "like_count": likes,
                    "comment_count": comments,
                    "share_count": shares,
                    "like_rate": likes / views if views else None,
                    "comment_rate": comments / views if views else None,
                    "share_rate": shares / views if views else None,
                    "engagement_rate": (likes + comments + shares) / views if views else None,
                    "delta_view_count": None,
                }
            )
        return (
            {
                "collected_at": manual.get("captured_at"),
                "account": {
                    "account_key": manual.get("account", {}).get("handle"),
                    "display_name": manual.get("account", {}).get("display_name"),
                    "follower_count": manual.get("account", {}).get("followers"),
                    "likes_count": manual.get("account", {}).get("profile_likes"),
                },
                "posts": posts,
            },
            "manual TikTok Studio baseline",
        )
    raise SystemExit("No analytics data found. Run tiktok_analytics.py collect first.")


def label(post: dict[str, Any]) -> str:
    title = str(post.get("title") or "").strip()
    if title:
        return title.replace("\n", " ")[:60]
    description = str(post.get("description") or "").strip()
    return description.replace("\n", " ")[:60] or str(post.get("id") or "unknown")


def fmt_delta(value: Any) -> str:
    if value is None:
        return "—"
    parsed = number(value)
    return f"+{parsed}" if parsed >= 0 else str(parsed)


def winner_threshold(posts: list[dict[str, Any]]) -> tuple[float, float]:
    recent = posts[:10]
    values = [number(post.get("view_count")) for post in recent if number(post.get("view_count")) > 0]
    if not values:
        return 0.0, 0.0
    median = float(statistics.median(values))
    return median, median * 1.5


def generate() -> str:
    data, source_name = load_source()
    posts = [item for item in data.get("posts", []) if isinstance(item, dict)]
    if any(post.get("created_at") for post in posts):
        posts.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)

    median, threshold = winner_threshold(posts)
    by_views = sorted(posts, key=lambda item: number(item.get("view_count")), reverse=True)
    by_delta = sorted(
        [post for post in posts if post.get("delta_view_count") is not None],
        key=lambda item: number(item.get("delta_view_count")),
        reverse=True,
    )
    winners = [post for post in posts[:10] if number(post.get("view_count")) >= threshold and threshold > 0]
    account = data.get("account", {}) if isinstance(data.get("account"), dict) else {}

    lines: list[str] = []
    lines.append("# TikTok コンディションレポート")
    lines.append("")
    lines.append(f"- 取得時刻: {data.get('collected_at', '—')}")
    lines.append(f"- データ源: {source_name}")
    lines.append(f"- アカウント: {account.get('display_name') or account.get('account_key') or '—'}")
    lines.append(f"- フォロワー: {account.get('follower_count', '—')}")
    lines.append(f"- 累計いいね: {account.get('likes_count', '—')}")
    lines.append("")
    lines.append("## 勝ち判定")
    lines.append("")
    lines.append(f"- 直近10本の再生中央値: **{median:.1f}**")
    lines.append(f"- 勝ち基準（中央値×1.5）: **{threshold:.1f}**")
    if winners:
        for post in sorted(winners, key=lambda item: number(item.get("view_count")), reverse=True):
            lines.append(f"- 勝ち: **{label(post)}** — {number(post.get('view_count'))} views")
    else:
        lines.append("- 現時点で勝ち基準を超えた投稿なし")

    lines.append("")
    lines.append("## 投稿ランキング")
    lines.append("")
    lines.append("| # | 投稿 | 再生 | いいね | コメント* | シェア | いいね率 | 総ER | 前回比再生 |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|")
    for index, post in enumerate(by_views[:15], start=1):
        lines.append(
            "| {idx} | {name} | {views} | {likes} | {comments} | {shares} | {like_rate} | {er} | {delta} |".format(
                idx=index,
                name=label(post).replace("|", "｜"),
                views=number(post.get("view_count")),
                likes=number(post.get("like_count")),
                comments=number(post.get("comment_count")),
                shares=number(post.get("share_count")),
                like_rate=pct(post.get("like_rate")),
                er=pct(post.get("engagement_rate")),
                delta=fmt_delta(post.get("delta_view_count")),
            )
        )
    lines.append("")
    lines.append("\* TikTok APIのcomment_countは投稿者自身のコメントも含み得るため、純粋な外部ユーザーコメント数ではありません。")

    if by_delta:
        lines.append("")
        lines.append("## 前回取得から伸びた投稿")
        lines.append("")
        for post in by_delta[:5]:
            lines.append(f"- {label(post)}: **{fmt_delta(post.get('delta_view_count'))} views**")

    lines.append("")
    lines.append("## 解釈上の注意")
    lines.append("")
    lines.append("- Display APIで取れるのは主に公開投稿の再生・いいね・コメント・シェア等です。")
    lines.append("- 平均閲覧写真数、継続率、保存数、検索クエリ、トラフィックソースはTikTok Studio側の手動データとして別管理します。")
    lines.append("- 写真カルーセル投稿が `/v2/video/list/` に返るかは実アカウントOAuth後の初回取得で検証します。")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    report = generate()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
