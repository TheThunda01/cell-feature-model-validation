# Why this project exists

Terminology: [glossary](glossary.md). Scientific and operational choices: [assumptions](assumptions.md).

A high model score can conceal choices that shape the result. How were the settings chosen? How much did the score depend on the data split? What changes when different mistakes carry different costs? This project examines those questions through a small biological-feature example that readers can run and inspect.

## Background and rationale

The [Wisconsin Diagnostic Breast Cancer dataset](https://doi.org/10.24432/C5DW2B) contains numerical summaries of cell nuclei from fine-needle aspirate images. Its modest size makes the complete analysis practical on a laptop. Here it provides a teaching setting for careful evaluation; it cannot represent all patients, laboratories, or present-day clinical workflows.

The design follows a central lesson from [Varma and Simon](https://doi.org/10.1186/1471-2105-7-91): choosing model settings and estimating performance need separate data roles. The documentation also draws on [TRIPOD+AI](https://doi.org/10.1136/bmj-2023-078378) and [PROBAST+AI](https://doi.org/10.1136/bmj-2024-082505) to make decisions and remaining weaknesses easier to assess.

## What it does

The workflow compares logistic regression, a random forest, and a simple baseline. Repeated nested cross-validation keeps model tuning inside each training partition and records the evaluation results for each fold. The analysis also examines probability calibration and selects thresholds from cross-fitted development predictions using hypothetical error penalties. Tests, dependency versions, and saved outputs help readers reproduce the calculations.

The original 114-record holdout was already inspected in version 0.1. It remains excluded from computational development, but its later results are labeled **descriptive replication**, not new blind validation. That history is part of the evidence.

## Why it matters

Computational biology often involves comparing models on limited data. A clear account of uncertainty and data reuse helps readers judge what the results support. [Calibration research](https://doi.org/10.1186/s12916-019-1466-7) also explains why good ranking does not establish reliable probabilities. The contribution here is an inspectable evaluation workflow, with examples of choices that fail to improve the historical holdout.

## Key themes

- Separating development decisions from performance assessment.
- Showing variability without treating overlapping folds as independent studies.
- Distinguishing ranking, probability quality, and threshold-dependent errors.
- Reporting dataset reuse and limits openly.

There is no claim of a new biomarker, clinical benefit, or deployment readiness. For the actual observations, start with [findings](findings.md); for the calculation details, see [methods](methods.md).

## Where this fits

The [GFP investigation](https://github.com/TheThunda01/gfp-active-learning) asks which stored measurement to reveal next. This study provides a complementary lesson: deciding how a model will be evaluated requires explicit data roles. The projects use different measurements and comparisons; this benchmark supplies no clinical validation for either.
