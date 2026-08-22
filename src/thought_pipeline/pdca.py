"""Create a repeatable baseline-versus-variant PDCA review packet."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .errors import ConfigurationError
from .models import GeneratedPackage
from .providers import OfflineGoldenProvider
from .repository import ProjectRepository
from .timeline import build_timeline


@dataclass(frozen=True)
class VersionMetrics:
    label: str
    timing_basis: str
    planned_duration_seconds: float
    actual_duration_seconds: float | None
    scene_count: int
    reveal_start_seconds: float
    reveal_duration_seconds: float
    second_question_start_seconds: float
    second_question_start_percent: float
    answer_pause_seconds: float
    narration_characters: int
    edit_profile: str | None
    soundbed: bool


@dataclass(frozen=True)
class PdcaResult:
    output_dir: Path
    report_path: Path
    data_path: Path
    log_path: Path


def build_pdca_packet(
    repository: ProjectRepository,
    experiment_id: str,
    variant: str,
    output_root: Path,
) -> PdcaResult:
    """Compare a golden baseline and a named variant and write review artifacts."""
    experiment = repository.experiment(experiment_id)
    baseline = OfflineGoldenProvider(repository.root).generate(experiment.id, object())
    candidate = OfflineGoldenProvider(repository.root, variant).generate(
        experiment.id,
        object(),
    )
    baseline_dir = output_root / f"{experiment.id}_{experiment.slug}"
    candidate_dir = output_root / "variants" / variant / f"{experiment.id}_{experiment.slug}"
    baseline_metrics = _metrics(
        repository,
        baseline,
        "baseline",
        baseline_dir,
    )
    candidate_metrics = _metrics(
        repository,
        candidate,
        variant,
        candidate_dir,
    )

    packet_dir = output_root / "pdca" / f"{experiment.id}_{variant}"
    packet_dir.mkdir(parents=True, exist_ok=True)
    data_path = packet_dir / "comparison.json"
    report_path = packet_dir / "review.md"
    log_path = packet_dir / "performance_log.csv"
    comparison = {
        "schema_version": "1.0",
        "created_at": datetime.now(UTC).isoformat(),
        "experiment_id": experiment.id,
        "experiment_title": experiment.title,
        "variant": variant,
        "baseline": asdict(baseline_metrics),
        "candidate": asdict(candidate_metrics),
        "delta": _delta(baseline_metrics, candidate_metrics),
        "hypotheses": _hypotheses(baseline_metrics, candidate_metrics),
        "decision_rule": {
            "primary": "平均視聴時間率または完視聴率が改善する",
            "guardrails": [
                "コメント率を悪化させない",
                "シェア率を悪化させない",
                "選択肢A/Bの表現を同格に保つ",
            ],
            "minimum_observation": "公開後2時間と48時間の2回を記録する",
        },
    }
    data_path.write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path.write_text(
        _markdown(experiment.title, baseline_metrics, candidate_metrics, comparison),
        encoding="utf-8",
    )
    _write_log_template(log_path, experiment.id, variant)
    return PdcaResult(packet_dir, report_path, data_path, log_path)


def _metrics(
    repository: ProjectRepository,
    package: GeneratedPackage,
    label: str,
    render_dir: Path,
) -> VersionMetrics:
    timeline = build_timeline(package, repository.video())
    timings = [item.as_dict() for item in timeline]
    timing_basis = "planned_script"
    actual_timeline = _optional_json_list(render_dir / "timeline_actual.json")
    if actual_timeline:
        timings = actual_timeline
        timing_basis = "measured_scene_audio"
    reveal = next(item for item in timings if item["purpose"] == "reveal")
    second = next(item for item in timings if item["purpose"] == "second_question")
    pauses = [
        float(item["pause_after_seconds"])
        for item in timings
        if item["purpose"] in {"choice", "second_question"}
    ]
    manifest = _optional_json(render_dir / "render_manifest.json")
    actual = manifest.get("actual_duration_seconds") if manifest else None
    actual_value = float(actual) if isinstance(actual, (int, float)) else None
    return VersionMetrics(
        label=label,
        timing_basis=timing_basis,
        planned_duration_seconds=package.planned_duration_seconds,
        actual_duration_seconds=actual_value,
        scene_count=len(package.scenes),
        reveal_start_seconds=float(reveal["start_seconds"]),
        reveal_duration_seconds=float(reveal["duration_seconds"]),
        second_question_start_seconds=float(second["start_seconds"]),
        second_question_start_percent=round(
            float(second["start_seconds"])
            / (
                actual_value
                if actual_value is not None
                else package.planned_duration_seconds
            )
            * 100,
            1,
        ),
        answer_pause_seconds=round(sum(pauses), 3),
        narration_characters=sum(len(scene.narration) for scene in package.scenes),
        edit_profile=(
            str(manifest["edit_profile"])
            if manifest and manifest.get("edit_profile")
            else None
        ),
        soundbed=bool(manifest and "soundbed.wav" in manifest.get("artifacts", [])),
    )


def _optional_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"比較対象のmanifestが不正です: {path}\n{exc}") from exc
    if not isinstance(value, dict):
        raise ConfigurationError(f"比較対象のmanifestがオブジェクトではありません: {path}")
    return value


def _optional_json_list(path: Path) -> list[dict[str, Any]] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"比較対象のtimelineが不正です: {path}\n{exc}") from exc
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ConfigurationError(f"比較対象のtimelineが配列ではありません: {path}")
    return value


def _delta(baseline: VersionMetrics, candidate: VersionMetrics) -> dict[str, float]:
    return {
        "planned_duration_seconds": round(
            candidate.planned_duration_seconds - baseline.planned_duration_seconds,
            3,
        ),
        "second_question_start_seconds": round(
            candidate.second_question_start_seconds
            - baseline.second_question_start_seconds,
            3,
        ),
        "second_question_start_percentage_points": round(
            candidate.second_question_start_percent
            - baseline.second_question_start_percent,
            1,
        ),
        "narration_characters": float(
            candidate.narration_characters - baseline.narration_characters
        ),
    }


def _hypotheses(
    baseline: VersionMetrics,
    candidate: VersionMetrics,
) -> list[str]:
    hypotheses: list[str] = []
    if candidate.planned_duration_seconds < baseline.planned_duration_seconds:
        hypotheses.append("総尺短縮により平均視聴時間率と完視聴率が上がる")
    if candidate.second_question_start_seconds < baseline.second_question_start_seconds:
        hypotheses.append("条件変更の前倒しにより中盤離脱が減り、コメントの理由が具体化する")
    if candidate.soundbed and not baseline.soundbed:
        hypotheses.append("意味のある効果音と低い環境音により、無音離脱を減らす")
    hypotheses.append("A/Bを同じ面積・明るさに戻すことで、回答誘導を抑える")
    return hypotheses


def _markdown(
    title: str,
    baseline: VersionMetrics,
    candidate: VersionMetrics,
    comparison: dict[str, Any],
) -> str:
    actual_baseline = _seconds(baseline.actual_duration_seconds)
    actual_candidate = _seconds(candidate.actual_duration_seconds)
    hypotheses = "\n".join(f"- {item}" for item in comparison["hypotheses"])
    return f"""# {title}｜{candidate.label} PDCAレビュー

