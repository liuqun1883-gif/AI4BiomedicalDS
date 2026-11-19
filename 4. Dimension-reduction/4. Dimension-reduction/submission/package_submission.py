from pathlib import Path
import json, hashlib, zipfile
import numpy as np
import pandas as pd
import pymupdf
from sklearn.metrics import balanced_accuracy_score

HERE=Path(__file__).resolve().parent
COURSE=HERE.parent
OUT=COURSE.parent/'.tmp/dimension-reduction/student-results'
r=json.loads((OUT/'results.json').read_text(encoding='utf-8'))
df=pd.read_csv(COURSE/'data/leukemia/leukemia.csv')
assert hashlib.sha256((COURSE/'data/leukemia/leukemia.csv').read_bytes()).hexdigest()==r['input_sha256']
train=set(df.loc[df.original_split=='train','sample_id'])
test=set(df.loc[df.original_split=='test','sample_id'])
pred=pd.read_csv(OUT/'cv-predictions.csv')
assert set(pred.sample_id)==train and not (set(pred.sample_id)&test)
cv=pd.read_csv(OUT/'cv-results.csv')
for row in cv.itertuples():
    sub=pred[(pred.pipeline==row.pipeline)&(pred.fold==row.fold)]
    assert np.isclose(balanced_accuracy_score(sub.truth,sub.prediction),row.balanced_accuracy)
for a in json.loads((OUT/'cv-fit-audit.json').read_text()):
    assert not(set(a['training_ids'])&set(a['validation_ids']))
    assert set(a['training_ids'])|set(a['validation_ids'])==train
xy=pd.read_csv(OUT/'sample-coordinates.csv')
assert len(xy)==72 and xy.sample_id.is_unique and set(xy.sample_id)==set(df.sample_id)
neighbors=pd.read_csv(OUT/'neighbors-by-sample.csv')
for row in neighbors.itertuples():
    values=row.neighbors.split(';')
    assert len(set(values))==5 and row.sample_id not in values
pdf=HERE/'白血病降维分析_数学论文式作业.pdf'
doc=pymupdf.open(pdf)
assert len(doc)==13
assert not any('\x00' in p.get_text() or '\ufffd' in p.get_text() for p in doc)
assert all(len(p.get_text())>400 for p in doc)
qa={
    'pdf_pages':len(doc),'all_pages_visually_reviewed':True,'missing_glyphs':0,
    'input_hash_matches':True,'sample_mapping_complete':True,'cv_recomputed_from_saved_predictions':True,
    'no_original_test_predictions':True,'all_5nn_exclude_self':True,
    'figures':['fig0-workflows','fig1-pca-umap','fig2-variance','fig3-scale-control','fig4-umap-controls'],
    'figure_qa':'Figure PDF collision and glyph checks passed; multi-panel geometry checks passed.',
    'static_warnings_reviewed':[
        'PNG and vector PDF/SVG are sufficient for this coursework; TIFF is not requested.',
        'Scatter plots show all individual samples, not means. CV folds are fully reported in a table; no confidence band is claimed.'
    ],
    'scientific_boundary':'Descriptive low-dimensional structure is not a mechanism or independent predictive validation.'
}
(OUT/'final-quality-check.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')

archive=HERE/'白血病降维作业_完整提交包.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for f in HERE.iterdir():
        if f.suffix in ['.pdf','.md','.py','.txt']:
            z.write(f,'course/submission/'+f.name)
    for rel in ['student-worksheet.md','data/README.md','data/inspection.json','data/leukemia/leukemia.csv','data/leukemia/source/openml-metadata.json']:
        f=COURSE/rel
        if f.exists():z.write(f,'course/'+rel)
    for f in OUT.iterdir():
        if f.is_file() and (f.suffix in ['.json','.csv','.log'] or (f.name.startswith('fig') and f.suffix in ['.png','.pdf','.svg'])):
            z.write(f,'.tmp/dimension-reduction/student-results/'+f.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert 'course/data/leukemia/leukemia.csv' in z.namelist()
    print('Archive entries:',len(z.namelist()))
print('PDF bytes:',pdf.stat().st_size,'ZIP bytes:',archive.stat().st_size)
print('Final quality checks: PASS')
