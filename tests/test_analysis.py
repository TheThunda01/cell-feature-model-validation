import unittest
import numpy as np

from cell_validation.analysis import (
    load_data, split_indices, make_search, metrics, conditional_auc_interval, fingerprint,
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


if __name__ == "__main__":
    unittest.main()
