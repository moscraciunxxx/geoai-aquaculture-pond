"""Drive the shipped public-slice F1 calculator. No hardcoded public-LB win."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src" / "public_slice_metric.py"


def _load():
    spec = importlib.util.spec_from_file_location("geoai_public_slice_metric", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_incumbent_f1_inverts_uniquely_via_shipped_function():
    mod = _load()
    tp, fp, fn, tn = mod.invert_f1(mod.INCUMBENT_F1)
    assert (tp, fp, fn, tn) == (164, 21, 17, 131)
    assert abs(mod.f1_from_counts(tp, fp) - mod.INCUMBENT_F1) < 1e-9
    inc = mod.incumbent_confusion()
    assert inc["errors"] == 38
    assert abs(inc["blended"] - mod.INCUMBENT_BLEND) < 1e-8


def test_f1_above_0983_requires_at_most_six_public_errors():
    mod = _load()
    report = mod.target_is_beyond_incumbent_and_field(0.983)
    assert report["n_legal_confusion_matrices"] > 0
    assert report["max_errors"] == 6
    assert report["max_fp"] == 6
    assert report["min_tp"] == 175
    assert report["can_certify_offline"] is False
    assert report["f1_if_max_tp_173_fp_0"] < 0.983
    assert report["error_reduction_needed"] >= 32


def test_cli_json_matches_shipped_incumbent_invert():
    proc = subprocess.run(
        [sys.executable, str(SRC), "--json"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["incumbent"]["tp"] == 164
    assert payload["incumbent"]["fp"] == 21
    assert payload["f1_gt_0983"]["can_certify_offline"] is False
    assert payload["f1_gt_0983"]["max_errors"] == 6
