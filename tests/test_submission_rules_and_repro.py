"""Submission rules and curated-artifact checks for the close-out tree."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
SUBS = REPO / "submissions"
SAMPLE = REPO / "data" / "raw" / "SampleSubmission.csv"
SCRIPTS = REPO / "scripts"

VERIFIED_ARTIFACTS = [
    "sub_202_clean_flagship.csv",
    "sub_201_clean_transduction.csv",
    "sub_056_notebook_w05r1.csv",
    "sub_076_aucmax_labels.csv",
    "FINAL_PRIMARY.csv",
    "FINAL_SECONDARY.csv",
    "sub_067_ratefix.csv",
    "sub_075_fpadopt.csv",
    "sub_307_flagship_f1_seedscale_rank.csv",
    "sub_308_flagship_f1_transduction_rank.csv",
    "sub_537_or_stratum_s1_or_4m_308_533.csv",
    "sub_542_f1lock537_restore308.csv",
]

PUBLIC_BEST_SHA = "bf7f5a8e71b78196321ff5e1096a6f42cc9628c85348c4df198709db6475f20c"


def _load(path: Path):
    rows = list(csv.DictReader(open(path)))
    ids = [r["ID"] for r in rows]
    f1 = np.array([int(float(r["TargetF1"])) for r in rows])
    p = np.array([float(r["TargetRAUC"]) for r in rows])
    return ids, f1, p


def test_sample_and_selected_rule_valid():
    sample_ids = [r["ID"] for r in csv.DictReader(open(SAMPLE))]
    assert len(sample_ids) == 1030
    for name in VERIFIED_ARTIFACTS:
        path = SUBS / name
        assert path.exists(), name
        ids, f1, p = _load(path)
        assert ids == sample_ids
        assert np.all(f1 == (p >= 0.5).astype(int))
        assert np.all((p > 0) & (p < 1))
        assert 0.30 <= float(f1.mean()) <= 0.75


def test_finals_match_selections():
    def sha(p):
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()

    assert sha(SUBS / "FINAL_PRIMARY.csv") == sha(SUBS / "sub_076_aucmax_labels.csv")
    assert sha(SUBS / "FINAL_SECONDARY.csv") == sha(SUBS / "sub_056_notebook_w05r1.csv")


def test_reproduce_sub_076_byte_exact():
    script = SCRIPTS / "reproduce_sub_076.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "byte-exactly" in proc.stdout


def test_sub_076_is_067_rank_with_075_labels():
    _, f76, p76 = _load(SUBS / "sub_076_aucmax_labels.csv")
    _, _, p67 = _load(SUBS / "sub_067_ratefix.csv")
    _, f75, p75 = _load(SUBS / "sub_075_fpadopt.csv")
    assert np.all(f76 == f75)
    agree = (p67 >= 0.5) == (p75 >= 0.5)
    assert np.allclose(p76[agree], p67[agree])
    disagree = ~agree
    assert np.allclose(p76[disagree], p75[disagree])


def test_validate_submission_cli():
    proc = subprocess.run(
        [sys.executable, str(REPO / "src" / "validate_submission.py"),
         str(SUBS / "sub_542_f1lock537_restore308.csv")],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "15/15" in proc.stdout or proc.stdout.count("[PASS]") >= 15


def test_every_submission_csv_validates():
    sample_ids = [r["ID"] for r in csv.DictReader(open(SAMPLE))]
    paths = sorted(SUBS.glob("*.csv"))
    assert paths
    for path in paths:
        ids, f1, p = _load(path)
        assert ids == sample_ids, path.name
        assert np.all(f1 == (p >= 0.5).astype(int)), path.name
        assert np.all(np.isfinite(p)), path.name
        assert np.all((p > 0) & (p < 1)), path.name
        assert len(np.unique(p)) > 100, path.name
        assert 0.30 <= float(f1.mean()) <= 0.75, path.name


def test_leaderboard_ledger_has_fixed_width_rows():
    ledger = REPO / "eda" / "lb_results.csv"
    with ledger.open(newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows
    width = len(rows[0])
    assert width == 14
    assert all(len(row) == width for row in rows[1:])
    scored = [
        row for row in rows[1:]
        if row[12] not in ("", "UNSCORED")
    ]
    best = max(scored, key=lambda row: float(row[12]))
    assert best[0] == "sub_542_f1lock537_restore308"
    assert best[1] == "bNsDafsS"
    assert float(best[12]) == 0.925724375


def test_public_best_hash_and_f1_lock_vs_537():
    best = SUBS / "sub_542_f1lock537_restore308.csv"
    assert hashlib.sha256(best.read_bytes()).hexdigest() == PUBLIC_BEST_SHA
    _, f542, _ = _load(best)
    _, f537, _ = _load(SUBS / "sub_537_or_stratum_s1_or_4m_308_533.csv")
    _, f308, _ = _load(SUBS / "sub_308_flagship_f1_transduction_rank.csv")
    assert np.array_equal(f542, f537)
    assert int(((f542 == 1) & (f308 == 0)).sum()) == 16
    assert int(((f542 == 0) & (f308 == 1)).sum()) == 0
