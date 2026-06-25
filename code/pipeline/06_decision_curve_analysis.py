# %% [markdown]
# # Notebook 06 — Decision Curve Analysis (DCA)
#
# **Goal:** Net Benefit curves for XGBoost + Nomogram LR
# vs treat-all and treat-none across probability thresholds.
#
# **Why DCA?** AUROC = discrimination; DCA = *clinical utility* —
# whether using the model improves patient outcomes at a given threshold
# compared to treating everyone or no one.
#
# NB(pt) = TP/n - FP/n × pt/(1-pt)   where pt = threshold, n = sample size

# %%
import sys
import pickle
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path("../src").resolve()))
from data_loader import PROCESSED_DIR

MODELS_DIR = Path("../../models")
FIG_DIR    = Path("../../results/figures")
TAB_DIR    = Path("../../results/tables")
FIG_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "evdeath_3M"

# %% [markdown]
# ## 1. Load models and test data

# %%
test_df = pd.read_csv(PROCESSED_DIR / "test.csv")
y_test  = test_df[TARGET].astype(int).values
n = len(y_test)
print(f"Test n={n}  deaths={y_test.sum()}  mortality={y_test.mean():.1%}")

with open(MODELS_DIR / "xgb_model.pkl", "rb") as f:
    xgb_model = pickle.load(f)

with open(MODELS_DIR / "lr_surrogate.pkl", "rb") as f:
    surrogate = pickle.load(f)

lr_model     = surrogate["lr_model"]
imputer      = surrogate["imputer"]
top_features = surrogate["top_features"]

y_prob_xgb = xgb_model.predict_proba(test_df.drop(columns=[TARGET]))[:, 1]

X_test_lr = pd.DataFrame(
    imputer.transform(test_df[top_features]),
    columns=top_features,
)
y_prob_lr = lr_model.predict_proba(X_test_lr)[:, 1]

print(f"XGBoost prob range: [{y_prob_xgb.min():.3f}, {y_prob_xgb.max():.3f}]")
print(f"LR prob range:      [{y_prob_lr.min():.3f},  {y_prob_lr.max():.3f}]")

# %% [markdown]
# ## 2. Net Benefit calculation

# %%
def net_benefit(y_true: np.ndarray, y_prob: np.ndarray, pt: float) -> float:
    """Net Benefit at probability threshold pt."""
    if pt <= 0 or pt >= 1:
        return np.nan
    pred_pos = (y_prob >= pt)
    tp = np.sum(pred_pos & (y_true == 1))
    fp = np.sum(pred_pos & (y_true == 0))
    return tp / len(y_true) - fp / len(y_true) * (pt / (1 - pt))


def treat_all_nb(y_true: np.ndarray, pt: float) -> float:
    """Net benefit of treating all patients."""
    prev = y_true.mean()
    return prev - (1 - prev) * pt / (1 - pt)


thresholds     = np.linspace(0.01, 0.99, 300)
nb_xgb         = np.array([net_benefit(y_test, y_prob_xgb, t) for t in thresholds])
nb_lr          = np.array([net_benefit(y_test, y_prob_lr,  t) for t in thresholds])
nb_treat_all   = np.array([treat_all_nb(y_test, t)            for t in thresholds])
nb_treat_none  = np.zeros_like(thresholds)

print("Net benefit computed for all thresholds.")

# %% [markdown]
# ## 3. Full DCA plot

# %%
fig, ax = plt.subplots(figsize=(10, 7))

ax.plot(thresholds, nb_xgb,       lw=2.5, color="steelblue",  label="XGBoost")
ax.plot(thresholds, nb_lr,        lw=2.5, color="darkorange", label="Nomogram LR (surrogate)")
ax.plot(thresholds, nb_treat_all, lw=1.5, color="darkgreen",  ls="--", label="Treat all")
ax.plot(thresholds, nb_treat_none, lw=1.5, color="black",     ls=":",  label="Treat none")

# Shade XGBoost net gain over treat-all
net_gain = (nb_xgb > nb_treat_all) & (nb_xgb > 0)
if net_gain.any():
    ax.fill_between(thresholds, nb_xgb, nb_treat_all,
                    where=net_gain, alpha=0.12, color="steelblue",
                    label="XGBoost net gain vs treat-all")

ax.set_xlim(0, 1)
ymin = min(-0.05, np.nanmin(nb_xgb) - 0.02, np.nanmin(nb_lr) - 0.02)
ymax = max(0.35,  np.nanmax(nb_xgb) + 0.02, np.nanmax(nb_treat_all) + 0.02)
ax.set_ylim(ymin, ymax)
ax.axhline(0, color="gray", lw=0.8)
ax.set_xlabel("Probability threshold (pt)", fontsize=12)
ax.set_ylabel("Net Benefit", fontsize=12)
ax.set_title("Decision Curve Analysis\nTBM 3-Month Mortality", fontsize=13)
ax.legend(fontsize=10)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_DIR / "06_dca.png", dpi=150)
plt.show()
print("Saved: 06_dca.png")

# %% [markdown]
# ## 4. Clinically relevant range (10–50%)

# %%
cr = (thresholds >= 0.10) & (thresholds <= 0.50)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(thresholds[cr], nb_xgb[cr],       lw=2.5, color="steelblue",  label="XGBoost")
ax.plot(thresholds[cr], nb_lr[cr],        lw=2.5, color="darkorange", label="Nomogram LR")
ax.plot(thresholds[cr], nb_treat_all[cr], lw=1.5, color="darkgreen",  ls="--", label="Treat all")
ax.axhline(0, color="black", lw=1, ls=":", label="Treat none")
ax.set_xlim(0.10, 0.50)
ax.set_xlabel("Probability threshold (pt)", fontsize=11)
ax.set_ylabel("Net Benefit", fontsize=11)
ax.set_title("DCA — Clinically relevant range (10–50%)", fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_DIR / "06_dca_clinical_range.png", dpi=150)
plt.show()
print("Saved: 06_dca_clinical_range.png")

# %% [markdown]
# ## 5. Save net benefit table

# %%
nb_df = pd.DataFrame({
    "threshold":    thresholds,
    "XGBoost":      nb_xgb,
    "LR_Surrogate": nb_lr,
    "Treat_All":    nb_treat_all,
    "Treat_None":   nb_treat_none,
})
nb_df.to_csv(TAB_DIR / "06_net_benefit.csv", index=False)
print("Saved: results/tables/06_net_benefit.csv")
print(nb_df[cr].describe().to_string())

# %% [markdown]
# ## 6. Interpretation summary

# %%
xgb_beats_all = np.sum((nb_xgb > nb_treat_all) & cr)
lr_beats_all  = np.sum((nb_lr  > nb_treat_all) & cr)
print("\n" + "=" * 60)
print("DCA Interpretation:")
print("=" * 60)
print(f"In clinical range [10%–50% threshold]  ({cr.sum()} steps):")
print(f"  XGBoost > Treat-All in {xgb_beats_all}/{cr.sum()} steps")
print(f"  LR Surrogate > Treat-All in {lr_beats_all}/{cr.sum()} steps")
print()
print("If models > Treat-All AND > Treat-None:")
print("  → Using model improves clinical decisions at that threshold.")
print("If LR ≈ XGBoost in net benefit:")
print("  → Nomogram achieves comparable utility with simpler calculation.")
print("=" * 60)
