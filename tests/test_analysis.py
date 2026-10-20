import unittest
import numpy as np
from unittest.mock import patch

from cell_validation.analysis import (
    load_data, split_indices, make_search, metrics, conditional_auc_interval, fingerprint,
    index_hash, EXPECTED_HOLDOUT_HASH, nested_comparison, threshold_study,
    calibration_bins, wilson_interval, bootstrap_intervals,
)


class ValidationTests(unittest.TestCase):
    def test_dataset_and_positive_label(self):
        x, y, names = load_data()
        self.assertEqual(x.shape, (569, 30))
        self.assertEqual(int(y.sum()), 212)
        self.assertEqual(len(names), 30)
        self.assertTrue(np.isfinite(x).all())

    def test_split_is_disjoint_complete_and_deterministic(self):
        _, y, _ = load_data()
        train, test = split_indices(y)
        self.assertEqual(len(train), 455)
        self.assertEqual(len(test), 114)
        self.assertFalse(set(train) & set(test))
        self.assertEqual(set(train) | set(test), set(range(len(y))))
        np.testing.assert_array_equal(test, split_indices(y)[1])
        self.assertEqual(index_hash(test), EXPECTED_HOLDOUT_HASH)
        self.assertLess(abs(y[train].mean() - y[test].mean()), 0.01)

    def test_scaler_refit_uses_training_rows_only(self):
        x, y, _ = load_data()
        train, test = split_indices(y)
        search = make_search()
        search.fit(x[train], y[train])
        scale = search.best_estimator_.named_steps["scale"]
        self.assertEqual(scale.n_samples_seen_, len(train))
        np.testing.assert_allclose(scale.mean_, x[train].mean(axis=0))
        self.assertFalse(np.allclose(scale.mean_, x.mean(axis=0)))
        # The unfitted template is still a pipeline, so GridSearchCV fits scaling
        # separately in each fold as well as during the final training-only refit.
        self.assertEqual(list(search.estimator.named_steps), ["scale", "model"])
        self.assertFalse(hasattr(search.estimator.named_steps["scale"], "mean_"))

    def test_metric_orientation_and_confusion_counts(self):
        result = metrics([0, 0, 1, 1], [0.1, 0.8, 0.4, 0.9])
        self.assertEqual(result["true_positive"], 1)
        self.assertEqual(result["false_negative"], 1)
        self.assertEqual(result["false_positive"], 1)
        self.assertEqual(result["true_negative"], 1)
        self.assertAlmostEqual(result["balanced_accuracy"], 0.5)
        self.assertAlmostEqual(result["roc_auc"], 0.75)

    def test_invalid_probability_rejected(self):
        for probability in ([0.1, np.nan], [0.2, 1.1], [0.1]):
            with self.assertRaises(ValueError):
                metrics([0, 1], probability)

    def test_conditional_interval_reproducible(self):
        y = np.array([0, 0, 1, 1])
        p = np.array([0.1, 0.6, 0.4, 0.9])
        result = conditional_auc_interval(y, p, repeats=100)
        self.assertEqual(result, conditional_auc_interval(y, p, repeats=100))
        self.assertLessEqual(result["lower"], result["upper"])
        self.assertGreater(result["valid_resamples"], 0)

    def test_fingerprint_changes_with_data(self):
        x, y, _ = load_data()
        original = fingerprint(x, y)
        x[0, 0] += 1
        self.assertNotEqual(original, fingerprint(x, y))

    def test_nested_crossfit_never_fits_its_evaluation_records(self):
        seen = []

        class AuditedEstimator:
            def __init__(self, fit_ids):
                self.fit_ids = set(fit_ids)

            def predict_proba(self, x):
                ids = set(x[:, 0].astype(int))
                if ids & self.fit_ids:
                    raise AssertionError("Evaluation record entered its own fit")
                seen.append(ids)
                p = np.where(x[:, 0].astype(int) % 2, 0.8, 0.2)
                return np.column_stack([1-p, p])

        class AuditedSearch:
            def fit(self, x, y):
                self.best_estimator_ = AuditedEstimator(x[:, 0].astype(int))
                self.best_params_ = {"test": True}
                return self

        x = np.arange(24).reshape(-1, 1)
        y = np.arange(24) % 2
        with patch("cell_validation.analysis.make_search", return_value=AuditedSearch()):
            rows, probabilities = nested_comparison(x, y, outer_splits=3, repeats=2, inner_splits=2)
        self.assertEqual(len(rows), 18)
        self.assertEqual(len(seen), 12)  # 2 learned models, 3 folds, 2 repeats
        for p in probabilities.values():
            self.assertEqual(p.shape, (24,))
            self.assertTrue(np.isfinite(p).all())
        np.testing.assert_allclose(probabilities["logistic_regression"], np.where(y, 0.8, 0.2))

    def test_cost_tradeoff_selects_only_supplied_candidates(self):
        y = np.array([0, 0, 1, 1])
        p = np.array([0.2, 0.6, 0.4, 0.9])
        low_fn, _ = threshold_study(y, p, 0.2, thresholds=[0.3, 0.5, 0.7])
        high_fn, _ = threshold_study(y, p, 5, thresholds=[0.3, 0.5, 0.7])
        self.assertEqual(low_fn["threshold"], 0.7)
        self.assertEqual(high_fn["threshold"], 0.3)
        self.assertLess(high_fn["false_negative"], low_fn["false_negative"])
        with self.assertRaises(ValueError):
            threshold_study(y, p, 0)

    def test_cutoff_tie_is_resolved_towards_point_five(self):
        selected, _ = threshold_study([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9], 2,
                                     thresholds=[0.3, 0.5, 0.7])
        self.assertEqual(selected["threshold"], 0.5)
        symmetric, _ = threshold_study([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9], 2,
                                      thresholds=[0.3, 0.7])
        self.assertEqual(symmetric["threshold"], 0.7)

    def test_forest_is_unscaled_and_reproducible(self):
        search = make_search("random_forest")
        self.assertEqual(search.estimator.named_steps["scale"], "passthrough")
        self.assertEqual(search.estimator.named_steps["model"].n_jobs, 1)
        self.assertIsInstance(search.estimator.named_steps["model"].random_state, int)

    def test_calibration_bins_keep_every_record_with_tied_predictions(self):
        rows = calibration_bins([0, 0, 0, 1, 1, 1], [0.5]*6, n_bins=5)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["n"], 6)
        self.assertEqual(rows[0]["malignant_count"], 3)
        self.assertLess(rows[0]["observed_fraction_wilson_lower"], 0.5)
        self.assertGreater(rows[0]["observed_fraction_wilson_upper"], 0.5)

    def test_wilson_boundaries_and_invalid_counts(self):
        low, high = wilson_interval(0, 10)
        self.assertEqual(low, 0.0)
        self.assertAlmostEqual(high, 0.2775327998628892)
        self.assertEqual(wilson_interval(10, 10)[1], 1.0)
        for successes, total in [(0, 0), (-1, 10), (11, 10)]:
            with self.assertRaises(ValueError):
                wilson_interval(successes, total)

    def test_bootstrap_rejects_invalid_inputs_and_reports_valid_resamples(self):
        with self.assertRaises(ValueError):
            bootstrap_intervals([0, 1], [0.2, 0.8], repeats=0)
        result = bootstrap_intervals([0, 0, 1, 1], [0.1, 0.4, 0.6, 0.9], repeats=50)
        self.assertTrue(0 < result["roc_auc"]["valid_resamples"] <= 50)
        self.assertEqual(result["roc_auc"]["lower"], 1.0)


if __name__ == "__main__":
    unittest.main()
