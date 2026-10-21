# Glossary

These definitions explain the terms used in this project. Read them alongside the [methods](methods.md) and [assumptions](assumptions.md); a familiar label does not establish a result’s validity.

| Term | Meaning here |
| --- | --- |
| Cytology; fine-needle aspirate; nucleus | Cytology studies cells. A fine-needle aspirate samples material through a thin needle; nuclei are cellular compartments containing most DNA. This dataset contains image-derived numerical summaries, not images or new specimens. |
| WDBC; UCI | Wisconsin Diagnostic Breast Cancer dataset; the University of California, Irvine Machine Learning Repository that distributes it. |
| Benign; malignant; reference label | Benign means noncancerous; malignant means cancerous. Here they are the archived diagnostic categories. A reference label is the supplied outcome used for comparison, not a new diagnosis made by the code. |
| Feature; predictor; vector; outcome | A feature or predictor is an input measurement; a vector lists inputs for a record. The outcome is the supplied category the model tries to predict. |
| Radius; perimeter; area; texture | Radius summarizes center-to-boundary distances; perimeter is boundary length; area is enclosed size; texture is variation in image gray-scale values. |
| Smoothness; compactness; concavity; concave points | Smoothness summarizes local variation in radius lengths; compactness is a perimeter/area-derived descriptor; concavity and concave points summarize inward boundary regions. They are image descriptors, not molecular activities. |
| Symmetry; fractal dimension | Symmetry summarizes similarity of shape regions. Fractal dimension is a boundary-complexity descriptor, described as a coastline approximation in the source. |
| Mean; standard error; worst | Mean averages nuclear measurements. Standard error summarizes uncertainty of an estimated mean. “Worst” is the source’s mean of the three largest feature values, not a prognosis. |
| Morphology; mechanism; association | Morphology describes appearance. A mechanism explains a process; an association is a statistical relationship. A classifier based on morphology does not establish a cancer mechanism. |
| Logistic regression; L2 regularization; C | Logistic regression maps a linear score to a class probability. L2 regularization penalizes squared coefficient size; smaller C imposes stronger regularization in scikit-learn. |
| Random forest; prior baseline | A forest averages randomized decision trees. The prior baseline assigns the training positive-label fraction to every record, using no image features. |
| Scaling; pipeline; hyperparameter | Scaling here uses training means and standard deviations. A pipeline fits transformations and a model together. A hyperparameter is a setting chosen outside the model’s ordinary parameter fit. |
| Cross-validation (CV); fold; stratification | CV repeatedly partitions data for development and evaluation; a fold is one partition. Stratification preserves approximate class proportions, not population representativeness. |
| Nested CV; cross-fitting; holdout | Nested CV tunes settings inside each outer training fold. Cross-fitting predicts each development record without fitting or tuning on that record. A holdout is set aside computationally; this historical holdout was previously inspected. |
| Leakage; tuning loss; generalization | Leakage lets evaluation information influence development. Tuning loss is the criterion used to choose a setting; generalization concerns unseen data. A minimized tuning loss is not an unbiased performance estimate. |
| ROC; AUC; discrimination | Receiver operating characteristic plots true-positive against false-positive rates across cutoffs. Its area (AUC) measures ranking discrimination, not calibrated probabilities or patient benefit. |
| Sensitivity; specificity; balanced accuracy | Sensitivity is the correctly called fraction of reference positives; specificity is the correctly called fraction of negatives. Balanced accuracy averages the two. |
| False negative (FN); false positive (FP); threshold | An FN misses a reference-positive record; an FP calls a negative positive. A threshold is the probability cutoff used to assign a class. |
| Calibration; Brier score | Calibration compares predicted probabilities with observed frequencies. Brier score averages squared probability errors; it combines aspects of prediction quality and is not a pure calibration statistic. |
| Prevalence; base rate; PPV; NPV | Prevalence/base rate is the positive-label fraction in a specified setting. Positive predictive value is the positive fraction among positive calls; negative predictive value is the negative fraction among negative calls. |
| Bayes’ rule; label shift; transportability | Bayes’ rule relates conditional probabilities. Label shift changes class proportions while holding feature distributions within classes fixed. Transportability concerns whether performance carries to another setting; it is not established here. |
| Standard deviation; standard error; confidence interval | Standard deviation describes spread; standard error describes sampling uncertainty of an estimator. A confidence interval is produced by a procedure with a stated repeated-sampling coverage target, under assumptions. |
| Bootstrap; Wilson interval; pointwise | Bootstrap resamples observed records with replacement. A Wilson interval estimates a binomial fraction. Pointwise intervals concern individual bins, not simultaneous coverage of a whole calibration curve. |
| Quantile; tied value; exchangeability | Quantiles divide a sorted distribution by proportion. Tied values are equal scores. Exchangeability means treating records as interchangeable under the sampling model; site/patient dependence can violate it. |
| External validation; cohort; ascertainment | External validation evaluates a previously developed model in a separately sourced setting. A cohort is a defined collection of participants/records. Ascertainment describes how outcomes were established. |
| TRIPOD+AI; PROBAST+AI | Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis, extended for AI; and Prediction model Risk Of Bias ASsessment Tool, extended for AI. They address reporting and appraisal respectively, not automatic certification. |
| Preflight; schema; semantic compatibility | Preflight checks input before analysis. A schema defines allowable structure and types. Semantic compatibility means measurements have equivalent scientific meaning; matching field names does not prove it. |
| Provenance; fingerprint; SHA-256; digest | Provenance records origins and processing. A fingerprint/digest identifies content; SHA-256 is the hash algorithm used. A hash does not establish truthful provenance. |
| CSV; JSON; UTF-8; CLI; CI | Comma-separated values and JavaScript Object Notation are text formats; UTF-8 encodes text. Command-line interface runs commands; continuous integration automates repository checks. |
| Floating point; finite; seed | Floating-point values approximate numbers. Finite excludes infinity and not-a-number. A seed initializes reproducible pseudorandom choices. |
| MIT; CC BY 4.0 | MIT covers this code. Creative Commons Attribution 4.0 covers the dataset and requires attribution; the code license does not replace it. |
