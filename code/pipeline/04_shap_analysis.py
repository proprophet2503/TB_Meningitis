# %% [markdown]
# # Notebook 04 — SHAP Analysis
#
# **Goal:** Explain the XGBoost model with SHAP:
# 1. Global feature ranking by mean |SHAP| → select top 5–8 features
# 2. Beeswarm summary plot
# 3. Waterfall plots for 3 representative patients
#
# Outputs: SHAP plots → results/figures/,  top features → results/tables/

# %%
import sys
import pickle
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap

sys.path.insert(0, str(Path("../src").resolve()))
from data_loader import PROCESSED_DIR

MODELS_DIR = Path("../../models")
FIG_DIR    = Path("../../results/figures")
TAB_DIR    = Path("../../results/tables")
FIG_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "evdeath_3M"

# %% [markdown]
# ## 1. Load model and data

# %%
with open(MODELS_DIR / "xgb_model.pkl", "rb") as f:
    model = pickle.load(f)

train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
test_df  = pd.read_csv(PROCESSED_DIR / "test.csv")

X_train = train_df.drop(columns=[TARGET])
X_test  = test_df.drop(columns=[TARGET])
y_test  = test_df[TARGET].astype(int)

print(f"Model: {type(model).__name__}")
print(f"Train: {X_train.shape}  Test: {X_test.shape}")

# %% [markdown]
# ## 2. Compute SHAP values (TreeExplainer)

# %%
print("Computing SHAP values...")
explainer = shap.TreeExplainer(model)
shap_train = explainer.shap_values(X_train)
shap_test  = explainer.shap_values(X_test)

print(f"SHAP train shape: {shap_train.shape}")
print(f"Base value (expected log-odds): {explainer.expected_value:.4f}")

np.save(FIG_DIR / "shap_values_train.npy", shap_train)
np.save(FIG_DIR / "shap_values_test.npy",  shap_test)

# %% [markdown]
# ## 3. Feature ranking by mean |SHAP|

# %%
mean_abs_shap = pd.Series(
    np.abs(shap_train).mean(axis=0),
    index=X_train.columns,
).sort_values(ascending=False)

print("Feature ranking (mean |SHAP|):")
print(mean_abs_shap.to_string())

fig, ax = plt.subplots(figsize=(9, max(4, len(mean_abs_shap) * 0.42)))
mean_abs_shap.plot(kind="barh", ax=ax, color="steelblue", edgecolor="k")
ax.set_xlabel("Mean |SHAP value|", fontsize=11)
ax.set_title("Global SHAP Feature Importance", fontsize=12)
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(FIG_DIR / "04_shap_global_bar.png", dpi=150)
plt.show()
print("Saved: 04_shap_global_bar.png")

# %% [markdown]
# ## 4. Beeswarm summary plot

# %%
shap.summary_plot(shap_train, X_train, plot_type="dot", max_display=20, show=False)
fig = plt.gcf()
fig.set_size_inches(10, max(5, len(X_train.columns) * 0.5))
plt.title("SHAP Summary — Training Set", fontsize=12, pad=10)
plt.tight_layout()
plt.savefig(FIG_DIR / "04_shap_beeswarm.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: 04_shap_beeswarm.png")

# %% [markdown]
# ## 5. Select top features for nomogram

# %%
TOP_N = min(8, max(5, len(mean_abs_shap)))
top_features = mean_abs_shap.head(TOP_N).index.tolist()

print(f"\nTop {TOP_N} features for nomogram:")
for i, feat in enumerate(top_features, 1):
    print(f"  {i:2d}. {feat:<28s} mean|SHAP|={mean_abs_shap[feat]:.4f}")

top_df = mean_abs_shap.head(TOP_N).reset_index()
top_df.columns = ["feature", "mean_abs_shap"]
top_df.to_csv(TAB_DIR / "04_shap_top_features.csv", index=False)
print(f"\nSaved: results/tables/04_shap_top_features.csv")

# %% [markdown]
# ## 6. Waterfall plots — 3 representative patients

# %%
y_prob_test = model.predict_proba(X_test)[:, 1]
idx_low    = int(np.argmin(y_prob_test))
idx_high   = int(np.argmax(y_prob_test))
idx_med    = int(np.argmin(np.abs(y_prob_test - np.median(y_prob_test))))

cases = [
    ("lowest_risk",  idx_low,  y_prob_test[idx_low]),
    ("highest_risk", idx_high, y_prob_test[idx_high]),
    ("median_risk",  idx_med,  y_prob_test[idx_med]),
]

for case_name, idx, prob in cases:
    sv = shap.Explanation(
        values=shap_test[idx],
        base_values=float(explainer.expected_value),
        data=X_test.iloc[idx].values,
        feature_names=X_test.columns.tolist(),
    )
    plt.figure(figsize=(10, 5))
    shap.waterfall_plot(sv, max_display=12, show=False)
    died_label = int(y_test.iloc[idx])
    plt.title(f"SHAP Waterfall — {case_name.replace('_', ' ')} "
              f"(prob={prob:.2f}, actual={'Died' if died_label else 'Survived'})",
              fontsize=10, pad=5)
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"04_shap_waterfall_{case_name}.png", dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Saved: 04_shap_waterfall_{case_name}.png")

# %% [markdown]
# ## 7. Summary

# %%
print("=" * 55)
print(f"Selected top {TOP_N} features for notebook 05:")
for i, f in enumerate(top_features, 1):
    print(f"  {i}. {f}")
print("=" * 55)
print("\nNext: 05_nomogram_construction.py")
