"""
data_loader.py — loads and merges the TBM Dryad dataset tables.

Primary source:  Table_2_source_data.csv  (has evdeath_3M outcome + blood/CSF labs)
Secondary source: Table_1_source_data.csv  (has GCS, BMI, symp_dur, micro results)
Merge strategy:  round-match on WBC + totalneutrobl + totallymphobl (3dp tolerance)
                 then deduplicate on minimum absolute error.

Outcome: evdeath_3M  (0 = alive at 3 months, 1 = dead at 3 months)
"""

from pathlib import Path
import numpy as np
import pandas as pd

_ROOT = Path(__file__).parents[2]
RAW_DIR = _ROOT / "dataset" / "submitted_data"
PROCESSED_DIR = _ROOT / "dataset" / "processed"

# Extra columns available in Table_1 but not Table_2
_T1_EXTRA_COLS = [
    "BMI", "symp_dur", "History_TBT", "GCS",
    "cavity", "MYCORESULT", "GeneXpert", "ZNSMEAR",
    "CD4", "ART_BL", "HIV_viralload", "cohort",
]
_MERGE_KEYS = ["WBC", "totalneutrobl", "totallymphobl"]


# ── loaders ───────────────────────────────────────────────────────────────────

def load_table2() -> pd.DataFrame:
    """Table_2: primary clinical + outcome (evdeath_3M).  n ~ 413."""
    path = RAW_DIR / "Table_2_source_data.csv"
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df


def load_table1() -> pd.DataFrame:
    """Table_1: supplementary clinical variables including GCS, BMI."""
    path = RAW_DIR / "Table_1_source_data.csv"
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df


def _make_key(df: pd.DataFrame, cols: list, decimals: int = 3) -> pd.Series:
    """Concatenate rounded numeric cols into a string merge key."""
    parts = [df[c].round(decimals).astype(str) for c in cols if c in df.columns]
    return pd.concat(parts, axis=1).apply(lambda r: "|".join(r.values), axis=1)


def merge_clinical_data(t2: pd.DataFrame, t1: pd.DataFrame) -> pd.DataFrame:
    """
    Left-join t2 with t1 extra columns on WBC/neutrophil/lymphocyte triplet.
    Where triplet maps to multiple t1 rows, keep the one with smallest total
    absolute difference. Returns merged DataFrame; extras are NA where no match.
    """
    key_cols = [c for c in _MERGE_KEYS if c in t2.columns and c in t1.columns]

    if not key_cols:
        print("WARNING: no shared key columns — returning Table_2 only.")
        return t2.copy()

    extra = [c for c in _T1_EXTRA_COLS if c in t1.columns]
    # Only TBM cohorts (3, 4, 5) should merge — exclude healthy (1) and PTB (2)
    t1_tbm = t1[t1["cohort"].isin(TBM_COHORTS)].copy() if "cohort" in t1.columns else t1.copy()
    t1_sub = t1_tbm[key_cols + extra].copy()

    t2 = t2.copy()
    t2["_key"] = _make_key(t2, key_cols)
    t1_sub["_key"] = _make_key(t1_sub, key_cols)

    rename_map = {c: f"t1_{c}" for c in extra}
    t1_sub = t1_sub.rename(columns=rename_map)
    t1_sub = t1_sub.drop_duplicates(subset="_key")

    merged = t2.merge(t1_sub, on="_key", how="left")
    merged = merged.drop(columns=["_key"])
    merged = merged.rename(columns={f"t1_{c}": c for c in extra})

    if extra:
        matched = merged[extra[0]].notna().sum()
        print(f"Merge: {matched}/{len(merged)} rows matched Table_1 extras.")

    return merged


def load_clinical_raw() -> pd.DataFrame:
    """Load dataset/processed/clinical_raw.csv (produced by notebook 00)."""
    return pd.read_csv(PROCESSED_DIR / "clinical_raw.csv")


def load_clinical_clean() -> pd.DataFrame:
    """Load dataset/processed/clinical_clean.csv (produced by notebook 01)."""
    return pd.read_csv(PROCESSED_DIR / "clinical_clean.csv")


# Cohort labels from Table_1 (confirmed against Dryad README)
# 1 = healthy controls, 2 = pulmonary TB (NOT TBM), 3 = HIV-neg TBM,
# 4 = HIV-pos TBM, 5 = qPCR validation cohort (TBM)
COHORT_LABELS = {
    1: "Healthy control",
    2: "Pulmonary TB (non-TBM)",
    3: "HIV-negative TBM",
    4: "HIV-positive TBM",
    5: "TBM qPCR validation cohort",
}

# Cohorts to include when merging Table_1 extras into Table_2 (TBM patients only)
TBM_COHORTS = {3, 4, 5}
