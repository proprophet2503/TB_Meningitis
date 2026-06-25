# %% [markdown]
# # Notebook 02 — Train/Test Split & Class Imbalance
#
# **Goal:** Stratified 70:30 split, assess class imbalance,
# compute `scale_pos_weight` for XGBoost, and save train/test CSVs.
#
# **Protocol decision:** Use `scale_pos_weight` first (cost-sensitive, native XGBoost,
# no synthetic data). Add SMOTE only if AUROC on cost-sensitive model < 0.70.

# %%
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit

sys.path.insert(0, str(Path("../src").resolve()))
from data_loader import load_clinical_clean, PROCESSED_DIR

FIG_DIR = Path("../../results/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

df = load_clinical_clean()
print(f"Loaded: {df.shape}")

TARGET = "evdeath_3M"

# %% [markdown]
# ## 1. Feature matrix & target

# %%
X = df.drop(columns=[TARGET])
y = df[TARGET].astype(int)

print(f"Features ({X.shape[1]}): {X.columns.tolist()}")
print(f"\nTarget:\n{y.value_counts()}")
print(f"Mortality rate: {y.mean():.1%}")

# %% [markdown]
# ## 2. Class imbalance analysis

# %%
n_neg = (y == 0).sum()
n_pos = (y == 1).sum()
SCALE_POS_WEIGHT = float(n_neg / n_pos)

print(f"Survived (0): {n_neg}")
print(f"Died     (1): {n_pos}")
print(f"Imbalance ratio (neg/pos): {SCALE_POS_WEIGHT:.2f}")
print(f"\nRecommended XGBoost scale_pos_weight: {SCALE_POS_WEIGHT:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].pie([n_neg, n_pos], labels=["Survived", "Died"],
            colors=["steelblue", "firebrick"], autopct="%1.1f%%",
            startangle=90, textprops={"fontsize": 11})
axes[0].set_title("Class distribution (all data)")

axes[1].bar(["Survived", "Died"], [n_neg, n_pos],
            color=["steelblue", "firebrick"], edgecolor="k", width=0.5)
axes[1].set_ylabel("Count")
axes[1].set_title("Class counts")
for i, v in enumerate([n_neg, n_pos]):
    axes[1].text(i, v + 0.5, str(v), ha="center", va="bottom", fontsize=10)

fig.tight_layout()
fig.savefig(FIG_DIR / "02_class_distribution.png", dpi=150)
plt.show()

# %% [markdown]
# ## 3. Stratified 70:30 split

# %%
RANDOM_STATE = 42
TEST_SIZE = 0.30

sss = StratifiedShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_STATE)
train_idx, test_idx = next(sss.split(X, y))

X_train = X.iloc[train_idx].reset_index(drop=True)
X_test  = X.iloc[test_idx].reset_index(drop=True)
y_train = y.iloc[train_idx].reset_index(drop=True)
y_test  = y.iloc[test_idx].reset_index(drop=True)

print(f"Train: {X_train.shape}  |  Deaths: {y_train.sum()} ({y_train.mean():.1%})")
print(f"Test:  {X_test.shape}   |  Deaths: {y_test.sum()} ({y_test.mean():.1%})")

# %% [markdown]
# ## 4. Verify stratification

# %%
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, (split_name, y_s) in zip(axes, [("Train", y_train), ("Test", y_test)]):
    counts = y_s.value_counts().sort_index()
    ax.bar(["Survived", "Died"], counts.values,
           color=["steelblue", "firebrick"], edgecolor="k", width=0.5)
    for i, v in enumerate(counts.values):
        ax.text(i, v + 0.3, f"{v} ({v/len(y_s)*100:.1f}%)",
                ha="center", va="bottom", fontsize=9)
    ax.set_title(f"{split_name} set (n={len(y_s)})")
    ax.set_ylabel("Count")

fig.suptitle("Class distribution after stratified split", fontsize=12)
fig.tight_layout()
fig.savefig(FIG_DIR / "02_split_distribution.png", dpi=150)
plt.show()
print("Saved: 02_split_distribution.png")

# %% [markdown]
# ## 5. Save splits

# %%
train_df = pd.concat([X_train, y_train], axis=1)
test_df  = pd.concat([X_test,  y_test],  axis=1)

train_df.to_csv(PROCESSED_DIR / "train.csv", index=False)
test_df.to_csv(PROCESSED_DIR / "test.csv",   index=False)

print(f"Saved train.csv  shape={train_df.shape}")
print(f"Saved test.csv   shape={test_df.shape}")
print(f"\nscale_pos_weight = {SCALE_POS_WEIGHT:.4f}  ← use this in notebook 03")
