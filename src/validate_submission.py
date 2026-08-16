"""Submission validator. Run before every upload.

Checks structure against SampleSubmission.csv and enforces the challenge rules
that are mechanically checkable - in particular that TargetF1 is exactly the
0.5-threshold binarisation of TargetRAUC, since setting any other threshold is
forbidden.

Usage: python3 src/validate_submission.py submissions/<file>.csv
Exit code 0 = all checks pass.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def validate(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    try:
        sample = pd.read_csv(RAW / "SampleSubmission.csv")
        test = pd.read_csv(RAW / "Test.csv")
        sub = pd.read_csv(path)
    except Exception as exc:
        print(f"\nvalidating {path}\n")
        print(f"  [FAIL]  CSV can be read -> {type(exc).__name__}: {exc}")
        return False

    if list(sub.columns) != list(sample.columns):
        print(f"\nvalidating {path}\n")
        print("  [FAIL]  columns match sample exactly"
              f" -> {list(sub.columns)} vs {list(sample.columns)}")
        return False

    checks = []

    def chk(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # --- structure -------------------------------------------------------
    chk("columns match sample exactly",
        list(sub.columns) == list(sample.columns),
        f"{list(sub.columns)} vs {list(sample.columns)}")
    chk("row count matches test set", len(sub) == len(test),
        f"{len(sub)} vs {len(test)}")
    chk("no duplicate IDs", sub.ID.duplicated().sum() == 0,
        f"{int(sub.ID.duplicated().sum())} duplicates")
    chk("ID set matches test exactly", set(sub.ID) == set(test.ID),
        f"missing {len(set(test.ID)-set(sub.ID))}, "
        f"extra {len(set(sub.ID)-set(test.ID))}")
    chk("ID order matches sample submission",
        (sub.ID.values == sample.ID.values).all())

    # --- dtypes and ranges ----------------------------------------------
    chk("TargetF1 is integer dtype",
        pd.api.types.is_integer_dtype(sub.TargetF1), str(sub.TargetF1.dtype))
    chk("TargetF1 values are only 0/1",
        set(sub.TargetF1.unique()) <= {0, 1},
        str(sorted(sub.TargetF1.unique())))
    chk("TargetRAUC is float dtype",
        pd.api.types.is_float_dtype(sub.TargetRAUC), str(sub.TargetRAUC.dtype))
    chk("no NaN anywhere", sub.notna().all().all().item(),
        f"{int(sub.isna().sum().sum())} NaN")
    chk("no infinities",
        np.isfinite(sub.TargetRAUC.values).all())
    chk("TargetRAUC within [0, 1]",
        (sub.TargetRAUC >= 0).all() and (sub.TargetRAUC <= 1).all(),
        f"[{sub.TargetRAUC.min():.6f}, {sub.TargetRAUC.max():.6f}]")

    # --- rules compliance ------------------------------------------------
    implied = (sub.TargetRAUC >= 0.5).astype(int)
    mismatch = int((implied != sub.TargetF1).sum())
    chk("TargetF1 == (TargetRAUC >= 0.5)  [threshold rule]",
        mismatch == 0, f"{mismatch} rows disagree")

    # probabilities must be raw, not rounded or clipped to game the metric
    n_unique = sub.TargetRAUC.nunique()
    chk("TargetRAUC not rounded/degenerate (>100 distinct values)",
        n_unique > 100, f"{n_unique} distinct values")
    at_bounds = int(((sub.TargetRAUC == 0) | (sub.TargetRAUC == 1)).sum())
    chk("TargetRAUC not hard-clipped to exactly 0/1",
        at_bounds == 0, f"{at_bounds} rows at a bound")

    # --- sanity ----------------------------------------------------------
    pos = sub.TargetF1.mean()
    chk("predicted positive rate in a plausible range (0.30-0.75)",
        0.30 <= pos <= 0.75, f"{pos:.4f}")

    # --- report ----------------------------------------------------------
    width = max(len(n) for n, _, _ in checks) + 2
    print(f"\nvalidating {path}\n")
    n_fail = 0
    for name, ok, detail in checks:
        flag = "PASS" if ok else "FAIL"
        if not ok:
            n_fail += 1
        line = f"  [{flag}]  {name:<{width}}"
        if detail and not ok:
            line += f" -> {detail}"
        elif detail:
            line += f" ({detail})"
        print(line)

    print(f"\n  {len(checks) - n_fail}/{len(checks)} checks passed")
    print("\nsummary")
    print(f"  rows                     {len(sub)}")
    print(f"  positive rate @0.5       {pos:.4f}")
    print(f"  mean probability         {sub.TargetRAUC.mean():.4f}")
    print(f"  probability range        [{sub.TargetRAUC.min():.4f}, "
          f"{sub.TargetRAUC.max():.4f}]")
    print(f"  distinct probabilities   {n_unique}")
    amb = ((sub.TargetRAUC > 0.2) & (sub.TargetRAUC < 0.8)).mean()
    print(f"  ambiguous (0.2-0.8)      {amb:.1%}")
    print(f"\n  first 3 rows:")
    print("   " + sub.head(3).to_string(index=False).replace("\n", "\n   "))
    return n_fail == 0


if __name__ == "__main__":
    paths = sys.argv[1:] or sorted((ROOT / "submissions").glob("*.csv"))
    ok = all(validate(p) for p in paths)
    print()
    sys.exit(0 if ok else 1)
