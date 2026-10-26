# The biology and concepts behind this example

Terminology: [glossary](glossary.md). Scientific and operational choices: [assumptions](assumptions.md).

This project connects a small cytology dataset with a larger question: what does good evidence for a prediction model look like? The distinction between the sampled material, the archived outcome label, and the model's output is essential to interpreting the results.

## What was sampled?

The Wisconsin Diagnostic Breast Cancer dataset describes cell nuclei in digitized images of fine-needle aspirates (material sampled using a thin needle) from breast masses. Its creators used image processing to summarize nuclear size, shape, and texture. The [original feature-extraction work](https://doi.org/10.1117/12.148698) explains this measurement approach; [UCI](https://doi.org/10.24432/C5DW2B) provides the archived data and attribution.

The analysis starts with the numerical table, where each record summarizes an image rather than a single nucleus. It does not examine a new specimen, process a microscope image, or inspect tissue architecture. The code therefore cannot revisit the original boundary selections or independently assess a specimen's diagnostic interpretation.

Ten measured properties were summarized in three ways, producing 30 features. They include radius, perimeter, area, smoothness, compactness, concavity, concave points, symmetry, texture, and a boundary-complexity measure called fractal dimension. In the [bundled dataset documentation](https://scikit-learn.org/1.8/datasets/toy_dataset.html#breast-cancer-dataset), each property has a mean, a standard-error summary, and a “worst” summary based on the three largest values. “Worst” is a historical feature name, not a prognosis. The stored standard-error features are not uncertainty intervals for this model's predictions.

## Morphology is a measurement, not a mechanism

Morphology describes appearance and geometry. Texture here summarizes image intensity variation; it is not a gene-expression measurement. Several size and shape features are related, so 30 columns should not be mistaken for 30 independent biological processes. A model can exploit correlations among them without explaining why a mass developed or how it will behave.

Sample preparation, image acquisition, selection of nuclei, and boundary measurement can affect the recorded features. This repository does not measure the effects of changing those steps. It also contains no mutation, transcriptomic, treatment-response, or longitudinal outcome data. A coefficient or tree split therefore cannot establish a causal cancer pathway.

## What do the labels mean?

The archive supplies a binary diagnosis field: benign or malignant. We use malignant as the positive class and explicitly reverse scikit-learn's original numeric encoding. These are reference labels supplied with this historical collection, not diagnoses made or independently verified by this code.

The task is to reproduce those labels from the archived features. It does not predict a person's future cancer risk, stage, survival, or treatment benefit. It also does not establish how ambiguous specimens, uncommon subtypes, or a different referral population should be handled. The dataset's label proportions are properties of this collection, not estimates of prevalence in a general screening population.

## Ranking, probabilities, and decisions answer different questions

**Discrimination** asks whether records with a malignant label tend to receive higher model scores than records with a benign label. The area under the receiver operating characteristic curve (ROC AUC) summarizes that ranking. A high value can coexist with inaccurate probability estimates.

**Calibration** asks whether predicted probabilities agree with observed frequencies. For example, a group assigned roughly 20% probability should have roughly a 20% positive fraction under the relevant conditions. The small bin summaries here are descriptive, with pointwise uncertainty. [Van Calster et al. (2019)](https://doi.org/10.1186/s12916-019-1466-7) explain why calibration deserves separate attention.

A **threshold** converts a continuous score into a class call. Lowering it usually trades some missed positives for additional false positives. Our error penalties are teaching choices rather than clinical valuations. Predictive values then ask a different question: among positive calls, what fraction has the positive reference label (positive predictive value, PPV), and among negative calls, what fraction has the negative label (negative predictive value, NPV)?

## Why base rates matter

The [prevalence exercise](prevalence-sensitivity.md) uses Bayes' rule to calculate how PPV and NPV change with the assumed positive-label fraction. Sensitivity and specificity stay fixed at each existing cutoff. These are conditional calculations, not newly observed outcomes.

This resembles one consequence of **label shift**, where class proportions change while feature distributions within each class stay stable. [Lipton et al. (2018)](https://proceedings.mlr.press/v80/lipton18a.html) formalize that assumption. We do not detect label shift or estimate a target population's prevalence. More importantly, fixed operating rates need not hold when case mix or measurement changes. [Murad et al. (2023)](https://doi.org/10.1503/cmaj.221802) found associations between prevalence and estimated sensitivity/specificity across diagnostic studies; their analysis cautions against assuming universal transportability.

## What validation can and cannot establish here

Repeated nested cross-validation separates parameter selection from assessment inside the development partition. It helps expose variability under that sampling scheme. It does not recreate a different laboratory, a prospective study, or an independent population.

The 114-record holdout was already inspected in version 0.1. We preserve it and exclude it from computational development, but its later results are descriptive replication rather than fresh blind evidence. Its small size also limits precision. The prevalence curves add no new patients and propagate neither operating-rate uncertainty nor population differences. Their purpose is to make assumptions visible. They supply no clinical recommendation, evidence of patient benefit, or permission to generalize beyond the studied setting.
