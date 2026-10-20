"""Conditional predictive-value scenarios with fixed, previously observed rates.

This module fits no model, selects no cutoff, estimates no target prevalence,
and detects no distribution shift. Its outputs follow stated assumptions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

PREVALENCES = (0.01, 0.05, 0.10, 0.25, 0.50)


def _probability(value, name):
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{name} must be a known probability between 0 and 1")
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be numeric") from error
    if not math.isfinite(result) or not 0 <= result <= 1:
        raise ValueError(f"{name} must be finite and between 0 and 1")
    return result


def operating_rates(true_positive, false_negative, true_negative, false_positive):
    """Compute observed class-conditional rates; an absent class stays undefined."""
    values = []
    for value in (true_positive, false_negative, true_negative, false_positive):
        if isinstance(value, bool):
            raise ValueError("Confusion counts must be nonnegative integers")
        try:
            numeric = float(value)
        except (ValueError, TypeError) as error:
            raise ValueError("Confusion counts must be numeric") from error
        if not math.isfinite(numeric) or numeric < 0 or not numeric.is_integer():
            raise ValueError("Confusion counts must be nonnegative integers")
        values.append(int(numeric))
    tp, fn, tn, fp = values
    return {"sensitivity": tp / (tp + fn) if tp + fn else None,
            "specificity": tn / (tn + fp) if tn + fp else None,
            "observed_positive_count": tp + fn, "observed_negative_count": tn + fp}


def predictive_values(prevalence, sensitivity, specificity):
    """Bayes identities for a hypothetical population with fixed operating rates.

    Undefined PPV/NPV (no positive/negative calls) is None, never zero. Unknown
    sensitivity/specificity is rejected rather than replaced by an assumed value.
    """
    pi = _probability(prevalence, "prevalence")
    se = _probability(sensitivity, "sensitivity")
    sp = _probability(specificity, "specificity")
    tp, fn = pi * se, pi * (1 - se)
    tn, fp = (1 - pi) * sp, (1 - pi) * (1 - sp)
    return {"assumed_prevalence": pi, "projected_true_positive_share": tp,
            "projected_false_negative_share": fn, "projected_true_negative_share": tn,
            "projected_false_positive_share": fp,
            "projected_ppv": tp / (tp + fp) if tp + fp else None,
            "projected_npv": tn / (tn + fn) if tn + fn else None}


def scenario_rows(holdout_rows, prevalences=PREVALENCES):
    """Use only existing logistic cutoffs; group duplicate cost scenarios."""
    points = {}
    for row in holdout_rows:
        if row["model"] != "logistic_regression":
            continue
        cutoff = _probability(row["training_selected_threshold"], "threshold")
        rates = operating_rates(row["true_positive"], row["false_negative"],
                                row["true_negative"], row["false_positive"])
        if rates["sensitivity"] is None or rates["specificity"] is None:
            raise ValueError("Both observed classes are required for this scenario")
        if cutoff in points and points[cutoff]["rates"] != rates:
            raise ValueError("Conflicting observed rates for the same cutoff")
        points.setdefault(cutoff, {"rates": rates, "cost_ratios": []})
        ratio = float(row["cost_ratio"])
        if not math.isfinite(ratio) or ratio <= 0:
            raise ValueError("Recorded penalty ratio must be finite and positive")
        points[cutoff]["cost_ratios"].append(ratio)
    if not points:
        raise ValueError("No existing logistic threshold results were supplied")
    rows = []
    for cutoff, item in sorted(points.items()):
        ratios = ";".join(f"{v:g}" for v in sorted(set(item["cost_ratios"])))
        for pi in prevalences:
            rows.append({"model": "logistic_regression", "development_selected_threshold": cutoff,
                         "development_fn_fp_penalty_ratios": ratios,
                         "operating_rate_source": "previously_observed_holdout",
                         **item["rates"], **predictive_values(pi, **{
                             key: item["rates"][key] for key in ("sensitivity", "specificity")})})
    if not rows:
        raise ValueError("At least one prevalence scenario is required")
    return rows


def draw_scenarios(rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8), layout="constrained")
    cutoff_values = sorted({row["development_selected_threshold"] for row in rows})
    colors = ["#126870", "#a15825", "#7d4685"]
    grid = np.linspace(0.01, 0.50, 200)
    npv_values = []
    for index, cutoff in enumerate(cutoff_values):
        point = next(row for row in rows if row["development_selected_threshold"] == cutoff)
        curve = [predictive_values(pi, point["sensitivity"], point["specificity"]) for pi in grid]
        selected = [row for row in rows if row["development_selected_threshold"] == cutoff]
        for ax, field in zip(axes, ("projected_ppv", "projected_npv")):
            values = [np.nan if r[field] is None else 100 * r[field] for r in curve]
            if field == "projected_npv":
                npv_values.extend(value for value in values if math.isfinite(value))
            ax.plot(grid * 100, values, color=colors[index % len(colors)],
                    label=f"Fixed cutoff {cutoff:.2f}", linewidth=2)
            ax.scatter([r["assumed_prevalence"] * 100 for r in selected],
                       [np.nan if r[field] is None else 100 * r[field] for r in selected],
                       color=colors[index % len(colors)], s=25)
    axes[0].set(ylabel="Conditional PPV (%)", ylim=(0, 100), title="Among positive classifier calls")
    npv_lower = max(0, math.floor(min(npv_values) / 5) * 5) if npv_values else 0
    axes[1].set(ylabel="Conditional NPV (%)", ylim=(npv_lower, 100.1),
                title="Among negative calls" + (" · zoomed scale" if npv_lower > 0 else ""))
    for ax in axes:
        ax.set(xlabel="Assumed malignant-label prevalence (%)", xlim=(0, 51))
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=8, loc="lower right")
        ax.grid(alpha=0.2)
    fig.suptitle("Conditional scenarios · fixed historical sensitivity and specificity", fontsize=13)
    fig.supxlabel("Assumed stable rates; no target-population data or uncertainty bands", fontsize=9)
    fig.savefig(path, dpi=160, metadata={"Software": "cell-feature-model-validation 0.3.0"})
    plt.close(fig)


def write_prevalence_outputs(holdout_rows, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = scenario_rows(holdout_rows)
    with (output_dir / "prevalence_sensitivity.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    source = output_dir / "holdout_thresholds.csv"
    payload = {"project_version": "0.3.0", "status": "Conditional illustration, not observed performance at new prevalences",
               "model_fitting_performed": False, "threshold_selection_performed": False,
               "operating_rates_source": "Previously observed holdout at existing development-selected cutoffs",
               "source_table_sha256": hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None,
               "assumption": "Fixed sensitivity and specificity at each cutoff; only the class fraction changes",
               "uncertainty": "Point calculations only; no propagation of rate-estimation or transportability uncertainty",
               "rows": rows}
    (output_dir / "prevalence_sensitivity.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    draw_scenarios(rows, output_dir / "prevalence_sensitivity.png")
    report = ["# Conditional prevalence sensitivity", "",
              "These are mathematical scenarios using fixed logistic-regression cutoffs already selected from development predictions. Sensitivity and specificity are descriptive estimates from the **previously observed holdout**, not new population measurements.", "",
              "Only the assumed malignant-label fraction changes. No model is refitted, no threshold is reselected, and no target prevalence is estimated. Stable class-conditional performance is an assumption, not a finding.", "",
              "| Existing cutoff | Assumed prevalence | Conditional PPV | Conditional NPV |",
              "| ---: | ---: | ---: | ---: |"]
    for row in rows:
        fmt = lambda x: "undefined" if x is None else f"{100*x:.2f}%"
        report.append(f"| {row['development_selected_threshold']:.2f} | {fmt(row['assumed_prevalence'])} | {fmt(row['projected_ppv'])} | {fmt(row['projected_npv'])} |")
    report += ["", "![Conditional predictive values](prevalence_sensitivity.png)", "",
               "The NPV panel uses a zoomed y-axis. Lines hold operating rates fixed; points mark the five tabulated assumptions. Neither line is a confidence band or a prediction for a real screening program.", "",
               f"The estimates use {rows[0]['observed_positive_count']} malignant and {rows[0]['observed_negative_count']} benign holdout records. Their sampling error and possible changes in case mix, measurement, or labeling are not propagated. A lower base rate can reduce PPV despite unchanged assumed sensitivity and specificity; it does not demonstrate a change in individual biology.", "",
               "For the equations and limits, read [prevalence methods](../docs/prevalence-sensitivity.md) and [biology and concepts](../docs/biology-and-concepts.md).", ""]
    (output_dir / "prevalence_report.md").write_text("\n".join(report), encoding="utf-8")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    with (args.results_dir / "holdout_thresholds.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    scenarios = write_prevalence_outputs(rows, args.results_dir)
    print(f"Wrote {len(scenarios)} conditional prevalence scenarios; no fitting or cutoff selection.")


if __name__ == "__main__":
    main()
