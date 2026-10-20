# The biology and concepts behind this example

This project connects a small cytology dataset with a larger question: what does good evidence for a prediction model look like? The distinction between the sampled material, the archived outcome label, and the model's output is essential to interpreting the results.

## What was sampled?

The Wisconsin Diagnostic Breast Cancer dataset describes cell nuclei in digitized images of fine-needle aspirates from breast masses. Its creators used image processing to summarize nuclear size, shape, and texture. The [original feature-extraction work](https://doi.org/10.1117/12.148698) explains this measurement approach; [UCI](https://doi.org/10.24432/C5DW2B) provides the archived data and attribution.

Our analysis begins with the resulting numerical table. It does not examine a new specimen, process a microscope image, or inspect tissue architecture. A record is an image-derived summary, not a single nucleus. The distinction also limits what can be checked: the code cannot revisit the original boundary selections or independently assess a specimen's diagnostic interpretation.

Ten measured properties were summarized in three ways, producing 30 features. They include radius, perimeter, area, smoothness, compactness, concavity, concave points, symmetry, texture, and a boundary-complexity measure called fractal dimension. In the [bundled dataset documentation](https://scikit-learn.org/stable/datasets/toy_dataset.html#breast-cancer-dataset), each property has a mean, a standard-error summary, and a “worst” summary based on the three largest values. “Worst” is a historical feature name, not a prognosis. The stored standard-error features are not uncertainty intervals for this model's predictions.

## Morphology is a measurement, not a mechanism

Morphology describes appearance and geometry. Texture here summarizes image intensity variation; it is not a gene-expression measurement. Several size and shape features are related, so 30 columns should not be mistaken for 30 independent biological processes. A model can exploit correlations among them without explaining why a mass developed or how it will behave.

Preparation, image acquisition, selection of nuclei, and boundary measurement are parts of the measurement process. A change in those steps could change feature distributions; this repository does not measure those effects. It also contains no mutation, transcriptomic, treatment-response, or longitudinal outcome data. Interpreting a coefficient or tree split as a causal cancer pathway would go beyond what was observed.

## What do the labels mean?

The archive supplies a binary diagnosis field: benign or malignant. We use malignant as the positive class and explicitly reverse scikit-learn's original numeric encoding. These are reference labels supplied with this historical collection, not diagnoses made or independently verified by this code.

The task is to reproduce those labels from the archived features. It does not predict a person's future cancer risk, stage, survival, or treatment benefit. It also does not establish how ambiguous specimens, uncommon subtypes, or a different referral population should be handled. The dataset's label proportions are properties of this collection, not estimates of prevalence in a general screening population.

## Ranking, probabilities, and decisions answer different questions

**Discrimination** asks whether records with a malignant label tend to receive higher model scores than records with a benign label. ROC AUC summarizes that ranking. A high value can coexist with inaccurate probability estimates.

**Calibration** asks whether predicted probabilities agree with observed frequencies. For example, a group assigned roughly 20% probability should have roughly a 20% positive fraction under the relevant conditions. The small bin summaries here are descriptive, with pointwise uncertainty. [Van Calster and colleagues](https://doi.org/10.1186/s12916-019-1466-7) explain why calibration deserves separate attention.

A **threshold** converts a continuous score into a class call. Lowering it usually trades some missed positives for additional false positives. Our error penalties are teaching choices rather than clinical valuations. Predictive values then ask a different question: among positive calls, what fraction has the positive reference label (PPV), and among negative calls, what fraction has the negative label (NPV)?

## Why base rates matter

The new [prevalence exercise](prevalence-sensitivity.md) changes an assumed positive-label fraction while holding sensitivity and specificity fixed at each existing cutoff. Bayes' rule then changes PPV and NPV. These are conditional calculations, not newly observed outcomes.

This resembles one consequence of **label shift**, where class proportions change while feature distributions within each class stay stable. [Lipton and colleagues](https://proceedings.mlr.press/v80/lipton18a.html) formalize that assumption. We do not detect label shift or estimate a target population's prevalence. More importantly, fixed operating rates need not hold when case mix or measurement changes. [Murad and colleagues](https://doi.org/10.1503/cmaj.221802) found associations between prevalence and estimated sensitivity/specificity across diagnostic studies; their analysis cautions against assuming universal transportability.

## What validation can and cannot establish here

Repeated nested cross-validation separates parameter selection from assessment inside the development partition. It helps expose variability under that sampling scheme. It does not recreate a different laboratory, a prospective study, or an independent population.

The 114-record holdout was already inspected in version 0.1. We preserve it and exclude it from computational development, but its later results are descriptive replication rather than fresh blind evidence. Its small size also limits precision. The prevalence curves add no new patients and propagate neither operating-rate uncertainty nor population differences. Their purpose is to make assumptions visible. They supply no clinical recommendation, evidence of patient benefit, or permission to generalize beyond the studied setting.
