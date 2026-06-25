"""
nomogram.py — manual matplotlib nomogram for TBM 3-month mortality.

No third-party library (pynomo is unmaintained).
Implements linear point-scale conversion from doc(2):
  - Feature with largest |coeff * range| gets max_scale pts (default 100)
  - Others scaled proportionally
  - Total points axis + probability axis derived from LR equation

Public API
----------
build_nomogram_points(coefs, feature_ranges, feature_names, intercept)
    -> (point_scales dict, total_to_prob callable)
plot_nomogram(point_scales, total_to_prob, ...)
    -> matplotlib Figure
"""

from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = Path(__file__).parents[2] / "results" / "figures"


def build_nomogram_points(
    coefs: np.ndarray,
    feature_ranges: dict,
    feature_names: list,
    intercept: float,
    n_ticks: int = 10,
    max_scale: int = 100,
) -> tuple:
    """
    Build linear point scales for each feature.

    Parameters
    ----------
    coefs          : 1-D array of LR coefficients
    feature_ranges : {name: (min, max)} from training data
    feature_names  : list of feature names (same order as coefs)
    intercept      : LR intercept
    n_ticks        : tick marks per feature scale
    max_scale      : point value assigned to anchor (highest-contributing) feature

    Returns
    -------
    point_scales : {name: {"values": ndarray, "points": ndarray, "coef": float, "range": tuple}}
    total_to_prob: callable(total_points: float) -> predicted probability (float)
    """
    contributions = {}
    for name, coef in zip(feature_names, coefs):
        lo, hi = feature_ranges.get(name, (0, 1))
        contributions[name] = abs(coef * (hi - lo))

    max_contrib = max(contributions.values()) if contributions else 1.0

    point_scales: dict = {}
    for name, coef in zip(feature_names, coefs):
        lo, hi = feature_ranges.get(name, (0, 1))
        values = np.linspace(lo, hi, n_ticks)
        scale_factor = contributions[name] / (max_contrib + 1e-9) * max_scale
        if hi > lo:
            pts = (values - lo) / (hi - lo) * scale_factor * np.sign(coef)
        else:
            pts = np.zeros_like(values)
        pts = pts - pts.min()  # floor at 0
        point_scales[name] = {
            "values": values,
            "points": pts,
            "coef": float(coef),
            "range": (float(lo), float(hi)),
        }

    # Build inverse mapping: total_points -> probability
    pt_min = sum(s["points"].min() for s in point_scales.values())
    pt_max_total = sum(s["points"].max() for s in point_scales.values())
    lo_vals = [point_scales[n]["range"][0] for n in feature_names]
    hi_vals = [point_scales[n]["range"][1] for n in feature_names]
    logit_at_min = intercept + float(np.dot(coefs, lo_vals))
    logit_at_max = intercept + float(np.dot(coefs, hi_vals))

    def total_to_prob(total_pts: float) -> float:
        pt_range = pt_max_total - pt_min + 1e-9
        logit = logit_at_min + (total_pts - pt_min) / pt_range * (logit_at_max - logit_at_min)
        return float(1.0 / (1.0 + np.exp(-logit)))

    return point_scales, total_to_prob


def plot_nomogram(
    point_scales: dict,
    total_to_prob: callable,
    feature_labels: dict | None = None,
    title: str = "TBM 3-Month Mortality Nomogram",
    save_path=None,
) -> plt.Figure:
    """
    Draw a horizontal nomogram.

    Rows (top to bottom):
      one row per feature → value axis with point tick labels
      total points axis
      predicted probability axis
    """
    features = list(point_scales.keys())
    n_feat = len(features)
    labels = feature_labels or {}

    pt_min = sum(s["points"].min() for s in point_scales.values())
    pt_max = sum(s["points"].max() for s in point_scales.values())

    n_rows = n_feat + 2
    fig_height = max(7, n_rows * 0.95)
    fig, axes = plt.subplots(n_rows, 1, figsize=(13, fig_height),
                              gridspec_kw={"hspace": 0.05})

    def _to_display(raw_pts: np.ndarray) -> np.ndarray:
        """Map raw cumulative points to 0-100 display scale."""
        r = pt_max - pt_min + 1e-9
        return (raw_pts - pt_min) / r * 100.0

    # Running baseline: sum of minimums of all other features
    running_mins = {
        n: sum(point_scales[f]["points"].min() for f in features if f != n)
        for n in features
    }

    for i, feat in enumerate(features):
        ax = axes[i]
        sc = point_scales[feat]
        vals = sc["values"]
        # Display positions: pts for THIS feature + minimums of all others
        disp = _to_display(sc["points"] + running_mins[feat])

        ax.axhline(0, color="k", lw=0.8)
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.5, 0.5)

        for v, dp in zip(vals, disp):
            ax.axvline(dp, ymin=0.3, ymax=0.7, color="k", lw=0.8)
            lbl = f"{v:.0f}" if abs(v) >= 1 or v == 0 else f"{v:.2f}"
            ax.text(dp, -0.35, lbl, ha="center", va="top", fontsize=7)

        display_label = labels.get(feat, feat.replace("_", " "))
        ax.set_ylabel(display_label, rotation=0, labelpad=90,
                      ha="right", va="center", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

    # ── total points axis ──
    ax_tp = axes[n_feat]
    ax_tp.axhline(0, color="k", lw=1.2)
    ax_tp.set_xlim(0, 100)
    ax_tp.set_ylim(-0.5, 0.5)
    for p in np.linspace(0, 100, 11):
        ax_tp.axvline(p, ymin=0.3, ymax=0.7, color="k", lw=0.8)
        ax_tp.text(p, -0.38, f"{p:.0f}", ha="center", va="top", fontsize=8)
    ax_tp.set_ylabel("Total Points", rotation=0, labelpad=90,
                      ha="right", va="center", fontsize=10, fontweight="bold")
    ax_tp.set_xticks([])
    ax_tp.set_yticks([])
    for sp in ax_tp.spines.values():
        sp.set_visible(False)

    # ── predicted probability axis ──
    ax_pr = axes[n_feat + 1]
    ax_pr.axhline(0, color="k", lw=1.2)
    ax_pr.set_xlim(0, 100)
    ax_pr.set_ylim(-0.5, 0.5)

    tp_dense = np.linspace(pt_min, pt_max, 2000)
    prob_dense = np.array([total_to_prob(tp) for tp in tp_dense])
    disp_dense = _to_display(tp_dense)

    for prob_target in [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95]:
        idx = np.argmin(np.abs(prob_dense - prob_target))
        xp = float(disp_dense[idx])
        if 2 <= xp <= 98:
            ax_pr.axvline(xp, ymin=0.3, ymax=0.7, color="darkred", lw=0.8)
            ax_pr.text(xp, -0.38, f"{prob_target:.2f}", ha="center", va="top",
                       fontsize=7, color="darkred")

    ax_pr.set_ylabel("3-mo Mortality\nProbability", rotation=0, labelpad=90,
                      ha="right", va="center", fontsize=10, fontweight="bold",
                      color="darkred")
    ax_pr.set_xticks([])
    ax_pr.set_yticks([])
    for sp in ax_pr.spines.values():
        sp.set_visible(False)

    fig.suptitle(title, fontsize=13, fontweight="bold", y=1.005)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")
    return fig
