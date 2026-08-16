# Official research note — GeoAI Aquaculture Pond Identification Challenge

Fetched live on **2026-08-15** (TinyFish search + `fetch_content` with `ttl=0`, plus an authenticated Chrome DevTools session on the submissions tab). This note records official wording, not recollection. Fetch log: see the companion scratch log written by this run.

**Designated solution (this run):** `submissions/sub_308_flagship_f1_transduction_rank.csv`  
Public incumbent **0.920592385** (AUC 0.957218668, F1 0.896174863, Zindi `Q7xLfCHt`).  
No upload and no private-selection change was made.

---

## Official rules and metric (verbatim / near-verbatim)

Source: [challenge Info page](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge) HTML (`#app` Evaluation + Rules), fetched 2026-08-15.

- **Score:** “The two metrics used in this phase are F1-Score and ROC-AUC. The final leaderboard score is the weighted average of the two:”
  - “**F1-Score (60%)** — provides a balanced measure of model effectiveness by considering both precision and recall…”
  - “**ROC-AUC (40%)** — measures how well the model ranks aquaculture pond locations above non-pond locations…”
  - Written as used in this repository: **`score = 0.60 × F1 + 0.40 × ROC-AUC`**.
- **Columns:** the official sample format is

  ```
  ID                      TargetF1         TargetRAUC
  ID_TS_xUR2T2                1                0.87
  ID_TS_yN4Ale                0                0.12
  ```

- **Default 0.5 / no-threshold rule:** “Setting a probability threshold is strictly forbidden. Your binary target should be based on the default threshold of 0.5.”
- **Raw probabilities:** “If the error metric requires probabilities to be submitted, do not set thresholds (or round your probabilities) to improve your place on the leaderboard. In order to ensure that the client receives the best solution Zindi will need the raw probabilities.”
- **Supplied data only:** “You may use only the datasets provided for this challenge.” Organizer confirmation in [discussion 33598](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/33598): “For this challenge, only the provided dataset may be used for training.”
- **No AutoML:** “Automated machine learning tools such as automl are not permitted.”
- **No paid / credit-card services:** “You may only use tools available to everyone i.e. no paid services or free trials that require a credit card.”
- **Limits:** “You may make a maximum of **5 submissions per day**.” “You may make a maximum of **100 submissions** for this challenge.” Rules list: “Submission Limits: 5 submissions per day, 100 submissions overall.”
- **Two private selections:** “Before the end of the challenge you need to choose **2 submissions** to be judged on for the private leaderboard. If you do not make a selection your 2 best public leaderboard submissions will be used…”
- **Public split:** “The Public Leaderboard includes approximately **30%** of the test dataset.”
- **Dates (timeline on the official page):** Start 08 Jun 26 · Enrolments close 07 Aug 26 · **Close 16 Aug 26** · **Reveal 16 Aug 26**. Header on 2026-08-15: “Closing soon! (1 day left)”.
- **Phase weights:** “Phase One Evaluation (**65%**) … 1st place receives 10 points … 5th place receiving 6 points.” “Innovation and Practicality (**35%**)” rubric 0 / 2–5 / 6–8 / 9–10 for the top 5 only.

## Official data notes

Source: [Data page](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/data) and [discussion 33587](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/33587) / [33603](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/33603).

- “You are provided with a tabular dataset consisting of **1,821** entries for training and **1,030** entries for testing.”
- “Months with no valid observations are filled with **-9999** for all bands.”
- “Each test sample contains **4, 5, or 6 consecutive months** of data with the remaining months masked. This design is intentional.”
- Revised-data announcement (33587): “**Train: original train data + original test data with labels**”; “**Test: new data supplied by the organisers**”; “each test sample now only includes a consecutive block of 4, 5, or 6 months”; “**TargetF1**: binary prediction, 0 or 1”; “**TargetRAUC**: probability between 0.0 and 1.0”; “Submission limits updated: now 5 per day 100 total”.
- S1-present / S2-missing (33603, organizer meganomaly): “Across the test set, 320 month-row entries (2.6%) have S1 data (VH/VV) present but S2 data missing, affecting **273 of the 1,030 test rows**.” “This reflects genuine data availability conditions in the source satellite imagery.”
- Local raw replay on 2026-08-15 (not a substitute for the official sentence): `data/raw/Test.csv` has 1,030 rows; **273** rows have at least one S1-only month; **320** S1-present/S2-missing month-entries; observed-window lengths are only 4/5/6. `Train.csv` is 1,821 rows, `label` positive rate 735/1821 ≈ 0.404.

