# What the current run shows

Terminology: [glossary](glossary.md). Scientific and operational choices: [assumptions](assumptions.md).

These observations describe version 0.2's fixed analysis. They are not new biomedical discoveries. The source tables are checked into `results/`, and the commands in the README reproduce them.

## Split-to-split variation is visible

The development-only investigation produced eight outer-fold estimates per model. Each fold tuned its model on an inner split before outer evaluation.

| Model | Mean AUC | Descriptive SD | Mean Brier score | Descriptive SD |
| --- | ---: | ---: | ---: | ---: |
| Logistic regression | 0.9928 | 0.0064 | 0.0230 | 0.0101 |
| Random forest | 0.9886 | 0.0091 | 0.0356 | 0.0118 |
| Prior baseline | 0.5000 | 0.0000 | 0.2340 | 0.0010 |

Logistic regression's mean AUC was slightly higher and its mean squared probability error lower in these splits. That is an observation about this run and its limited parameter grids. It does not establish a generally superior classifier. The folds overlap, so the SD column is not a standard error and the eight values are not eight independent studies. Different development data, candidate settings, or acquisition methods could change the comparison.

## Error penalties change development choices

A false negative means a malignant record labeled benign; a false positive is the reverse. The penalties below are arbitrary teaching units.

| Model | FN:FP penalty | Selected cutoff | Development false negatives | Development false positives |
| --- | ---: | ---: | ---: | ---: |
| Logistic regression | 1:1 | 0.50 | 9 | 3 |
| Logistic regression | 2:1 | 0.35 | 5 | 9 |
| Logistic regression | 5:1 | 0.35 | 5 | 9 |
| Random forest | 1:1 | 0.55 | 14 | 5 |
| Random forest | 2:1 | 0.40 | 7 | 14 |
| Random forest | 5:1 | 0.30 | 5 | 23 |

These counts use each development record's mean cross-fitted probability from two repeats. The cutoff was selected using those same labels. The resulting loss is a tuning result, even though the probability for a record was generated without fitting or tuning on that record. It is not an unbiased estimate of the full threshold-selection procedure.

The forest's progressively lower cutoff exchanged fewer false negatives for more false positives in development. There is no single universally correct tradeoff. Actual clinical valuation would require a defined use, consequences, preferences, prevalence, and suitable independent evidence; none is estimated here.

## The old holdout illustrates the limits of a cutoff choice

The 114 historical holdout records were already observed in version 0.1. After development choices were frozen in this run, both learned models had AUC about 0.9944 on them. At cutoff 0.5, logistic regression made one false positive and one false negative; the forest made two of each. The small count differences should not be overinterpreted.

Moving logistic regression to its development-selected 0.35 cutoff for a 2:1 penalty kept its one holdout false negative and added a false positive. Its illustrative holdout loss became `4/114`, compared with `3/114` at 0.5 under that same penalty. We report the failed transfer of the development improvement rather than changing the cutoff again. Selecting whichever looks best here would reuse the holdout for tuning.

## Good ranking does not settle calibration

The ROC curves look strong in this particular sample. The five-bin probability summaries are less precise than a line close to the diagonal might suggest: each bin contains only about a fifth of 114 records. Pointwise Wilson bars expose uncertainty in the observed fraction within each fixed bin. They do not quantify the full uncertainty of the probability model or prove that it will remain calibrated elsewhere.

The conditional bootstrap AUC interval is approximately 0.981–1.000 for logistic regression. It resamples fixed historical-holdout predictions and labels only. It cannot account for a new development sample, tuning instability, repeated use of this benchmark, or a change of site. Strong-looking internal numbers are a starting point for questions, not deployment evidence.

## A defensible next study

A useful extension would freeze a protocol before seeing an appropriately licensed independent dataset, define why the prediction would matter, assess acquisition and population differences, and evaluate both probability calibration and a prespecified decision process. If the aim stays educational, nesting threshold selection inside every outer training partition would be a worthwhile next implementation. Neither step is presented as completed here.
