"""Historical composition helper for submissions/sub_075_fpadopt.csv.

This is not a current clean raw-data reproduction path. It composes the
archived vectors already present in this checkout; the original r19 generator
and its round-specific state are not shipped. sub_075 is a piecewise
composition of two historical vectors:
  p71 = 0.80 * sub_056 + 0.20 * impute_member   (sub_071_impute2)
  p75 = sub_073, except rows where (p73 >= 0.5) and (p71 < 0.5) take p71
No threshold is tuned; TargetF1 == (TargetRAUC >= 0.5) as everywhere.
"""
import numpy as np, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBS = ROOT / "submissions"

s56 = pd.read_csv(SUBS / "sub_056_notebook_w05r1.csv")
p56 = s56.TargetRAUC.values
member = np.load(ROOT / "eda/r18_impute_member_test.npy")
# sub_071's own regeneration is eda/r19_impute2.py; its recomposition here is
# verified to 1 ulp (float expression-order differs), and the sub_075 build
# below uses the CSV values exactly as the original construction did.
recomp = 0.80 * p56 + 0.20 * member
ref71 = pd.read_csv(SUBS / "sub_071_impute2.csv").TargetRAUC.values
assert np.abs(recomp - ref71).max() <= 2.3e-16, "sub_071 recomposition failed"
assert ((recomp >= 0.5) == (ref71 >= 0.5)).all(), "sub_071 label mismatch"
p71 = ref71

p73 = pd.read_csv(SUBS / "sub_073_harvest.csv").TargetRAUC.values
dem = (p73 >= 0.5) & (p71 < 0.5)
p75 = p73.copy(); p75[dem] = p71[dem]
out = pd.DataFrame({"ID": s56.ID.values,
                    "TargetF1": (p75 >= 0.5).astype(int),
                    "TargetRAUC": p75})
ref = pd.read_csv(SUBS / "sub_075_fpadopt.csv")
assert (out.TargetRAUC.values == ref.TargetRAUC.values).all()
assert (out.TargetF1.values == ref.TargetF1.values).all()
print(f"sub_075 reproduced byte-exactly: {int(dem.sum())} adopted demotions, "
      f"predpos {(p75 >= 0.5).mean():.4f}")
