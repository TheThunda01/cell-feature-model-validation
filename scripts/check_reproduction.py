"""Compare generated aggregate tables to the checked-in numerical evidence.

Floating point results use a small tolerance; categorical values and table rows
must agree exactly. Images are deliberately left to visual review.
"""
import argparse
import csv
import json
import math
from pathlib import Path


def equivalent(expected, actual, location="root"):
    if isinstance(expected, dict):
        assert isinstance(actual, dict) and expected.keys() == actual.keys(), location
        for key in expected:
            equivalent(expected[key], actual[key], f"{location}.{key}")
    elif isinstance(expected, list):
        assert isinstance(actual, list) and len(expected) == len(actual), location
        for i, (a, b) in enumerate(zip(expected, actual)):
            equivalent(a, b, f"{location}[{i}]")
    elif isinstance(expected, (float, int)) and not isinstance(expected, bool):
        assert isinstance(actual, (float, int)) and math.isclose(expected, actual, rel_tol=1e-8, abs_tol=1e-10), location
    else:
        assert expected == actual, f"{location}: {expected!r} != {actual!r}"


def scalar(value):
    try:
        return float(value)
    except ValueError:
        return value


def check(expected_dir, actual_dir):
    expected_dir, actual_dir = Path(expected_dir), Path(actual_dir)
    equivalent(json.loads((expected_dir / "metrics.json").read_text()),
               json.loads((actual_dir / "metrics.json").read_text()), "metrics.json")
    files = sorted(expected_dir.glob("*.csv"))
    for file in files:
        with file.open(newline="") as stream:
            expected = [{k: scalar(v) for k, v in row.items()} for row in csv.DictReader(stream)]
        with (actual_dir / file.name).open(newline="") as stream:
            actual = [{k: scalar(v) for k, v in row.items()} for row in csv.DictReader(stream)]
        equivalent(expected, actual, file.name)
    print(f"Reproduced metrics.json and {len(files)} aggregate CSV tables within numeric tolerance.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("actual_dir", type=Path)
    parser.add_argument("--expected-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    check(args.expected_dir, args.actual_dir)
