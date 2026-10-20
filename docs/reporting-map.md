# Reporting and risk-of-bias questions

TRIPOD+AI (2024) addresses transparent prediction-model reporting. PROBAST+AI (2025) addresses quality, risk of bias, and applicability. They serve different purposes. This short map borrows their concerns as prompts for an educational project; it does not reproduce their complete checklists or claim a formal assessment.

| Question | Evidence in this repository | What remains unresolved |
| --- | --- | --- |
| What is the intended task? | README and analysis plan identify a methods demonstration using cell-image features. | There is no defined clinical deployment setting or action. |
| Which data and outcome were used? | Provenance note, source citation, label coding, input fingerprint, and counts. | The bundled copy is insufficient for a detailed audit of selection, current representativeness, or measurement practice. |
| Can development be separated from evaluation? | Preserved holdout, nested-CV code, fold fingerprints, and isolation tests. | The analyst previously inspected holdout results; human adaptive reuse cannot be undone by code. |
| Can the model and tuning be reproduced? | Pinned dependencies, parameter grids, seeds, fold-level choices, code, and CI. | Small platform-dependent numerical differences and future dependency availability are possible. |
| Are performance and uncertainty reported? | Discrimination, probability error, cutoff-dependent metrics, scoped bootstrap intervals, and calibration-bin counts. | No external validation; no uncertainty analysis that refits the entire development process. |
| Are thresholds and their rationale clear? | A declared candidate grid and illustrative penalty ratios, using development cross-fitted predictions only. | The penalty values are not patient preferences or clinical consequences; threshold tuning is not nested inside each outer evaluation. |
| Is applicability addressed? | Explicit cautions about data reuse, site changes, population differences, and absence of deployment claims. | No meaningful site, subgroup, temporal, workflow, or prospective impact assessment. |
| What can be reused? | Code license, dataset attribution, contribution instructions, reproducible aggregate output. | Open availability does not establish validity, safety, or utility in a new setting. |

See Collins et al., [TRIPOD+AI](https://doi.org/10.1136/bmj-2023-078378), and Moons et al., [PROBAST+AI](https://doi.org/10.1136/bmj-2024-082505), for the actual statements and their supporting materials. A genuine clinical prediction study would need a task-specific protocol and a complete, appropriately conducted assessment.
