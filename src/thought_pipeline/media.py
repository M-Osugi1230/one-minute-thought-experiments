"""Small, explicit wrappers around the bundled FFmpeg executable."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .errors import ConfigurationError, GenerationError


def ffmpeg_executable() -> str:
    try:
        from imageio_ffmpeg import get_ffmpeg_exe

        return get_ffmpeg_exe()
    except Exception as exc:
        raise ConfigurationError(
            "FFmpegを利用できません。requirements.txtを再インストールしてください。"
        ) from exc


def run_media_command(command: list[str], cwd: Path | None = None) -> None:
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        if len(detail) > 4000:
            detail = detail[-4000:]
        raise GenerationError(f"メディア処理に失敗しました:\n{detail}")
