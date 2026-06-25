# %% [markdown]
# # Notebook 01 — EDA & Preprocessing
#
# **Goal:** Explore `clinical_raw.csv`, encode categoricals, drop leaky columns,
# produce Table 1 (baseline characteristics), and save `clinical_clean.csv`.
#
# **Key decisions (protocol doc2):**
# - Age: ordinal <20=0, 21-40=1, 41-60=2, >60=3
# - BMI: ordinal <18.5=0, 18.5-25=1, 25-30=2, >30=3
# - Binary yes/no → 1/0 (preserve NaN)
# - `ttdeath_3M` and `dataset`/`cohort` dropped (leaky or admin)
# - XGBoost handles NaN natively — no imputation here
# - SimpleImputer for LR surrogate handled in notebook 05

# %%
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sys.path.insert(0, str(Path("../src").resolve()))
from data_loader import load_clinical_raw, PROCESSED_DIR

FIG_DIR = Path("../../results/figures")
TAB_DIR = Path("../../results/tables")
FIG_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)

df = load_clinical_raw()
print(f"Loaded clinical_raw: {df.shape}")

# %% [markdown]
# ## 1. Outcome variable

# %%
TARGET = "evdeath_3M"
y = df[TARGET].astype(int)
print(f"Died (1): {y.sum()}   Survived (0): {(y==0).sum()}   Total: {len(y)}")
print(f"3-month mortality rate: {y.mean():.1%}")

fig, ax = plt.subplots(figsize=(5, 4))
counts = y.value_counts().sort_index()
bars = ax.bar(["Survived (0)", "Died (1)"], counts.values,
              color=["steelblue", "firebrick"], edgecolor="k", width=0.5)
for bar, val in zip(bars, counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            str(val), ha="center", va="bottom", fontsize=11, fontweight="bold")
ax.set_title("3-month mortality distribution", fontsize=12)
ax.set_ylabel("Count")
fig.tight_layout()
fig.savefig(FIG_DIR / "01_outcome_distribution.png", dpi=150)
plt.show()
print("Saved: 01_outcome_distribution.png")

# %% [markdown]
# ## 2. Encode categorical features

# %%
AGE_ORDER = {"<20": 0, "21-40": 1, "41-60": 2, ">60": 3}
BMI_ORDER = {"<18.5": 0, "18.5-25": 1, "25-30": 2, ">30": 3}
DIAG_ORDER = {"possible TBM": 0, "probable TBM": 1, "definite TBM": 2}

def encode_binary(col: pd.Series) -> pd.Series:
    """yes→1, no→0; preserve NaN."""
    return col.str.lower().map({"yes": 1, "no": 0})

df_enc = df.copy()

if "AGE" in df_enc.columns:
    df_enc["AGE"] = df_enc["AGE"].map(AGE_ORDER)
    print("AGE value counts:", df_enc["AGE"].value_counts().sort_index().to_dict())

if "BMI" in df_enc.columns:
    df_enc["BMI"] = df_enc["BMI"].map(BMI_ORDER)
    print("BMI value counts:", df_enc["BMI"].value_counts().sort_index().to_dict())

if "DIAGNOSTIC_SCORE" in df_enc.columns:
    df_enc["DIAGNOSTIC_SCORE"] = df_enc["DIAGNOSTIC_SCORE"].map(DIAG_ORDER)
    print("DIAGNOSTIC_SCORE:", df_enc["DIAGNOSTIC_SCORE"].value_counts().to_dict())

binary_cols = ["SEX", "HIV", "History_TBT", "cavity",
               "MYCORESULT", "GeneXpert", "ZNSMEAR", "ART_BL"]
for col in binary_cols:
    if col in df_enc.columns:
        df_enc[col] = encode_binary(df_enc[col].astype(str))

print("\nEncoding complete. dtypes:")
print(df_enc.dtypes.to_string())

# %% [markdown]
# ## 3. Drop leaky & admin columns

# %%
LEAKY = ["ttdeath_3M", "dataset", "cohort", "HIV_viralload"]
drop = [c for c in LEAKY if c in df_enc.columns]
print(f"Dropping leaky/admin columns: {drop}")
df_enc = df_enc.drop(columns=drop)
print(f"Shape: {df_enc.shape}")

