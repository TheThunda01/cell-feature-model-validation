"""Compare generated aggregate tables to the checked-in numerical evidence.

Floating point results use a small tolerance; categorical values and table rows
must agree exactly. Images are deliberately left to visual review.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def equivalent(expected, actual, location="root"):
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or expected.keys() != actual.keys():
            raise ValueError(f"{location}: fields differ")
        for key in expected:
            equivalent(expected[key], actual[key], f"{location}.{key}")
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            raise ValueError(f"{location}: sequence length or type differs")
        for i, (a, b) in enumerate(zip(expected, actual)):
            equivalent(a, b, f"{location}[{i}]")
    elif type(expected) in (float, int):
        if type(actual) not in (float, int) or not math.isclose(expected, actual, rel_tol=1e-8, abs_tol=1e-10):
            raise ValueError(f"{location}: expected {expected!r}, received {actual!r}")
    elif type(expected) is not type(actual) or expected != actual:
        raise ValueError(f"{location}: expected {expected!r}, received {actual!r}")


def scalar(value):
    try:
        return float(value)
    except ValueError:
        return value


def checked_json(path):
    """Verify byte provenance inside each run before comparing numeric results."""
    value = json.loads(path.read_text())
    if path.name == "prevalence_sensitivity.json":
        source = path.parent / "holdout_thresholds.csv"
        observed = hashlib.sha256(source.read_bytes()).hexdigest()
        if value.get("source_table_sha256") != observed:
            raise ValueError(f"{path}: source-table fingerprint mismatch")
        # Equivalent floats can have different CSV text across numerical runtimes.
        # Each hash is checked above; CSV values are compared below with tolerance.
        value = {key: item for key, item in value.items() if key != "source_table_sha256"}
    return value


def check(expected_dir, actual_dir):
    expected_dir, actual_dir = Path(expected_dir), Path(actual_dir)
    json_files = sorted(expected_dir.glob("*.json"))
    files = sorted(expected_dir.glob("*.csv"))
    if not json_files and not files:
        raise ValueError(f"No reference JSON or CSV files found in {expected_dir}")
    for file in json_files:
        equivalent(checked_json(file), checked_json(actual_dir / file.name), file.name)
    for file in files:
        with file.open(newline="") as stream:
            expected = [{k: scalar(v) for k, v in row.items()} for row in csv.DictReader(stream)]
        with (actual_dir / file.name).open(newline="") as stream:
            actual = [{k: scalar(v) for k, v in row.items()} for row in csv.DictReader(stream)]
        equivalent(expected, actual, file.name)
    print(f"Reproduced {len(json_files)} JSON outputs and {len(files)} aggregate CSV tables within numeric tolerance.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("actual_dir", type=Path)
    parser.add_argument("--expected-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    check(args.expected_dir, args.actual_dir)
