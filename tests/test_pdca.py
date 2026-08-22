from __future__ import annotations

import csv
import json

from thought_pipeline.pdca import build_pdca_packet
from thought_pipeline.repository import ProjectRepository


def test_pdca_packet_compares_baseline_and_fast44(tmp_path) -> None:
    result = build_pdca_packet(ProjectRepository(), "001", "fast44", tmp_path)
    comparison = json.loads(result.data_path.read_text(encoding="utf-8"))

    assert comparison["baseline"]["planned_duration_seconds"] == 50.0
    assert comparison["candidate"]["planned_duration_seconds"] == 40.1
    assert comparison["delta"]["second_question_start_seconds"] < 0
    assert result.report_path.is_file()

    with result.log_path.open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert [row["version"] for row in rows] == ["baseline", "fast44"]
