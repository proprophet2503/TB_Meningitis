# TBM Mortality Prediction

XGBoost + SHAP + clinical nomogram for predicting 3-month mortality in adult tuberculous meningitis (TBM) patients.

## Overview

This project builds a machine-learning pipeline on a Vietnamese TBM cohort to:

1. Train an XGBoost classifier (binary outcome: dead/alive at 3 months)
2. Explain the model globally and locally with SHAP values
3. Select top 5-8 SHAP features and construct a point-based clinical nomogram usable without a computer
4. Evaluate clinical utility via decision curve analysis (Net Benefit curves)

**Scope constraints (deliberate):** single dataset, internal 70:30 split only, no external validation, no survival analysis, no multi-model comparison.

## Dataset

**Source:** "Whole blood transcriptional profiles and the pathogenesis of tuberculous meningitis"  
**DOI:** `10.5061/dryad.s4mw6m9gf`  
**License:** CC0

281 Vietnamese adults with TBM (207 HIV-negative, 74 HIV-positive).  
Outcome variable: `evdeath_3M` (3-month mortality, binary).

> **Manual download required.** Dryad blocks automated `curl`/`wget` requests with bot protection. Download `README.md` and `submitted_data.zip` from the DOI link in a browser, then place both files in `dataset/raw/`.

This is primarily a transcriptomics dataset. The project only uses the clinical metadata tables (`Table_1_source_data.csv`, `Table_2_source_data.csv`), not the gene-expression matrix.

## Project Structure

```
.
├── code/
│   ├── notebooks_experiment/    interactive Jupyter notebooks (00-06)
│   ├── pipeline/                pipeline scripts (Python equivalents of notebooks)
│   └── src/
│       ├── data_loader.py       loads and merges clinical tables
│       ├── eval_metrics.py      AUROC, AUPRC, Brier score, calibration plots
│       └── nomogram.py          point-scale conversion and matplotlib nomogram
├── dataset/
│   ├── raw/                     manual downloads land here (gitignored)
│   ├── submitted_data/          extracted source data files
│   └── processed/               cleaned CSVs produced by notebooks
├── docs/
│   └── PROJECT_PLAN.md          full scope and design decisions
├── models/                      saved model artifacts (.pkl)
├── results/
│   ├── figures/                 SHAP plots, nomogram, calibration, DCA curves
│   └── tables/                  Table 1, metrics summary
└── requirements.txt
```

## Pipeline

Each step reads from the previous step's output in `dataset/processed/`.

| Step | Notebook | Description |
|------|----------|-------------|
| 00 | `00_data_acquisition` | Unzip, inventory files, isolate clinical tables, produce `clinical_raw.csv` |
| 01 | `01_eda_preprocessing` | Missingness audit, drop variables with >80% missing, impute, encode, Table 1 |
| 02 | `02_split_and_balance` | 70:30 stratified split, assess class imbalance, set `scale_pos_weight` |
| 03 | `03_model_training_xgboost` | Hyperparameter search (RandomizedSearchCV), fit XGBoost, evaluate on test set |
| 04 | `04_shap_analysis` | SHAP summary (global) + waterfall (local), rank features by mean |SHAP| |
| 05 | `05_nomogram_construction` | Logistic surrogate on SHAP-selected features, point-scale nomogram, ROC overlay |
| 06 | `06_decision_curve_analysis` | Net Benefit curves for XGBoost and nomogram vs treat-all/treat-none |

## Setup

```bash
pip install -r requirements.txt
```

Run notebooks in order from `code/notebooks_experiment/`, or run scripts from `code/pipeline/`.

## Key Clinical Variables

From `Table_2_source_data.csv` (primary):

- `evdeath_3M`: outcome (1 = dead at 3 months, 0 = alive)
- `WBC`, `totalneutrobl`, `totallymphobl`: blood leucocyte/neutrophil/lymphocyte counts
- `CSFWBC`, `totalcsfneutro`, `totalcsflympho`: CSF cell counts
- `HIV`, `TBMGRADE`, `DIAGNOSTIC_SCORE`

Additional variables merged from `Table_1_source_data.csv`:

- `GCS` (Glasgow Coma Scale), `BMI`, `symp_dur` (symptom duration)
- Microbiology: `MYCORESULT`, `GeneXpert`, `ZNSMEAR`
- `CD4`, `HIV_viralload`, `ART_BL`

## Evaluation Metrics

- **AUROC** and **AUPRC** (preferred under class imbalance)
- **Brier score**
- Calibration plot
- ROC overlay comparing XGBoost vs nomogram surrogate

## Limitations

- Single cohort, no external validation
- n=281 is small; minority-class stability depends on death count in the 70:30 split
- Nomogram is a surrogate of XGBoost (logistic regression on top SHAP features); it approximates but does not replicate model predictions
