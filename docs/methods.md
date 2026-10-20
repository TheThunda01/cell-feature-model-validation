# Methods, explained from the data outward

## The three data roles

The historical split contains 455 development records and 114 holdout records. The latter are unchanged from version 0.1, and were previously inspected. They remain outside the computational development path, but their final evaluation is a descriptive replication rather than a new blind test.

Within the development data, an **outer** split creates a temporary training partition and a temporary evaluation partition. An **inner** cross-validation search uses only that outer training partition to choose settings. The winning pipeline is refit on the outer training partition, then predicts the outer evaluation records. This repeats across four folds and two seeded repetitions. All 455 development records are evaluated once per repetition.

This arrangement distinguishes parameter selection from outer assessment. Varma and Simon [1] demonstrated optimism when tuning and performance estimation use the same cross-validation results. Their work motivates the separation; it does not guarantee that this project's small internal dataset is representative of clinical practice.

## Models and parameter searches

The logistic pipeline contains `StandardScaler` and L2-regularized `LogisticRegression`. Scaling is fitted anew inside every inner training fold, and the selected pipeline is refitted only on the relevant outer training rows. The search tries `C` values 0.01, 0.1, 1, and 10; lower `C` means stronger regularization in this implementation. All features are retained.

The comparator is a random forest [2] with 100 trees, square-root feature subsampling, and a fixed seed. It tries maximum depth 3 versus no explicit depth limit and minimum leaf size 2 versus 8. Trees receive the numeric features directly: scaling would not add a useful role to this implementation. This limited search is an inspectable modeling contrast, not a comprehensive algorithm competition.

A prior baseline learns the malignant fraction in each outer training partition and assigns that probability to every evaluation record. It uses no feature values. With the observed class balance and cutoff 0.5, it classifies every record as benign; balanced accuracy and AUC are therefore 0.5.

All searches maximize inner ROC AUC. After the nested analysis, each learned model is tuned again with five folds over all 455 development records and refitted. Both families are retained; the script does not select a winner based on the historical holdout.

## What the nested-CV summaries mean

`nested_cv_folds.csv` contains 24 rows: eight folds for each of three models. Parameter choices and index fingerprints accompany the metrics. The summary gives unweighted means, standard deviations, and ranges across the eight folds. Evaluation folds differ in size by at most one record. Averaging each fold equally is an explicit descriptive choice.

Folds share training records, and repeated splits reuse evaluation records. They are not independent experimental replications. The standard deviation describes observed split-to-split variability; it is not a standard error or confidence interval. The code does not run a paired t-test across folds, pool repeated predictions as if they were new participants, or assert superiority from a small average difference.

## Cross-fitting and the threshold experiment

For each development record, the code retains its two outer-fold predictions, each made by a pipeline tuned without that record. Their mean forms one cross-fitted development probability. No historical-holdout record participates.

For candidate threshold `t`, a record is labeled positive when `p >= t`. The illustrative loss is:

`(FN penalty × number of false negatives + number of false positives) / number of records`

The false-positive penalty is fixed to one arbitrary unit. We repeat the calculation with false-negative penalties 1, 2, and 5. A fixed grid from 0.05 to 0.95 is searched. Ties favor a threshold closest to 0.5, then the larger one. These declared penalties do not estimate the costs of any clinical action. They also depend on the class mix in these data.

Although the predictions are cross-fitted, their labels are reused to choose the cutoff. The minimized development loss is consequently **tuning loss**. It should not be read as unbiased performance. Averaged cross-fitted probabilities also come from several smaller fitted models and need not share the same distribution as probabilities from the final full-development fit. To evaluate threshold selection itself, a future extension would need another selection step entirely inside each outer training partition. This version instead shows fixed-0.5 outer metrics and describes the training-selected cutoffs on the historical holdout.

## Metrics and uncertainty

Malignant is always the positive class. AUC measures ranking, while balanced accuracy averages sensitivity and specificity at the stated cutoff. Brier score is mean squared probability error. AUC is insensitive to the classification cutoff, whereas sensitivity and specificity change with it. Brier score combines multiple aspects of probability prediction and is not a stand-alone calibration test.

For the final pipelines at cutoff 0.5, 1,000 ordinary bootstrap samples are drawn with replacement from the historical-holdout records. The 2.5th and 97.5th percentiles are saved for AUC, balanced accuracy, and Brier score. Any resample lacking a class is discarded for consistency across the metrics. Predictions remain fixed throughout. These approximate intervals describe test-row sampling conditional on the fitted model; they exclude refitting, tuning, selection of this dataset, previous inspection, and geographic or temporal changes. A degenerate interval for the prior baseline's AUC or balanced accuracy is a mathematical property of that baseline, not proof of certainty about practice.

Calibration is summarized in five quantile bins separately for each learned model. Tied predicted values stay together, so fewer than five populated bins are possible. Each row records its size, malignant count, mean probability, and observed fraction. The vertical bars are 95% Wilson score intervals [3] for each observed fraction, conditional on the fixed model and binning. They are pointwise, not simultaneous bands; treating observations as independent is an assumption. They do not capture uncertainty in the fitted probabilities or chosen bin edges. A few dozen observations per bin cannot establish stable calibration. No recalibration is fitted here.

## Limits that matter to interpretation

This is a small and repeatedly used historical dataset. Features are image-derived summaries, not independent molecular mechanisms. The current copy does not provide the information needed here for meaningful subgroup, site, or temporal validation. No result establishes equity, clinical utility, benefit to patients, or suitability for deployment. Neither model identifies causal processes.

The open code and scoped uncertainty help readers inspect the work. They do not repair limitations of the available sample. The project's reporting map uses TRIPOD+AI [4] and PROBAST+AI [5] as guidance, without claiming formal compliance or a completed risk-of-bias assessment. Van Calster and colleagues [6] explain why strong discrimination should not substitute for calibration assessment.

References are listed in [references.md](references.md). The bracket numbers in this document follow its numbered list.
