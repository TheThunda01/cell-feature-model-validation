# Analysis decisions and data roles

Terminology: [glossary](glossary.md). Scientific and operational choices: [assumptions](assumptions.md).

This is a versioned educational methods investigation, not a prospectively registered clinical study. The version-0.2 choices below were written into the code for this extension after the version-0.1 benchmark had already been published. We therefore cannot honestly describe the original holdout as unknown.

## Questions

- How variable are two tuned model families across repeated internal evaluation splits?
- How does changing an explicit error penalty change a threshold selected from development predictions?
- What uncertainty remains when a small internal sample appears to perform well?

## Fixed choices for this version

| Decision | Choice and reason |
| --- | --- |
| Data copy | The pinned scikit-learn bundled WDBC matrix; no additional datasets |
| Outcome encoding | $`\text{malignant}=1`$, $`\text{benign}=0`$; stated explicitly to prevent reversed interpretation |
| Historical holdout | Preserve the original 114 records; verify its index hash before running |
| Development partition | The other 455 records only |
| Primary model | Logistic regression, retained from version 0.1; L2-regularized, scaled inside each fit |
| Comparator | Random forest as a contrasting nonlinear model; no claim that complexity should improve results |
| Negative-control baseline | Training class-prior probabilities, with no feature use |
| Outer evaluation | Four stratified folds, two repeats, fixed seeds |
| Inner tuning | Three stratified folds per outer fit, maximize ROC AUC |
| Logistic grid | `C` = 0.01, 0.1, 1, 10 |
| Forest grid | 100 trees; depth 3 or unrestricted; minimum leaf size 2 or 8; square-root feature subsampling |
| Final refit | Five-fold tuning of each family using all development records; no champion chosen from holdout scores |
| Threshold grid | 0.05 through 0.95 in steps of 0.05 |
| Error penalties | $`\mathrm{FN}:\mathrm{FP}=1:1,\;2:1,\;5:1`$; arbitrary examples, not elicited patient preferences or clinical costs |
| Tie-breaking | Minimum tuning loss; then closest to 0.5; then larger threshold |
| Uncertainty | 1,000 ordinary test-row bootstrap resamples for fixed-threshold metrics; pointwise binomial intervals for calibration bins |
| Exports | Aggregate results and fingerprints; no patient IDs, per-record predictions, or fitted model |

## What is isolated, and what is not

The code isolates holdout features and labels from model and threshold development. Within nested CV, outer evaluation records are also absent from parameter selection and scaling. Tests audit both forms of separation.

The analyst has already seen version-0.1 holdout scores. That information can influence future human choices even if no variable crosses a code boundary. These version-0.2 results remain exploratory. Repeated tuning against this dataset would not manufacture a new external validation set. A confirmatory follow-up would need a protocol fixed before inspection of a genuinely independent dataset with suitable provenance and reuse permission.

The threshold study optimizes on cross-fitted probabilities averaged across repeats. It does not evaluate the complete threshold-selection procedure within each outer fold. Its development loss is accordingly marked as tuning loss throughout. The fixed 0.5 cutoff is used for the outer-fold performance comparison.

## Reproducibility record

The data fingerprint and ordered training/holdout index fingerprints are saved in `metrics.json`. The historical holdout index hash is a constant in the source, so an accidental change fails instead of silently creating a more favorable split. All estimators and splitters use fixed seeds where randomness is involved. Library versions and selected parameter values are exported. Small floating-point differences across numerical libraries or platforms remain possible.

## Version 0.3 conditional prevalence extension

The new scenario calculation keeps the existing logistic cutoffs and their historical-holdout sensitivity/specificity fixed. It uses declared hypothetical positive-label fractions of 1%, 5%, 10%, 25%, and 50%. These are scenario inputs, not new estimates. No model or threshold is chosen again. The assumptions, equations, undefined-value handling, and limits are in [prevalence sensitivity](prevalence-sensitivity.md).
