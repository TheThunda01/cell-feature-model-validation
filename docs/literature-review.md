# Rapid evidence and practice review — 2026-10-20

## Question and scope

What should be checked and recorded before a candidate feature file could support a future independent evaluation of this educational classifier? The review focuses on transparent predictor definitions, dataset independence, and evaluation boundaries. It does not establish clinical utility or add a new validation cohort.

## Search record

PubMed was searched first on 2026-10-20, filtering publication dates to 2022/01/01–2026/10/20 and sorting by relevance:

- `"TRIPOD+AI"[Title] OR "PROBAST+AI"[Title]`: 25 reported results. Offsets 0 and 10 returned 10 and 15 records, respectively, with no next page. PMID 41320158 appeared twice, leaving 24 unique records. The provider's total and the unique retrieval count therefore differ; pagination did not establish that every unique result was retrieved.
- `"external validation"[Title] AND "prediction models"[Title] AND (guidance[Title/Abstract] OR reporting[Title/Abstract])`: 5 results, all returned at offset 0.

The combined search returned 30 record slots and 29 unique records for title/abstract screening. Three publications were retained. The first 20,000 PMC full-text characters of each were retrieved; all three were truncated. Appraisal used the accessible definitions, rationale, and methods, not a complete supplementary review. Exact identifiers and decisions are in [search-log.json](search-log.json). An official scikit-learn source file and license were inspected at a resolved commit as a targeted practice comparison.

## What the sources support

| Source | Type and access | Useful finding | Limit | Consequence here |
| --- | --- | --- | --- | --- |
| [Collins et al., 2024, PMID 38626948](https://pubmed.ncbi.nlm.nih.gov/38626948/) | Peer-reviewed TRIPOD+AI reporting guideline; partial PMC full text | Clear data roles, predictors, outcomes, and nonoverlapping evaluation participants support appraisal. | A reporting guideline cannot certify this benchmark's validity or transportability. | Require declared feature definitions, label mapping, and independence; keep the historical holdout's observed status explicit. |
| [Moons et al., 2025, PMID 40127903](https://pubmed.ncbi.nlm.nih.gov/40127903/) | Peer-reviewed PROBAST+AI quality/risk/applicability tool; partial PMC full text | Participants, predictors, outcomes, and analysis need separate consideration when judging applicability. | This code does not implement or complete a formal PROBAST+AI assessment. | A passed structural check never becomes a claim that external evaluation or clinical deployment is suitable. |
| [John et al., 2022, PMID 36471238](https://pubmed.ncbi.nlm.nih.gov/36471238/) | Primary external-validation investigation of dementia models; partial PMC full text | Recovering predictor definitions and model specifications was a practical obstacle to independent validation. | Different disease, inputs, and modelling tasks; its performance estimates do not transfer. | Add measurement-method and feature-definition metadata before accepting a candidate file for inspection. |
| [scikit-learn input validation source](https://github.com/scikit-learn/scikit-learn/blob/106573971c28d82a1b5579aea7a23eecd80355f0/sklearn/utils/validation.py) | Official source lines 2800–3000; commit `106573971c28d82a1b5579aea7a23eecd80355f0`; BSD 3-Clause license inspected | Estimator validation can compare feature names/counts and reject inconsistencies. | Software schema consistency does not establish shared measurement meaning. The inspected development commit differs from the pinned runtime 1.8.0. | Parse named columns before any model use; explicit name-based reordering is documented. No source code copied. |

The practical inference is to add a provenance-aware preflight step, not to claim that metadata solves transportability. Exact benchmark-row overlap is a useful warning; lack of exact equality does not demonstrate independence.

## Changes made

Added `cell_validation.preflight`, explicit metadata requirements, bounded CSV input, strict numeric/label checks, and aggregate exact-overlap/duplicate/constant-feature diagnostics. It never fits a model, produces predictions, or treats a new file as validated. The example contains three invented arithmetic feature vectors and explicitly synthetic labels. Tests exercise schema errors, nonfinite data, label direction, metadata types, reordered columns, and a benchmark row falsely declared independent. Existing models, cutoffs, historical split, data fingerprints, and scientific results are unchanged.

The [practical-use contract](practical-use.md) states error behavior and operator responsibilities. README structure is standardized while retaining the prior methodology, result caveats, and references.

## Remaining work

An independently sourced cohort with compatible acquisition and outcome definitions would be a substantial separate study. Before that, prioritize explicit feature mapping, a prespecified evaluation protocol, and reviewed approximate-overlap diagnostics. [Acceptance criteria](practical-use.md#next-improvements) keep those tasks distinct from the implemented parser.

## Limits of this review

This is a bounded single-reviewer search, not a complete systematic review or formal risk-of-bias assessment. English query terms, title restrictions, relevance sorting, and a duplicate pagination result limit coverage. No independent screening or comprehensive supplement extraction was performed. Full texts were partial and only inspected sections support the table. Existing foundational references remain in [references.md](references.md), but were not counted as newly searched publications. Official source inspection supplies implementation context, not evidence of clinical readiness.
