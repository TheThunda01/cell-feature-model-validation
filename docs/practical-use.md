# Practical use

Terminology: [glossary](glossary.md). Scientific and operational choices: [assumptions](assumptions.md).

## Where this fits

The main study teaches model validation on a familiar public feature dataset. The preflight command checks whether a candidate file meets the feature and provenance contract before anyone applies a model. It does not evaluate a model on that file. The historical 114-record holdout remains previously observed, and the project adds no new external cohort.

## Input and output contract

`python -m cell_validation.preflight --data FILE.csv --metadata FILE.json` reads UTF-8 CSV and JSON and prints an aggregate JSON report to standard output. It writes no files and exports no record-level predictions. The 30 exact feature names come from the pinned scikit-learn Wisconsin diagnostic dataset. Column order may differ: checks use names. Missing, extra, or duplicate columns, malformed CSV quoting or row widths, blank/nonnumeric/nonfinite values, and empty data fail with exit status 2. Limits are 10 MB per input and 100,000 records. No imputation or unit conversion occurs.

An optional `reference_label` accepts only `0` for benign and `1` for malignant. A labelled file must declare exactly that `label_mapping`. Metadata requires nonempty `source`, `measurement_method`, and `feature_definition_reference`; `data_kind` must be `synthetic` or `public_deidentified_features`. `independent_of_development` and `known_overlap_checked` must be JSON booleans. These are operator declarations, not facts established by software.

The output reports input SHA-256 hashes, counts, constant features, repeated feature-vector counts, and exact numeric overlap with all 569 benchmark records, including development and historical holdout data. Duplicate counts include occurrences after the first, regardless of label. Overlap counts include every matching input row.

Exact matching cannot establish independence. It compares parsed floating-point feature values, so rounding, transformations, or measurement changes can conceal a relationship. `suitable_for_external_validation` is always `not_assessed`.

The optional `--feature-map FILE.json` checks the [30-feature mapping contract](feature-mapping.md). It reports missing definitions, units, transformations, review declarations, and file binding. `--require-feature-map` additionally requires all those declarations and a matching CSV digest. It does not perform transformations or establish measurement equivalence. Malformed map types, duplicate/unknown feature names, unsupported versions, or a wrong digest fail in either mode. Without these flags, preflight output is unchanged.

## Worked use case

```sh
python -m cell_validation.preflight \
  --data examples/synthetic_features.csv \
  --metadata examples/synthetic_metadata.json
```

The [example report](../examples/preflight_report.json) contains three invented feature vectors, two illustrative benign labels, and one illustrative malignant label. The values and labels are arithmetic fixtures, not measured cells. There are no exact benchmark matches. The incomplete independence declaration remains visible. This exercises the contract without presenting synthetic data as external evidence.

For the mapping feature, run `python -m cell_validation.preflight --data examples/synthetic_features.csv --metadata examples/synthetic_metadata.json --feature-map examples/synthetic_feature_map.json --require-feature-map`. The [result](../examples/feature_map_report.json) accepts the fixture's complete declarations while explicitly leaving semantic compatibility unestablished.

Run the original study separately with `python -m cell_validation --output-dir reproduced-results`, then `python scripts/check_reproduction.py reproduced-results`. Preflight does not change its models, cutoffs, data split, or results.

## Checks before relying on a result

Before any future external evaluation, a reviewer must establish feature definitions and units, acquisition and summary procedures, label ascertainment, sampling criteria, and independence from development data. A shared column name cannot establish those facts. Review access and reuse permission for any candidate file; this repository provides no patient-data import service. Prespecify a genuinely independent evaluation and the intended use before assessing model utility. [The literature review](literature-review.md) explains why these are separate responsibilities.

## Known limits

There is no trained-model export, inference endpoint, external performance estimate, fairness analysis, or clinical validation. The metadata fields are a minimum record, not a complete research protocol. Aggregate checks cannot authenticate provenance or detect every duplicate, leakage pathway, or mismatch in measurement meaning. Conditional prevalence scenarios still assume unchanged historical sensitivity and specificity.

## Next improvements

1. Add protocol metadata for candidate evaluations. Acceptance: sampling, outcome ascertainment, timing, missingness, and prespecified metrics are required before an evaluation runner is considered.
2. Add an independent mapping-review workflow. Acceptance: two recorded reviews and unresolved disagreements remain visible; software never infers scientific agreement from matching text.
3. Add reviewed approximate-overlap diagnostics. Acceptance: controlled rounding fixtures are detected, false matches are quantified, and every result remains a review flag.
4. Obtain a genuinely independent, appropriately licensed cohort if feasible. Acceptance: documented independence and acquisition compatibility are reviewed before any performance results are generated.
