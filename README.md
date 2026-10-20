# Cell-feature model validation

This project asks a modest question: how should we evaluate a classifier when we have a small, familiar biological dataset and many opportunities to make its performance look better than it is?

The example uses **cell-image measurements**, not gene expression, from the Wisconsin Diagnostic Breast Cancer dataset. It includes 569 records and 30 numerical features derived from images of fine-needle aspirates [1]. The goal is to demonstrate a careful workflow, not to propose a diagnostic tool or a new biological finding.

## What you can inspect here

- A fixed, stratified training/test split made before preprocessing.
- Scaling and logistic regression inside one pipeline, with tuning confined to training folds.
- A prior-only baseline, aggregate held-out metrics, a confusion matrix, and a descriptive calibration plot.
- Tests for split isolation, label direction, preprocessing, and invalid metric inputs.
- Dataset attribution, a data fingerprint, dependency versions, and limitations next to the results.

## Run it

Use Python 3.12 from the repository root. The data is bundled with scikit-learn, so the analysis itself does not need network access after installation.

```sh
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m cell_validation --output-dir results
```

The run writes `metrics.json`, `model_comparison.csv`, `training_cv.csv`, `calibration_bins.csv`, and `diagnostics.png`. It does not export row-level predictions or a fitted model. The checked-in output comes from the pinned environment; small numerical differences on other platforms are possible.

![Held-out ROC and descriptive calibration plots](results/diagnostics.png)

## How to read the result

In the checked-in run, logistic regression selected `C=1` using training folds. Its 114 held-out records produced the following aggregate results:

| Model | ROC AUC | Balanced accuracy | Brier score |
| --- | ---: | ---: | ---: |
| Logistic regression | 0.9944 | 0.9812 | 0.0180 |
| Prior-only baseline | 0.5000 | 0.5000 | 0.2327 |

The logistic model made one false-positive and one false-negative classification. Its conditional test-row bootstrap AUC interval was approximately 0.981 to 1.000; read the limits of that calculation below before interpreting it.

The positive class is **malignant**. This explicitly reverses scikit-learn's original numeric encoding, so sensitivity-related counts are not accidentally interpreted backwards. Labels are predicted at a fixed probability threshold of 0.5; this is a demonstration choice, not a clinical decision threshold.

ROC AUC describes ranking in the held-out sample. Balanced accuracy averages the two class recalls. The Brier score is the mean squared probability error; lower is better on the same test set. A good Brier score alone does not establish calibration. The five-bin calibration curve is descriptive and has few observations per bin.

**This is internal validation on a well-known benchmark.** The test set is small, and random splitting within this dataset does not demonstrate performance at a new hospital or in present-day practice. The bootstrap interval conditions on the fitted model and resamples only test records; it does not capture uncertainty from training, model selection, or changes in data collection. Once the test results have been inspected, they should not become a target for further tuning. See [methods and limitations](docs/methods.md).

## Where to start reading the code

`cell_validation/analysis.py` contains the workflow. `tests/test_analysis.py` checks assumptions that matter to interpretation. [Data provenance](docs/data-provenance.md) explains which data copy is used and how it is attributed.

## References and reuse

1. Wolberg, W., Mangasarian, O., Street, N., & Street, W. (1993). *Breast Cancer Wisconsin (Diagnostic)* [Dataset]. UCI Machine Learning Repository. [doi:10.24432/C5DW2B](https://doi.org/10.24432/C5DW2B).
2. Varma, S., & Simon, R. (2006). Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics, 7*, 91. [doi:10.1186/1471-2105-7-91](https://doi.org/10.1186/1471-2105-7-91).
3. scikit-learn developers. [Common pitfalls: data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage) and [dataset loader](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html).

The code is released under the repository's MIT license. The upstream dataset has its own **CC BY 4.0** license [1]; the code license does not replace it. This is an educational portfolio project. Its documentation and code were developed with AI assistance and checked through the included tests and reproducible run.
