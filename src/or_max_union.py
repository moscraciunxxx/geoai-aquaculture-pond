"""Add-only OR / max of two default-0.5 heads.

This is the complement of the refuted AND/min construction. ``max`` of two
raw probabilities keeps every positive of the first head and adds the
second head's extras. ``TargetF1`` is exactly ``(TargetRAUC >= 0.5)``.

Stratum gates are derived from Test sentinels (``-9999``), not from a
cached mask file.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

SENTINEL_THRESHOLD = -9990.0
S1_PREFIXES = ("VH_", "VV_")


def build_or_max(p_a: np.ndarray, p_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Union of two default-0.5 heads via elementwise max.

    Returns ``(target_f1, target_rauc)`` with ``target_f1 == (rauc >= 0.5)``.
    Every row where ``p_a >= 0.5`` stays positive.
    """
    a = np.asarray(p_a, dtype=np.float64)
    b = np.asarray(p_b, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(f"probability shapes differ: {a.shape} vs {b.shape}")
    rauc = np.maximum(a, b)
    f1 = (rauc >= 0.5).astype(int)
    return f1, rauc


def build_or_stratum(
    p_anchor: np.ndarray,
    p_other: np.ndarray,
    allow_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Add-only OR, but extras are allowed only where ``allow_mask`` is True.

    Complementary rows keep the anchor probability (and therefore its 0.5
    decision). Allowed rows use ``max(anchor, other)``.
    """
    a = np.asarray(p_anchor, dtype=np.float64)
    b = np.asarray(p_other, dtype=np.float64)
    allow = np.asarray(allow_mask, dtype=bool)
    if a.shape != b.shape or a.shape != allow.shape:
        raise ValueError(
            f"shape mismatch: anchor {a.shape} other {b.shape} allow {allow.shape}"
        )
    rauc = np.where(allow, np.maximum(a, b), a)
    f1 = (rauc >= 0.5).astype(int)
    return f1, rauc


def _month_columns(columns: Iterable[str]) -> dict[str, list[str]]:
    months: dict[str, list[str]] = {}
    for name in columns:
        if name == "ID" or "_" not in name:
            continue
        _band, month = name.rsplit("_", 1)
        months.setdefault(month, []).append(name)
    return dict(sorted(months.items()))


def _is_missing(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    return ~np.isfinite(arr) | (arr <= SENTINEL_THRESHOLD)


def observed_window_length(frame: pd.DataFrame) -> np.ndarray:
    """Count months with any non-sentinel band, per row."""
    months = _month_columns(frame.columns)
    n = len(frame)
    lengths = np.zeros(n, dtype=int)
    for cols in months.values():
        block = frame.loc[:, cols].to_numpy(dtype=np.float64)
        present = ~_is_missing(block).all(axis=1)
        lengths += present.astype(int)
    return lengths


def s1_only_row_mask(frame: pd.DataFrame) -> np.ndarray:
    """True if any observed month has SAR present and every optical band missing."""
    months = _month_columns(frame.columns)
    n = len(frame)
    out = np.zeros(n, dtype=bool)
    for cols in months.values():
        s1 = [c for c in cols if c.startswith(S1_PREFIXES)]
        s2 = [c for c in cols if not c.startswith(S1_PREFIXES)]
        if not s1 or not s2:
            continue
        s1_present = ~_is_missing(frame.loc[:, s1].to_numpy(dtype=np.float64)).all(axis=1)
        s2_missing = _is_missing(frame.loc[:, s2].to_numpy(dtype=np.float64)).all(axis=1)
        out |= s1_present & s2_missing
    return out


def restore_anchor_on_agreements(
    p_anchor: np.ndarray,
    p_other: np.ndarray,
    extra_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Keep add-only extras but restore the anchor score everywhere else.

    ``extra_mask`` rows must be anchor-negatives with ``p_other >= 0.5``.
    Complementary rows use ``p_anchor`` unchanged, so a measured ranking is
    not replaced by ``max()``.
    """
    a = np.asarray(p_anchor, dtype=np.float64)
    b = np.asarray(p_other, dtype=np.float64)
    extra = np.asarray(extra_mask, dtype=bool)
    if a.shape != b.shape or a.shape != extra.shape:
        raise ValueError(
            f"shape mismatch: anchor {a.shape} other {b.shape} extra {extra.shape}"
        )
    if extra.any() and np.any(b[extra] < 0.5):
        raise ValueError("extra rows must have other >= 0.5")
    if extra.any() and np.any(a[extra] >= 0.5):
        raise ValueError("extras must be anchor-negatives")
    rauc = np.where(extra, b, a)
    f1 = (rauc >= 0.5).astype(int)
    return f1, rauc


def rank_lock_within_side(decisions: np.ndarray, ranking: np.ndarray) -> np.ndarray:
    """Preserve every 0.5 decision; replace order only inside each side."""
    labels = np.asarray(decisions)
    scores = np.asarray(ranking, dtype=np.float64)
    if labels.shape != scores.shape:
        raise ValueError(f"shape mismatch: {labels.shape} vs {scores.shape}")
    out = np.empty_like(scores)
    for label, lo, hi in ((0, 1e-6, 0.5 - 1e-9), (1, 0.5, 1.0 - 1e-6)):
        idx = np.flatnonzero(labels == label)
        if idx.size == 0:
            continue
        order = np.argsort(np.argsort(scores[idx], kind="mergesort"))
        out[idx] = lo + (hi - lo) * ((order + 0.5) / idx.size)
    return out


def stratum_masks_from_test(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    """Boolean row masks derived only from Test sentinels."""
    length = observed_window_length(frame)
    s1_only = s1_only_row_mask(frame)
    four_month = length == 4
    return {
        "s1_only": s1_only,
        "four_month": four_month,
        "s1_or_four": s1_only | four_month,
        "window_length": length,
    }
