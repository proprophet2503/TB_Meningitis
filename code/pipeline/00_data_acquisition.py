# %% [markdown]
# # Notebook 00 — Data Acquisition & Inspection
#
# **Goal:** Load Dryad TBM dataset files from `dataset/submitted_data/`,
# inspect structure, merge Table_1 (clinical vars) + Table_2 (outcome),
# and write `dataset/processed/clinical_raw.csv`.
#
# **Outcome variable:** `evdeath_3M`  (0 = alive at 3 months, 1 = died)
#
# Run this notebook FIRST before any others.

# %%
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, str(Path("../src").resolve()))
from data_loader import load_table1, load_table2, merge_clinical_data, PROCESSED_DIR, COHORT_LABELS, TBM_COHORTS

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = Path("../../results/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## 1. Load Table_2 — Primary source (outcome variable here)

# %%
t2 = load_table2()
print(f"Table_2 shape: {t2.shape}")
print("\nColumn dtypes:")
print(t2.dtypes.to_string())
t2.head(3)

# %%
print("Outcome (evdeath_3M) distribution:")
print(t2["evdeath_3M"].value_counts())
print(f"\nOverall 3-month mortality rate: {t2['evdeath_3M'].mean():.1%}")

# %%
if "dataset" in t2.columns:
    print("Dataset sub-cohort breakdown:")
    print(t2["dataset"].value_counts())
    print(f"\nMortality by dataset:")
    print(t2.groupby("dataset")["evdeath_3M"].agg(["sum", "mean", "count"]))

# %% [markdown]
# ## 2. Load Table_1 — Supplementary clinical variables (GCS, BMI, etc.)

# %%
t1 = load_table1()
print(f"Table_1 shape: {t1.shape}")
print("\nCohort value counts:")
cohort_counts = t1["cohort"].value_counts().sort_index()
for cohort, count in cohort_counts.items():
    label = COHORT_LABELS.get(int(cohort), "Unknown")
    print(f"  Cohort {cohort} ({label}): n={count}")
print(f"\nTBM cohorts (used in merge): {TBM_COHORTS}")
print(f"TBM rows in Table_1: {t1['cohort'].isin(TBM_COHORTS).sum()}")
t1.head(3)

# %% [markdown]
# ## 3. Merge Table_2 (primary) + Table_1 (supplementary)

# %%
df = merge_clinical_data(t2, t1)
print(f"\nMerged DataFrame shape: {df.shape}")
print("\nAll columns:")
print(df.columns.tolist())

# %% [markdown]
# ## 4. Missingness audit

# %%
missing = df.isnull().mean().sort_values(ascending=False)
print("Missing fraction per column:")
print(missing.to_string())

# %%
fig, ax = plt.subplots(figsize=(12, 5))
colors = ["red" if m > 0.80 else "steelblue" for m in missing.values]
missing.plot(kind="bar", ax=ax, color=colors, edgecolor="k", width=0.8)
ax.axhline(0.80, color="red", ls="--", lw=1.5, label="80% drop threshold")
ax.set_xlabel("Feature", fontsize=10)
ax.set_ylabel("Missing fraction", fontsize=10)
ax.set_title("Missingness per feature (red = will be dropped)", fontsize=12)
ax.legend(fontsize=10)
ax.tick_params(axis="x", rotation=60, labelsize=7)
fig.tight_layout()
fig.savefig(FIG_DIR / "00_missingness.png", dpi=150)
plt.show()

# %% [markdown]
# ## 5. Drop columns with >80% missingness

# %%
HIGH_MISS_THRESHOLD = 0.80
drop_cols = missing[missing > HIGH_MISS_THRESHOLD].index.tolist()
print(f"Dropping {len(drop_cols)} columns (>{HIGH_MISS_THRESHOLD:.0%} missing):")
print(drop_cols)

df = df.drop(columns=drop_cols)
print(f"\nShape after drop: {df.shape}")

# %% [markdown]
# ## 6. Duplicate & integrity checks

# %%
print(f"Duplicate rows: {df.duplicated().sum()}")
print(f"\nOutcome distribution after drop:")
print(df["evdeath_3M"].value_counts())
print(f"Mortality rate: {df['evdeath_3M'].mean():.1%}")

# %% [markdown]
# ## 7. Preview & save

# %%
out_path = PROCESSED_DIR / "clinical_raw.csv"
df.to_csv(out_path, index=False)
print(f"Saved: {out_path}")
print(f"Shape: {df.shape}")
df.describe(include="all").T
