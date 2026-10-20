"""Inspect a candidate feature file without fitting a model or making predictions."""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path

from sklearn.datasets import load_breast_cancer

CONTRACT_VERSION = '1.0'
MAX_BYTES = 10_000_000
MAX_ROWS = 100_000


def inspect_inputs(data_path, metadata_path):
    data_path, metadata_path = Path(data_path), Path(metadata_path)
    if data_path.stat().st_size > MAX_BYTES or metadata_path.stat().st_size > MAX_BYTES:
        raise ValueError('input exceeds the 10 MB preflight limit')
    raw, metadata_raw = data_path.read_bytes(), metadata_path.read_bytes()
    metadata = json.loads(metadata_raw)
    if not isinstance(metadata, dict):
        raise ValueError('metadata must be a JSON object')
    for key in ('source', 'measurement_method', 'feature_definition_reference'):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            raise ValueError(f'metadata {key} must be a nonempty string')
    for key in ('independent_of_development', 'known_overlap_checked'):
        if type(metadata.get(key)) is not bool:
            raise ValueError(f'metadata {key} must be a JSON boolean')
    if not isinstance(metadata.get('data_kind'), str) or metadata['data_kind'] not in {'synthetic', 'public_deidentified_features'}:
        raise ValueError('metadata data_kind must be synthetic or public_deidentified_features')
    benchmark = load_breast_cancer()
    names = list(benchmark.feature_names)
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')), strict=True)
    header = reader.fieldnames
    if header is None or len(header) != len(set(header)):
        raise ValueError('CSV requires unique named columns')
    labelled = 'reference_label' in header
    expected = set(names) | ({'reference_label'} if labelled else set())
    if set(header) != expected:
        raise ValueError('CSV must contain exactly the 30 named benchmark features and optional reference_label')
    if labelled and metadata.get('label_mapping') != {'0': 'benign', '1': 'malignant'}:
        raise ValueError('labelled files require label_mapping 0=benign, 1=malignant')
    seen, duplicates, overlap, count = set(), 0, 0, 0
    benchmark_rows = {tuple(row) for row in benchmark.data}
    minima, maxima = [math.inf]*len(names), [-math.inf]*len(names)
    label_counts = {'0': 0, '1': 0} if labelled else None
    for count, row in enumerate(reader, 1):
        if count > MAX_ROWS:
            raise ValueError('input exceeds the 100000 row preflight limit')
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f'CSV line {count+1}: incorrect row width')
        values = []
        for index, name in enumerate(names):
            try:
                value = float(row[name])
            except ValueError:
                raise ValueError(f'CSV line {count+1}: {name} must be numeric') from None
            if not math.isfinite(value):
                raise ValueError(f'CSV line {count+1}: {name} must be finite')
            values.append(value)
            minima[index], maxima[index] = min(minima[index], value), max(maxima[index], value)
        if labelled:
            label = row['reference_label']
            if label not in {'0', '1'}:
                raise ValueError(f'CSV line {count+1}: reference_label must be 0 or 1')
            label_counts[label] += 1
        key = tuple(values)
        duplicates += key in seen
        overlap += key in benchmark_rows
        seen.add(key)
    if count == 0:
        raise ValueError('CSV must contain at least one record')
    findings = []
    if duplicates:
        findings.append('Repeated feature vectors need review; identical vectors do not prove repeated people.')
    if overlap:
        findings.append('Exact feature vectors overlap the public benchmark, including development and historical holdout records.')
    if not metadata['independent_of_development'] or not metadata['known_overlap_checked']:
        findings.append('Independence or overlap review is not declared complete.')
    constant = [name for i, name in enumerate(names) if minima[i] == maxima[i]]
    if constant:
        findings.append('Constant features need review; they are not automatically invalid.')
    return {'contract_version': CONTRACT_VERSION, 'contract_valid': True,
            'data_kind': metadata['data_kind'], 'rows': count, 'features': len(names),
            'columns_reordered_to_contract': header[:len(names)] != names,
            'label_counts': label_counts, 'duplicate_feature_rows': duplicates,
            'exact_benchmark_overlap_rows': overlap, 'constant_features': constant,
            'data_sha256': hashlib.sha256(raw).hexdigest(),
            'metadata_sha256': hashlib.sha256(metadata_raw).hexdigest(),
            'independence_declared': metadata['independent_of_development'],
            'overlap_review_declared': metadata['known_overlap_checked'],
            'findings': findings, 'suitable_for_external_validation': 'not_assessed',
            'interpretation': 'Structural checks and exact numeric overlap only. Metadata declarations are unverified; no model is fitted or applied. Matching names do not establish measurement equivalence or clinical utility.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect_inputs(args.data, args.metadata), indent=2, allow_nan=False))
    except (ValueError, OSError, UnicodeError, csv.Error) as error:
        parser.exit(2, f'feature preflight failed: {error}\n')


if __name__ == '__main__':
    main()
