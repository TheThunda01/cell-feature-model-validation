import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_reproduction import check


class ReproductionTests(unittest.TestCase):
    def write_run(self, folder, number):
        folder.mkdir()
        source = folder / "holdout_thresholds.csv"
        source.write_text(f"score\n{number}\n")
        payload = {"source_table_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                   "projected_ppv": 0.5}
        (folder / "prevalence_sensitivity.json").write_text(json.dumps(payload))

    def test_numeric_equivalence_still_verifies_distinct_byte_fingerprints(self):
        with tempfile.TemporaryDirectory() as tmp:
            expected, actual = Path(tmp) / "expected", Path(tmp) / "actual"
            self.write_run(expected, "0.1")
            self.write_run(actual, "0.10000000000000001")
            self.assertNotEqual((expected / "holdout_thresholds.csv").read_bytes(),
                                (actual / "holdout_thresholds.csv").read_bytes())
            check(expected, actual)

    def test_stale_source_hash_fails_even_for_equivalent_numeric_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            expected, actual = Path(tmp) / "expected", Path(tmp) / "actual"
            self.write_run(expected, "0.1")
            self.write_run(actual, "0.1")
            (actual / "holdout_thresholds.csv").write_text("score\n0.10000000000000001\n")
            with self.assertRaisesRegex(AssertionError, "fingerprint mismatch"):
                check(expected, actual)

    def test_material_numeric_difference_fails_with_valid_fingerprints(self):
        with tempfile.TemporaryDirectory() as tmp:
            expected, actual = Path(tmp) / "expected", Path(tmp) / "actual"
            self.write_run(expected, "0.1")
            self.write_run(actual, "0.2")
            with self.assertRaises(AssertionError):
                check(expected, actual)


if __name__ == "__main__":
    unittest.main()
