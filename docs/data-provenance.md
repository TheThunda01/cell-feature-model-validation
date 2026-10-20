# Data provenance

The workflow calls `sklearn.datasets.load_breast_cancer()` from the pinned scikit-learn package. It uses the bundled numeric feature matrix and diagnosis labels, without fetching another copy or including the source patient identifier. No raw data file is added to this repository.

The upstream source is Wolberg, W., Mangasarian, O., Street, N., & Street, W. (1993), *Breast Cancer Wisconsin (Diagnostic)*, UCI Machine Learning Repository, [doi:10.24432/C5DW2B](https://doi.org/10.24432/C5DW2B). UCI currently distributes it under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Source and license pages were checked on 2026-10-20. The source describes features computed from digitized fine-needle aspirate images. It should not be described as sequencing or gene-expression data.

Processing in this project is limited to reversing the numeric label to make malignant positive, splitting records, and fitting training-only scaling. The data fingerprint in `results/metrics.json` hashes the full numeric feature matrix as little-endian float64 bytes followed by the recoded labels as little-endian int64 bytes, both in original row order. The hash identifies this input representation; it is not proof of biological accuracy.

The outputs contain aggregate statistics only. This minimizes unnecessary republication, but the public source and its reuse conditions still apply. Dataset availability does not establish representativeness for other populations or clinical workflows.
