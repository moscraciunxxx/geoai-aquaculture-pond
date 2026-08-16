"""Drive the shipped max/union and stratum-gate functions, plus their CLIs."""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src" / "or_max_union.py"
MAX_CLI = REPO / "scripts" / "build_or_max_union_20260816.py"
STRATUM_CLI = REPO / "scripts" / "build_or_stratum_20260816.py"
PY = "/opt/anaconda3/envs/geoai/bin/python"


def _load_mod():
    import importlib.util

    spec = importlib.util.spec_from_file_location("geoai_or_max_union", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_build_or_max_is_union_and_keeps_anchor_positives():
    mod = _load_mod()
    rng = np.random.default_rng(1)
    a = rng.random(300)
    b = rng.random(300)
    f1, rauc = mod.build_or_max(a, b)
    assert np.array_equal(f1, ((a >= 0.5) | (b >= 0.5)).astype(int))
    assert np.array_equal(f1, (rauc >= 0.5).astype(int))
    assert np.allclose(rauc, np.maximum(a, b))
    assert int(((f1 == 0) & (a >= 0.5)).sum()) == 0


def test_build_or_stratum_restricts_extras_to_allow_mask():
    mod = _load_mod()
    rng = np.random.default_rng(2)
    a = rng.random(400)
    b = rng.random(400)
    allow = rng.random(400) < 0.25
    f1, rauc = mod.build_or_stratum(a, b, allow)
    assert np.array_equal(f1, (rauc >= 0.5).astype(int))
    extras = (f1 == 1) & (a < 0.5)
    assert extras.sum() == 0 or bool(np.all(allow[extras]))
    assert np.array_equal(f1[~allow], (a[~allow] >= 0.5).astype(int))
    assert np.allclose(rauc[~allow], a[~allow])
    assert int(((f1 == 0) & (a >= 0.5)).sum()) == 0


def test_stratum_masks_from_live_test_csv():
    mod = _load_mod()
    test = pd.read_csv(REPO / "data" / "raw" / "Test.csv")
    masks = mod.stratum_masks_from_test(test)
    assert int(masks["s1_only"].sum()) == 273
    assert int(masks["four_month"].sum()) == 345
    assert int(masks["s1_or_four"].sum()) == int((masks["s1_only"] | masks["four_month"]).sum())
    assert set(np.unique(masks["window_length"])).issubset({4, 5, 6})


def test_or_max_cli_writes_zero_drop_file():
    proc = subprocess.run(
        [PY, str(MAX_CLI)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    out = REPO / "submissions" / "sub_536_or_max_308_533.csv"
    assert out.is_file()
    val = subprocess.run(
        [PY, str(REPO / "src" / "validate_submission.py"), str(out)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert val.returncode == 0, val.stdout + val.stderr
    assert "15/15" in val.stdout or "15/15 checks passed" in val.stdout or "checks passed" in val.stdout

    rows_or = list(csv.DictReader(out.open()))
    rows_308 = list(csv.DictReader((REPO / "submissions" / "sub_308_flagship_f1_transduction_rank.csv").open()))
    rows_533 = list(csv.DictReader((REPO / "submissions" / "sub_533_seqheavy_c50_sub201.csv").open()))
    sample = [r["ID"] for r in csv.DictReader((REPO / "data" / "raw" / "SampleSubmission.csv").open())]
    assert [r["ID"] for r in rows_or] == sample
    f_or = np.array([int(float(r["TargetF1"])) for r in rows_or])
    p_or = np.array([float(r["TargetRAUC"]) for r in rows_or])
    f308 = np.array([int(float(r["TargetF1"])) for r in rows_308])
    p308 = np.array([float(r["TargetRAUC"]) for r in rows_308])
    p533 = np.array([float(r["TargetRAUC"]) for r in rows_533])
    assert np.array_equal(f_or, (np.maximum(p308, p533) >= 0.5).astype(int))
    assert int(((f_or == 0) & (f308 == 1)).sum()) == 0
    assert np.array_equal(f_or, (p_or >= 0.5).astype(int))


def test_or_stratum_cli_changes_only_allowed_rows():
    proc = subprocess.run(
        [PY, str(STRATUM_CLI), "--gate", "all"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    mod = _load_mod()
    test = pd.read_csv(REPO / "data" / "raw" / "Test.csv")
    sample = [r["ID"] for r in csv.DictReader((REPO / "data" / "raw" / "SampleSubmission.csv").open())]
    if test["ID"].astype(str).tolist() != sample:
        indexer = {k: i for i, k in enumerate(test["ID"].astype(str).tolist())}
        test = test.iloc[[indexer[k] for k in sample]].reset_index(drop=True)
    masks = mod.stratum_masks_from_test(test)
    f308 = np.array(
        [
            int(float(r["TargetF1"]))
            for r in csv.DictReader((REPO / "submissions" / "sub_308_flagship_f1_transduction_rank.csv").open())
        ]
    )
    primary = REPO / "submissions" / "sub_537_or_stratum_s1_or_4m_308_533.csv"
    assert primary.is_file()
    f1 = np.array([int(float(r["TargetF1"])) for r in csv.DictReader(primary.open())])
    extras = (f1 == 1) & (f308 == 0)
    assert extras.sum() == 0 or bool(np.all(masks["s1_or_four"][extras]))
    assert np.array_equal(f1[~masks["s1_or_four"]], f308[~masks["s1_or_four"]])
    assert int(((f1 == 0) & (f308 == 1)).sum()) == 0


def test_restore_anchor_keeps_extras_and_raw_anchor():
    mod = _load_mod()
    a = np.array([0.9, 0.8, 0.2, 0.1])
    b = np.array([0.6, 0.4, 0.7, 0.3])
    extra = np.array([False, False, True, False])
    f1, rauc = mod.restore_anchor_on_agreements(a, b, extra)
    assert np.array_equal(f1, np.array([1, 1, 1, 0]))
    assert np.allclose(rauc, np.array([0.9, 0.8, 0.7, 0.1]))
    assert np.array_equal(f1, (rauc >= 0.5).astype(int))


def test_rank_lock_within_side_preserves_decisions():
    mod = _load_mod()
    dec = np.array([1, 1, 0, 0, 1])
    rank = np.array([0.2, 0.9, 0.8, 0.1, 0.4])
    locked = mod.rank_lock_within_side(dec, rank)
    assert np.array_equal((locked >= 0.5).astype(int), dec)
    assert locked[1] > locked[4] > locked[0] >= 0.5
    assert locked[3] < locked[2] < 0.5


def test_f1lock537_cli_writes_zero_decision_flip_vs_537():
    script = REPO / "scripts" / "build_f1lock537_restore308_20260816.py"
    proc = subprocess.run(
        [PY, str(script)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    out = REPO / "submissions" / "sub_542_f1lock537_restore308.csv"
    rows_542 = list(csv.DictReader(out.open()))
    rows_537 = list(csv.DictReader((REPO / "submissions" / "sub_537_or_stratum_s1_or_4m_308_533.csv").open()))
    rows_308 = list(csv.DictReader((REPO / "submissions" / "sub_308_flagship_f1_transduction_rank.csv").open()))
    f542 = np.array([int(float(r["TargetF1"])) for r in rows_542])
    p542 = np.array([float(r["TargetRAUC"]) for r in rows_542])
    f537 = np.array([int(float(r["TargetF1"])) for r in rows_537])
    p308 = np.array([float(r["TargetRAUC"]) for r in rows_308])
    assert np.array_equal(f542, f537)
    assert np.array_equal(f542, (p542 >= 0.5).astype(int))
    extras = f537 != (p308 >= 0.5).astype(int)
    assert int(extras.sum()) == 16
    assert np.allclose(p542[~extras], p308[~extras])
    val = subprocess.run(
        [PY, str(REPO / "src" / "validate_submission.py"), str(out)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert val.returncode == 0, val.stdout + val.stderr
    assert "15/15 checks passed" in val.stdout
