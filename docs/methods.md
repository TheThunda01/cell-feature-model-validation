# Methods and limits

## Prespecified example workflow

The script uses seed `20261020` to create an 80% training / 20% test split, stratified by the recoded label. There are 455 training and 114 test records. All 30 features are retained. Within training data, five shuffled stratified folds compare logistic-regression `C` values of 0.01, 0.1, 1, and 10 using ROC AUC. `StandardScaler` remains inside the pipeline, so each validation fold uses scaling learned from its corresponding training fold. The selected pipeline is then refit on all training records. A `DummyClassifier(strategy="prior")` learns only the training class proportions.

The two specified models are evaluated on the held-out records in one analysis run. `training_cv.csv` contains **selection scores**, not independent performance estimates. Varma and Simon [1] showed that using tuning scores to estimate the selected model's performance can be optimistic. This project uses a separate internal holdout; it does not implement or claim nested cross-validation. Scikit-learn's documentation [2] explains why preprocessing also belongs within the training process.

## Metrics

- **ROC AUC** evaluates how often the model ranks a positive case above a negative one, with ties handled by the library implementation.
- **Balanced accuracy** is the mean of malignant recall and benign recall at threshold 0.5.
- **Brier score** is the mean squared difference between the malignant probability and binary label. It reflects multiple aspects of probability prediction and is not a stand-alone calibration test.
- **Confusion counts** are saved as true negative, false positive, false negative, and true positive, with malignant always positive.

The calibration curve divides test predictions into five quantile bins and compares mean predicted probability with observed malignant fraction. No recalibration is fitted. It is a visual diagnostic, not evidence that the probabilities are reliable in new settings.

The AUC interval resamples test rows with replacement 2,000 times and takes the 2.5th and 97.5th percentiles, discarding resamples with only one class. This is a conditional, approximate interval for this fixed model and test sample. It excludes variation from fitting the model and selecting `C`. It also assumes test rows can be resampled as independent observations. This convenience calculation is not an external validation study.

## What this example cannot establish

The data is small and widely reused. It lacks the context needed here to audit contemporary subgroup performance, acquisition differences, prevalence changes, or prospective use. A random split does not test geographic or temporal transportability. Test-set inspection may influence subsequent human decisions even when the script itself avoids leakage; do not tune against the published test result.

Correlated image summaries are not independent biological mechanisms. A predictive association does not establish causation. This repository does not claim clinical utility, patient benefit, treatment prediction, regulatory readiness, or a novel cancer biomarker. It also does not compare a broad range of model families: logistic regression and the baseline were selected to keep the validation process inspectable.

## References

1. Varma, S., & Simon, R. (2006). *Bias in error estimation when using cross-validation for model selection.* BMC Bioinformatics, 7, 91. [doi:10.1186/1471-2105-7-91](https://doi.org/10.1186/1471-2105-7-91).
2. scikit-learn developers. [Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html).
