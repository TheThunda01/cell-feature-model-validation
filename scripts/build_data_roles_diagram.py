"""Generate an editable draw.io map of the saved benchmark's data roles."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def build(metrics_path: Path, destination: Path) -> None:
    raw = metrics_path.read_bytes()
    metrics = json.loads(raw)
    if metrics['n_train'] + metrics['n_test'] != metrics['n_samples']:
        raise ValueError('Development and holdout counts do not sum to the dataset')
    if 'Previously observed' not in metrics['holdout_status']:
        raise ValueError('This diagram describes the historical, already inspected holdout')
    nested = metrics['nested_cv']
    ntrain, ntest = metrics['n_train'], metrics['n_test']
    doc = ET.Element('mxfile', host='app.diagrams.net', version='32.6.1')
    page = ET.SubElement(doc, 'diagram', name='Development, assessment and historical holdout', id='data-roles')
    model = ET.SubElement(page, 'mxGraphModel', dx='1280', dy='1000', grid='1', gridSize='10', page='1', pageScale='1', pageWidth='1280', pageHeight='1000', background='#ffffff')
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    def box(key, text, x, y, width, height, fill='#e8f1f7', stroke='#27617f', size=19):
        node = ET.SubElement(root, 'mxCell', id=key, value=text,
            style=f'rounded=1;html=0;fillColor={fill};strokeColor={stroke};fontColor=#1f3443;fontSize={size};fontFamily=Arial;spacing=14;', vertex='1', parent='1')
        ET.SubElement(node, 'mxGeometry', x=str(x), y=str(y), width=str(width), height=str(height), attrib={'as': 'geometry'})

    def arrow(key, source, target, label='', style=''):
        node = ET.SubElement(root, 'mxCell', id=key, value=label, edge='1', parent='1', source=source, target=target,
            style='edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;endArrow=block;strokeWidth=2;strokeColor=#506c7b;fontSize=16;labelBackgroundColor=#ffffff;' + style)
        ET.SubElement(node, 'mxGeometry', relative='1', attrib={'as': 'geometry'})

    box('title', 'Where data can influence a decision', 70, 20, 1140, 55, '#ffffff', '#ffffff', 30)
    box('input', f"Historical dataset\n{metrics['n_samples']} records · {metrics['n_features']} features", 460, 100, 340, 90)
    box('development', f'{ntrain} development records\nAll model and threshold choices stay here', 60, 245, 710, 85, '#dcece7', '#386c5c')
    box('holdout', f'{ntest} historical holdout records\nAlready inspected in version 0.1', 870, 245, 350, 105, '#fff0dc', '#a66b28')
    box('nested', f"Repeated nested assessment\n{nested['outer_splits']} outer folds × {nested['repeats']} repeats\n{nested['inner_splits']} inner folds tune only inside\neach outer training partition", 60, 405, 335, 155)
    box('refit', f'Final model fitting\n5-fold tuning on all {ntrain}\ndevelopment records\nRefit both learned models', 435, 405, 335, 155, '#dcece7', '#386c5c')
    box('outer', f"Outputs from the outer fits\n{nested['outer_splits'] * nested['repeats']} fold scores per model\nFixed 0.5 classification cutoff\n{nested['repeats']} predictions per record, each\nexcluded from fitting/tuning\nAverage the {nested['repeats']} predictions", 60, 640, 335, 175)
    box('threshold', 'Threshold development\nFixed cutoff grid searched\non averaged cross-fitted\nprobabilities\nLoss uses development labels', 435, 640, 335, 175, '#dcece7', '#386c5c')
    box('historical', 'Historical evaluation\nApply final models and\ndevelopment-selected cutoffs\nDescriptive replication only', 870, 575, 350, 175, '#fff0dc', '#a66b28')
    box('limits', 'Interpretation boundaries\nFold variability is not a confidence interval. Minimized threshold loss is tuning loss.\nThe inspected holdout provides no fresh blind validation; it never feeds back into scripted choices.', 60, 885, 1160, 95, '#f3f5f7', '#8195a3', 18)
    arrow('split-development', 'input', 'development')
    arrow('split-holdout', 'input', 'holdout')
    arrow('development-nested', 'development', 'nested')
    arrow('development-refit', 'development', 'refit')
    arrow('nested-outputs', 'nested', 'outer')
    arrow('crossfit-threshold', 'outer', 'threshold')
    arrow('refit-evaluate', 'refit', 'historical', 'Fitted models', 'exitX=1;exitY=0.5;entryX=0;entryY=0.2;')
    arrow('threshold-evaluate', 'threshold', 'historical', 'Selected cutoffs', 'exitX=1;exitY=0.5;entryX=0;entryY=0.8;')
    arrow('holdout-evaluate', 'holdout', 'historical', 'Evaluation only')
    destination.mkdir(parents=True, exist_ok=True)
    ET.indent(doc)
    ET.ElementTree(doc).write(destination / 'data-roles.drawio', encoding='utf-8', xml_declaration=True)
    (destination / 'source-manifest.json').write_text(json.dumps({
        'schema_version': 1, 'source': 'results/metrics.json',
        'sha256_lf_normalized': hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest(),
        'scope': 'Data-role explanation of the saved protocol; no analysis rerun or new validation claim.',
        'counts': {k: metrics[k] for k in ('n_samples', 'n_train', 'n_test', 'n_features')},
        'method_source': 'docs/methods.md',
    }, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metrics', type=Path, default=ROOT / 'results/metrics.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'docs/figures/data-roles')
    arguments = parser.parse_args()
    build(arguments.metrics, arguments.output_dir)
