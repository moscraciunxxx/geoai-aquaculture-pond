#!/usr/bin/env python3
"""Add-only OR of two default-0.5 heads via elementwise max.

Default parents: sub_308 ∪ sub_533. Extra --other heads are recorded.
No upload. Zero drops of sub_308 positives.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.or_max_union import build_or_max  # noqa: E402
from src.validate_submission import validate  # noqa: E402

SAMPLE = ROOT / "data" / "raw" / "SampleSubmission.csv"
A308 = ROOT / "submissions" / "sub_308_flagship_f1_transduction_rank.csv"
DEFAULT_OTHER = ROOT / "submissions" / "sub_533_seqheavy_c50_sub201.csv"
OUT = ROOT / "submissions" / "sub_536_or_max_308_533.csv"
REPORT = ROOT / "eda" / "or_max_union_20260816.json"
VALIDATOR = ROOT / "src" / "validate_submission.py"


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


def compare(f308: np.ndarray, f1: np.ndarray, p308: np.ndarray, rauc: np.ndarray) -> dict:
    add = int(((f1 == 1) & (f308 == 0)).sum())
    drop = int(((f1 == 0) & (f308 == 1)).sum())
    return {
        "positives": int(f1.sum()),
        "flips_vs_308": int((f1 != f308).sum()),
        "adds_vs_308": add,
        "drops_vs_308": drop,
        "pearson_vs_308": float(np.corrcoef(rauc, p308)[0, 1]),
        "spearman_vs_308": float(
            pd_spearman(rauc, p308)
        ),
    }


def pd_spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = np.argsort(np.argsort(a))
    rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra.astype(np.float64), rb.astype(np.float64))[0, 1])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--anchor", type=Path, default=A308)
    parser.add_argument("--other", type=Path, default=DEFAULT_OTHER)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--report", type=Path, default=REPORT)
    args = parser.parse_args(argv)

    ids_s = [r["ID"] for r in csv.DictReader(SAMPLE.open())]
    ids_a, f308, p308 = load(args.anchor)
    ids_b, f_other, p_other = load(args.other)
    if ids_a != ids_s or ids_b != ids_s:
        raise RuntimeError("ID order does not match SampleSubmission")
    f1, rauc = build_or_max(p308, p_other)
    if not np.array_equal(f1, ((p308 >= 0.5) | (p_other >= 0.5)).astype(int)):
        raise RuntimeError("max() did not reproduce the 0.5 OR")
    if not np.array_equal(f1, (rauc >= 0.5).astype(int)):
        raise RuntimeError("0.5 identity broken")
    if int(((f1 == 0) & (f308 == 1)).sum()) != 0:
        raise RuntimeError("OR dropped a sub_308 positive")
    write_submission(args.out, ids_s, f1, rauc)
    if validate(args.out) is not True:
        raise RuntimeError("validator failed")
    stats = compare(f308, f1, p308, rauc)
    payload = {
        "construction": "OR of two default-0.5 heads; RAUC=max; add-only vs first head",
        "anchor": str(args.anchor.relative_to(ROOT) if args.anchor.is_absolute() else args.anchor),
        "other": str(args.other.relative_to(ROOT) if args.other.is_relative_to(ROOT) else args.other),
        "file": str(args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out),
        "sha256": sha256(args.out),
        "upload_performed": False,
        **stats,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
