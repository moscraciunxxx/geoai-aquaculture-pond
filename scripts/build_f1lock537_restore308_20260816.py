#!/usr/bin/env python3
"""Lock sub_537 F1 extras; restore sub_308 ranking on every agreed row.

sub_537 beat 0.92059 by adding 16 S1-only/4-month sub_533 extras (+4 TP +2 FP)
but max() rewrote 532 of the 571 sub_308 positives and lost 107 AUC pairs.
This file keeps those 16 extras and puts p308 back on the other 1014 rows.

A second file fully rank-locks the 537 decisions with the sub_308 order.
No upload.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.or_max_union import (  # noqa: E402
    rank_lock_within_side,
    restore_anchor_on_agreements,
    stratum_masks_from_test,
)
from src.validate_submission import validate  # noqa: E402

SAMPLE = ROOT / "data" / "raw" / "SampleSubmission.csv"
TEST = ROOT / "data" / "raw" / "Test.csv"
A308 = ROOT / "submissions" / "sub_308_flagship_f1_transduction_rank.csv"
A533 = ROOT / "submissions" / "sub_533_seqheavy_c50_sub201.csv"
A537 = ROOT / "submissions" / "sub_537_or_stratum_s1_or_4m_308_533.csv"
OUT_RESTORE = ROOT / "submissions" / "sub_542_f1lock537_restore308.csv"
OUT_RANKLOCK = ROOT / "submissions" / "sub_543_f1lock537_ranklock308.csv"
REPORT = ROOT / "eda" / "f1lock537_restore308_20260816.json"


def load(path: Path):
    rows = list(csv.DictReader(path.open()))
    ids = [r["ID"] for r in rows]
    f1 = np.array([int(float(r["TargetF1"])) for r in rows], dtype=int)
    p = np.array([float(r["TargetRAUC"]) for r in rows], dtype=np.float64)
    return ids, f1, p


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_submission(path: Path, ids: list[str], f1: np.ndarray, rauc: np.ndarray) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["ID", "TargetF1", "TargetRAUC"])
        for i, row_id in enumerate(ids):
            writer.writerow([row_id, int(f1[i]), f"{rauc[i]:.16g}"])


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = np.argsort(np.argsort(a))
    rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra.astype(np.float64), rb.astype(np.float64))[0, 1])


def stats(f1, rauc, f308, p308, f537) -> dict:
    return {
        "positives": int(f1.sum()),
        "flips_vs_308": int((f1 != f308).sum()),
        "flips_vs_537": int((f1 != f537).sum()),
        "adds_vs_308": int(((f1 == 1) & (f308 == 0)).sum()),
        "drops_vs_308": int(((f1 == 0) & (f308 == 1)).sum()),
        "pearson_vs_308": float(np.corrcoef(rauc, p308)[0, 1]),
        "spearman_vs_308": spearman(rauc, p308),
        "n_unique": int(len(np.unique(rauc))),
    }


def main() -> int:
    ids_s = [r["ID"] for r in csv.DictReader(SAMPLE.open())]
    ids_a, f308, p308 = load(A308)
    ids_b, _f533, p533 = load(A533)
    ids_c, f537, p537 = load(A537)
    if ids_a != ids_s or ids_b != ids_s or ids_c != ids_s:
        raise RuntimeError("ID order does not match SampleSubmission")
    test = pd.read_csv(TEST)
    if test["ID"].astype(str).tolist() != ids_s:
        indexer = {key: i for i, key in enumerate(test["ID"].astype(str).tolist())}
        test = test.iloc[[indexer[k] for k in ids_s]].reset_index(drop=True)
    allow = stratum_masks_from_test(test)["s1_or_four"]
    extras = (f308 == 0) & (p533 >= 0.5) & allow
    if int(extras.sum()) != 16:
        raise RuntimeError(f"expected 16 extras, got {int(extras.sum())}")
    if not np.array_equal(f537, ((f308 == 1) | extras).astype(int)):
        raise RuntimeError("537 F1 is not 308 OR the 16 extras")

    f1_r, rauc_r = restore_anchor_on_agreements(p308, p533, extras)
    if not np.array_equal(f1_r, f537):
        raise RuntimeError("restore changed 537 decisions")
    if not np.array_equal(f1_r, (rauc_r >= 0.5).astype(int)):
        raise RuntimeError("restore broke 0.5 identity")
    if not np.allclose(rauc_r[~extras], p308[~extras]):
        raise RuntimeError("non-extra rows must be raw p308")
    write_submission(OUT_RESTORE, ids_s, f1_r, rauc_r)
    if validate(OUT_RESTORE) is not True:
        raise RuntimeError("validator failed on restore file")

    rauc_l = rank_lock_within_side(f537, p308)
    f1_l = (rauc_l >= 0.5).astype(int)
    if not np.array_equal(f1_l, f537):
        raise RuntimeError("rank-lock changed 537 decisions")
    write_submission(OUT_RANKLOCK, ids_s, f1_l, rauc_l)
    if validate(OUT_RANKLOCK) is not True:
        raise RuntimeError("validator failed on rank-lock file")

    payload = {
        "construction": (
            "sub_537 add-only extras (16) kept; sub_308 scores restored on "
            "the other 1014 rows. Sibling fully rank-locks 537 labels with 308 order."
        ),
        "why": (
            "537 max() lifted 532 of 571 sub_308 positives (mean +0.147) and "
            "lost 107 public AUC pairs. F1 is locked at the winning 168/23 cut."
        ),
        "files": [
            {"file": str(OUT_RESTORE.relative_to(ROOT)), "sha256": sha256(OUT_RESTORE),
             **stats(f1_r, rauc_r, f308, p308, f537)},
            {"file": str(OUT_RANKLOCK.relative_to(ROOT)), "sha256": sha256(OUT_RANKLOCK),
             **stats(f1_l, rauc_l, f308, p308, f537)},
        ],
        "n_extras": 16,
        "upload_performed": False,
        "beat_537_certified": False,
    }
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
