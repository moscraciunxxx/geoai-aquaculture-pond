#!/usr/bin/env python3
"""Public-slice F1 / blended-score arithmetic for the official 333-row set.

Public partition (inverted from reported AUCs): 181 positive, 152 negative.
F1 = 2 * TP / (P + 181) with P = TP + FP and FN = 181 - TP.
AUC for continuous scores is C / (181 * 152).

This module is the fail-closed calculator for claims such as F1 > 0.983.
It does not train models and does not upload.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

N_POS = 181
N_NEG = 152
N_PUBLIC = N_POS + N_NEG
AUC_DENOM = N_POS * N_NEG  # 27512
F1_TARGET = 0.983
INCUMBENT_F1 = 0.896174863
INCUMBENT_AUC = 0.957218668
INCUMBENT_BLEND = 0.920592385


def f1_from_counts(tp: int, fp: int, n_pos: int = N_POS) -> float:
    den = tp + fp + n_pos
    if den <= 0:
        return 0.0
    return 2.0 * tp / den


def invert_f1(f1: float, n_pos: int = N_POS, n_neg: int = N_NEG, atol: float = 1e-9):
    """Return the unique (tp, fp, fn, tn) matching F1, or raise if not unique."""
    hits = []
    for tp in range(0, n_pos + 1):
        for fp in range(0, n_neg + 1):
            if abs(f1_from_counts(tp, fp, n_pos) - f1) <= atol:
                hits.append((tp, fp, n_pos - tp, n_neg - fp))
    if len(hits) != 1:
        raise ValueError(f"F1={f1!r} is not a unique public-slice confusion ({len(hits)} hits)")
    return hits[0]


def invert_f1_and_public_p(f1: float, public_p: int, n_pos: int = N_POS):
    tp = f1 * (public_p + n_pos) / 2.0
    if abs(tp - round(tp)) > 1e-4:
        raise ValueError(f"F1={f1} and P={public_p} do not yield integer TP")
    tp_i = int(round(tp))
    fp = int(public_p - tp_i)
    return tp_i, fp, n_pos - tp_i


def configs_above_f1(threshold: float = F1_TARGET, n_pos: int = N_POS, n_neg: int = N_NEG):
    out = []
    for tp in range(0, n_pos + 1):
        for fp in range(0, n_neg + 1):
            f1 = f1_from_counts(tp, fp, n_pos)
            if f1 > threshold:
                out.append(
                    {
                        "tp": tp,
                        "fp": fp,
                        "fn": n_pos - tp,
                        "tn": n_neg - fp,
                        "public_p": tp + fp,
                        "f1": f1,
                        "errors": fp + (n_pos - tp),
                    }
                )
    return out


def blended_score(f1: float, auc: float) -> float:
    return 0.60 * f1 + 0.40 * auc


def incumbent_confusion():
    tp, fp, fn, tn = invert_f1(INCUMBENT_F1)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "f1": f1_from_counts(tp, fp),
        "auc": INCUMBENT_AUC,
        "blended": blended_score(INCUMBENT_F1, INCUMBENT_AUC),
        "errors": fp + fn,
    }


def f1_ceiling_if_max_tp(max_tp: int, n_pos: int = N_POS) -> float:
    """Best F1 if no model can find more than max_tp public positives (FP=0)."""
    return f1_from_counts(max_tp, 0, n_pos)


def target_is_beyond_incumbent_and_field(threshold: float = F1_TARGET) -> dict:
    cfgs = configs_above_f1(threshold)
    inc = incumbent_confusion()
    return {
        "threshold": threshold,
        "n_legal_confusion_matrices": len(cfgs),
        "min_tp": min(c["tp"] for c in cfgs) if cfgs else None,
        "max_fn": max(c["fn"] for c in cfgs) if cfgs else None,
        "max_fp": max(c["fp"] for c in cfgs) if cfgs else None,
        "max_errors": max(c["errors"] for c in cfgs) if cfgs else None,
        "incumbent_errors": inc["errors"],
        "incumbent_tp": inc["tp"],
        "incumbent_fp": inc["fp"],
        "incumbent_fn": inc["fn"],
        "error_reduction_needed": inc["errors"] - (max(c["errors"] for c in cfgs) if cfgs else inc["errors"]),
        "f1_if_max_tp_173_fp_0": f1_ceiling_if_max_tp(173),
        "perfect_f1_with_incumbent_auc_blended": blended_score(1.0, INCUMBENT_AUC),
        "can_certify_offline": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = {
        "incumbent": incumbent_confusion(),
        "f1_gt_0983": target_is_beyond_incumbent_and_field(0.983),
    }
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0
    inc = payload["incumbent"]
    tgt = payload["f1_gt_0983"]
    print(f"incumbent confusion TP={inc['tp']} FP={inc['fp']} FN={inc['fn']} TN={inc['tn']}")
    print(f"F1>0.983 configs={tgt['n_legal_confusion_matrices']} min_tp={tgt['min_tp']} max_fp={tgt['max_fp']} max_errors={tgt['max_errors']}")
    print(f"incumbent errors={tgt['incumbent_errors']} reduction_needed={tgt['error_reduction_needed']}")
    print(f"ledger_max_tp_173 ceiling={tgt['f1_if_max_tp_173_fp_0']:.6f}")
    print("can_certify_offline", tgt["can_certify_offline"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