# %% [markdown]
# ## 4. Remaining missingness summary

# %%
miss = df_enc.isnull().mean().sort_values(ascending=False)
miss_nonzero = miss[miss > 0]
print("Features with remaining missingness:")
print(miss_nonzero.to_string())

# %% [markdown]
# ## 5. Table 1 — Baseline characteristics

# %%
survived = df_enc[df_enc[TARGET] == 0]
died = df_enc[df_enc[TARGET] == 1]

def _med_iqr(s: pd.Series) -> str:
    s = s.dropna()
    if len(s) == 0:
        return "NA"
    return f"{s.median():.1f} [{s.quantile(.25):.1f}–{s.quantile(.75):.1f}]"

def _n_pct(s: pd.Series) -> str:
    n = s.notna().sum()
    pos = s.sum()
    return f"{pos:.0f} ({pos/n*100:.1f}%)" if n > 0 else "NA"

cont_cols = [c for c in ["AGE", "GCS", "WBC", "totalneutrobl", "totallymphobl",
                          "CSFWBC", "totalcsfneutro", "totalcsflympho",
                          "symp_dur", "BMI", "CD4"] if c in df_enc.columns]
bin_cols  = [c for c in ["SEX", "HIV", "DIAGNOSTIC_SCORE", "TBMGRADE",
                          "History_TBT", "MYCORESULT", "GeneXpert", "ZNSMEAR"]
             if c in df_enc.columns]

rows = []
for col in cont_cols:
    rows.append({"Variable": col, "All": _med_iqr(df_enc[col]),
                 "Survived": _med_iqr(survived[col]),
                 "Died": _med_iqr(died[col]), "Type": "median [IQR]"})
for col in bin_cols:
    rows.append({"Variable": col, "All": _n_pct(df_enc[col]),
                 "Survived": _n_pct(survived[col]),
                 "Died": _n_pct(died[col]), "Type": "n (%)"})

table1 = pd.DataFrame(rows)
print(table1.to_string(index=False))
table1.to_csv(TAB_DIR / "01_table1_baseline.csv", index=False)
print("\nSaved: results/tables/01_table1_baseline.csv")

# %% [markdown]
# ## 6. Distribution plots for key predictors

# %%
key_cont = [c for c in ["GCS", "WBC", "CSFWBC", "totalneutrobl"] if c in df_enc.columns]
if key_cont:
    fig, axes = plt.subplots(1, len(key_cont), figsize=(4*len(key_cont), 4))
    if len(key_cont) == 1:
        axes = [axes]
    for ax, col in zip(axes, key_cont):
        for label, grp, color in [(0, survived, "steelblue"), (1, died, "firebrick")]:
            sns.kdeplot(grp[col].dropna(), ax=ax, label=f"evdeath={label}",
                        color=color, fill=True, alpha=0.3)
        ax.set_title(col)
        ax.legend(fontsize=8)
    fig.suptitle("Key predictors by outcome", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "01_predictor_distributions.png", dpi=150)
    plt.show()
    print("Saved: 01_predictor_distributions.png")

# %% [markdown]
# ## 7. Correlation heatmap

# %%
num_cols = df_enc.select_dtypes(include=[np.number]).columns.drop(TARGET, errors="ignore").tolist()
fig, ax = plt.subplots(figsize=(max(8, len(num_cols)), max(7, len(num_cols)-1)))
corr = df_enc[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, cmap="RdBu_r", center=0,
            annot=True, fmt=".2f", annot_kws={"size": 7},
            linewidths=0.4, ax=ax)
ax.set_title("Feature correlation heatmap", fontsize=12)
fig.tight_layout()
fig.savefig(FIG_DIR / "01_correlation_heatmap.png", dpi=150)
plt.show()
print("Saved: 01_correlation_heatmap.png")

# %% [markdown]
# ## 8. Save clinical_clean.csv

# %%
out_path = PROCESSED_DIR / "clinical_clean.csv"
df_enc.to_csv(out_path, index=False)
print(f"Saved: {out_path}  shape={df_enc.shape}")
print(f"Columns: {df_enc.columns.tolist()}")
df_enc.head()
