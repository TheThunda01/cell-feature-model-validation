import unittest
import tempfile
from pathlib import Path
import json
from cell_validation.prevalence import operating_rates, predictive_values, scenario_rows, write_prevalence_outputs


class PrevalenceTests(unittest.TestCase):
    def test_bayes_arithmetic_at_low_prevalence(self):
        result = predictive_values(0.01, 0.9, 0.95)
        self.assertAlmostEqual(result['projected_ppv'], 0.009 / 0.0585)
        self.assertAlmostEqual(result['projected_npv'], 0.9405 / 0.9415)
        shares = [value for key, value in result.items() if key.endswith('_share')]
        self.assertAlmostEqual(sum(shares), 1)

    def test_observed_class_fraction_recovers_confusion_predictive_values(self):
        rates = operating_rates(41, 1, 71, 1)
        result = predictive_values(42 / 114, rates['sensitivity'], rates['specificity'])
        self.assertAlmostEqual(result['projected_ppv'], 41 / 42)
        self.assertAlmostEqual(result['projected_npv'], 71 / 72)

    def test_symmetric_half_prevalence(self):
        result = predictive_values(0.5, 0.9, 0.9)
        self.assertAlmostEqual(result['projected_ppv'], 0.9)
        self.assertAlmostEqual(result['projected_npv'], 0.9)

    def test_absent_predicted_class_has_undefined_value(self):
        all_negative = predictive_values(0.1, 0, 1)
        self.assertIsNone(all_negative['projected_ppv'])
        self.assertAlmostEqual(all_negative['projected_npv'], 0.9)
        all_positive = predictive_values(0.1, 1, 0)
        self.assertIsNone(all_positive['projected_npv'])
        self.assertAlmostEqual(all_positive['projected_ppv'], 0.1)

    def test_absent_observed_class_does_not_become_zero_sensitivity(self):
        rates = operating_rates(0, 0, 20, 0)
        self.assertIsNone(rates['sensitivity'])
        self.assertEqual(rates['specificity'], 1)
        with self.assertRaises(ValueError):
            predictive_values(0.1, rates['sensitivity'], rates['specificity'])

    def test_invalid_probabilities_fail(self):
        for value in [-0.1, 1.1, float('nan'), float('inf'), None, True, 'bad']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                predictive_values(value, 0.9, 0.9)
        for value in [-1, float('nan'), None]:
            with self.assertRaises(ValueError):
                predictive_values(0.1, value, 0.9)

    def test_operating_rates_use_correct_denominators(self):
        rates = operating_rates(41, 1, 71, 1)
        self.assertAlmostEqual(rates['sensitivity'], 41 / 42)
        self.assertAlmostEqual(rates['specificity'], 71 / 72)
        for counts in [(-1, 1, 2, 3), (0.5, 1, 2, 3), (True, 1, 2, 3)]:
            with self.assertRaises(ValueError):
                operating_rates(*counts)

    def test_population_extremes_are_supported_when_defined(self):
        self.assertEqual(predictive_values(0, 0.8, 0.9)['projected_ppv'], 0)
        self.assertEqual(predictive_values(1, 0.8, 0.9)['projected_npv'], 0)
        self.assertIsNone(predictive_values(0, 1, 1)['projected_ppv'])
        self.assertIsNone(predictive_values(1, 1, 1)['projected_npv'])

    def test_only_existing_logistic_cutoffs_are_used(self):
        rows = [dict(model='logistic_regression', training_selected_threshold='0.35',
                     cost_ratio=str(cost), true_positive='41', false_negative='1',
                     true_negative='70', false_positive='2') for cost in (2, 5)]
        rows += [dict(rows[0], model='random_forest', training_selected_threshold='0.99')]
        result = scenario_rows(rows)
        self.assertEqual(len(result), 5)
        self.assertEqual({row['development_selected_threshold'] for row in result}, {0.35})
        self.assertEqual(result[0]['development_fn_fp_penalty_ratios'], '2;5')
        self.assertTrue(all(row['operating_rate_source'] == 'previously_observed_holdout' for row in result))
        with self.assertRaises(ValueError):
            scenario_rows([*rows, dict(rows[0], true_positive='40')])



    def test_undefined_ppv_survives_report_serialization(self):
        row = dict(model='logistic_regression', training_selected_threshold=0.5,
                   cost_ratio=1, true_positive=0, false_negative=1,
                   true_negative=1, false_positive=0)
        with tempfile.TemporaryDirectory() as path:
            write_prevalence_outputs([row], Path(path))
            payload = json.loads((Path(path) / 'prevalence_sensitivity.json').read_text())
            self.assertTrue(all(r['projected_ppv'] is None for r in payload['rows']))
            self.assertTrue((Path(path) / 'prevalence_sensitivity.png').is_file())

if __name__ == '__main__':
    unittest.main()
