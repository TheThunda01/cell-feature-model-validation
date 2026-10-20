"""Declarative feature mapping; never transforms data or certifies measurement equivalence."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re

from sklearn.datasets import load_breast_cancer

SCHEMA_VERSION = '1.0'
MAX_MAP_BYTES = 1_000_000
SOURCE = 'https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic'
TEXT_FIELDS = ('source_field', 'source_definition', 'source_units', 'transform_description', 'transform_reference')


def template(data_sha256=''):
    return {'schema_version': SCHEMA_VERSION, 'mapping_id': '', 'data_sha256': data_sha256,
            'reviewer': '', 'reviewed_on': '', 'benchmark_reference': SOURCE,
            'benchmark_units_note': 'Units are not established by a matching column name. Consult the source measurement procedure.',
            'mappings': [{'feature': str(feature), **{key: '' for key in TEXT_FIELDS},
                          'transform_kind': 'unknown', 'reviewed': False}
                         for feature in load_breast_cancer().feature_names]}


def validate_feature_map(path, names, data_sha256, required=False):
    path = Path(path)
    if path.stat().st_size > MAX_MAP_BYTES:
        raise ValueError('feature map exceeds the 1 MB limit')
    raw = path.read_bytes()
    document = json.loads(raw)
    if not isinstance(document, dict) or document.get('schema_version') != SCHEMA_VERSION:
        raise ValueError('feature map must be an object with schema_version 1.0')
    missing_metadata = []
    for key in ('mapping_id', 'reviewer', 'reviewed_on', 'benchmark_reference', 'data_sha256'):
        value = document.get(key, '')
        if not isinstance(value, str):
            raise ValueError(f'feature map {key} must be a string')
        if not value.strip():
            missing_metadata.append(key)
    digest = document.get('data_sha256', '')
    if digest and not re.fullmatch('[0-9a-f]{64}', digest):
        raise ValueError('feature map data_sha256 must be empty or lowercase SHA-256')
    if digest and digest != data_sha256:
        raise ValueError('feature map data_sha256 does not match the input CSV')
    reviewed_on = document.get('reviewed_on', '')
    if reviewed_on:
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', reviewed_on):
                raise ValueError()
            date.fromisoformat(reviewed_on)
        except ValueError:
            raise ValueError('feature map reviewed_on must be empty or YYYY-MM-DD') from None
    mappings = document.get('mappings')
    if not isinstance(mappings, list):
        raise ValueError('feature map mappings must be a list')
    seen, incomplete = set(), []
    for item in mappings:
        if not isinstance(item, dict):
            raise ValueError('each feature mapping must be an object')
        name = item.get('feature')
        if not isinstance(name, str) or name not in names or name in seen:
            raise ValueError('feature map names must be supported and unique')
        seen.add(name)
        missing = []
        for key in TEXT_FIELDS:
            value = item.get(key, '')
            if not isinstance(value, str):
                raise ValueError(f'feature map {name}: {key} must be a string')
            if not value.strip():
                missing.append(key)
        kind = item.get('transform_kind', 'unknown')
        if not isinstance(kind, str) or kind not in {'identity', 'precomputed', 'unknown'}:
            raise ValueError(f'feature map {name}: unsupported transform_kind')
        if kind == 'unknown':
            missing.append('transform_kind')
        reviewed = item.get('reviewed', False)
        if type(reviewed) is not bool:
            raise ValueError(f'feature map {name}: reviewed must be a JSON boolean')
        if not reviewed:
            missing.append('reviewed')
        if missing:
            incomplete.append({'feature': name, 'missing_declarations': missing})
    missing_features = [str(name) for name in names if name not in seen]
    complete = not missing_metadata and not missing_features and not incomplete
    if required and not complete:
        raise ValueError('feature map review declarations are incomplete; inspect in optional mode first')
    return {'schema_version': SCHEMA_VERSION, 'map_sha256': hashlib.sha256(raw).hexdigest(),
            'bound_to_input': bool(digest), 'mappings_present': len(mappings), 'expected_features': len(names),
            'declarations_complete': complete, 'missing_metadata': missing_metadata,
            'missing_features': missing_features, 'incomplete_features': incomplete,
            'semantic_compatibility_established': False,
            'interpretation': 'Only declaration structure/completeness and CSV byte binding checked. No transformation, unit verification, clinical validation, or measurement-equivalence assessment is performed.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='new template path; existing files are not overwritten')
    parser.add_argument('--data', type=Path, help='optionally bind the template to these exact CSV bytes')
    args = parser.parse_args()
    try:
        if args.data and args.data.stat().st_size > 10_000_000:
            raise ValueError('data exceeds the 10 MB limit')
        digest = hashlib.sha256(args.data.read_bytes()).hexdigest() if args.data else ''
        with args.output.open('x',encoding='utf-8') as stream:
            json.dump(template(digest),stream,indent=2,allow_nan=False)
            stream.write('\n')
        print('Wrote an incomplete feature-map template; operator review is required.')
    except (ValueError,OSError) as error:
        parser.exit(2,f'feature-map template failed: {error}\n')


if __name__ == '__main__':
    main()
