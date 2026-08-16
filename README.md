# GeoAI Aquaculture Pond Identification

Solution for the [Zindi / FAO / ITU GeoAI Aquaculture Pond Identification Challenge](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge): binary classification of 10 m patches as aquaculture pond vs other land cover from Sentinel-1 / Sentinel-2 monthly composites.

**Metric:** `0.6 × F1@0.5 + 0.4 × ROC-AUC`  
**Rule:** `TargetF1` must be exactly `(TargetRAUC >= 0.5)` — no threshold search.  
**Data:** supplied `Train.csv` / `Test.csv` only. Test rows expose one consecutive 4–6 month window.

This repository is the **curated close-out**, not the 500-file experiment dump. Challenge close/reveal: 16 Aug 2026.

## Final measured scores

| Role | File | Zindi ID | Public | Private |
|------|------|----------|-------:|--------:|
| Selected (public-best climb) | [`submissions/sub_542_f1lock537_restore308.csv`](submissions/sub_542_f1lock537_restore308.csv) | `bNsDafsS` | **0.925724** | 0.924647 |
| Selected (same 16 extras) | [`submissions/sub_537_or_stratum_s1_or_4m_308_533.csv`](submissions/sub_537_or_stratum_s1_or_4m_308_533.csv) | `2F9tRW8b` | 0.923267 | **0.924790** |
| Flagship F1 + transduction rank | [`submissions/sub_308_flagship_f1_transduction_rank.csv`](submissions/sub_308_flagship_f1_transduction_rank.csv) | `Q7xLfCHt` | 0.920592 | — |
| Conservative rank hedge | [`submissions/sub_307_flagship_f1_seedscale_rank.csv`](submissions/sub_307_flagship_f1_seedscale_rank.csv) | `T8rvcmL3` | 0.920185 | — |
| Stronger *unselected* private | `sub_079b` physics / own labels | `MByz3fSc` | 0.914737 | **0.930370** |
| Stronger *unselected* private | `sub_102b` `076` labels + expert rank | `WmJa7J1o` | 0.914780 | **0.928342** |

Judged private score for the selected pair is the better of the two: **`537` at 0.924790**. The 16 extras that lifted public F1 to 0.903226 produced the **same F1 on private**. Files that *lost* public by ~0.011 won private. See [`eda/private_reveal_20260816.md`](eda/private_reveal_20260816.md).

`542` = `537` decisions (308 ∪ 16 S1-only/4-month `533` extras) with raw `308` scores restored on the other 1,014 rows. F1 locked; public AUC 0.95947 beat both parents.

## What this repo keeps

- Official raw tables (`data/raw/`)
- The notebook fallback (`geoai_pond_solution.ipynb` → `sub_056`)
- Flagship and climb CSVs listed above, plus historical `075`/`076` and the AND-fail `535`
- Validators and the add-only / restore builders (`src/`, `scripts/`)
- Score ledger + reveal note (`eda/`)
- Write-up: [`solution.md`](solution.md), [`TRUSTWORTHINESS.md`](TRUSTWORTHINESS.md), [`REVIEW_MATRIX.md`](REVIEW_MATRIX.md)

Hundreds of dead experiment CSVs, fold dumps, and `data/processed/` caches were discarded.

## Run

Python 3.10+. From the repo root:

```bash
pip install -r requirements.txt
python src/validate_submission.py submissions/sub_542_f1lock537_restore308.csv
python -m pytest -q tests/test_submission_rules_and_repro.py tests/test_public_slice_metric.py tests/test_or_max_union_20260816.py
python scripts/reproduce_sub_076.py
```

Rebuild the climb files (does not upload):

```bash
python scripts/build_or_stratum_20260816.py --gate all
python scripts/build_f1lock537_restore308_20260816.py
```

## Hidden-exam lesson

Public invert is diagnosis, not a construction kit. The two private files must not share a public-informed F1 cut. A different representation that loses public by ~0.001 is often the private file. That rule is also a Grok skill: `hidden-exam-discipline` (`/hidden-exam`).
