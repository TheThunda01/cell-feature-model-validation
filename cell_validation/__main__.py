import argparse
from pathlib import Path

from .analysis import run

parser = argparse.ArgumentParser(description="Run an educational cell-feature validation benchmark.")
parser.add_argument("--output-dir", type=Path, default=Path("results"))
args = parser.parse_args()
result = run(args.output_dir)
print(f"Saved aggregate results to {args.output_dir}; held-out n={result['n_test']}")
print(f"Logistic ROC AUC: {result['models']['logistic_regression']['roc_auc']:.4f}")
