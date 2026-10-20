"""Inspect model-selection variability without borrowing from the held-out split.

The input consists of cell-image summaries, not molecular measurements.
The historical holdout has already been observed, so its results are descriptive.
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
from sklearn.datasets import load_breast_cancer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED = 20261020
C_VALUES = (0.01, 0.1, 1.0, 10.0)
MODELS = ("logistic_regression", "random_forest", "prior_baseline")
THRESHOLDS = np.round(np.linspace(0.05, 0.95, 19), 2)
COST_RATIOS = (1.0, 2.0, 5.0)  # illustrative false-negative:false-positive penalties
EXPECTED_HOLDOUT_HASH = "e2e7df67893e740c7f9279f5d40a05d00e985e5b1042f5238e686969e4f86385"
COLORS = {"logistic_regression": "#126870", "random_forest": "#7d4685", "prior_baseline": "#9c4f21"}


def load_data():
    source = load_breast_cancer()
    x = np.asarray(source.data, dtype=np.float64)
    y = (source.target == 0).astype(np.int64)  # malignant is explicitly positive
    if x.shape != (569, 30) or len(y) != 569 or not np.isfinite(x).all():
        raise ValueError("Unexpected dataset shape or nonfinite feature value")
    return x, y, list(map(str, source.feature_names))


def index_hash(indices):
    return hashlib.sha256(np.asarray(indices, dtype="<i8").tobytes()).hexdigest()


def split_indices(y, seed=SEED):
    return train_test_split(np.arange(len(y)), test_size=0.2, random_state=seed, stratify=y)


def make_search(kind="logistic_regression", seed=SEED, inner_splits=5):
    if kind == "logistic_regression":
        pipeline = Pipeline([("scale", StandardScaler()),
                             ("model", LogisticRegression(solver="lbfgs", max_iter=5000))])
        grid = {"model__C": list(C_VALUES)}
    elif kind == "random_forest":
        pipeline = Pipeline([("scale", "passthrough"), ("model", RandomForestClassifier(
            n_estimators=100, max_features="sqrt", random_state=seed, n_jobs=1))])
        grid = {"model__max_depth": [3, None], "model__min_samples_leaf": [2, 8]}
    else:
        raise ValueError(f"Unknown model: {kind}")
    return GridSearchCV(pipeline, grid, scoring="roc_auc", cv=StratifiedKFold(
        n_splits=inner_splits, shuffle=True, random_state=seed), refit=True,
        n_jobs=1, error_score="raise")


def checked_vectors(y, probability):
    y, p = np.asarray(y), np.asarray(probability)
    if y.ndim != 1 or p.shape != y.shape or len(y) == 0:
        raise ValueError("Labels and probabilities must be equal-length nonempty vectors")
    if set(np.unique(y)) != {0, 1}:
        raise ValueError("Evaluation requires both binary classes")
    if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("Probabilities must be finite and between 0 and 1")
    return y, p


def metrics(y, probability, threshold=0.5):
    y, p = checked_vectors(y, probability)
    if not np.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("Threshold must be finite and between 0 and 1")
    pred = (p >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {"roc_auc": float(roc_auc_score(y, p)),
            "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
            "brier_score": float(brier_score_loss(y, p)),
            "sensitivity": float(tp / (tp + fn)), "specificity": float(tn / (tn + fp)),
            "true_negative": int(tn), "false_positive": int(fp),
            "false_negative": int(fn), "true_positive": int(tp)}


def threshold_study(y, probability, cost_ratio, thresholds=THRESHOLDS):
    """Select a threshold from training cross-fitted predictions only.

    The minimized quantity is a tuning loss, not an independent performance estimate.
    """
    y, p = checked_vectors(y, probability)
    if not np.isfinite(cost_ratio) or cost_ratio <= 0:
        raise ValueError("Cost ratio must be finite and positive")
    rows = []
    for threshold in thresholds:
        m = metrics(y, p, float(threshold))
        rows.append({"threshold": float(threshold), "cost_ratio": float(cost_ratio),
                     "training_oof_tuning_loss": float((cost_ratio * m["false_negative"] + m["false_positive"]) / len(y)),
                     "sensitivity": m["sensitivity"], "specificity": m["specificity"],
                     "false_negative": m["false_negative"], "false_positive": m["false_positive"]})
    if not rows:
        raise ValueError("At least one threshold is required")
    # Resolve equal losses deterministically: closest to 0.5, then larger threshold.
    selected = min(rows, key=lambda r: (r["training_oof_tuning_loss"],
                                       round(abs(r["threshold"] - 0.5), 12), -r["threshold"]))
    return selected, rows


def nested_comparison(x, y, outer_splits=4, repeats=2, inner_splits=3):
    """Return repeated nested-CV records and cross-fitted development predictions.

    Call with development data only. Every prediction excludes that row from
    scaling, parameter selection and model fitting. Repeated folds are correlated.
    """
    x, y = np.asarray(x), np.asarray(y)
    oof = {name: np.full((repeats, len(y)), np.nan) for name in MODELS}
    coverage = np.zeros((repeats, len(y)), dtype=int)
    records = []
    for repeat in range(repeats):
        splitter = StratifiedKFold(n_splits=outer_splits, shuffle=True, random_state=SEED + repeat)
        for fold, (fit_idx, eval_idx) in enumerate(splitter.split(x, y), start=1):
            if np.intersect1d(fit_idx, eval_idx).size:
                raise RuntimeError("Outer training/evaluation overlap")
            coverage[repeat, eval_idx] += 1
            for name in MODELS:
                if name == "prior_baseline":
                    model = DummyClassifier(strategy="prior").fit(x[fit_idx], y[fit_idx])
                    parameters = {}
                else:
                    search = make_search(name, seed=SEED + repeat * 100 + fold, inner_splits=inner_splits)
                    search.fit(x[fit_idx], y[fit_idx])
                    model, parameters = search.best_estimator_, search.best_params_
                probability = model.predict_proba(x[eval_idx])[:, 1]
                oof[name][repeat, eval_idx] = probability
                records.append({"repeat": repeat + 1, "fold": fold, "model": name,
                                "n_fit": len(fit_idx), "n_evaluate": len(eval_idx),
                                "fit_indices_sha256": index_hash(fit_idx),
                                "evaluate_indices_sha256": index_hash(eval_idx),
                                "selected_parameters": json.dumps(parameters, sort_keys=True),
                                **metrics(y[eval_idx], probability)})
    if not np.all(coverage == 1) or any(not np.isfinite(p).all() for p in oof.values()):
        raise RuntimeError("Every development record must receive one prediction per repeat")
    return records, {name: values.mean(axis=0) for name, values in oof.items()}


def summarize_folds(records):
    summary = []
    for name in MODELS:
        rows = [r for r in records if r["model"] == name]
        for metric in ("roc_auc", "balanced_accuracy", "brier_score"):
            vals = np.array([r[metric] for r in rows])
            summary.append({"model": name, "metric": metric, "n_correlated_folds": len(vals),
                            "mean": float(vals.mean()), "sd_descriptive": float(vals.std(ddof=1)),
                            "minimum": float(vals.min()), "maximum": float(vals.max())})
    return summary


def bootstrap_intervals(y, probability, threshold=0.5, seed=SEED, repeats=1000):
    """Ordinary test-row bootstrap, conditional on the fitted pipeline and cutoff."""
    y, p = checked_vectors(y, probability)
    if repeats < 1:
        raise ValueError("Bootstrap repeats must be positive")
    rng = np.random.default_rng(seed)
    values = {k: [] for k in ("roc_auc", "balanced_accuracy", "brier_score")}
    for _ in range(repeats):
        idx = rng.integers(0, len(y), size=len(y))
        if len(np.unique(y[idx])) != 2:
            continue
        result = metrics(y[idx], p[idx], threshold)
        for name in values:
            values[name].append(result[name])
    if not values["roc_auc"]:
        raise ValueError("No bootstrap resample contained both classes")
    return {name: {"lower": float(np.quantile(v, 0.025)),
                   "upper": float(np.quantile(v, 0.975)), "valid_resamples": len(v),
                   "requested_resamples": repeats} for name, v in values.items()}


def conditional_auc_interval(y, p, seed=SEED, repeats=2000):
    # Keep the version-0.1 API available for a narrow reproducibility check.
    return bootstrap_intervals(y, p, seed=seed, repeats=repeats)["roc_auc"]


def wilson_interval(successes, total):
    if total < 1 or successes < 0 or successes > total:
        raise ValueError("Wilson interval requires 0 <= successes <= total and total > 0")
    z = 1.959963984540054
    p = successes / total
    scale = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / scale
    width = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / scale
    return (0.0 if successes == 0 else float(centre - width),
            1.0 if successes == total else float(centre + width))


def calibration_bins(y, probability, n_bins=5):
    y, p = checked_vectors(y, probability)
    if n_bins < 1:
        raise ValueError("n_bins must be positive")
    edges = np.quantile(p, np.linspace(0, 1, n_bins + 1))
    ids = np.searchsorted(edges[1:-1], p)
    rows = []
    for b in range(n_bins):
        keep = ids == b
        if keep.any():
            n, k = int(keep.sum()), int(y[keep].sum())
            lo, hi = wilson_interval(k, n)
            rows.append({"bin": b + 1, "n": n, "malignant_count": k,
                         "mean_predicted_probability": float(p[keep].mean()),
                         "observed_malignant_fraction": k / n,
                         "observed_fraction_wilson_lower": lo,
                         "observed_fraction_wilson_upper": hi})
    return rows


def fingerprint(x, y):
    h = hashlib.sha256()
    h.update(np.asarray(x, dtype="<f8").tobytes(order="C"))
    h.update(np.asarray(y, dtype="<i8").tobytes(order="C"))
    return h.hexdigest()


def write_csv(path, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(output_dir: Path):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    x, y, names = load_data()
    train, test = split_indices(y)
    if index_hash(test) != EXPECTED_HOLDOUT_HASH:
        raise RuntimeError("Historical holdout split changed; do not silently redefine it")
    # No holdout features or outcomes enter development, tuning, or cutoff selection.
    folds, oof = nested_comparison(x[train], y[train])
    fold_summary = summarize_folds(folds)
    cutoff_choices, curves = [], []
    for name in MODELS[:2]:
        for ratio in COST_RATIOS:
            selected, rows = threshold_study(y[train], oof[name], ratio)
            cutoff_choices.append({"model": name, **selected})
            curves.extend({"model": name, **row} for row in rows)
    fitted, selections, tuning = {}, {}, []
    for name in MODELS:
        if name == "prior_baseline":
            fitted[name] = DummyClassifier(strategy="prior").fit(x[train], y[train])
            selections[name] = {}
        else:
            search = make_search(name)
            search.fit(x[train], y[train])
            fitted[name], selections[name] = search.best_estimator_, search.best_params_
            for params, mean, sd in zip(search.cv_results_["params"], search.cv_results_["mean_test_score"], search.cv_results_["std_test_score"]):
                tuning.append({"model": name, "parameters": json.dumps(params, sort_keys=True),
                               "mean_training_selection_auc": float(mean), "sd_training_selection_auc": float(sd)})
    # Freeze the above choices before this descriptive replication is evaluated.
    probability = {name: model.predict_proba(x[test])[:, 1] for name, model in fitted.items()}
    model_results = {name: metrics(y[test], p) for name, p in probability.items()}
    intervals = {name: bootstrap_intervals(y[test], p) for name, p in probability.items()}
    holdout_thresholds = []
    for chosen in cutoff_choices:
        name, threshold = chosen["model"], chosen["threshold"]
        m = metrics(y[test], probability[name], threshold)
        holdout_thresholds.append({"model": name, "cost_ratio": chosen["cost_ratio"],
                                   "training_selected_threshold": threshold,
                                   "holdout_descriptive_cost": (chosen["cost_ratio"] * m["false_negative"] + m["false_positive"]) / len(test), **m})
    bins = [{"model": name, **row} for name in MODELS[:2]
            for row in calibration_bins(y[test], probability[name])]
    report = {
        "project_version": "0.2.0", "seed": SEED,
        "purpose": "Exploratory model-validation methods study; not clinical validation",
        "holdout_status": "Previously observed in version 0.1; descriptive replication, not fresh blind evidence",
        "dataset": "Wisconsin Diagnostic Breast Cancer, sklearn bundled copy",
        "source_doi": "10.24432/C5DW2B", "data_sha256": fingerprint(x, y),
        "n_samples": len(y), "n_features": len(names), "n_train": len(train), "n_test": len(test),
        "train_indices_sha256": index_hash(train), "holdout_indices_sha256": index_hash(test),
        "positive_label": "malignant", "fixed_threshold": 0.5,
        "training_malignant_count": int(y[train].sum()), "test_malignant_count": int(y[test].sum()),
        "nested_cv": {"outer_splits": 4, "repeats": 2, "inner_splits": 3,
                      "summary_scope": "Descriptive distribution of correlated outer-fold estimates; SD is not a confidence interval",
                      "crossfit_scope": "Every training row is excluded from its own fitting and tuning; two predictions averaged for threshold development"},
        "final_training_selected_parameters": selections,
        "selection_metric": "ROC AUC; final 5-fold training-only selection",
        "threshold_selection": {"candidates": THRESHOLDS.tolist(), "illustrative_fn_fp_cost_ratios": list(COST_RATIOS),
                                "scope": "Training OOF tuning loss only; not clinical costs or independent performance"},
        "models": model_results, "conditional_test_bootstrap_95_percentile_intervals": intervals,
        "interval_scope": "Fixed models/cutoffs, test-row sampling only; excludes training, selection, dataset reuse, and site uncertainty",
        "calibration_interval_scope": "Pointwise Wilson intervals for bin event fractions; fixed model/bins, not simultaneous calibration bands",
        "versions": {name: importlib.metadata.version(name) for name in ("numpy", "scipy", "scikit-learn", "matplotlib")},
    }
    (output_dir / "metrics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_csv(output_dir / "nested_cv_folds.csv", folds)
    write_csv(output_dir / "nested_cv_summary.csv", fold_summary)
    write_csv(output_dir / "training_cv.csv", tuning)
    write_csv(output_dir / "threshold_selection.csv", cutoff_choices)
    write_csv(output_dir / "threshold_tuning_curves.csv", curves)
    write_csv(output_dir / "holdout_thresholds.csv", holdout_thresholds)
    write_csv(output_dir / "calibration_bins.csv", bins)
    write_csv(output_dir / "model_comparison.csv", [{"model": name, **m} for name, m in model_results.items()])
    draw_diagnostics(y[test], probability, bins, output_dir / "diagnostics.png")
    draw_nested(folds, output_dir / "nested_cv.png")
    draw_thresholds(curves, cutoff_choices, output_dir / "threshold_sensitivity.png")
    return report


def plot_style():
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 160})


def draw_diagnostics(y, probabilities, bins, target):
    plot_style()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.9), constrained_layout=True)
    for name, probability in probabilities.items():
        fpr, tpr, _ = roc_curve(y, probability)
        axes[0].plot(fpr, tpr, label=name.replace("_", " "), color=COLORS[name], linewidth=2)
    axes[0].plot([0, 1], [0, 1], color="#aaaaaa", linestyle="--", linewidth=1)
    axes[0].set(xlabel="False-positive rate", ylabel="True-positive rate",
                title="Previously observed holdout: discrimination", xlim=(0, 1), ylim=(0, 1.03))
    axes[0].legend(loc="lower right", fontsize=8)
    axes[1].plot([0, 1], [0, 1], color="#aaaaaa", linestyle="--", linewidth=1)
    for name in MODELS[:2]:
        rows = [row for row in bins if row["model"] == name]
        observed = np.array([r["observed_malignant_fraction"] for r in rows])
        lower = np.array([r["observed_fraction_wilson_lower"] for r in rows])
        upper = np.array([r["observed_fraction_wilson_upper"] for r in rows])
        axes[1].errorbar([r["mean_predicted_probability"] for r in rows], observed,
                         yerr=[np.maximum(0, observed-lower), np.maximum(0, upper-observed)],
                         fmt="o-", capsize=3, color=COLORS[name], label=name.replace("_", " "))
    axes[1].set(xlabel="Mean predicted malignant probability", ylabel="Observed malignant fraction",
                title="5 bins: pointwise Wilson intervals", xlim=(0, 1), ylim=(-0.02, 1.03))
    axes[1].legend(loc="lower right", fontsize=8)
    fig.suptitle(f"Descriptive replication · {len(y)} historical holdout records", fontsize=14)
    fig.savefig(target, metadata={"Software": "cell-feature-model-validation 0.2.0"})
    plt.close(fig)


def draw_nested(rows, target):
    plot_style()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), constrained_layout=True)
    for ax, metric, label in zip(axes, ["roc_auc", "brier_score"], ["ROC AUC (higher is better)", "Brier score (lower is better)"]):
        for i, name in enumerate(MODELS):
            values = [r[metric] for r in rows if r["model"] == name]
            ax.scatter(i + np.linspace(-0.10, 0.10, len(values)), values, color=COLORS[name], alpha=0.8)
            ax.plot([i-0.18, i+0.18], [np.mean(values)]*2, color=COLORS[name], linewidth=3)
        ax.set(xticks=range(3), xticklabels=["Logistic", "Forest", "Prior"], ylabel=label)
        ax.grid(axis="y", color="#dddddd", linewidth=0.6)
    fig.suptitle("Training-only nested CV: 4 outer folds × 2 repeats", fontsize=14)
    fig.supxlabel("Dots are correlated fold estimates; horizontal lines are descriptive means", fontsize=10)
    fig.savefig(target, metadata={"Software": "cell-feature-model-validation 0.2.0"})
    plt.close(fig)


def draw_thresholds(curves, selected, target):
    plot_style()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), constrained_layout=True)
    for ax, name in zip(axes, MODELS[:2]):
        for ratio, color in zip(COST_RATIOS, ["#126870", "#c46c23", "#7d4685"]):
            rows = [r for r in curves if r["model"] == name and r["cost_ratio"] == ratio]
            choice = next(r for r in selected if r["model"] == name and r["cost_ratio"] == ratio)
            ax.plot([r["threshold"] for r in rows], [r["training_oof_tuning_loss"] for r in rows],
                    color=color, label=f"FN:FP penalty {ratio:g}:1")
            ax.scatter([choice["threshold"]], [choice["training_oof_tuning_loss"]], color=color, s=40)
        ax.axvline(0.5, color="#888888", linestyle="--", linewidth=1)
        ax.set(title=name.replace("_", " "), xlabel="Candidate probability threshold",
               ylabel="Training OOF tuning loss per record", xlim=(0.04, 0.96))
        ax.legend(fontsize=8)
    fig.suptitle("Illustrative cutoff development · not clinical decision thresholds", fontsize=14)
    fig.savefig(target, metadata={"Software": "cell-feature-model-validation 0.2.0"})
    plt.close(fig)