## Authenticated account snapshot (Chrome, no mutation)

Source: signed-in tab `https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/submissions` (user MosCraciunXXX), 2026-08-15.

- Header: **Submissions 77 / 100**. Close/Reveal **16 Aug 26**.
- Newest scored row: `7r2M71g1` / `sub_527_sub308_q15_temporal_monthshape_q080_t005.csv` / **0.886441675** (AUC 0.921198022, F1 0.863270777).
- Measured incumbent still on the board: `Q7xLfCHt` / `sub_308_flagship_f1_transduction_rank.csv` / **0.920592385**.
- Hedge: `T8rvcmL3` / `sub_307_flagship_f1_seedscale_rank.csv` / 0.92018529.
- **Private selections rechecked read-only on 2026-08-15 (page 2, checkboxes checked, not changed):** `dQtvmvBZ` (`WINNING_PRIMARY.csv`, 0.916074036) and `24GcnwvD` (`sub_056_notebook_w05r1.csv`, 0.912770942). These are older and weaker than `sub_308`/`sub_307`. This run does **not** authorize a selection click.
- Page-1 checkboxes for `Q7xLfCHt` / `T8rvcmL3` were still unchecked. No checkbox was toggled during the audit.

## Other discussion excerpts used

- [33480](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/33480): participants confused `TargetF1`/`TargetRAUC` with scalar metrics; no organizer contradiction of the two-column format.
- [33912](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/33912): rechecked in the signed-in browser on **2026-08-15**. The thread still contains only two participant replies and no organizer answer; the later prior-shift (BBSE) question is also unanswered. Repository policy stays at the written 0.5 rule and does not treat prior matching as authorized.
- [33903](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/33903): rank-2 participant `sdv` reports a CatBoost-family solution, recommends relative/ratio signals and whole-window behaviour, and says the F1 and AUC columns are independent heads. This is participant advice, not an organizer ruling. The rule ambiguity and a fail-closed dual-head provenance contract are recorded in `eda/dual_head_rule_audit_20260815.md`.
- [33902](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/33902): ensembling discussed by participants; no organizer ban. It does not resolve whether the binary head must threshold the same probability submitted for AUC, and no participant statement is an organizer waiver.
- [34402](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/34402): participant asked whether Test missingness statistics may drive training inputs; no answer was posted when checked.
- [34056](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/34056): calendar-month equivalence between Train and Test remains unconfirmed; the only reply is participant speculation.
- [34406](https://zindi.world/competitions/geoai-aquaculture-pond-identification-challenge/discussions/34406): private-selection UI save errors; reporter later said prior selections blocked new saves.

---

## Prior mistakes — closed, do not reopen

These already burned slots or are structurally refuted. They are **closed**, not a backlog.

| Closed item | Public evidence | Why it stays closed |
|---|---|---|
| Treating masked / local CV as a public-LB forecast | v1 `0.821360817`, v2 `0.878659389`, v3 `0.882569466`; later families with 0.97+ local composites then collapsed on the 333-row public slice | Source-side / masked CV does not contain the Test-period class-conditional shift. Local gates are rejection-only. |
| Public-feedback boundary edits (v4) | user-reported **0.916681323** from `scripts/agent_candidate_model_v4.py` reading `eda/lb_results.csv` and epsilon-editing the 0.5 boundary | Not a raw-data model; unsafe for code review; excluded from selection. |
| Changing the measured 571 `sub_308` decisions | `sub_385` kept the 571 labels and **AUC collapsed** to 0.921598 (public **0.906344057**); direct families that replaced decisions also lost F1 | Ranking experiments that keep F1 can still destroy AUC. Decision-changing families are closed without a certified public beat. |
| Reconstruction family | `sub_387` `FT4KqKiQ` **0.885879425** (AUC 0.927813317, F1 0.857923497) | Five-fold local composite 0.980 still failed publicly. Correlated `sub_386` withdrawn. |
| Compositional family | `sub_310` `rq1Ptrxj` **0.891056317** (AUC 0.934683047, F1 0.861971830) | Below incumbent by −0.0295. `sub_311` withdrawn. |
| Joint raw-physical family | `sub_381` **0.86142774**, `sub_384` **0.871477173**, `sub_385` **0.906344057** (range **0.861–0.906**) | All three scored uploads lost. Standalone and blended variants closed. |
| q15 / temporal month-shape family | `sub_527` `7r2M71g1` **0.886441675** (AUC 0.921198022, F1 0.863270777) | Live 2026-08-15 score. Withdraw `sub_528`. |
| Three-flip shared-unmixing correction | Offline only; no CSV and no upload | Independent falsification rejected all three rows. Two had robust negative-family counterevidence; no positive family passed the minimum-20-row, all-five-fold, zero-error source-analogue gate. |
| Minimax cross-root stack | Retrospective pooled composite gain **+0.014864**, but no Test vector | Every cached base-fold scheme was misaligned with the meta folds; all 1,821 rows were affected by same-meta-valid label contamination. Exact r20 training-index provenance was unavailable. The corrected report fails closed as non-prospective. |
| Pairwise CatBoost AUC complement | Initial subset-local report gains **+0.000313 to +0.000854 AUC**, but no CSV and no upload | A single deployable rank vector had negative folds; duplicate-group bootstrap q05 was negative; all five predeclared seed/pair-cap/objective refits failed. `FAIL_CLOSED_PAIRWISE_AUC_HEAD_NOT_ROBUST`. |
| Joint domain-calibrated state-space model | Offline only; no Test vector, CSV, or upload | Identity pooled delta **−0.001131**; S1-shift pooled **−0.001018**, worst-window **−0.009756**; phase pooled **−0.001001**. Four gates failed. `FAIL_CLOSED_NO_REFERENCE_NO_TEST_VECTOR`. |
| Predictive-subspace measurement restoration | Offline first-fold gate only; no later fold, Test vector, CSV, or upload | Identity changed **97.5%** of probabilities; raw-shift F1 **−0.003322**; covariance composite **−0.010030**. `FAIL_CLOSED_FIRST_PROSPECTIVE_FOLD`. |
| Standalone CatBoost-year | `sub_306` `ekcp7ybg` **0.891401570** (AUC 0.928503925, F1 0.866666666; ≈ TP 156 / FP 23 / FN 25 / TN 129) | Imputation helped source F1 and erased transferable ranking/recall. Family closed. |
| Graph smoothing, CORAL / quantile / rank-transform, self-training | prior offline + scored probes (alignment / self-train nulls; adversarial separability → 1.0 on mapping) | Closed in this campaign’s non-goals. Not reopened. |

Fuller lineage (filename errors, cache-as-provenance, float rounding, geometry-axis bugs) remains in `REVIEW_MATRIX.md`. This section is the **do-not-reopen** list required by the current goal.

---

## Designation (no upload)

Hidden labels make a 100% public beat of **0.920592385** impossible to certify. Therefore the minimally engineered, rules-correct solution for this run **is the already-scored incumbent**, not another speculative CSV.

The final offline candidates were deliberately killed before submission. The three-flip unmixing audit rejected every proposed correction. The minimax stack's apparent +0.014864 gain was invalidated by misaligned cached base folds. The pairwise AUC complement reproduced only under subset-local reranking; a deployable locked rank had negative folds, its grouped-bootstrap q05 was negative, and all five alternative refits failed. The subsequent domain-calibrated state-space model failed identity, S1, phase, and worst-window gates. Predictive-subspace restoration then failed its first prospective fold on identity, covariance, F1, and domain-separability controls. The controlling latest verdict is `FAIL_CLOSED_FIRST_PROSPECTIVE_FOLD` in `eda/predictive_subspace_restoration_fold0_20260815.json`; the earlier state-space and pairwise verdicts remain fail-closed.

| Field | Value |
|---|---|
| File | `submissions/sub_308_flagship_f1_transduction_rank.csv` |
| Zindi ID | `Q7xLfCHt` |
| Public score | **0.920592385** |
| AUC / F1 | 0.957218668 / 0.896174863 |
| SHA-256 | `39c05443ecb515b7bde5fca3131374cfcd6c2b7f3299be364976ae568fb660e8` |
| Positives @ 0.5 | 571 |
| Validator | `python3 src/validate_submission.py` (15 mechanical checks, including `TargetF1 == (TargetRAUC >= 0.5)`) |
| Upload this run | **none** (`competition_state.json` `uploads_enabled: false`) |

Conservative already-scored hedge (not uploaded, not selected here): `submissions/sub_307_flagship_f1_seedscale_rank.csv` (`T8rvcmL3`, 0.920185290), same 571 decisions.

Unscored rank-lock files (`sub_402` / `sub_403`) are **not** designated: `sub_385` already showed that a new ranking on locked labels can tank public AUC.
