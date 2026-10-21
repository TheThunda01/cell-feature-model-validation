# References and how they are used

Checked on **20 October 2026**. The [reference audit](reference-audit.json) records access and metadata status for every source below. An abstract check is not a full-text appraisal. These sources support background or method choices; none independently validates this repository’s results. See the [glossary](glossary.md) and [assumptions](assumptions.md) for interpretation.

## Research and methods

- Varma, S., & Simon, R. (2006). Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics, 7*, 91. [doi:10.1186/1471-2105-7-91](https://doi.org/10.1186/1471-2105-7-91). [PMID: 16504092](https://pubmed.ncbi.nlm.nih.gov/16504092/). Using the same CV results for model selection and error estimation can cause optimistic error estimates.

- Collins, G. S., et al. (2024). TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ, 385*, e078378. [doi:10.1136/bmj-2023-078378](https://doi.org/10.1136/bmj-2023-078378). [PMID: 38626948](https://pubmed.ncbi.nlm.nih.gov/38626948/). Transparent reporting of data roles, predictors, outcomes and model evaluation. Reporting guideline, not certification of this project; original article distinguished from affiliation correction.

- Moons, K. G. M., et al. (2025). PROBAST+AI: an updated quality, risk of bias, and applicability assessment tool for prediction models using regression or artificial intelligence methods. *BMJ, 388*, e082505. [doi:10.1136/bmj-2024-082505](https://doi.org/10.1136/bmj-2024-082505). [PMID: 40127903](https://pubmed.ncbi.nlm.nih.gov/40127903/). Appraising participant, predictor, outcome and analysis domains and applicability. Formal PROBAST+AI appraisal not completed.

- Van Calster, B., et al. (2019). Calibration: the Achilles heel of predictive analytics. *BMC Medicine, 17*(1), 230. [doi:10.1186/s12916-019-1466-7](https://doi.org/10.1186/s12916-019-1466-7). [PMID: 31842878](https://pubmed.ncbi.nlm.nih.gov/31842878/). Discrimination and calibration differ, and calibration assessment matters. Methods guidance; not evidence that this benchmark is calibrated in other settings.

- Lange, K., & Brunner, E. (2013). Analysis of Predictive Values Based on Individual Risk Factors in Multi-Modality Trials. *Diagnostics, 3*(1), 192–209. [doi:10.3390/diagnostics3010192](https://doi.org/10.3390/diagnostics3010192). [PMID: 26835674](https://pubmed.ncbi.nlm.nih.gov/26835674/). Bayes equations connect sensitivity, specificity, prevalence and predictive values. The repository does not implement the paper’s full modality/trial methods.

- Murad, M. H., et al. (2023). The association of sensitivity and specificity with disease prevalence: analysis of 6909 studies of diagnostic test accuracy. *CMAJ : Canadian Medical Association journal = journal de l'Association medicale canadienne, 195*(27), E925–E931. [doi:10.1503/cmaj.221802](https://doi.org/10.1503/cmaj.221802). [PMID: 37460126](https://pubmed.ncbi.nlm.nih.gov/37460126/). Sensitivity/specificity estimates were associated with prevalence across diagnostic studies. Meta-epidemiological association is not a causal effect of prevalence alone and is not quantified for this classifier.

- Luijken, K., Song, J., & Groenwold, R. H. H. (2022). Quantitative prediction error analysis to investigate predictive performance under predictor measurement heterogeneity at model implementation. *Diagnostic and Prognostic Research, 6*(1), 7. [doi:10.1186/s41512-022-00121-1](https://doi.org/10.1186/s41512-022-00121-1). [PMID: 35387683](https://pubmed.ncbi.nlm.nih.gov/35387683/). Predictor measurement differences can affect implementation performance. Time-to-event simulation/applied setting differs from this classifier.

- John, L. H., et al. (2022). External validation of existing dementia prediction models on observational health data. *BMC Medical Research Methodology, 22*(1), 311. [doi:10.1186/s12874-022-01793-5](https://doi.org/10.1186/s12874-022-01793-5). [PMID: 36471238](https://pubmed.ncbi.nlm.nih.gov/36471238/). Recovering predictors and model specifications can obstruct external validation. Dementia models differ from the breast-feature dataset; no performance transferred.

- Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32. [doi:10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324). Random-forest model-family background. Publisher abstract and bibliographic page inspected; full text is subscription access.

- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association, 22*(158), 209–212. [doi:10.1080/01621459.1927.10502953](https://doi.org/10.1080/01621459.1927.10502953). Historical source for score intervals; equation implementation checked separately in code. Publisher returned 403. JSTOR verified title, author, volume, issue and pages; full article was not inspected in this pass.

- Street, W. N., Wolberg, W. H., & Mangasarian, O. L. (1993). Nuclear feature extraction for breast tumor diagnosis. *Proceedings of SPIE, 1905*, 861–870. [doi:10.1117/12.148698](https://doi.org/10.1117/12.148698). Historical feature-extraction source identified by UCI and the bundled dataset description. Publisher search metadata and official dataset attribution inspected; full publisher page timed out. Measurement descriptions rely on official dataset documentation rather than uninspected article passages.

- Lipton, Z., Wang, Y.-X., & Smola, A. (2018). Detecting and Correcting for Label Shift with Black Box Predictors. *Proceedings of Machine Learning Research, 80*, 3122–3130. [Source](https://proceedings.mlr.press/v80/lipton18a.html). Label shift holds feature distributions within classes fixed while class proportions change. Publisher abstract and full citation inspected. Its estimation/correction methods are not implemented here.

## Data, software, standards, and reuse

- Wolberg, W., Mangasarian, O., Street, N., & Street, W. (1993). *Breast Cancer Wisconsin (Diagnostic)* [Dataset]. UCI Machine Learning Repository. [Source](https://doi.org/10.24432/C5DW2B). Dataset origin, nuclear-image measurement definitions, 569 records, 30 features, binary diagnoses and CC BY 4.0 terms. Citation year is 1993; UCI separately records donation on 1995-10-31. Neither is a new observation date.

- scikit-learn developers. (n.d.). *datasets.load_breast_cancer* [Official documentation], 1.8.0. [Source](https://scikit-learn.org/1.8/modules/generated/sklearn.datasets.load_breast_cancer.html). Bundled data or estimator behavior corresponding to the pinned runtime.

- scikit-learn developers. (n.d.). *model_selection.GridSearchCV* [Official documentation], 1.8.0. [Source](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.GridSearchCV.html). Bundled data or estimator behavior corresponding to the pinned runtime.

- scikit-learn developers. (n.d.). *ensemble.RandomForestClassifier* [Official documentation], 1.8.0. [Source](https://scikit-learn.org/1.8/modules/generated/sklearn.ensemble.RandomForestClassifier.html). Bundled data or estimator behavior corresponding to the pinned runtime.

- scikit-learn developers. (n.d.). *Common pitfalls: data leakage* [Official documentation], 1.8. [Source](https://scikit-learn.org/1.8/common_pitfalls.html#data-leakage). Preprocessing and tuning need appropriate separation from evaluation.

- scikit-learn developers. (n.d.). *Breast cancer dataset description* [Official documentation], 1.8.0; installed DESCR inspected. [Source](https://scikit-learn.org/1.8/datasets/toy_dataset.html#breast-cancer-dataset). Mean, standard-error and worst nuclear feature summaries; target coding.

- scikit-learn developers. (n.d.). *Input validation source* [Software], 106573971c28d82a1b5579aea7a23eecd80355f0. [Source](https://github.com/scikit-learn/scikit-learn/blob/106573971c28d82a1b5579aea7a23eecd80355f0/sklearn/utils/validation.py). Feature name/count consistency checks are distinct from measurement-semantic compatibility. Relevant source lines inspected through GitHub; development commit differs from runtime 1.8.0. No code copied.

- scikit-learn developers. (n.d.). *Probability Calibration curves* [Software], main read 2026-10-20; blob 7db1e41ccbc37532f28c9d7fe0890a3841b8f6d3. [Source](https://github.com/scikit-learn/scikit-learn/blob/main/examples/calibration/plot_calibration_curve.py). Separate inspection of score calibration and prediction behavior. Moving main-branch example used for context, not copied or reproduced.

- scikit-learn developers. (n.d.). *Cost-sensitive learning example* [Software], main read 2026-10-20; blob 57d6cbe7eb2e6be03672397060bc372c3b74f025. [Source](https://github.com/scikit-learn/scikit-learn/blob/main/examples/model_selection/plot_cost_sensitive_learning.py). Threshold decisions and score quality answer different questions. Uses TunedThresholdClassifierCV; this repository uses an independent small-grid study.

- Python Software Foundation. (n.d.). *CSV File Reading and Writing* [Official documentation], 3.12.15. [Source](https://docs.python.org/3.12/library/csv.html). Strict CSV parser behavior and text/row handling.

- Creative Commons. (n.d.). *Creative Commons Attribution 4.0 International* [Official documentation]. [Source](https://creativecommons.org/licenses/by/4.0/). UCI dataset attribution/reuse terms. License is specified on the inspected UCI dataset page; no legal determination beyond preserving those terms.
