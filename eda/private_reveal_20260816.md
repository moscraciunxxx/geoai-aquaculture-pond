# Private reveal — 2026-08-16

Uploads are closed. User-reported authenticated Zindi rows after reveal.

## Selected pair (what was judged)

You selected `bNsDafsS` + `2F9tRW8b` (`sub_542` + `sub_537`). Both share
the same 16 add-only extras, so they share the same F1 on **both** boards.

| file | ID | public blend | private blend | public AUC / F1 | private AUC / F1 |
|---|---|---:|---:|---|---|
| `sub_542` | `bNsDafsS` | 0.925724375 | 0.924647353 | 0.959472 / 0.903226 | 0.956780 / **0.903226** |
| `sub_537` | `2F9tRW8b` | 0.923267266 | **0.924790066** | 0.953329 / 0.903226 | 0.957136 / **0.903226** |

Zindi takes the better of the two selected files. That is **`537` at
0.924790066**, not `542`. `542` won public and lost the selected-pair
private comparison by 0.000143.

F1 is the same rational `0.903225806` on public and private. The 16 extras
did not improve private F1 beyond that cut. `542`’s restored `308` ranking
was slightly public-lucky (AUC 0.95947 → 0.95678). `537`’s `max()` ranking
recovered on private (0.95333 → 0.95714).

## Older files that beat the selected pair on private

| file | ID | public blend | **private blend** | private AUC / F1 |
|---|---|---:|---:|---|
| `sub_079b_feats_freelabels` | `MByz3fSc` | 0.91473656 | **0.930370162** | 0.962289 / 0.909091 |
| `sub_102b_integrated_076labels` | `WmJa7J1o` | 0.914780055 | **0.928342371** | (AUC/F1 not pasted for this row) |

`MByz3fSc` is +0.00558 private vs the selected `537`. Public said this
physics-feature file was a net loss versus `sub_076` (+2 TP / +3 FP).
Private F1 0.909 and AUC 0.962 are the account’s revealed private records
among the pasted rows.

`WmJa7J1o` locked `sub_076` labels and used a window-expert ranking that
*lost* public AUC. That ranking transferred.

## What this means

The close-day climb optimized the 333-row public slice: 16 extras that were
4 TP + 2 FP there, then a ranking restore that added 62 public AUC pairs.
Those edits did not find the private ponds that `079b` found.

`308` / `307` private scores were not pasted. They were the recommended
hedge (`542` + `308`) and were not the selected pair.

## Why (the actual mechanism)

1. **The last two days solved the public invert, not the shift.**
   `537` added 16 `533` extras on S1-only/4-month rows because 6 of them
   landed on the 333-row public slice as 4 TP + 2 FP. That is a 6-row
   sample. The other 10 extras were always private. We never had a
   reason to believe they were ponds.

2. **Identical F1 0.903225806 on both boards is the tell.**
   Public and private are different label sets. The same 9-decimal F1
   means we locked an operating point (571 `308` positives + those 16
   extras), not that we found a more transferable classifier. `079b`
   reached private F1 **0.909** with a *different* label set.

3. **`542` beating `308` on public AUC was also public-conditioned.**
   Promoting those 4 public FNs onto `308`’s ranking added 62 public
   pairs. On private, `542` AUC fell 0.95947 → 0.95678, and `537`’s
   “worse” `max()` ranking *won* private AUC (0.95714). Ranking restore
   was not a free lunch.

4. **Selecting `542`+`537` doubled the same error.**
   Both files share the extras. The pair cannot cancel a bad extra.
   `079b` and `102b` disagree with that cut; that disagreement is why
   they could win private.

5. **Public was already used as a teacher.**
   `308`/`202`/`076` operating points were public-informed. Climbing
   them with more public-slice arithmetic (`535` AND, `537` extras,
   `542` pair recovery) is the same feedback loop. `079b` used its own
   physics labels and looked *worse* on that teacher. The ledger
   retired it for that. Reveal reversed the verdict.

6. **`102b` is the ranking version of the same lesson.**
   Expert ranking lost public AUC vs `076` (−0.0032) and was closed.
   Private 0.92834. A ranking that is worse on the 333 can be better
   on the 697.

## What to do next time

- The two private selections must have **different F1 decisions** if
  those decisions were public-informed. Same extras is not a hedge.
- Do not kill a file for losing public by ~0.001 when its features or
  labels are not the public-tuned family (`079b`, `102b`).
- Public invert is for *diagnosis* (AND killed TPs; extras need >45%
  precision). It is not a construction kit for the hidden 70%.
- Prefer a representation that can be wrong on public for physical
  reasons (SAR drain, wind-roughness, window experts) over another
  edit of the public-best 571-row cut.

No further upload is possible. This note does not change private
checkboxes (close already happened).
