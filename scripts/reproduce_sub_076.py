"""Reproduce the historical composition in sub_076_aucmax_labels.csv.

sub_076 = sub_067_ratefix's archived probability vector with
sub_075_fpadopt's values adopted on every row where the two disagree on the
0.5-side, so the label set is exactly sub_075's. This helper validates the
composition from stored historical parent CSVs; the original r19 parent
generators are not shipped and this is not a clean raw-data reproduction.
TargetF1 == (TargetRAUC >= 0.5).
"""
import numpy as np, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBS = ROOT / "submissions"

ids = pd.read_csv(SUBS / "sub_056_notebook_w05r1.csv").ID.values
p67 = pd.read_csv(SUBS / "sub_067_ratefix.csv").TargetRAUC.values
p75 = pd.read_csv(SUBS / "sub_075_fpadopt.csv").TargetRAUC.values
diff = (p67 >= 0.5) != (p75 >= 0.5)
p76 = p67.copy(); p76[diff] = p75[diff]
out = pd.DataFrame({"ID": ids, "TargetF1": (p76 >= 0.5).astype(int),
                    "TargetRAUC": p76})
ref = pd.read_csv(SUBS / "sub_076_aucmax_labels.csv")
assert (out.TargetRAUC.values == ref.TargetRAUC.values).all()
assert (out.TargetF1.values == ref.TargetF1.values).all()
print(f"sub_076 reproduced byte-exactly: {int(diff.sum())} adopted rows, "
      f"predpos {(p76 >= 0.5).mean():.4f}")
