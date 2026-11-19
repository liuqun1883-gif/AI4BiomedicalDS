from pathlib import Path
import json, hashlib, platform, datetime, sys
import numpy as np
import pandas as pd
import scipy
from scipy import stats

OUT = Path(__file__).resolve().parent
PROJECT = OUT.parents[3]
ROOT = PROJECT / '6. multiple-test'
nb = json.loads((ROOT/'notebooks/multiple-test-lab.ipynb').read_text(encoding='utf-8'))
# Reuse the unmodified numerical functions from the supplied teaching notebook.
exec(''.join(nb['cells'][3]['source']))
def stamp():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
protocol = {'question':'AML minus ALL; two-sided Welch tests', 'family':7130-1,
 'alpha':.05,'discovery':'train: ALL 27, AML 11','validation':'test: ALL 20, AML 14',
 'selection':'BH <= 0.05, then raw p and probe ascending, first 10',
 'validation_rule':'Bonferroni within locked family <= 0.05 and same direction',
 'preprocessing':'Original supplied scale; no log, filter or imputation',
 'recorded_at':stamp()}
if not (OUT/'protocol.json').exists():
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
sha = hashlib.sha256((ROOT/'data/leukemia.csv').read_bytes()).hexdigest()
assert sha == '915bce00295ac470f6bd970a4032730a170a080642a5da53ab0bcb0545156f19'
table=discovery()
np.testing.assert_allclose(table.bh,stats.false_discovery_control(table.raw))
table.to_csv(OUT/'discovery.csv',index=False)
top20=table.sort_values(['raw','probe']).head(20).copy()
wrong=adjust(top20.raw)
top20['WRONG_bh_after_selecting_top20']=wrong.bh.to_numpy()
top20['WRONG_bonf_after_selecting_top20']=wrong.bonferroni.to_numpy()
top20.to_csv(OUT/'selection-bias.csv',index=False)
lock=OUT/'locked-candidates.csv'
if not lock.exists():
    frozen=freeze_candidates(table,lock)
    (OUT/'lock-record.json').write_text(json.dumps({'locked_at':stamp(),
        'sha256':hashlib.sha256(lock.read_bytes()).hexdigest(),
        'validation_results_computed':False},indent=2),encoding='utf-8')
else:
    expected=table.loc[table.bh.le(.05)].sort_values(['raw','probe']).head(10)
    assert pd.read_csv(lock).probe.tolist()==expected.probe.tolist()
rep=replicate(lock)
rep.to_csv(OUT/'replication.csv',index=False)
(OUT/'validation-record.json').write_text(json.dumps({'computed_at':stamp(),
 'lock_sha256':hashlib.sha256(lock.read_bytes()).hexdigest()},indent=2),encoding='utf-8')
summaries=[]
for name,delta,signals in [('all-null',0,0),('signal-1.0',1,100),('signal-0.5',.5,100)]:
    runs=simulate(1000,42,delta,signals)
    runs.to_csv(OUT/f'simulation-{name}.csv',index=False)
    summary=summarize_simulation(runs)
    summary['scenario']=name
    summary['first_R']=[int(runs.loc[(runs.run==0)&(runs.method==m),'R'].iloc[0]) for m in summary.method]
    summary['sd_R']=[runs.loc[runs.method==m,'R'].std() for m in summary.method]
    summary['p05_R']=[runs.loc[runs.method==m,'R'].quantile(.05) for m in summary.method]
    summary['p95_R']=[runs.loc[runs.method==m,'R'].quantile(.95) for m in summary.method]
    summaries.append(summary)
summary=pd.concat(summaries,ignore_index=True)
summary.to_csv(OUT/'simulation-summary.csv',index=False)
versions={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
 'scipy':scipy.__version__,'data_sha256':sha,'seed':42,'repeats':1000}
(OUT/'versions.json').write_text(json.dumps(versions,indent=2),encoding='utf-8')
print('DISCOVERY',counts(table),'REPLICATION',int(rep.replicated.sum()))
print(summary.to_string(index=False))
print(table.sort_values(['raw','probe']).head(1).to_string(index=False))
print(rep.to_string(index=False))
