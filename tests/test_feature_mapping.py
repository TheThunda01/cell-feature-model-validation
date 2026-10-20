from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sklearn.datasets import load_breast_cancer
from cell_validation.feature_mapping import template, validate_feature_map
from cell_validation.preflight import inspect_inputs

ROOT=Path(__file__).resolve().parents[1]


class FeatureMappingTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)/'map.json'
        self.names=list(load_breast_cancer().feature_names)
        self.data=ROOT/'examples/synthetic_features.csv'
        self.metadata=ROOT/'examples/synthetic_metadata.json'
        self.digest=hashlib.sha256(self.data.read_bytes()).hexdigest()
        self.complete=json.loads((ROOT/'examples/synthetic_feature_map.json').read_text())

    def check_map(self,document,required=False):
        self.path.write_text(json.dumps(document))
        return validate_feature_map(self.path,self.names,self.digest,required)

    def test_template_has_all_features_but_no_implied_review(self):
        document=template()
        self.assertEqual([r['feature'] for r in document['mappings']],self.names)
        self.assertEqual(json.loads((ROOT/'templates/feature-map-v1.json').read_text()),document)
        result=self.check_map(document)
        self.assertFalse(result['declarations_complete'])
        self.assertEqual(len(result['incomplete_features']),30)
        self.assertFalse(result['bound_to_input'])
        with self.assertRaisesRegex(ValueError,'incomplete'):self.check_map(document,True)

    def test_complete_declarations_do_not_establish_compatibility_or_transform_data(self):
        before=self.data.read_bytes()
        result=inspect_inputs(self.data,self.metadata,ROOT/'examples/synthetic_feature_map.json',True)
        self.assertTrue(result['feature_mapping']['declarations_complete'])
        self.assertFalse(result['feature_mapping']['semantic_compatibility_established'])
        self.assertEqual(result['suitable_for_external_validation'],'not_assessed')
        self.assertEqual(self.data.read_bytes(),before)
        baseline=inspect_inputs(self.data,self.metadata)
        result.pop('feature_mapping')
        self.assertEqual(result,baseline)

    def test_required_mode_needs_map(self):
        with self.assertRaisesRegex(ValueError,'feature map is required'):
            inspect_inputs(self.data,self.metadata,require_feature_map=True)

    def test_wrong_csv_digest_is_rejected_even_in_optional_mode(self):
        document=deepcopy(self.complete);document['data_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'does not match'):self.check_map(document)

    def test_missing_features_reported_and_duplicate_or_unknown_names_rejected(self):
        document=deepcopy(self.complete);missing=document['mappings'].pop()
        result=self.check_map(document)
        self.assertEqual(result['missing_features'],[missing['feature']])
        with self.assertRaisesRegex(ValueError,'incomplete'):self.check_map(document,True)
        for name in [self.names[0],'unknown',[]]:
            document=deepcopy(self.complete);document['mappings'][-1]['feature']=name
            with self.assertRaisesRegex(ValueError,'supported and unique'):self.check_map(document)

    def test_mapping_order_does_not_change_feature_matching(self):
        document=deepcopy(self.complete);document['mappings'].reverse()
        self.assertTrue(self.check_map(document,True)['declarations_complete'])

    def test_missing_units_or_transform_or_review_block_required_mode(self):
        for field,value in [('source_units',''),('source_definition',''),('transform_kind','unknown'),
                            ('transform_description',''),('transform_reference',''),('reviewed',False)]:
            document=deepcopy(self.complete);document['mappings'][0][field]=value
            result=self.check_map(document)
            self.assertIn(field,result['incomplete_features'][0]['missing_declarations'])
            with self.assertRaisesRegex(ValueError,'incomplete'):self.check_map(document,True)

    def test_invalid_schema_types_dates_and_transform_labels_fail(self):
        documents=[[],{**self.complete,'schema_version':'2.0'},
                   {**self.complete,'reviewed_on':'2026-02-30'},
                   {**self.complete,'data_sha256':'xyz'},
                   {**self.complete,'mappings':None}]
        for field,value in [('reviewed','yes'),('source_units',None),('transform_kind','execute_python')]:
            doc=deepcopy(self.complete);doc['mappings'][0][field]=value;documents.append(doc)
        for document in documents:
            with self.subTest(document=document),self.assertRaises(ValueError):self.check_map(document)

    def test_template_cli_binds_bytes_and_refuses_overwrite(self):
        command=[sys.executable,'-m','cell_validation.feature_mapping','--output',str(self.path),'--data',str(self.data)]
        first=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(first.returncode,0,first.stderr)
        self.assertEqual(json.loads(self.path.read_text())['data_sha256'],self.digest)
        before=self.path.read_bytes()
        second=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(second.returncode,2)
        self.assertEqual(self.path.read_bytes(),before)


if __name__=='__main__':unittest.main()
