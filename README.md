# Cell-feature model validation

**An inspectable study of what changes when model evaluation goes beyond one train/test score.**

**New here? [Read the project background, purpose, and key themes](docs/project-context.md).**

This project compares a scaled logistic regression, a small random forest, and a prior-only baseline on the Wisconsin Diagnostic Breast Cancer dataset. The input is 30 cell-image features across 569 records [1]. It is a biological-feature classification example, not a genomics dataset, clinical tool, or new cancer finding.

The useful question is methodological: can we separate model selection, threshold selection, and performance assessment while making their remaining limitations visible? Version 0.2 adds repeated nested cross-validation, cross-fitted threshold development, uncertainty summaries, and a clear record of what has already been seen.

**The 114-record holdout was inspected in version 0.1.** We preserve it and keep it out of all computation used to develop models and thresholds. Its new results are descriptive replication, not fresh blind validation. The main new investigation uses the other 455 records.

## What the investigation does

1. Keeps the original 455/114 split, verified by a stored index fingerprint.
2. Runs four outer stratified folds twice on the development data. In every outer training partition, three inner folds tune each model separately.
3. Reports each outer-fold score, selected settings, and a descriptive summary of the eight correlated estimates.
4. Builds cross-fitted development probabilities: each record is predicted only by pipelines fitted and tuned without that record. The two repeat predictions are averaged for threshold development.
5. Uses those development predictions to compare illustrative false-negative:false-positive penalties of 1:1, 2:1, and 5:1. All thresholds come from a fixed candidate grid.
6. Fits final pipelines using development data, then describes their performance on the previously observed holdout. No holdout result feeds back into the script's choices.

The source code never exports patient identifiers, row-level predictions, or a deployable model. It saves aggregate results and fingerprints instead.

## Run the complete study

Use Python 3.12 from this repository's root. The dataset comes with scikit-learn, so the analysis runs offline once dependencies are installed.

```sh
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m cell_validation --output-dir results
```

The default workload uses small parameter grids and 100 trees per forest. The complete study took about 21 seconds in the tested environment; timing will vary with hardware. A separate output directory lets you compare a reproduction with the checked-in files:

```sh
python -m cell_validation --output-dir reproduced-results
python scripts/check_reproduction.py reproduced-results
```

## Start with the new evidence

![Training-only nested cross-validation results](results/nested_cv.png)

In the checked-in run, logistic regression's mean outer-fold AUC was **0.9928**, compared with **0.9886** for the forest and **0.5000** for the prior baseline. Mean Brier scores were **0.0230**, **0.0356**, and **0.2340**, respectively. The dots are overlapping fold estimates, not eight independent experiments. We do not turn their standard deviation into a confidence interval or claim that this small difference establishes model superiority.

![Threshold development using cross-fitted training predictions](results/threshold_sensitivity.png)

Changing the illustrative penalty changed the selected cutoff. For logistic regression it was **0.50** under equal penalties and **0.35** when false negatives received twice the weight. These are teaching assumptions, not clinical valuations. The plotted quantity was minimized on the same cross-fitted development labels, so it is a **tuning loss**, not an unbiased estimate of future cost.

On the historical holdout, the lower logistic cutoff added a false positive without removing its one false negative. That is a useful reminder: a development-data choice does not guarantee improvement in another sample. Read [the findings](docs/findings.md) for the full interpretation.

![Previously observed holdout ROC and calibration summaries](results/diagnostics.png)

The calibration bars are pointwise Wilson intervals for observed bin fractions. They are not simultaneous uncertainty bands for the calibration function. The small sample, estimated probabilities, and data reuse all limit the conclusion.

## Files worth opening

| File | What it tells you |
| --- | --- |
| `results/nested_cv_folds.csv` | Every outer-fold estimate, split fingerprints, and selected settings |
| `results/nested_cv_summary.csv` | Descriptive means, SDs, and ranges; folds are correlated |
| `results/threshold_selection.csv` | Cutoffs selected only from cross-fitted development predictions |
| `results/threshold_tuning_curves.csv` | Every candidate cutoff and its development tuning loss |
| `results/holdout_thresholds.csv` | Descriptive historical-holdout results at those fixed cutoffs |
| `results/calibration_bins.csv` | Bin counts, observed fractions, and pointwise intervals |
| `results/metrics.json` | Data/split fingerprints, parameters, versions, metrics, and scoped bootstrap intervals |
| `docs/version-0.1-results.json` | The earlier published results, preserved for transparency |

[The analysis plan](docs/analysis-plan.md) records the choices. [Methods](docs/methods.md) explains the mathematics and separation of data roles. [The reporting map](docs/reporting-map.md) draws practical lessons from TRIPOD+AI [3] and PROBAST+AI [4] while identifying gaps. It is not a claim of formal guideline compliance or low risk of bias.

## Scope, attribution, and contributions

A familiar public benchmark can teach a workflow, but cannot establish clinical utility, fairness across populations, or performance under different acquisition practices. Neither associations nor forest splits identify biological mechanisms. Discrimination and calibration are different properties [5].

The code is MIT-licensed. The upstream dataset is CC BY 4.0 and has separate attribution requirements; see [data provenance](docs/data-provenance.md). This project was developed with AI assistance. Automated checks support reproducibility; they do not replace scientific review. Small, documented contributions are welcome through [the contribution guide](CONTRIBUTING.md).

## References

1. Wolberg et al. *Breast Cancer Wisconsin (Diagnostic)* [Dataset]. [doi:10.24432/C5DW2B](https://doi.org/10.24432/C5DW2B).
2. Varma & Simon (2006). Bias in error estimation when using cross-validation for model selection. [doi:10.1186/1471-2105-7-91](https://doi.org/10.1186/1471-2105-7-91).
3. Collins et al. (2024). TRIPOD+AI statement. [doi:10.1136/bmj-2023-078378](https://doi.org/10.1136/bmj-2023-078378).
4. Moons et al. (2025). PROBAST+AI. [doi:10.1136/bmj-2024-082505](https://doi.org/10.1136/bmj-2024-082505).
5. Van Calster et al. (2019). Calibration: the Achilles heel of predictive analytics. [doi:10.1186/s12916-019-1466-7](https://doi.org/10.1186/s12916-019-1466-7).

Full citations and implementation references are in [references](docs/references.md).
