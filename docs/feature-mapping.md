# Feature-definition mapping

A feature called `mean radius` is only useful across datasets if its measurement and summary procedures mean compatible things. The [UCI description](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic) identifies ten nuclear-image properties. The bundled scikit-learn description distinguishes each property's mean, standard error, and largest-value summary. Those names and definitions guide review; they do not establish compatible units or acquisition in another dataset.

The new map records what an operator knows about a candidate file. It does not execute transformations or approve an external evaluation. Research on [predictor measurement heterogeneity](https://pubmed.ncbi.nlm.nih.gov/35387683/) illustrates why differing measurement procedures can matter even when predictors share a name; its simulation results are not performance estimates for this classifier.

## Generate a template

```sh
python -m cell_validation.feature_mapping --data examples/synthetic_features.csv --output candidate-map.json
```

The command writes a new JSON file with all 30 canonical feature names, blank source definitions/units, unknown transformation kinds, and false review declarations. It refuses to overwrite a file. `--data` is optional; when supplied, it records the SHA-256 of those exact bytes. Template creation hashes the file but does not validate its data or infer a mapping. An unbound, incomplete copy is also available at [templates/feature-map-v1.json](../templates/feature-map-v1.json).

## What to record

| Field | Operator responsibility |
| --- | --- |
| `schema_version` | Use `1.0`; other versions are rejected |
| `mapping_id`, `reviewer`, `reviewed_on` | Name this review and its responsible reviewer; date uses YYYY-MM-DD |
| `data_sha256` | Bind the declarations to the exact candidate CSV; a nonempty wrong digest is rejected |
| `benchmark_reference` | Identify the benchmark definition source used for comparison |
| Per-feature `feature` | Exactly one of the 30 canonical input names |
| `source_field`, `source_definition`, `source_units` | Document the original field, its measurement/summary meaning, and units |
| `transform_kind` | `identity`, `precomputed`, or `unknown` |
| `transform_description`, `transform_reference` | Describe and locate any transformation performed before this CSV; document no transformation explicitly for identity |
| `reviewed` | A boolean declaration that this feature's mapping has been reviewed |

The input CSV still requires canonical columns. `source_field` documents an upstream field; it does not rename columns. `precomputed` means a transformation was already done outside this tool. Expressions, formulas, or paths in mapping text are never executed. Unknown units or procedures should remain clearly unresolved, with `reviewed` false; the tool cannot verify the truth of entered prose or a true review declaration.

## Optional and required modes

```sh
# Inspect missing declarations without requiring completeness.
python -m cell_validation.preflight --data examples/synthetic_features.csv --metadata examples/synthetic_metadata.json --feature-map templates/feature-map-v1.json

# Require a complete, CSV-bound declaration record.
python -m cell_validation.preflight --data examples/synthetic_features.csv --metadata examples/synthetic_metadata.json --feature-map examples/synthetic_feature_map.json --require-feature-map
```

Optional mode reports missing features, blank fields, unknown transformations, and incomplete reviews. Structural mistakes such as duplicate/unknown feature names, wrong field types, malformed dates, unsupported versions, or a mismatching digest fail in either mode. Required mode additionally rejects a missing map or incomplete declarations. A complete map contains all 30 unique features, nonblank required metadata/text fields, a matching digest, a declared transformation kind, and true review declarations for every feature.

`declarations_complete: true` means those structural requirements passed. `semantic_compatibility_established` is always false. The map and CSV digests make a review record identifiable; they do not prove that its author, units, definitions, or judgments are correct.

## Synthetic example

The [complete-looking example](../examples/synthetic_feature_map.json) is bound to three existing invented arithmetic vectors. Its review text is explicitly a fixture declaration, not a real measurement review. The [report](../examples/feature_map_report.json) demonstrates accepted structure while retaining `data_kind: synthetic`, `suitable_for_external_validation: not_assessed`, and `semantic_compatibility_established: false`. No new biological observations, prediction results, or clinical evidence are added.
