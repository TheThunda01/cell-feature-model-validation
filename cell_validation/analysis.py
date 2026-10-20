"""Training-only model selection followed by one held-out evaluation.

The dataset contains cell-image summaries, not gene-expression measurements.
No fitted model or per-record predictions are saved by this teaching workflow.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.datasets import load_breast_cancer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED = 20261020
C_VALUES = (0.01, 0.1, 1.0, 10.0)


def load_data():
    """Return numeric features and a documented malignant-positive label."""
    source = load_breast_cancer()
    x = np.asarray(source.data, dtype=np.float64)
    # sklearn uses 0=malignant, 1=benign. This example explicitly reverses it.
    y = (source.target == 0).astype(np.int64)
    if x.shape != (569, 30) or len(y) != 569 or not np.isfinite(x).all():
        raise ValueError("Unexpected dataset shape or nonfinite feature value")
    return x, y, list(map(str, source.feature_names))


def split_indices(y, seed=SEED):
    """Make the held-out split before fitting any preprocessing operation."""
    return train_test_split(
        np.arange(len(y)), test_size=0.2, random_state=seed, stratify=y
    )


def make_search(seed=SEED):
    """Keep the scaler inside each training fold, not outside the search."""
    pipeline = Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(solver="lbfgs", max_iter=5000)),
    ])
    return GridSearchCV(
        pipeline,
        {"model__C": list(C_VALUES)},
        scoring="roc_auc",
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=seed),
        refit=True,
        n_jobs=1,
        error_score="raise",
    )


def metrics(y, probability):
    y = np.asarray(y)
    p = np.asarray(probability)
    if y.ndim != 1 or p.shape != y.shape:
        raise ValueError("Labels and probabilities must be equal-length vectors")
    if set(np.unique(y)) != {0, 1}:
        raise ValueError("Evaluation requires both binary classes")
    if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("Probabilities must be finite and between 0 and 1")
    predicted = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    return {
        "roc_auc": float(roc_auc_score(y, p)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predicted)),
        "brier_score": float(brier_score_loss(y, p)),
        "true_negative": int(tn), "false_positive": int(fp),
        "false_negative": int(fn), "true_positive": int(tp),
    }


def conditional_auc_interval(y, p, seed=SEED, repeats=2000):
    """Percentile bootstrap over test rows, conditional on this fitted model.

    This excludes variation from training, tuning, sites, and acquisition.
    Resamples missing either class have undefined AUC and are discarded.
    """
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(repeats):
        sample = rng.integers(0, len(y), size=len(y))
        if len(np.unique(y[sample])) == 2:
            values.append(roc_auc_score(y[sample], p[sample]))
    if not values:
        raise ValueError("No bootstrap resample contained both classes")
    low, high = np.quantile(values, [0.025, 0.975])
    return {"lower": float(low), "upper": float(high),
            "valid_resamples": len(values), "requested_resamples": repeats}


def fingerprint(x, y):
    """Hash canonical little-endian arrays to identify the bundled data copy."""
    h = hashlib.sha256()
    h.update(np.asarray(x, dtype="<f8").tobytes(order="C"))
    h.update(np.asarray(y, dtype="<i8").tobytes(order="C"))
    return h.hexdigest()


def run(output_dir: Path):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    x, y, names = load_data()
    train, test = split_indices(y)
    search = make_search()
    search.fit(x[train], y[train])
    # Both models are specified before viewing the held-out predictions.
    baseline = DummyClassifier(strategy="prior")
    baseline.fit(x[train], y[train])
    fitted = {"logistic_regression": search.best_estimator_, "prior_baseline": baseline}
    probabilities = {name: model.predict_proba(x[test])[:, 1]
                     for name, model in fitted.items()}
    model_results = {name: metrics(y[test], p) for name, p in probabilities.items()}
    interval = conditional_auc_interval(y[test], probabilities["logistic_regression"])
    report = {
        "project_version": "0.1.0", "seed": SEED,
        "purpose": "Educational internal holdout benchmark; not clinical validation",
        "dataset": "Wisconsin Diagnostic Breast Cancer, sklearn bundled copy",
        "source_doi": "10.24432/C5DW2B",
        "data_sha256": fingerprint(x, y),
        "n_samples": len(y), "n_features": len(names),
        "n_train": len(train), "n_test": len(test),
        "positive_label": "malignant", "threshold": 0.5,
        "training_malignant_count": int(y[train].sum()),
        "test_malignant_count": int(y[test].sum()),
        "selected_C": float(search.best_params_["model__C"]),
        "selection_metric": "five-fold training-only ROC AUC",
        "models": model_results,
        "logistic_conditional_test_auc_95_percentile_interval": interval,
        "interval_scope": "Test-row resampling only; excludes training and site uncertainty",
        "versions": {name: importlib.metadata.version(name) for name in
                     ("numpy", "scipy", "scikit-learn", "matplotlib")},
    }
    (output_dir / "metrics.json").write_text(json.dumps(report, indent=2) + "\n")
    with (output_dir / "model_comparison.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["model"] + list(next(iter(model_results.values()))))
        writer.writeheader()
        for name, result in model_results.items():
            writer.writerow({"model": name, **result})
    with (output_dir / "training_cv.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["C", "mean_training_cv_auc", "sd_training_cv_auc"])
        for c, mean, sd in zip(search.cv_results_["param_model__C"],
                               search.cv_results_["mean_test_score"],
                               search.cv_results_["std_test_score"]):
            writer.writerow([c, mean, sd])
    # Expose bin sizes alongside the calibration picture. Bins use the same
    # quantile-edge convention as sklearn.calibration.calibration_curve.
    p = probabilities["logistic_regression"]
    edges = np.percentile(p, np.linspace(0, 100, 6))
    bin_ids = np.searchsorted(edges[1:-1], p)
    with (output_dir / "calibration_bins.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["bin", "n", "mean_predicted_probability", "observed_malignant_fraction"])
        for b in range(5):
            selected = bin_ids == b
            if selected.any():
                writer.writerow([b + 1, int(selected.sum()), float(p[selected].mean()),
                                 float(y[test][selected].mean())])
    draw_diagnostics(y[test], probabilities, output_dir / "diagnostics.png")
    return report


def draw_diagnostics(y, probabilities, target):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.dpi": 160})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), constrained_layout=True)
    colors = {"logistic_regression": "#126870", "prior_baseline": "#9c4f21"}
    for name, probability in probabilities.items():
        fpr, tpr, _ = roc_curve(y, probability)
        label = name.replace("_", " ")
        axes[0].plot(fpr, tpr, label=label, color=colors[name], linewidth=2)
    axes[0].plot([0, 1], [0, 1], color="#aaaaaa", linestyle="--", linewidth=1)
    axes[0].set(xlabel="False-positive rate", ylabel="True-positive rate",
                title="Internal held-out discrimination", xlim=(0, 1), ylim=(0, 1.03))
    axes[0].legend(loc="lower right", fontsize=8)
    observed, predicted = calibration_curve(y, probabilities["logistic_regression"],
                                            n_bins=5, strategy="quantile")
    axes[1].plot([0, 1], [0, 1], color="#aaaaaa", linestyle="--", linewidth=1)
    axes[1].plot(predicted, observed, marker="o", color=colors["logistic_regression"])
    axes[1].set(xlabel="Mean predicted malignant probability", ylabel="Observed malignant fraction",
                title="Descriptive calibration (5 quantile bins)",
                xlim=(0, 1), ylim=(0, 1.03))
    fig.suptitle(f"Cell-feature benchmark · {len(y)} held-out records", fontsize=14)
    fig.savefig(target, metadata={"Software": "cell-feature-model-validation 0.1.0"})
    plt.close(fig)
