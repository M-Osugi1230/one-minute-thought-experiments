"""Command-line interface for local and CI usage."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ValidationError

from .core import Pipeline
from .errors import PipelineError
from .models import GeneratedPackage
from .providers import OfflineGoldenProvider, OpenAIStructuredProvider
from .quality import validate_generated_package
from .render import render_phase2
from .repository import ProjectRepository


COMMANDS = {"generate", "render", "validate", "list", "prompt"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipeline.py",
        description="『1分思考実験』半自動動画生成パイプライン",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="台本と編集素材を生成")
    generate.add_argument("experiment_id", help="例: 001")
    generate.add_argument(
        "--offline",
        action="store_true",
        help="APIを使わずゴールデンサンプルで全工程を確認",
    )
    generate.add_argument("--overwrite", action="store_true", help="既存成果物を上書き")
    generate.add_argument("--output-root", type=Path, help="出力ルートを変更")

    render = subparsers.add_parser("render", help="音声・実測字幕・縦型動画を生成")
    render.add_argument("experiment_id", help="例: 001")
    render.add_argument(
        "--voice-provider",
        choices=("auto", "openai", "system", "silent"),
        default="auto",
        help="autoはAPIキー、macOS音声、無音の順に自動選択",
    )
    render.add_argument(
        "--preview",
        action="store_true",
        help="確認用の軽量な540×960動画を生成",
    )
    render.add_argument("--overwrite", action="store_true", help="既存成果物を上書き")
    render.add_argument("--output-root", type=Path, help="出力ルートを変更")

    validate = subparsers.add_parser("validate", help="設定・Fact Pack・生成物を検証")
    validate.add_argument("--experiment", help="特定IDだけを検証")
    validate.add_argument("--generated", type=Path, help="任意のscript.jsonを追加検証")

    subparsers.add_parser("list", help="登録済み思考実験を一覧表示")

    prompt = subparsers.add_parser("prompt", help="APIへ送るプロンプトを表示")
    prompt.add_argument("experiment_id", help="例: 001")
    return parser


def main(argv: list[str] | None = None) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)
    if args_list and args_list[0] not in COMMANDS and not args_list[0].startswith("-"):
        args_list.insert(0, "generate")

    args = _parser().parse_args(args_list)
    repository = ProjectRepository()
    load_dotenv(repository.root / ".env")

    try:
        if args.command == "generate":
            return _generate(args, repository)
        if args.command == "render":
            return _render(args, repository)
        if args.command == "validate":
            return _validate(args, repository)
        if args.command == "list":
            return _list(repository)
        if args.command == "prompt":
            return _prompt(args, repository)
    except (PipelineError, ValidationError, json.JSONDecodeError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 2
    return 1


def _generate(args: argparse.Namespace, repository: ProjectRepository) -> int:
    experiment = repository.experiment(args.experiment_id)
    llm = repository.llm()
    provider = (
        OfflineGoldenProvider(repository.root)
        if args.offline
        else OpenAIStructuredProvider(llm)
    )
    output_root = _output_root(args, repository)

    result = Pipeline(repository).run(
        experiment.id,
        provider,
        output_root=output_root,
        overwrite=args.overwrite,
    )
    mode = "オフライン" if args.offline else f"OpenAI / {provider.model}"
    print(f"生成完了: {experiment.title} ({mode})")
    print(f"予定尺: {result.planned_duration_seconds:.1f}秒")
    print(f"出力先: {result.output_dir}")
    print(f"成果物: {len(result.artifacts)}ファイル")
    return 0


def _render(args: argparse.Namespace, repository: ProjectRepository) -> int:
    experiment = repository.experiment(args.experiment_id)
    output_root = _output_root(args, repository)
    output_dir = output_root / f"{experiment.id}_{experiment.slug}"
    script_path = output_dir / "script.json"
    if not script_path.is_file():
        print("Phase 1成果物がないため、オフライン合格サンプルから先に生成します。")
        Pipeline(repository).run(
            experiment.id,
            OfflineGoldenProvider(repository.root),
            output_root=output_root,
            overwrite=False,
        )

    result = render_phase2(
        repository=repository,
        experiment_id=experiment.id,
        output_root=output_root,
        voice_mode=args.voice_provider,
        preview=args.preview,
        overwrite=args.overwrite,
    )
    mode = "軽量プレビュー" if args.preview else "投稿解像度"
    print(f"動画生成完了: {experiment.title} ({mode})")
    print(f"音声: {result.provider_name}")
    print(f"実測尺: {result.actual_duration_seconds:.1f}秒")
    if not result.duration_in_target_range:
        print("注意: 実測尺がFact Packの目標範囲外です。音声速度を調整してください。")
    print(f"映像: {result.width}×{result.height} / {result.fps}fps")
    print(f"動画: {result.video_path}")
    print(f"絵コンテ: {result.storyboard_path}")
    return 0


def _validate(args: argparse.Namespace, repository: ProjectRepository) -> int:
    experiments = repository.validate_all()
    if args.experiment:
        target_id = args.experiment.zfill(3)
        experiments = [item for item in experiments if item.id == target_id]
        if not experiments:
            repository.experiment(target_id)  # Raise the standard not-found error.

    errors = 0
    for experiment in experiments:
        golden_path = repository.root / "content" / "golden" / f"{experiment.id}.json"
        if golden_path.is_file():
            package = OfflineGoldenProvider(repository.root).generate(
                experiment.id,
                Pipeline(repository).prompt(experiment.id),
            )
            report = validate_generated_package(package, experiment, repository.brand())
            errors += _print_report(f"{experiment.id} {experiment.title}", report)
        else:
            print(f"OK  {experiment.id} {experiment.title} (Fact Pack)")

    if args.generated:
        path = args.generated
        if not path.is_absolute():
            path = repository.root / path
        package = GeneratedPackage.model_validate_json(path.read_text(encoding="utf-8"))
        experiment = repository.experiment(package.experiment_id)
        report = validate_generated_package(package, experiment, repository.brand())
        errors += _print_report(str(path), report)

    print(f"検証完了: {len(experiments)}件 / エラー {errors}件")
    return 0 if errors == 0 else 2


def _print_report(label: str, report: object) -> int:
    if report.is_valid:
        print(f"OK  {label}")
    for issue in report.issues:
        prefix = "WARN" if issue.severity == "warning" else "NG"
        print(f"{prefix} {label} [{issue.code}] {issue.path}: {issue.message}")
    return len(report.errors)


def _list(repository: ProjectRepository) -> int:
    for record in repository.experiment_records():
        print(
            f"{record.id}  {record.title}  "
            f"template={record.template}  status={record.status}"
        )
    return 0


def _prompt(args: argparse.Namespace, repository: ProjectRepository) -> int:
    prompt = Pipeline(repository).prompt(args.experiment_id)
    print("--- system ---")
    print(prompt.system)
    print("\n--- user ---")
    print(prompt.user)
    return 0


def _output_root(args: argparse.Namespace, repository: ProjectRepository) -> Path:
    output_root = args.output_root or Path(os.getenv("OUTPUT_ROOT", "output"))
    if not output_root.is_absolute():
        output_root = repository.root / output_root
    return output_root


if __name__ == "__main__":
    raise SystemExit(main())
