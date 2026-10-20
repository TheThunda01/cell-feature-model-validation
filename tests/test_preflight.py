import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sklearn.datasets import load_breast_cancer
from cell_validation.preflight import inspect_inputs

ROOT=Path(__file__).resolve().parents[1]


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)
        self.meta=json.loads((ROOT/'examples/synthetic_metadata.json').read_text())
        self.names=list(load_breast_cancer().feature_names)
        self.row={name:str((i+1)/100) for i,name in enumerate(self.names)}

    def run_check(self, rows=None, fields=None, meta=None):
        data=self.path/'input.csv';metadata=self.path/'metadata.json'
        with data.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields or self.names)
            writer.writeheader();writer.writerows([self.row] if rows is None else rows)
        metadata.write_text(json.dumps(self.meta if meta is None else meta))
        return inspect_inputs(data,metadata)

    def test_example_no_prediction_or_biological_claim(self):
        result=inspect_inputs(ROOT/'examples/synthetic_features.csv',ROOT/'examples/synthetic_metadata.json')
        self.assertEqual(result['rows'],3)
        self.assertEqual(result['data_kind'],'synthetic')
        self.assertEqual(result['exact_benchmark_overlap_rows'],0)
        self.assertEqual(result['suitable_for_external_validation'],'not_assessed')
        self.assertNotIn('predictions',result)

    def test_reordering_uses_names_and_duplicate_vectors_are_reported(self):
        result=self.run_check([self.row,self.row],fields=self.names[::-1])
        self.assertTrue(result['columns_reordered_to_contract'])
        self.assertEqual(result['duplicate_feature_rows'],1)
        self.assertEqual(len(result['constant_features']),30)

    def test_exact_benchmark_overlap_is_detected_despite_declaration(self):
        row=dict(zip(self.names,map(str,load_breast_cancer().data[0])))
        result=self.run_check([row],meta={**self.meta,'independent_of_development':True,'known_overlap_checked':True})
        self.assertEqual(result['exact_benchmark_overlap_rows'],1)
        self.assertTrue(any('overlap' in finding for finding in result['findings']))

    def test_missing_extra_duplicate_columns_and_empty_data_fail(self):
        cases=[([],self.names),([{k:v for k,v in self.row.items() if k!=self.names[0]}],self.names[1:]),
               ([{**self.row,'identifier':'123'}],self.names+['identifier']),
               ([self.row],self.names+[self.names[0]])]
        for rows,fields in cases:
            with self.subTest(fields=fields),self.assertRaises(ValueError):self.run_check(rows,fields)

    def test_nonfinite_blank_and_text_fail(self):
        for value in ['nan','inf','-inf','','unknown']:
            with self.subTest(value=value),self.assertRaises(ValueError):
                self.run_check([{**self.row,self.names[0]:value}])

    def test_metadata_requires_explicit_booleans_and_measurements(self):
        for key,value in [('known_overlap_checked','false'),('independent_of_development',1),
                          ('measurement_method',''),('feature_definition_reference',None),('data_kind','patients'),('data_kind',[])]:
            with self.subTest(key=key),self.assertRaises(ValueError):self.run_check(meta={**self.meta,key:value})

    def test_labels_need_exact_orientation(self):
        rows=[{**self.row,'reference_label':'1'}]
        result=self.run_check(rows,self.names+['reference_label'])
        self.assertEqual(result['label_counts'],{'0':0,'1':1})
        with self.assertRaises(ValueError):
            self.run_check(rows,self.names+['reference_label'],meta={**self.meta,'label_mapping':{'0':'malignant','1':'benign'}})
        with self.assertRaises(ValueError):
            self.run_check([{**self.row,'reference_label':'M'}],self.names+['reference_label'])

    def test_malformed_width_fails(self):
        self.run_check()
        with (self.path/'input.csv').open('a') as stream:stream.write('1,2\n')
        with self.assertRaisesRegex(ValueError,'width'):
            inspect_inputs(self.path/'input.csv',self.path/'metadata.json')

    def test_unclosed_quote_rejected_by_parser_and_cli(self):
        self.run_check()
        data=self.path/'input.csv';metadata=self.path/'metadata.json'
        header=','.join(self.names)+'\n'
        prefix=','.join(self.row[name] for name in self.names[:-1])+','
        data.write_text(header+prefix+'"0.30"\n')
        self.assertEqual(inspect_inputs(data,metadata)['rows'],1)
        data.write_text(header+prefix+'"0.30\n')
        with self.assertRaises(csv.Error):
            inspect_inputs(data,metadata)
        result=subprocess.run([sys.executable,'-m','cell_validation.preflight',
                               '--data',str(data),'--metadata',str(metadata)],
                              cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertEqual(result.stdout,'')
        self.assertIn('feature preflight failed:',result.stderr)
        self.assertNotIn('Traceback',result.stderr)


if __name__=='__main__':unittest.main()
