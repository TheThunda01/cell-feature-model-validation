# Verification record

The reproduction checker verifies each prevalence report's SHA-256 against the source CSV from the same run. It then compares numeric tables with the documented tolerance. Equivalent floating-point values can be serialized differently across numerical environments, so byte hashes from different runs are not required to match. A stale within-run fingerprint or a material numerical difference still fails the check.

Version 0.2 was run locally on 2026-10-20 with Python 3.12 and the pinned dependency versions recorded in `results/metrics.json`.

- All 14 unit tests passed. They cover the preserved split, label orientation, training-only scaler fitting, nested cross-fit exclusion, cutoff penalties and tie-breaking, probability input validation, tied calibration values, Wilson boundaries, and bootstrap behavior.
- The complete study ran successfully in approximately 21 seconds in this environment.
- A separate full run reproduced `metrics.json` and all eight aggregate CSV tables within the comparator's declared tolerance (relative `1e-8`, absolute `1e-10`).
- All three PNGs were byte-identical between these two runs and were visually inspected for labels, overlap, and uncertainty presentation.
- The starting GitHub commit was `6ddd8bbdfcee1a96f88c00fc82b45ebb14225ad1`; all 19 source/output blobs matched that version before this extension began. No historical holdout records were moved.

This local verification does not certify the scientific validity of the data or clinical use. The GitHub Actions workflow includes tests, a complete rerun, and numerical output comparison, but its status for version 0.2 depends on running it after the upgrade is published.


## Version 0.3 prevalence and biology extension

The extension adds a source-linked biology/concepts guide and a conditional predictive-value calculation using existing logistic cutoffs. All **24 tests** passed, including Bayes identities, recovery of observed predictive values from confusion counts, invalid prevalence/rates, absent-class handling, and undefined predictive-value serialization. A full rerun reproduced the existing model results; the new arithmetic step requires no retraining or threshold selection. Two JSON outputs and nine aggregate CSV tables passed numerical comparison, and all four figures were byte-identical across reproductions. The prevalence figure was visually checked.

The new curves are point calculations under assumed stable sensitivity/specificity, not external validation or uncertainty intervals. Documentation and source links were reviewed against the original dataset, published methods, and official scikit-learn examples. Nothing in these checks establishes clinical utility or transportability.
