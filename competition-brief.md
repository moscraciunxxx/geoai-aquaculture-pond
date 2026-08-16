# GeoAI Aquaculture Pond Identification Challenge

**Host:** FAO + ITU (AI for Good), via Zindi
**URL:** https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge
**Brief compiled:** 2026-07-26

---

## Task

Binary classification on tabular data. Each row is one **10m × 10m ground patch**. Predict whether the patch is an aquaculture pond (1) or other land cover (0).

No lat/lon is provided. Features are derived from satellite imagery over two pilot regions.

## Data

| File | Rows | Notes |
|---|---|---|
| `Train.csv` | 1,821 | includes target |
| `Test.csv` | 1,030 | no target |
| `SampleSubmission.csv` | — | format reference |
| `Trustworthiness_Evaluation.pdf` | — | AI trustworthiness evaluation document |

**Feature structure:** 12 monthly composites per location.

- **Sentinel-1 (SAR):** VH, VV backscatter. Cloud-independent — present for all valid months.
- **Sentinel-2 (optical):** blue, green, red, red-edge 1/2/3, NIR, narrow NIR, SWIR 1/2. May be absent for a month due to cloud cover even when S1 is present.

**Missing data sentinel:** `-9999` fills all bands for months with no valid observation. This is not NaN by default — convert explicitly.

**Test-set masking:** each test row contains only **4, 5, or 6 consecutive months** of real data; the rest is masked. Deliberate — the model must work from whatever seasonal window is available rather than a fixed time of year.

**Class balance:** train is ~40% positive. Organisers state test *may* have a
higher positive rate. A public clarification request about whether prior-shift
probability corrections are allowed remains unanswered, so this repository
does not treat prior matching as an authorized modelling lever.

## Metric

Weighted blend, computed on the test set:

```
score = 0.60 × F1 + 0.40 × ROC-AUC
```

Submission requires two prediction columns:

```
ID              TargetF1    TargetRAUC
ID_TS_xUR2T2    1           0.87
ID_TS_yN4Ale    0           0.12
```

- `TargetF1` — binary label
- `TargetRAUC` — probability of pond

## Dates

| Event | Date |
|---|---|
| Start | 2026-06-08 |
| Enrolment closes | 2026-08-07 |
| Submissions close | 2026-08-16 |
| Private LB reveal | 2026-08-16 |

The official public pages state the date but not a precise closing timezone.
Do not convert it to an exact local cutoff without checking the authenticated
competition UI.

## Split

Public leaderboard = ~30% of test. Private = remaining 70%, revealed at close.

Train and test are drawn from **different time periods**.

## Scoring (two phases)

**Phase 1 — leaderboard (65% of final).** Points by rank: 1st = 10, 2nd = 9, 3rd = 8, 4th = 7, 5th = 6.

**Phase 2 — innovation and practicality (35%).** Rubric applied to the top 5 only:

| Points | Criterion |
|---|---|
| 0 | Not reproducible |
| 2–5 | Reproducible, unclear workflow, vague explanation |
| 6–8 | Reproducible, clear workflow, adequate explanation of novelty |
| 9–10 | Reproducible, workflow well aligned with proposed approach, clearly explains key challenges and how they were addressed |

Note the weighting: the gap between 1st and 5th on the leaderboard is 4 points, while the rubric spans 10. A well-documented 4th place can beat a poorly documented 1st.

## Prizes

1st 500 CHF · 2nd 300 CHF · 3rd 200 CHF. 1,000 Zindi points available.

---

## Constraints

Re-read this section before every modelling decision.

**Hard bans**

- **No threshold tuning.** `TargetF1` must use the default 0.5 cutoff on the predicted probability. Setting a threshold is "strictly forbidden".
- **No probability rounding or clipping** to improve leaderboard position. Zindi wants raw probabilities.
- **No AutoML** tools.
- **No external data.** Only the data supplied for this challenge.
- **No paid services** or free trials requiring a credit card.
- **No custom private packages** in the submitted notebook.

**Limits**

- Max **1,000 training samples per pilot region**, including any self-collected samples.
- **5 submissions/day, 100 total.**
- Team size max 4. No new members in the final 5 days.
- Select **2 submissions** for private scoring before close; otherwise the best 2 public are used.

**Permitted**

- Open-source languages and tools only.
- Scripts limited to **Python and Google Earth Engine JavaScript**.
- Pretrained models allowed if openly available to everyone.
- Data usable under CC-BY SA 4.0.

**Code review**

- Top 5 on the private leaderboard are emailed at close; **48 hours** to submit code.
- Must run end-to-end from raw data to output. Seeds set. If it doesn't reproduce the leaderboard score, rank is adjusted down. If it doesn't run at all, dropped from top 5.
- Zindi may request code from any user at any time during the challenge — 24 hours to respond.

**Penalties:** first offence = 6-month prize ban and −2000 points. Second = account disabled.

---

## Central difficulty

**Temporal distribution shift under partial observation.**

Three things compound:

1. Train and test come from different time periods, so features that separate ponds in the training window may not in the test window.
2. Test rows expose only a 4–6 month consecutive slice, and *which* slice varies by row. Any feature built on a fixed calendar month, or on full-year aggregates, will be unavailable or biased for most test rows.
3. The positive rate is expected to differ between train and test, and the threshold-tuning ban removes the usual lever for correcting it.

Consequences for the approach:

- Features must be **window-relative, not calendar-relative** — statistics over available months, not "March NDWI".
- Local validation must **simulate the masking**: subsample train rows to random 4–6 consecutive month windows. Validating on full 12-month train rows measures the wrong thing entirely.
- Calibration has to be built into the model — class weights, resampling, or a calibration layer fit on train — since a post-hoc cutoff is banned.
- Adversarial validation (train-vs-test classifier) is worth running early to identify which features carry the shift.

## Official clarifications used in this repository

- [Revised-data announcement](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/33587): the leaderboard was reset for the revised files and the current Test rows use partial consecutive windows.
- [External-data clarification](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/33598): only the supplied challenge dataset may be used for training.
- [S1/S2 missingness clarification](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/33603): S1 may be present while all S2 bands are missing inside the observed span; this affects 273 Test rows.
- [Threshold discussion](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/33912): the default `0.5` rule is the governing interpretation; the clean builders enforce it mechanically.

---

## Status

- [x] Recon complete
- [x] Data downloaded and verified (checksums in `data/raw/CHECKSUMS.txt`)
- [x] EDA complete — historical `eda/findings.md` is not shipped; current
  findings are consolidated in `solution.md` and the candidate reports.
- [x] Validation harness (masked windows + gap injection + prior resampling)
- [x] Baseline submission
- [x] Reproducibility write-up

### EDA headlines

- Train rows are **fully observed** (all 12 months, zero sentinels); only test
  is masked. Validating on unmasked train measures the wrong task.
- Test masking is **uniform random 4–6 month consecutive windows** — the
  mid-year availability peak is geometry, not seasonal selection.
- Genuine radiometric shift: month-matched, all-bands-present adversarial
  AUC **0.955–0.980**. 11 of 12 bands darker in test; VV down 31.7%.
- Label signal and shift are **largely orthogonal** (6/30 feature overlap,
  ρ = 0.17). VV is the exception and the main risk.
- Test positive rate estimated **0.50–0.58** vs 0.404 in train, but prior
  correction is **not** the lever — only 7.3% of test rows sit near the 0.5
  boundary, so correcting to 0.55 flips 27 rows.
- Local masked CV ≈ **0.965 blended**. Upper bound, not a forecast.
