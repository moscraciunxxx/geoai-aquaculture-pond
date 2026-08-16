#!/usr/bin/env python3
"""Stratum-gated add-only OR of sub_308 and another default-0.5 head.

Extras are allowed only on S1-only and/or 4-month Test rows derived from
``data/raw/Test.csv`` sentinels. Complementary rows keep sub_308.
"""
from __future__ import annotations

import argparse
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
    build_or_stratum,
    stratum_masks_from_test,
)
from src.validate_submission import validate  # noqa: E402

SAMPLE = ROOT / "data" / "raw" / "SampleSubmission.csv"
TEST = ROOT / "data" / "raw" / "Test.csv"
A308 = ROOT / "submissions" / "sub_308_flagship_f1_transduction_rank.csv"
DEFAULT_OTHER = ROOT / "submissions" / "sub_533_seqheavy_c50_sub201.csv"
OUT_DEFAULT = ROOT / "submissions" / "sub_537_or_stratum_s1_or_4m_308_533.csv"
REPORT = ROOT / "eda" / "or_stratum_20260816.json"

GATE_TO_KEY = {
    "s1": "s1_only",
    "m4": "four_month",
    "s1_or_m4": "s1_or_four",
}
GATE_TO_OUT = {
    "s1": ROOT / "submissions" / "sub_538_or_stratum_s1only_308_533.csv",
    "m4": ROOT / "submissions" / "sub_539_or_stratum_4m_308_533.csv",
    "s1_or_m4": OUT_DEFAULT,
}


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


def build_one(gate: str, ids_s: list[str], f308, p308, p_other, allow: np.ndarray, out: Path) -> dict:
    f1, rauc = build_or_stratum(p308, p_other, allow)
    if int(((f1 == 0) & (f308 == 1)).sum()) != 0:
        raise RuntimeError(f"{gate}: dropped a sub_308 positive")
    # extras must sit on the allow mask
    extra = (f1 == 1) & (f308 == 0)
    if extra.any() and not bool(np.all(allow[extra])):
        raise RuntimeError(f"{gate}: extra positive outside the stratum")
    complementary = ~allow
    if complementary.any() and not np.array_equal(f1[complementary], f308[complementary]):
        raise RuntimeError(f"{gate}: complementary rows changed vs sub_308")
    if not np.array_equal(f1, (rauc >= 0.5).astype(int)):
        raise RuntimeError(f"{gate}: 0.5 identity broken")
    write_submission(out, ids_s, f1, rauc)
    if validate(out) is not True:
        raise RuntimeError(f"validator failed: {out}")
    return {
        "gate": gate,
        "file": str(out.relative_to(ROOT)),
        "sha256": sha256(out),
        "allow_rows": int(allow.sum()),
        "positives": int(f1.sum()),
        "flips_vs_308": int((f1 != f308).sum()),
        "adds_vs_308": int(extra.sum()),
        "drops_vs_308": 0,
        "pearson_vs_308": float(np.corrcoef(rauc, p308)[0, 1]),
        "spearman_vs_308": spearman(rauc, p308),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--anchor", type=Path, default=A308)
    parser.add_argument("--other", type=Path, default=DEFAULT_OTHER)
    parser.add_argument(
        "--gate",
        choices=("s1", "m4", "s1_or_m4", "all"),
        default="all",
    )
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=REPORT)
    args = parser.parse_args(argv)

    ids_s = [r["ID"] for r in csv.DictReader(SAMPLE.open())]
    test = pd.read_csv(TEST)
    if test["ID"].astype(str).tolist() != ids_s:
        indexer = {key: i for i, key in enumerate(test["ID"].astype(str).tolist())}
        test = test.iloc[[indexer[k] for k in ids_s]].reset_index(drop=True)
    masks = stratum_masks_from_test(test)
    if int(masks["s1_only"].sum()) != 273:
        raise RuntimeError(f"expected 273 S1-only rows, got {int(masks['s1_only'].sum())}")
    if int(masks["four_month"].sum()) != 345:
        raise RuntimeError(f"expected 345 4-month rows, got {int(masks['four_month'].sum())}")

    ids_a, f308, p308 = load(args.anchor)
    ids_b, _f_other, p_other = load(args.other)
    if ids_a != ids_s or ids_b != ids_s:
        raise RuntimeError("ID order does not match SampleSubmission")

    gates = ("s1", "m4", "s1_or_m4") if args.gate == "all" else (args.gate,)
    built = []
    for gate in gates:
        allow = masks[GATE_TO_KEY[gate]]
        out = args.out if (args.out is not None and args.gate != "all") else GATE_TO_OUT[gate]
        built.append(build_one(gate, ids_s, f308, p308, p_other, allow, out))

    payload = {
        "construction": "stratum-gated add-only OR; RAUC=max on allow mask else anchor",
        "anchor": "submissions/sub_308_flagship_f1_transduction_rank.csv",
        "other": "submissions/sub_533_seqheavy_c50_sub201.csv",
        "stratum_counts": {
            "s1_only": int(masks["s1_only"].sum()),
            "four_month": int(masks["four_month"].sum()),
            "s1_or_four": int(masks["s1_or_four"].sum()),
        },
        "files": built,
        "upload_performed": False,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
