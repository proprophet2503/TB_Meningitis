# Data From: Whole blood transcriptional profiles and the pathogenesis of **tuberculous meningitis**

### Principle Investigator Contact Information

```
Name: Thuong Nguyen Thuy Thuong <thuongntt@oucru.org> 
Institution: Oxford University Clinical Research Unit - VN
Email: thuongntt@oucru.org
```

### Alternate Contact Information

```
Name: Hai Hoang Thanh
Institution: Oxford University Clinical Research Unit - VN
Email: haiht@oucru.org
```

## Dataset Overview

This dataset contains the data and code required to replicate analyses in [https://doi.org/10.7554/eLife.92344.2](https://doi.org/10.7554/eLife.92344.2), a bioinformatic analysis of whole blood transcriptomic data to find associated hub genes, pathways with tuberculous meningitis collected from clinical trial in VN.

### Dates of Data Collection

```
A. RNAseq gene expression data: 2020-2022
B. qPCR gene expresion data: 2022-2024
C. Metadata: 2019-2024
```

### Funding

This work was supported by Wellcome Trust Fellowship in Public Health and Tropical Medicine to NTTT (206724/Z/17/Z), Wellcome Trust Investigator Award to GT and Wellcome Trust to Vietnam Africa Asia Programme.

### Ethics Approval

Ethics approval was obtained from the institutional review board at the Hospital for Tropical Diseases, Pham Ngoc Thach Hospital and the ethics committee of the Ministry of Health in Vietnam, and the Oxford Tropical Research Ethics Committee, UK (OxTREC 52-16, 36-16, 24-17, 33-17 and 532-22). All participants provided their written informed consent to take part in the study, or from their relatives if they were incapacitated.

### Sharing/Access information

This work is licensed under Creative Commons Attribution 4.0 International Public License (CC BY 4.0).

## Description of the data and file structure

Multiple files in this repository are source data to generate main tables and figures in [https://doi.org/10.7554/eLife.92344.2](https://doi.org/10.7554/eLife.92344.2).
Missing value are coded as "NA".
Files with common descriptions, structure, are grouped as below.

### 1. Table\_1\_source\_data.csv

**Description:** Metadata for generating Table 1
\- cohort: study cohort (categorical - 1=healthy,2=PTB,3=HIV-negative TBM, 4=HIV-positive TBM, 5=qPCR validation cohort)
\- AGE: Age range (categorical)
\- SEX: Male gender (binary - yes/no)
\- BMI: 	BMI range (categorical)
\- symp_dur: Symptom duration (continuous - days)
\- History_TBT: History of TB treatment (binary - yes/no)
\- GCS: Glasgow coma score (continuous - 3-15)
\- cavity: Cavity chest X-ray (binary - yes/no)
\- MYCORESULT: Mtb MGIT culture positivity (binary - yes/no)
\- GeneXpert: Xpert/Ultra positivity (binary - yes/no)
\- ZNSMEAR: AFB Smear Microscopy positivity (binary - yes/no)
\- WBC: Leucocyte count in Blood (continuous - 10^6 cells/ml)
\- totalneutrobl: Neutrophil count in Blood (continuous - 10^6 cells/ml)
\- totallymphobl: Lymphocyte count in Blood (continuous - 10^6 cells/ml)
\- CSFWBC: Leucocyte count in CSF (continuous - 10^3 cells/ml)
\- totalcsfneutro: Neutrophil count in CSF (continuous - 10^3 cells/ml)
\- totalcsflympho: Lymphocyte count in CSF (continuous - 10^3 cells/ml)
\- CD4: CD4 cell count (ccontinuous - cells/ml)
\- ART_BL: Antiretroviral therapy at baseline (binary - yes/no)
\- HIV_viralload: HIV load (ccontinuous - 10^3 copy/ml)
\- missing data codes: NA

**Table 1.** Baseline characteristics of participants in the study

### 2. Table\_2\_source\_data.csv

**Description:** Metadata for generating Table 2
\- SEX: Male gender (binary - yes/no)
\- AGE: Age range (categorical)
\- HIV:  HIV infection (binary - yes/no)
\- DIAGNOSTIC_SCORE: TBM Diagnostic category (categorical)
\- TBMGRADE: Severity grade by modified British Medical Research Council criteria (categorical)
\- WBC: Leucocyte count in Blood (continuous - 10^6 cells/ml)
\- totalneutrobl: Neutrophil count in Blood (continuous - 10^6 cells/ml)
\- totallymphobl: Lymphocyte count in Blood (continuous - 10^6 cells/ml)
\- CSFWBC: Leucocyte count in CSF (continuous - 10^3 cells/ml)
\- totalcsfneutro: Neutrophil count in CSF (continuous - 10^3 cells/ml)
\- totalcsflympho: Lymphocyte count in CSF (continuous - 10^3 cells/ml)
\- evdeath_3M: 3-month mortality event (binary - 1=yes, 0=no)
\- ttdeath_3M: time to mortality event (continuous - days)
\- dataset: (categorical)
\- missing data codes: NA

**Table 2.** Association between baseline clinical characteristics with TBM mortality in RNA-seq cohorts

### 3. Table\_3\_source\_data\_1.csv,  Table\_3\_source\_data\_2.csv

**Description:** Metadata and gene expression data for generating Table 3
**Table_3_source_data_1.csv**
\- evdeath_3M: 3-month mortality event (binary - 1=yes, 0=no)
\- ttdeath_3M: time to mortality event (continuous - days)
\- columns 3-11: reverse normalized CT value of genes (continuous)
\- missing data codes: NA
**Table_3_source_data_2.csv**
\- evdeath_3M: 3-month mortality event (binary - 1=yes, 0=no)
\- ttdeath_3M: time to mortality event (continuous - days)
\- columns 3-11: Log2 normalized expression by VST for genes (continuous)
\- missing data codes: NA

**Table 3.** Validation of hub genes in PCR validation cohort

### 4. Table\_4\_source\_data\_1.csv,  Table\_4\_source\_data\_2.csv

**Description:** Metadata and gene expression data for generating Table 4
**Table_4_source_data_1.csv**
\- AGE: Z-score transformed age (continuous)
\- cohort: study cohort (categorical - 1=HIV-positive TBM, 2=HIV-negative TBM)
\- evdeath_3M: 3-month mortality event (binary - 1=yes, 0=no)
\- ttdeath_3M: time to mortality event (continuous - days)
\- History_TBT: History of TB treatment (binary - yes/no)
\- TBMGRADE: Severity grade by modified British Medical Research Council criteria (categorical)
\- totalcsflympho: Lymphocyte count in CSF (continuous - 10^3 cells/ml)
\- totalneutrobl: Neutrophil count in Blood (continuous - 10^6 cells/ml)
\- WEIGHT: Z-score transformed weight (continuous)
\- BL_CD4: CD4 cell count (continuous - cells/ml)
\- SODIUM: levels of sodium in blood (continuous - mEq/L)
\- columns 12-16: Log2 normalized expression by VST for genes (continuous)
\- missing data codes: NA
**Table_4_source_data_2.csv**
\- AGE: Z-score transformed age (continuous)
\- evdeath_3M: 3-month mortality event (binary - 1=yes, 0=no)
\- ttdeath_3M: time to mortality event (continuous - days)
\- TBMGRADE: Severity grade by modified British Medical Research Council criteria (categorical)
\- totalcsflympho: Lymphocyte count in CSF (continuous - 10^3 cells/ml)
\- totalneutrobl: Neutrophil count in Blood (continuous - 10^6 cells/ml)
\- columns 7-9: reverse normalized CT value of genes (continuous)
\- missing data codes: NA

**Table 4.** Comparison of gene signatures in distinguishing survival and death in TBM prognostic models

### 5. Figure\_2\_6\_7\_9\_source\_data.txt

**Description:** Metadata and gene expression data for generating Figure 2, 6, 7 and 9
\- cohort: study cohort (categorical - 1=healthy,2=PTB,3=HIV-negative TBM, 4=HIV-positive TBM, 5=qPCR validation cohort)
\- evdeath_3M: 3-month mortality event (binary - yes/no)
\- batch: RNA sequencing batch (categorical)
\- columns 4-20004: Log2 normalized expression by VST for genes (continuous)
\- missing data codes: NA

**Figure 2.** Blood transcriptomic profiles of four cohorts: healthy controls (n=30), PTB (n=295), HIV-negative TBM (n=207) and HIV-positive TBM (n=74)
**(A)** Principle component analysis (PCA) of whole transcriptomic profile of HC, PTB and TBM with and without HIV. Each symbol represents one individual with color coding different cohorts. The x-axis represents principle component (PC) 1, while y-axis represents PC2. **(B-G)** Enrichment scores of known innate immunity pathways associated with TBM pathogenesis. Pathway enrichment scores were calculated using single sample GSEA algorithm (ssGSEA) 47. Each dot represents one participant. The box presents median, 25th to 75th percentile and the whiskers present the minimum to the maximum points in the data.

**Figure 6.** Gene expression of representative hub genes in healthy controls (n=30), PTB (n=295), HIV-negative TBM (n=207) and HIV-positive TBM (n=74)
Each dot represents gene expression from one participant. **(A, B)** expression of FCAR and MCEMP1 hub genes from the blue module. **(C, D)** expression of NELL2 and TRABD2A hub genes from the brown modules. **(E, F)** expression of PLCG1 and NLRC3 hub genes from the red module. **(G, H)** expression of CD247 and MATK hub genes from the black module. The box presents median, 25th to 75th percentile and the whiskers present the minimum to the maximum points in the data. Comparisons were made between dead (red) with survival (blue) or between HIV-negative and HIV-positive TBM by Wilcoxon rank sum test with p-values displayed as significance level above the boxes and the horizontal bars  (* < .05, ** < .01, *** <.001).

**Figure 7:** Relationship between known pathways associated with TBM pathogenesis and mortality
**(A-F)** Enrichment scores of known immune pathways associated with TBM pathogenesis. Pathway enrichment scores were calculated using single sample GSEA algorithm 47. Each dot represents one participant. The box presents median, 25th to 75th percentile and the whiskers present the minimum to the maximum points in the data. The comparisons were made between survival and death using Wilcoxon rank sum test. Only significant results are presented with * < .05, ** < .01, *** <.001.

**Figure 9.** Enrichment score of immunity pathways in healthy controls (n=30), PTB (n=295), HIV-negative TBM (n=207) and HIV-positive TBM (n=74)
Pathway enrichment scores were calculated using single sample GSEA algorithm 47. Each dot represents one participant. **(A-C)** showed box-plots depicting enrichment scores of the innate immunity pathways from the blue module. **(E-H)** enrichment scores of the adaptive immunity pathways from the red and brown modules and **(D)** normalized expression of TNF. The box presents median, 25th to 75th percentile and the whiskers present the minimum to the maximum points in the data. Comparisons were made between dead (red) with survival (blue) or between HIV-negative and HIV-positive TBM by Wilcoxon rank sum test with p-values displayed as significance level above the boxes and the horizontal bars, respectively (* < .05, ** < .01, *** <.001).

### 6. Figure\_3\_source\_data.txt

**Description:** Metadata and gene expression data for generating Figure 3
\- cohort: study cohort (categorical - 1=healthy,2=PTB,3=HIV-negative TBM, 4=HIV-positive TBM, 5=qPCR validation cohort)
\- AGE: Z-score transformed age (continuous)
\- ttdeath: time to mortality event (continuous - days)
\- evdeath_3M: 3-month mortality event (binary - 1=yes, 0=no)
\- group: Treatment group (binary)
\- columns 5-20005: Log2 normalized expression by VST for genes (continuous)
\- missing data codes: NA

**Figure 3.** Blood transcriptomic profiles of three-month mortality at baseline in all TBM and TBM stratified by HIV status
Volcano plot showed differential expression (DE) genes by fold change (FC) between death and survival in all TBM **(A)**, HIV-negative **(B)** and HIV-positive TBM **(C)**. Each dot represents one gene. The x-axis represents log2 FC. The y-axis showed –log10 FDR of genes. DE genes were colored with red indicating up-regulated, blue indicating down-regulated genes which having fold discovery rate (FDR) <0.05 and absolute FC > 1.5.

### 7. Figure\_4\_source\_data\_1.txt, Figure\_4\_source\_data\_2.txt, Figure\_4\_source\_data\_3.csv

**Description:** Metadata and gene expression data for generating Figure 4
**Figure_4_source_data_1.txt**: 5000 most variant gene expression matrix
\- Each column is Log2 normalized expression by VST for gene (continuous)
**Figure_4_source_data_2.txt**: Metadata
\- AGE: Z-score transformed age (continuous)
\- cohort: study cohort (categorical - 1=HIV-positive TBM, 2=HIV-negative TBM)
\- evdeath_3M: 3-month mortality event (binary - 1=yes, 0=no)
\- ttdeath_3M: time to mortality event (continuous - days)
\- TBMGRADE: Severity grade by modified British Medical Research Council criteria (categorical)
\- group: Treatment group (binary)
\- missing data codes: NA
**Figure_4_source_data_3.csv** WGCNA module annotation

**Figure 4.** Blood transcriptional modules associated with mortality in TBM
**(A)** Associations between WGCNA modules with two clinical phenotypes TBM disease severity (MRC grade) and three-month mortality in discovery and validation cohorts, and their associated biological processes. The heatmap showed the association between principle component 1 (PC1) of each module and the phenotypes, particularly Spearman correlation r for MRC grade and hazard ratio per increase 1/10 unit of PC1 (HR) for mortality. The HRs were estimated using a Cox regression model adjusted for age, HIV status and dexamethasone treatment. False discovery rate (FDR) corrected based on Benjamini & Yekutieli procedure, with significant level denoted as * < .05, ** < .01 and *** <.001. Gradient colors were used to fill the cell with green indicating negative r or HR < 1, red color indicating positive r or HR > 1. The order of modules was based on hierarchical clustering using Pearson correlation distance for module eigengene. On the left, biological processes, corresponding to modules, were identified using Gene Ontology and KEGG database. **(B)** Validation of the association between WGCNA modules and mortality in discovery and validation cohorts. X-axis represents –log10 FDR in discovery cohort and Y-axis represents –log10 FDR in validation cohort. Red dash lines indicate FDR = 0.05 as the threshold for statistically significant in both cohorts. Five modules (blue, brown, red, black and cyan) with FDR < 0.05 were validated.

### 8. Figure\_5\_source\_data.xlsx, Figure\_4\_source\_data\_1.txt, Figure\_4\_source\_data\_2.txt

**Description:** Metadata, gene expression data and ORA pathway enrichment results data for generating Figure 5
**Figure_5_source_data.xlsx** ORA pathway enrichment results for significant modules
\- Enrichment.FDR: FDR of ORA test
\- nGenes: number of genes in input list belongs to pathways
\- Pathway.Genes: number of genes belongs to pathways in background
\- Pathway: Pathway description
\- Fold.Enrichment: Fold Enrichment

**Figure 5.** Biological processes, pathways and hub genes of validated modules associated with mortality
**(A-D)** showed biological processes and pathways identified in four mortality associated modules: blue, brown, red and black module, by over representation analysis (ORA). Bar plots show the top representative GO biological processes or KEGG pathways. The bars indicates biological processes or pathways having ORA FDR < 0.05 and size corresponding to fold enrichment calculated as the ratio of gene number of pathway in the input list divided by the ratio of gene number of the pathway in reference. **(E-H)** showed gene co-expression networks and hub genes of blue, brown, red and black module, respectively. Each node represents one gene. Each edge represents the link between two genes. Hub genes were shown by bigger nodes and bold text. The gradient color of node corresponds to its HR to mortality, with red indicating HR > 1, and blue HR < 1.

### 9. Figure\_8\_source\_data\_1.txt, Figure\_8\_source\_data\_2.txt, Figure\_8\_source\_data\_3.csv, Figure\_8\_source\_data\_4.xlsx

**Description:** Metadata, gene expression data and ORA pathway enrichment results data for generating Figure 8
**Figure_8_source_data_1.txt**: 5000 most variant gene expression matrix
\- Each column is Log2 normalized expression by VST for gene (continuous)
**Figure_8_source_data_2.txt**: Metadata
\- AGE: Z-score transformed age (continuous)
\- cohort: study cohort (categorical - 1=HIV-positive TBM, 2=HIV-negative TBM)
\- evdeath_3M: 3-month mortality event (binary - 1=yes, 0=no)
\- ttdeath_3M: time to mortality event (continuous - days)
\- TBMGRADE: Severity grade by modified British Medical Research Council criteria (categorical)
\- group: Treatment group (binary)
\- missing data codes: NA
**Figure_8_source_data_3.csv** WGCNA module annotation
**Figure_8_source_data_4.csv** ORA pathway enrichment results for significant modules
\- Enrichment.FDR: FDR of ORA test
\- nGenes: number of genes in input list belongs to pathways
\- Pathway.Genes: number of genes belongs to pathways in background
\- Pathway: Pathway description
\- Fold.Enrichment: Fold Enrichment
\- Type: KEGG or GO database
\- Genes: enriched genes in the pathway

**Figure 8.** Consensus transcriptional modules associated with TBM mortality stratified by HIV-infection
**(A)** Associations between 16 consensus WGCNA modules with two clinical phenotypes TBM severity (MRC grade) and mortality in HIV-negative (n=207) and HIV-positive (n=74) TBM participants, and their associated BP Gene ontology or KEEG database. The heatmap showed the association between modules and the phenotypes, with Spearman correlation r for MRC grade and hazard ratio per increase 1/10 unit of PC1 of module (HR) for mortality in HIV-positive and HIV-negative cohorts. The consensus sub-panel presented associations of the consensus modules and clinical phenotypes with same trend detected in both HIV cohorts, otherwise were annotated with missing (NA) values. False discovery rate (FDR) corrected using Benjamini & Yekutieli procedure, with significant level denoted as * < .05, ** < .01 and *** <.001. Gradient colors were used to fill the cell with green indicating negative r or HR < 1, red color indicating positive r or HR > 1. The order of modules was based on hierarchical clustering using Pearson correlation distance for module eigengene. It is noted that these consensus modules were not identical to the identified modules in the primary analysis in Figure 4A. **(B-C)** Functional enrichment analysis of HIV-positive pathway (blue module) and HIV-negative pathway (yellow module), respectively. **(D-E)** Gene co-expression network of blue and yellow modules. Each node represents one gene. Each edge represents the link between two genes. Hub genes were shown by bigger nodes with bold text. The gradient color of node corresponds to its HR to mortality, with red indicating HR>1, and blue HR<1.

## Code/Software

The majority of analyses used in the manuscript were done using R Environment for Statistical Computing version R 4.3.3.

### 1. Table\_1\_soucre\_code.Rmd

This R Markdown file contains the source code for generating Table 1.

### 2. Table\_2\_soucre\_code.Rmd

This R Markdown file contains the source code for generating Table 2

### 3. Table\_3\_soucre\_code.Rmd

This R Markdown file contains the source code for processing gene expression data from qPCR and RNAseq to generate Table 3

### 4. Table\_4\_soucre\_code.Rmd

This R Markdown file contains the source code for calculating AUC and Brier score for gene signatures in distinguishing survival and death in TBM prognostic models to generate Table 4

### 5. Figure\_2\_soucre\_code.Rmd

This R Markdown file contains the source code for processing gene expression data to calculate ssGSEA scores and compare TBM-related pathways across four cohorts, which is then used to generate Figure 2.

### 6. Figure\_3\_soucre\_code.Rmd

This R Markdown file contains the source code for performing differentially expressed analysis (DE) between Death vs survival in TBM. DE Genes is then used to generate volcano plot in Figure 3.

### 7. Figure\_4\_soucre\_code.Rmd

This R Markdown file contains the source code for constructing WGCNA and preservation analysis. At the end this file generates module vs trait association heatmap as well association of modules vs motality in Figure 4.

### 8. Figure\_5\_soucre\_code.Rmd

This R Markdown file contains the source code for processing WGCNA network to identify associated hub genes and pathways in Figure 5.

### 9. Figure\_6\_soucre\_code.Rmd

This R Markdown file contains the source code for visualizing the gene expression of representative hub genes in 4 cohorts.

### 10. Figure\_7\_soucre\_code.Rmd

This R Markdown file contains the source code for calulated ssGSEA enrichment score and compares between death and survival in TBM cohorts in Figure 7.

### 11. Figure\_8\_soucre\_code.Rmd

This R Markdown file contains the source code for conducting consensus WGCNA to idenitfy modules, hub genes and pathways which are specific for either mortality in HIV-negative or HIV-positive TBM. At the end, this file gernated Figure 8

### 12. Figure\_9\_soucre\_code.Rmd

This R Markdown file contains the source code for processing gene expression data to calculate ssGSEA scores and compare TBM-related pathways across four cohorts, as well as between death and survival, which is then used to generate Figure 9.

### Dependencies or R packages

* ggplot2
* YesSiR
* AnnotationDbi
* BiocParallel
* circlize
* data.table
* dplyr
* extrafont
* flextable
* ggplot2
* ggpubr
* ggraph
* ggrepel
* ggthemes
* GO.db
* gridExtra
* gt
* gtools
* gtsummary
* Hmisc
* igraph
* kableExtra
* limma
* magrittr
* minqa
* officer
* org.Hs.eg.db
* PCAtools
* plyr
* qgraph
* readxl
* scales
* stringr
* survival
* survminer
* WGCNA
* riskRegression
* lrm

