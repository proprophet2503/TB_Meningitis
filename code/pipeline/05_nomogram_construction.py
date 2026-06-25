# %% [markdown]
# # Notebook 05 — Nomogram Construction
#
# **Goal:** Logistic regression (LR) surrogate on top SHAP features
# → point-based nomogram → validate LR vs XGBoost.
#
# **Why LR surrogate?** Nomograms require a linear model.
# XGBoost is non-linear and cannot directly be converted to a point scale.
#
# **Point scaling (protocol doc2):**
# - Anchor (largest |coef × range|) = 100 pts; others scaled proportionally.
# - Total points axis → predicted probability via LR equation.

# %%
import sys
import pickle
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer

sys.path.insert(0, str(Path("../src").resolve()))
from data_loader import PROCESSED_DIR
from eval_metrics import compute_metrics, plot_roc_curve, plot_calibration, metrics_table
from nomogram import build_nomogram_points, plot_nomogram

MODELS_DIR = Path("../../models")
FIG_DIR    = Path("../../results/figures")
TAB_DIR    = Path("../../results/tables")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "evdeath_3M"

# %% [markdown]
# ## 1. Load data and SHAP top features

# %%
train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
test_df  = pd.read_csv(PROCESSED_DIR / "test.csv")

top_feat_df = pd.read_csv(TAB_DIR / "04_shap_top_features.csv")
TOP_FEATURES = top_feat_df["feature"].tolist()
print(f"Top {len(TOP_FEATURES)} SHAP features: {TOP_FEATURES}")

X_train = train_df[TOP_FEATURES]
y_train = train_df[TARGET].astype(int)
X_test  = test_df[TOP_FEATURES]
y_test  = test_df[TARGET].astype(int)

print(f"Train: {X_train.shape}  Test: {X_test.shape}")

# %% [markdown]
# ## 2. Impute (required for LR — XGBoost handles NaN natively)

# %%
imputer = SimpleImputer(strategy="median")
X_train_imp = pd.DataFrame(imputer.fit_transform(X_train), columns=TOP_FEATURES)
X_test_imp  = pd.DataFrame(imputer.transform(X_test),       columns=TOP_FEATURES)
print("Imputation complete. Remaining NaN:", X_train_imp.isnull().sum().sum())

# %% [markdown]
# ## 3. Fit logistic regression surrogate

# %%
lr = LogisticRegression(
    penalty="l2",
    C=1.0,
    solver="lbfgs",
    max_iter=2000,
    random_state=42,
    class_weight="balanced",
)
lr.fit(X_train_imp, y_train)

coefs     = lr.coef_[0]
intercept = float(lr.intercept_[0])

print("LR coefficients (sorted by |coef|):")
sorted_coefs = sorted(zip(TOP_FEATURES, coefs), key=lambda x: abs(x[1]), reverse=True)
for feat, coef in sorted_coefs:
    print(f"  {feat:<28s}  coef={coef:+.4f}")
print(f"  intercept: {intercept:.4f}")

# %% [markdown]
# ## 4. LR vs XGBoost comparison

# %%
with open(MODELS_DIR / "xgb_model.pkl", "rb") as f:
    xgb_model = pickle.load(f)

y_prob_lr  = lr.predict_proba(X_test_imp)[:, 1]
y_prob_xgb = xgb_model.predict_proba(test_df.drop(columns=[TARGET]))[:, 1]

metrics_lr  = compute_metrics(y_test.values, y_prob_lr,  model_name="LR Surrogate")
metrics_xgb = compute_metrics(y_test.values, y_prob_xgb, model_name="XGBoost")

mt = metrics_table([metrics_xgb, metrics_lr])
print("\nModel comparison (test set):")
print(mt)
mt.to_csv(TAB_DIR / "05_metrics_comparison.csv")
print("Saved: results/tables/05_metrics_comparison.csv")

# %% [markdown]
# ## 5. ROC comparison

# %%
plot_roc_curve(
    y_test.values,
    {"XGBoost (all features)": y_prob_xgb,
     "LR Surrogate (top SHAP)": y_prob_lr},
    title="ROC — XGBoost vs Nomogram LR (Test Set)",
    save_path=FIG_DIR / "05_roc_comparison.png",
)
plt.show()