## 比較結果

| 指標 | 現行版 | 改善版 | 判断 |
|---|---:|---:|---|
| 予定尺 | {baseline.planned_duration_seconds:.1f}秒 | {candidate.planned_duration_seconds:.1f}秒 | 短いほど冒頭仮説を検証しやすい |
| 実測尺 | {actual_baseline} | {actual_candidate} | 音声込みの最終値 |
| シーン数 | {baseline.scene_count} | {candidate.scene_count} | 情報量を整理 |
| 名称公開 | {baseline.reveal_start_seconds:.1f}秒 | {candidate.reveal_start_seconds:.1f}秒 | 長いタイトル停止を圧縮 |
| 条件変更 | {baseline.second_question_start_seconds:.1f}秒 ({baseline.second_question_start_percent:.1f}%) | {candidate.second_question_start_seconds:.1f}秒 ({candidate.second_question_start_percent:.1f}%) | 72%以前を目安 |
| 回答用の間 | {baseline.answer_pause_seconds:.1f}秒 | {candidate.answer_pause_seconds:.1f}秒 | 視聴者が実際に選べる時間 |
| ナレーション文字数 | {baseline.narration_characters}字 | {candidate.narration_characters}字 | 読み上げ密度を抑制 |
| 編集方式 | {baseline.edit_profile or '未記録'} | {candidate.edit_profile or '未記録'} | 改善版は意味のある動きを使用 |
| 音響レイヤー | {'あり' if baseline.soundbed else 'なし'} | {'あり' if candidate.soundbed else 'なし'} | 選択時は音量を落とす |
| 時刻の根拠 | {baseline.timing_basis} | {candidate.timing_basis} | 実測音声があれば実測値を優先 |

## 今回の仮説

{hypotheses}

## 投稿前チェック

- A/Bが停止画面で同じ大きさ・明るさになっている
- 音声を切っても状況と選択肢が理解できる
- スマートフォンで字幕がUIに隠れない
- レバー音、心拍、衝撃音が声より前へ出ていない
- 説明文と固定コメントが「最初→最後＋理由」を求めている

## 計測と判断

公開後2時間と48時間に `performance_log.csv` を埋める。主判定は平均視聴時間率または完視聴率、補助判定は1,000再生あたりコメント数・シェア数。改善版が主判定を上げ、補助判定を悪化させなければ次の動画へ採用する。

一度に検証する大きな変更は1テーマに絞る。次サイクルでは声、Hook、字幕、音響のうち最も弱い1項目だけを変更する。
"""


def _seconds(value: float | None) -> str:
    return "未生成" if value is None else f"{value:.1f}秒"


def _write_log_template(path: Path, experiment_id: str, variant: str) -> None:
    if path.exists():
        return
    columns = [
        "experiment_id",
        "version",
        "platform",
        "published_at",
        "observed_at",
        "hours_since_publish",
        "views",
        "average_watch_seconds",
        "completed_views_percent",
        "likes",
        "comments",
        "shares",
        "saves",
        "answer_change_comments",
        "notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for version in ("baseline", variant):
            writer.writerow({"experiment_id": experiment_id, "version": version})
