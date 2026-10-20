# Conditional prevalence sensitivity: equations and scope

This extension performs arithmetic on previously saved operating points. It trains no model and selects no threshold. The existing logistic cutoffs come from the development-only threshold study; their sensitivity and specificity are recomputed from the historical-holdout confusion counts. Duplicate cutoff choices for different penalties are grouped.

## Calculation

Let `pi` be the assumed fraction with the malignant reference label, `Se` the fixed sensitivity, and `Sp` the fixed specificity. In a hypothetical unit population:

- True-positive share = `pi × Se`
- False-negative share = `pi × (1 − Se)`
- True-negative share = `(1 − pi) × Sp`
- False-positive share = `(1 − pi) × (1 − Sp)`

The Bayes identities are:

`PPV = pi × Se / [pi × Se + (1 − pi) × (1 − Sp)]`

`NPV = (1 − pi) × Sp / [(1 − pi) × Sp + pi × (1 − Se)]`

If a denominator is zero, that predictive value is undefined and is represented as `null` in JSON or a blank CSV field. It is not assigned zero. Unknown sensitivity or specificity also cannot support this calculation, so the program rejects it explicitly. These equations are presented in [Lange and Brunner (2013)](https://doi.org/10.3390/diagnostics3010192).

The table uses assumed prevalences of 1%, 5%, 10%, 25%, and 50%. Curves interpolate the same formula over 1–50%; they are not fits to new observations. Every result is conditional on the stored operating rates and the chosen cutoff. The NPV plot uses a zoomed axis to keep small changes visible.

## Assumptions and interpretation

Stable sensitivity and specificity are assumptions. Full label shift holds class-conditional feature distributions fixed while class proportions change [Lipton et al., 2018](https://proceedings.mlr.press/v80/lipton18a.html). This exercise demonstrates the resulting predictive-value arithmetic for a fixed classifier, but does not implement that paper's shift detector or correction method. It also does not establish that label shift describes a real target setting.

The rates come from 42 malignant and 72 benign records in the **previously observed** holdout. The curves treat those estimated rates as exact; operating-rate sampling error, previous inspection, feature-measurement changes, and population differences are not propagated. They are point scenarios, not confidence or credible bands. [Murad et al. (2023)](https://doi.org/10.1503/cmaj.221802) provide empirical reason to question fixed sensitivity/specificity across populations. No new disease prevalence is estimated, and none of the displayed cutoffs is recommended for clinical use.

The calculation is not individual risk recalibration. PPV averages over the classifier's positive calls under the assumed population, rather than assigning each record a corrected probability. It therefore cannot turn the fitted model into a validated screening tool.

## Reproduce without refitting

After the complete study has produced `holdout_thresholds.csv`, run:

```sh
python -m cell_validation.prevalence --results-dir results
```

This writes `prevalence_sensitivity.csv`, `prevalence_sensitivity.json`, `prevalence_sensitivity.png`, and `prevalence_report.md`. The JSON records the input table's SHA-256. The complete study also runs this step automatically.

## Related tools worth comparing

The official scikit-learn repository has a [probability-calibration example](https://github.com/scikit-learn/scikit-learn/blob/main/examples/calibration/plot_calibration_curve.py) and a [cost-sensitive threshold example](https://github.com/scikit-learn/scikit-learn/blob/main/examples/model_selection/plot_cost_sensitive_learning.py). They are useful references for separating score calibration from threshold decisions. This project uses scikit-learn estimators, but its small-grid cutoff study and conditional prevalence arithmetic are independently written. It does not reproduce those examples, use `TunedThresholdClassifierCV`, or claim equivalent validation. No external repository code was copied for this extension.