# %% [markdown]
# ## 6. Calibration comparison

# %%
plot_calibration(
    y_test.values,
    {"XGBoost": y_prob_xgb, "LR Surrogate": y_prob_lr},
    n_bins=8,
    title="Calibration — XGBoost vs LR Surrogate (Test Set)",
    save_path=FIG_DIR / "05_calibration_comparison.png",
)
plt.show()

# %% [markdown]
# ## 7. Build nomogram point scales

# %%
feature_ranges = {
    feat: (float(X_train_imp[feat].min()), float(X_train_imp[feat].max()))
    for feat in TOP_FEATURES
}
print("Feature ranges from training data:")
for feat, (lo, hi) in feature_ranges.items():
    print(f"  {feat:<28s}: [{lo:.2f}, {hi:.2f}]")

point_scales, total_to_prob = build_nomogram_points(
    coefs=coefs,
    feature_ranges=feature_ranges,
    feature_names=TOP_FEATURES,
    intercept=intercept,
    n_ticks=10,
    max_scale=100,
)

# Verify total points → probability mapping
print("\nPoint scale verification:")
for test_pts in [0, 25, 50, 75, 100]:
    pt_min = sum(s["points"].min() for s in point_scales.values())
    pt_max = sum(s["points"].max() for s in point_scales.values())
    actual_pts = pt_min + (test_pts / 100) * (pt_max - pt_min)
    prob = total_to_prob(actual_pts)
    print(f"  Total pts={test_pts:3d}  → predicted prob={prob:.3f}")

# %% [markdown]
# ## 8. Draw nomogram

# %%
DISPLAY_LABELS = {
    "GCS": "Glasgow Coma Scale",
    "AGE": "Age group (0=<20, 3=>60)",
    "BMI": "BMI (0=<18.5, 3=>30)",
    "HIV": "HIV positive",
    "TBMGRADE": "TBM grade (1-3)",
    "DIAGNOSTIC_SCORE": "TBM certainty (0=poss, 2=def)",
    "WBC": "Blood WBC (×10⁹/L)",
    "totalneutrobl": "Blood neutrophils (×10⁹/L)",
    "totallymphobl": "Blood lymphocytes (×10⁹/L)",
    "CSFWBC": "CSF WBC (cells/μL)",
    "totalcsfneutro": "CSF neutrophils (cells/μL)",
    "totalcsflympho": "CSF lymphocytes (cells/μL)",
    "SEX": "Sex (1=male)",
    "symp_dur": "Symptom duration (days)",
    "History_TBT": "Prior TB treatment",
    "MYCORESULT": "MGIT culture +ve",
    "GeneXpert": "GeneXpert +ve",
    "ZNSMEAR": "AFB smear +ve",
    "CD4": "CD4 count (cells/μL)",
}

fig_nomo = plot_nomogram(
    point_scales=point_scales,
    total_to_prob=total_to_prob,
    feature_labels={f: DISPLAY_LABELS.get(f, f) for f in TOP_FEATURES},
    title="TBM 3-Month Mortality Nomogram",
    save_path=FIG_DIR / "05_nomogram.png",
)
plt.show()
print("Saved: results/figures/05_nomogram.png")

# %% [markdown]
# ## 9. Save surrogate model

# %%
surrogate_pkg = {
    "lr_model": lr,
    "imputer": imputer,
    "top_features": TOP_FEATURES,
    "feature_ranges": feature_ranges,
    "point_scales": point_scales,
    "intercept": intercept,
    "coefs": dict(zip(TOP_FEATURES, coefs)),
}
with open(MODELS_DIR / "lr_surrogate.pkl", "wb") as f:
    pickle.dump(surrogate_pkg, f)
print("Saved: models/lr_surrogate.pkl")

print(f"\nLR surrogate AUROC = {metrics_lr['AUROC']:.4f}")
print(f"XGBoost AUROC      = {metrics_xgb['AUROC']:.4f}")
print("\nAcceptable if LR AUROC is within ~0.05 of XGBoost.")
