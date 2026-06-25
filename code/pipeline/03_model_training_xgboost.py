# %% [markdown]
# # Notebook 03 — XGBoost Model Training & Evaluation
#
# **Goal:** Hyperparameter search → fit XGBoost → evaluate on test set:
# AUROC, AUPRC, Brier score, ROC/PR curves, calibration plot.
#
# **Protocol notes:**
# - `scale_pos_weight` (n_neg/n_pos) for class imbalance — no synthetic data
# - RandomizedSearchCV with 5-fold stratified CV (scoring: AUROC)
# - Model saved to `models/xgb_model.pkl` for SHAP in notebook 04

# %%
import sys
import pickle
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
import xgboost as xgb

sys.path.insert(0, str(Path("../src").resolve()))
from data_loader import PROCESSED_DIR
from eval_metrics import compute_metrics, plot_roc_curve, plot_pr_curve, plot_calibration, metrics_table

MODELS_DIR = Path("../../models")
FIG_DIR    = Path("../../results/figures")
TAB_DIR    = Path("../../results/tables")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "evdeath_3M"
RANDOM_STATE = 42

# %% [markdown]
# ## 1. Load splits

# %%
train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
test_df  = pd.read_csv(PROCESSED_DIR / "test.csv")

X_train = train_df.drop(columns=[TARGET])
y_train = train_df[TARGET].astype(int)
X_test  = test_df.drop(columns=[TARGET])
y_test  = test_df[TARGET].astype(int)

n_neg = (y_train == 0).sum()
n_pos = (y_train == 1).sum()
SCALE_POS_WEIGHT = float(n_neg / n_pos)

print(f"Train: {X_train.shape}  |  Deaths: {y_train.sum()} ({y_train.mean():.1%})")
print(f"Test:  {X_test.shape}   |  Deaths: {y_test.sum()} ({y_test.mean():.1%})")
print(f"scale_pos_weight: {SCALE_POS_WEIGHT:.4f}")
print(f"\nFeatures: {X_train.columns.tolist()}")

# %% [markdown]
# ## 2. Hyperparameter search

# %%
param_dist = {
    "n_estimators":     [100, 200, 300, 400, 500],
    "max_depth":        [3, 4, 5, 6],
    "learning_rate":    [0.01, 0.05, 0.1, 0.15, 0.2],
    "subsample":        [0.6, 0.7, 0.8, 0.9, 1.0],
    "colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],
    "reg_alpha":        [0, 0.01, 0.1, 0.5, 1.0],
    "reg_lambda":       [0.5, 1.0, 1.5, 2.0],
    "min_child_weight": [1, 3, 5, 7],
    "gamma":            [0, 0.1, 0.3, 0.5],
}

base_xgb = xgb.XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss",
    scale_pos_weight=SCALE_POS_WEIGHT,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    verbosity=0,
)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

search = RandomizedSearchCV(
    base_xgb,
    param_distributions=param_dist,
    n_iter=50,
    scoring="roc_auc",
    cv=cv,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    verbose=1,
    refit=True,
)

print("Running RandomizedSearchCV (50 iterations, 5-fold CV)...")
search.fit(X_train, y_train)

print(f"\nBest CV AUROC: {search.best_score_:.4f}")
print(f"Best params:")
for k, v in search.best_params_.items():
    print(f"  {k}: {v}")

# %% [markdown]
# ## 3. Test set evaluation

# %%
best_model = search.best_estimator_
y_prob = best_model.predict_proba(X_test)[:, 1]

metrics = compute_metrics(y_test.values, y_prob, model_name="XGBoost")
print("\nTest set performance:")
for k, v in metrics.items():
    print(f"  {k}: {v}")

# %% [markdown]
# ## 4. ROC curve

# %%
plot_roc_curve(
    y_test.values, {"XGBoost": y_prob},
    title="XGBoost ROC Curve (Test Set)",
    save_path=FIG_DIR / "03_roc_curve.png",
)
plt.show()

# %% [markdown]
# ## 5. Precision-Recall curve

# %%
plot_pr_curve(
    y_test.values, {"XGBoost": y_prob},
    title="XGBoost Precision-Recall Curve (Test Set)",
    save_path=FIG_DIR / "03_pr_curve.png",
)
plt.show()

# %% [markdown]
# ## 6. Calibration plot

# %%
plot_calibration(
    y_test.values, {"XGBoost": y_prob},
    n_bins=8,
    title="XGBoost Calibration (Test Set)",
    save_path=FIG_DIR / "03_calibration.png",
)
plt.show()

# %% [markdown]
# ## 7. Feature importances (gain-based)

# %%
imp = pd.Series(
    best_model.feature_importances_,
    index=X_train.columns,
).sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(9, max(4, len(imp) * 0.4)))
imp.plot(kind="barh", ax=ax, color="steelblue", edgecolor="k")
ax.set_xlabel("Feature importance (gain)", fontsize=11)
ax.set_title("XGBoost built-in feature importance", fontsize=12)
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(FIG_DIR / "03_feature_importance.png", dpi=150)
plt.show()
print("Top features:")
print(imp.head(10).to_string())

# %% [markdown]
# ## 8. Save model & metrics

# %%
with open(MODELS_DIR / "xgb_model.pkl", "wb") as f:
    pickle.dump(best_model, f)
print("Saved: models/xgb_model.pkl")

with open(MODELS_DIR / "xgb_best_params.pkl", "wb") as f:
    pickle.dump(search.best_params_, f)
print("Saved: models/xgb_best_params.pkl")

mt = metrics_table([metrics])
mt.to_csv(TAB_DIR / "03_xgb_metrics.csv")
print("Saved: results/tables/03_xgb_metrics.csv")
print(mt)
