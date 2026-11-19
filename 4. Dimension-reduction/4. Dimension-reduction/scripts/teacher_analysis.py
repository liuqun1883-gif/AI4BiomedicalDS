"""Reproduce teacher-reference evidence; run from any working directory."""
from pathlib import Path
import os
import sys

BASE = Path(__file__).resolve().parents[1]
WORK = BASE.parents[2] / '.tmp/dimension-reduction'
sys.dont_write_bytecode = True
os.environ.setdefault('NUMBA_CACHE_DIR', str(WORK / 'numba-cache'))
os.environ.setdefault('MPLCONFIGDIR', str(WORK / 'matplotlib'))
import hashlib
import importlib.metadata
import json
import platform
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from umap import UMAP

OUT = WORK / 'teacher-results'
OUT.mkdir(parents=True, exist_ok=True)
src = BASE / 'data/leukemia/leukemia.csv'
df = pd.read_csv(src)
X = df.iloc[:, 3:].to_numpy(dtype=float)
y = df.diagnosis.to_numpy()
names = df.columns[3:].to_numpy()
train = df.original_split.eq('train').to_numpy()
assert X.shape == (72, 7129) and np.isfinite(X).all()
expected = json.loads((BASE / 'data/inspection.json').read_text())['sha256']['leukemia/leukemia.csv']
assert hashlib.sha256(src.read_bytes()).hexdigest() == expected
Z = StandardScaler().fit_transform(X)
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
cv_rows = []
for use_pca in [False, True]:
    steps = [StandardScaler()]
    if use_pca:
        steps.append(PCA(n_components=10, svd_solver='full'))
    steps.append(KNeighborsClassifier(n_neighbors=1, metric='euclidean'))
    scores = cross_validate(make_pipeline(*steps), X[train], y[train], cv=cv,
                            scoring='balanced_accuracy', return_train_score=True)
    for fold, (tr, va) in enumerate(zip(scores['train_score'], scores['test_score']), 1):
        cv_rows.append(dict(labels='real', pca10=use_pca, fold=fold, train_ba=tr, validation_ba=va))
pd.DataFrame(cv_rows).to_csv(OUT / 'cross-validation.csv', index=False)
summary = {'python': platform.python_version(),
           'packages': {n: importlib.metadata.version(n) for n in ['numpy','pandas','scipy','scikit-learn','umap-learn','matplotlib']},
           'csv_sha256': expected, 'n': len(X), 'p': X.shape[1],
           'standardization': {'max_abs_mean': float(abs(Z.mean(axis=0)).max()),
                               'max_abs_sd_minus_one': float(abs(Z.std(axis=0)-1).max())},
           'pca': {}, 'umap': []}
loadings = []; embeddings = {}; variance_rows = []
for kind, A in [('standardized', Z), ('raw', X)]:
    pca = PCA(svd_solver='full').fit(A)
    embedding = pca.transform(A)[:, :2]
    embeddings[kind] = embedding
    evr = pca.explained_variance_ratio_; cumulative = np.cumsum(evr)
    top = np.argsort(abs(pca.components_[0]))[::-1][:5]
    summary['pca'][kind] = {'pc1': float(evr[0]), 'pc2': float(evr[1]), 'pc1_pc2':float(cumulative[1]),
        'n80':int(np.searchsorted(cumulative, .8)+1), 'n90':int(np.searchsorted(cumulative, .9)+1),
        'top5': [{'probe':names[i], 'weight':float(pca.components_[0,i]), 'raw_sd':float(X[:,i].std())} for i in top]}
    for k, (v,c) in enumerate(zip(evr,cumulative),1):
        variance_rows.append(dict(input=kind, component=k, explained_ratio=v, cumulative=c))
    for i in top:
        loadings.append(dict(input=kind, probe=names[i], weight=pca.components_[0,i], raw_sd=X[:,i].std()))
    pd.DataFrame({'sample_id':df.sample_id, 'diagnosis':y, 'PC1':embedding[:,0], 'PC2':embedding[:,1]}).to_csv(OUT/f'pca-{kind}-coordinates.csv', index=False)
pd.DataFrame(loadings).to_csv(OUT/'pca-loadings.csv', index=False)
vr = pd.DataFrame(variance_rows); vr.to_csv(OUT/'pca-variance.csv', index=False)
fig, ax = plt.subplots(figsize=(6,4))
for kind in ['standardized','raw']:
    a=vr[vr.input==kind]; ax.plot(a.component,a.cumulative,label=kind)
ax.set(xlabel='Number of PCs',ylabel='Cumulative explained variance',ylim=(0,1.02)); ax.legend()
fig.tight_layout(); fig.savefig(OUT/'pca-variance.png',dpi=160); plt.close(fig)

def neighbors(A, k=5):
    D=squareform(pdist(A)); np.fill_diagonal(D,np.inf)
    return np.argsort(D,axis=1)[:,:k]

original_neighbors = neighbors(Z); umap_neighbors = {}
for label, nn, md, seed in [('baseline',15,.1,42),('neighbors5',5,.1,42),('mindist05',15,.5,42),('seed7',15,.1,7)]:
    print('Fitting UMAP:',label,flush=True)
    emb = UMAP(n_components=2,n_neighbors=nn,min_dist=md,metric='euclidean',random_state=seed,n_jobs=1).fit_transform(Z)
    assert emb.shape==(72,2) and np.isfinite(emb).all()
    embeddings[label] = emb
    knn = neighbors(emb); umap_neighbors[label] = knn
    retain = np.mean([len(set(a)&set(b))/5 for a,b in zip(original_neighbors,knn)])
    overlap = np.mean([len(set(a)&set(b))/5 for a,b in zip(umap_neighbors['baseline'],knn)])
    summary['umap'].append(dict(setting=label,n_neighbors=nn,min_dist=md,seed=seed,
                                original_knn5_retained=float(retain),baseline_knn5_overlap=float(overlap)))
    pd.DataFrame({'sample_id':df.sample_id,'diagnosis':y,'UMAP1':emb[:,0],'UMAP2':emb[:,1]}).to_csv(OUT/f'umap-{label}-coordinates.csv',index=False)
stable_rows=[]
for i in range(len(X)):
    shared = set.intersection(*(set(knn[i]) for knn in umap_neighbors.values()))
    stable_rows.append(dict(sample_id=df.sample_id.iloc[i],all_settings_neighbors=';'.join(df.sample_id.iloc[j] for j in sorted(shared)),count=len(shared)))
pd.DataFrame(stable_rows).to_csv(OUT/'umap-stable-neighbors.csv',index=False)
fig, axes = plt.subplots(2,3,figsize=(13,8))
for ax,key in zip(axes.flat,['standardized','raw','baseline','neighbors5','mindist05','seed7']):
    emb=embeddings[key]
    for label,color in [('ALL','#387ca3'),('AML','#d57839')]:
        mask=y==label; ax.scatter(emb[mask,0],emb[mask,1],s=24,c=color,label=label,alpha=.85)
    if key in summary['pca']:
        info=summary['pca'][key]
        ax.set(xlabel=f"PC1 ({info['pc1']:.1%})",ylabel=f"PC2 ({info['pc2']:.1%})",title='PCA '+key)
    else:
        ax.set(xlabel='UMAP1',ylabel='UMAP2',title='UMAP '+key)
    ax.legend()
fig.tight_layout(); fig.savefig(OUT/'pca-umap.png',dpi=180); plt.close(fig)
(OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2),flush=True)
