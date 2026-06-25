"""
eval_metrics.py — evaluation utilities for TBM mortality prediction.

Provides:
  compute_metrics()   — AUROC, AUPRC, Brier score dict
  plot_roc_curve()    — overlaid ROC curves
  plot_pr_curve()     — overlaid Precision-Recall curves
  plot_calibration()  — calibration (reliability) plot
  metrics_table()     — tidy DataFrame from list of metric dicts
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    brier_score_loss, roc_curve, precision_recall_curve,
)
from sklearn.calibration import calibration_curve

FIG_DIR = Path(__file__).parents[2] / "results" / "figures"
TAB_DIR = Path(__file__).parents[2] / "results" / "tables"


def compute_metrics(y_true: np.ndarray, y_prob: np.ndarray, model_name: str = "Model") -> dict:
    """Return AUROC, AUPRC, Brier score for a binary classifier."""
    return {
        "model": model_name,
        "AUROC": round(roc_auc_score(y_true, y_prob), 4),
        "AUPRC": round(average_precision_score(y_true, y_prob), 4),
        "Brier": round(brier_score_loss(y_true, y_prob), 4),
    }


def plot_roc_curve(
    y_true: np.ndarray,
    y_prob_dict: dict,
    title: str = "ROC Curve",
    save_path=None,
) -> plt.Figure:
    """Overlay ROC curves. y_prob_dict = {model_name: y_prob_array}."""
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Random (AUC=0.50)")

    for name, y_prob in y_prob_dict.items():
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        auc = roc_auc_score(y_true, y_prob)
        ax.plot(fpr, tpr, lw=2, label=f"{name} (AUC={auc:.3f})")

    ax.set_xlabel("1 − Specificity (FPR)", fontsize=12)
    ax.set_ylabel("Sensitivity (TPR)", fontsize=12)
    ax.set_title(title, fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")
    return fig


def plot_pr_curve(
    y_true: np.ndarray,
    y_prob_dict: dict,
    title: str = "Precision-Recall Curve",
    save_path=None,
) -> plt.Figure:
    """Overlay Precision-Recall curves. y_prob_dict = {model_name: y_prob_array}."""
    prevalence = float(np.mean(y_true))
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.axhline(prevalence, color="k", ls="--", lw=1,
               label=f"No-skill baseline (prev={prevalence:.2f})")

    for name, y_prob in y_prob_dict.items():
        prec, rec, _ = precision_recall_curve(y_true, y_prob)
        auprc = average_precision_score(y_true, y_prob)
        ax.plot(rec, prec, lw=2, label=f"{name} (AUPRC={auprc:.3f})")

    ax.set_xlabel("Recall (Sensitivity)", fontsize=12)
    ax.set_ylabel("Precision (PPV)", fontsize=12)
    ax.set_title(title, fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")
    return fig


def plot_calibration(
    y_true: np.ndarray,
    y_prob_dict: dict,
    n_bins: int = 10,
    title: str = "Calibration Plot",
    save_path=None,
) -> plt.Figure:
    """Reliability diagram for multiple models."""
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Perfect calibration")

    for name, y_prob in y_prob_dict.items():
        frac_pos, mean_pred = calibration_curve(
            y_true, y_prob, n_bins=n_bins, strategy="uniform"
        )
        ax.plot(mean_pred, frac_pos, marker="o", lw=2, label=name)

    ax.set_xlabel("Mean predicted probability", fontsize=12)
    ax.set_ylabel("Fraction of positives", fontsize=12)
    ax.set_title(title, fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")
    return fig


def metrics_table(results: list) -> pd.DataFrame:
    """Convert list of compute_metrics() dicts into a tidy DataFrame."""
    return pd.DataFrame(results).set_index("model")
