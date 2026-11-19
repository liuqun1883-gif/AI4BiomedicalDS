                                                                                                                                                                                                                                                    """Reproduce the 72-sample worksheet. No held-out test performance is computed."""
from pathlib import Path
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMBA_NUM_THREADS']:
    os.environ[key] = '1'
import json, hashlib, platform, importlib.metadata as md
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score
from umap import UMAP
from threadpoolctl import threadpool_limits
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
threadpool_limits(1)
HERE = Path(__file__).resolve().parent
COURSE = HERE.parent
DATA = COURSE/'data/leukemia/leukemia.csv'
OUT = COURSE.parent/'.tmp/dimension-reduction/student-results'
OUT.mkdir(parents=True, exist_ok=True)
os.environ['NUMBA_CACHE_DIR'] = str(OUT/'numba-cache')
SEED = 42
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':9,
    'axes.spines.top':False,'axes.spines.right':False,
    'pdf.fonttype':42,'svg.fonttype':'none','legend.frameon':False})

def dump(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2,
        default=lambda x: x.item() if hasattr(x,'item') else str(x)), encoding='utf-8')

def savefig(fig, name):
    # Audit is optional on other machines; the figures themselves are portable.
    import sys
    audit_dir = HERE
    if (audit_dir/'audit_panel_alignment.py').exists():
        sys.path.insert(0,str(audit_dir))
        from audit_panel_alignment import require_matplotlib_panel_alignment
        require_matplotlib_panel_alignment(fig,json_out=str(OUT/(name+'.alignment.json')),strict=True)
    fig.savefig(OUT/(name+'.png'),dpi=600)
    fig.savefig(OUT/(name+'.pdf'))
    fig.savefig(OUT/(name+'.svg'))
    plt.close(fig)

def scatter(ax, xy, labels, xlabel, ylabel, title):
    for lab,col,mark in [('ALL','#2878A0','o'),('AML','#C36B31','^')]:
        m=labels==lab
        ax.scatter(xy[m,0],xy[m,1],s=26,c=col,marker=mark,label=lab,alpha=.88,linewidths=.35,edgecolors='white')
    ax.set(xlabel=xlabel,ylabel=ylabel,title=title)

def neighbors(x, k=5):
    d=cdist(x,x)
    np.fill_diagonal(d,np.inf)
    return np.argsort(d,axis=1,kind='stable')[:,:k]

def overlap(a,b):
    return np.array([len(set(i)&set(j))/len(i) for i,j in zip(a,b)])

def run():
    # Recorded before fitting; these are hypotheses, not claimed observations.
    dump('protocol.json',{'task':'72-sample leukemia Markdown worksheet',
        'predictions':[
            'Separation in two dimensions is not sufficient evidence of causality or generalization.',
            'Scaling may change PCA directions and explained variance.',
            'UMAP neighborhoods and geometry may change with hyperparameters and seeds.',
            'PCA(10) may improve or worsen 1NN; the direction is not presumed.'
        ],'fit_scope_descriptive':72,'fit_scope_prediction':'original train only; each training fold',
        'seed':42,'no_test_scoring':True,'no_label_feature_selection':True})
    df=pd.read_csv(DATA)
    meta=['sample_id','original_split','diagnosis']
    X=df.drop(columns=meta).to_numpy(dtype=float)
    names=df.drop(columns=meta).columns.to_numpy()
    y=df.diagnosis.to_numpy(); ids=df.sample_id.to_numpy()
    assert X.shape==(72,7129) and np.isfinite(X).all()
    assert len(set(names))==7129 and not np.any(X.std(0)==0)
    sc=StandardScaler().fit(X); Z=sc.transform(X)
    pc=PCA(svd_solver='full').fit(Z); score=pc.transform(Z)
    raw=PCA(svd_solver='full').fit(X); rscore=raw.transform(X)
    E=pc.explained_variance_ratio_; R=raw.explained_variance_ratio_
    assert np.allclose(score,(Z-pc.mean_)@pc.components_.T)
    assert np.allclose(pc.components_@pc.components_.T,np.eye(72),atol=1e-8)
    loadrows=[]
    for kind,obj in [('standardized',pc),('centered',raw)]:
        top=np.argsort(-np.abs(obj.components_[0]))[:5]
        for rank,j in enumerate(top,1):
            loadrows.append(dict(preprocessing=kind,rank=rank,probe=names[j],weight=obj.components_[0,j],raw_sd=sc.scale_[j]))
    loads=pd.DataFrame(loadrows);loads.to_csv(OUT/'pc1-loadings.csv',index=False)
    pd.DataFrame({'component':np.arange(1,73),'standardized':E,'centered':R,
        'standardized_cumulative':E.cumsum(),'centered_cumulative':R.cumsum()}).to_csv(OUT/'explained-variance.csv',index=False)
    coords=df[meta].copy()
    coords['pca1']=score[:,0];coords['pca2']=score[:,1]
    coords['raw_pca1']=rscore[:,0];coords['raw_pca2']=rscore[:,1]
    embeddings={}; settings={
        'baseline':dict(n_neighbors=15,min_dist=.1,random_state=42),
        'neighbors5':dict(n_neighbors=5,min_dist=.1,random_state=42),
        'min_dist05':dict(n_neighbors=15,min_dist=.5,random_state=42),
        'seed7':dict(n_neighbors=15,min_dist=.1,random_state=7)}
    dump('umap-settings.json',{'common':{'n_components':2,'metric':'euclidean','n_jobs':1},'settings':settings})
    for key,params in settings.items():
        print('Fitting UMAP:',key,flush=True)
        model=UMAP(n_components=2,metric='euclidean',n_jobs=1,**params)
        embeddings[key]=model.fit_transform(Z)
        dump('umap-'+key+'-all-params.json',model.get_params())
        coords[key+'_1']=embeddings[key][:,0];coords[key+'_2']=embeddings[key][:,1]
    coords.to_csv(OUT/'sample-coordinates.csv',index=False)
    knn={'high_dim':neighbors(Z),'pca2':neighbors(score[:,:2])}
    knn.update({key:neighbors(xy) for key,xy in embeddings.items()})
    nrows=[]; summary=[]
    for key,nn in knn.items():
        retained=overlap(knn['high_dim'],nn); stable=overlap(knn['baseline'],nn)
        summary.append(dict(representation=key,high_dim_retention=retained.mean(),baseline_overlap=stable.mean()))
        for i in range(72):
            nrows.append(dict(representation=key,sample_id=ids[i],neighbors=';'.join(ids[nn[i]]),high_dim_retention=retained[i],baseline_overlap=stable[i]))
    pd.DataFrame(nrows).to_csv(OUT/'neighbors-by-sample.csv',index=False)
    pd.DataFrame(summary).to_csv(OUT/'neighbor-summary.csv',index=False)
    stable_rows=[]
    for i in range(72):
        common=set.intersection(*(set(knn[k][i]) for k in embeddings))
        stable_rows.append(dict(sample_id=ids[i],common_count=len(common),common_neighbors=';'.join(ids[sorted(common)]),high_dim_common=';'.join(ids[sorted(common & set(knn['high_dim'][i]))])))
    pd.DataFrame(stable_rows).to_csv(OUT/'stable-neighbors.csv',index=False)
    # The only prediction experiment: fixed pipelines in the original 38 train rows.
    train=df.original_split.eq('train').to_numpy()
    Xt=X[train];yt=y[train];tid=ids[train]
    assert Xt.shape[0]==38
    folds=list(StratifiedKFold(3,shuffle=True,random_state=42).split(Xt,yt))
    cv=[]; preds=[]; audits=[]
    for f,(itr,iva) in enumerate(folds,1):
        audits.append(dict(fold=f,training_ids=tid[itr].tolist(),validation_ids=tid[iva].tolist()))
        for label,pipe in [
            ('Scaled 1NN',make_pipeline(StandardScaler(),KNeighborsClassifier(n_neighbors=1))),
            ('Scaled PCA10 1NN',make_pipeline(StandardScaler(),PCA(n_components=10,svd_solver='full'),KNeighborsClassifier(n_neighbors=1)))]:
            pipe.fit(Xt[itr],yt[itr]); pred=pipe.predict(Xt[iva])
            cv.append(dict(pipeline=label,fold=f,n_train=len(itr),n_valid=len(iva),balanced_accuracy=balanced_accuracy_score(yt[iva],pred)))
            preds.extend(dict(pipeline=label,fold=f,sample_id=tid[j],truth=yt[j],prediction=p) for j,p in zip(iva,pred))
    pd.DataFrame(cv).to_csv(OUT/'cv-results.csv',index=False)
    pd.DataFrame(preds).to_csv(OUT/'cv-predictions.csv',index=False)
    dump('cv-fit-audit.json',audits)
    # A paired scatter explicitly contrasts the same 72 samples and color mapping.
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.25))
    fig.subplots_adjust(left=.10,right=.98,bottom=.19,top=.84,wspace=.32)
    scatter(axs[0],score,y,f'PC1 ({E[0]:.2%})',f'PC2 ({E[1]:.2%})','a   Standardized PCA')
    scatter(axs[1],embeddings['baseline'],y,'UMAP 1','UMAP 2','b   Baseline UMAP')
    axs[1].legend(loc='upper left',bbox_to_anchor=(0,1.19),ncol=2,fontsize=8)
    savefig(fig,'fig1-pca-umap')
    fig,ax=plt.subplots(figsize=(7.2,3.25));fig.subplots_adjust(left=.11,right=.97,bottom=.18,top=.92)
    ax.plot(np.arange(1,73),E.cumsum(),label='Standardized',color='#2878A0')
    ax.plot(np.arange(1,73),R.cumsum(),label='Centered only',color='#C36B31')
    ax.axhline(.9,color='.5',lw=.8,ls=':')
    ax.set(xlabel='Number of principal components',ylabel='Cumulative explained variance',xlim=(1,72),ylim=(0,1.02))
    ax.legend(loc='lower right');savefig(fig,'fig2-variance')
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.25));fig.subplots_adjust(left=.10,right=.98,bottom=.19,top=.85,wspace=.34)
    scatter(axs[0],score,y,f'PC1 ({E[0]:.2%})',f'PC2 ({E[1]:.2%})','a   Standardized')
    scatter(axs[1],rscore,y,f'PC1 ({R[0]:.2%})',f'PC2 ({R[1]:.2%})','b   Centered only')
    savefig(fig,'fig3-scale-control')
    fig,axs=plt.subplots(2,2,figsize=(7.2,5.7));fig.subplots_adjust(left=.10,right=.98,bottom=.10,top=.91,wspace=.32,hspace=.43)
    for ax,key,title in zip(axs.flat,embeddings,['a   Baseline: k=15, d=0.1, s=42','b   Neighbors: k=5, d=0.1, s=42','c   Min. distance: k=15, d=0.5, s=42','d   Seed: k=15, d=0.1, s=7']):
        scatter(ax,embeddings[key],y,'UMAP 1','UMAP 2',title)
    savefig(fig,'fig4-umap-controls')
    # Score reconstruction validates both variance and feature-level interpretation.
    mse2=float(np.mean((Z-pc.inverse_transform(np.column_stack([score[:,:2],np.zeros((72,70))])))**2))
    contrib=(Z[0]-pc.mean_)*pc.components_[0]
    top=np.argsort(-np.abs(pc.components_[0]))[:5]
    pd.DataFrame({'probe':names[top],'z_G001':Z[0,top],'weight':pc.components_[0,top],'contribution':contrib[top]}).to_csv(OUT/'G001-contributions.csv',index=False)
    result={
        'shape':list(X.shape),'classes':df.diagnosis.value_counts().to_dict(),
        'train_classes':df.loc[train,'diagnosis'].value_counts().to_dict(),
        'input_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(),
        'negative_count':int((X<0).sum()),'zero_count':int((X==0).sum()),'min':X.min(),'max':X.max(),
        'max_abs_z_mean':abs(Z.mean(0)).max(),'max_abs_z_sd_error':abs(Z.std(0,ddof=0)-1).max(),
        'pca_evr':E[:2].tolist(),'pca_sum2':E[:2].sum(),'raw_evr':R[:2].tolist(),'raw_sum2':R[:2].sum(),
        'k90_standardized':int(np.searchsorted(E.cumsum(),.9)+1),'k90_centered':int(np.searchsorted(R.cumsum(),.9)+1),
        'numerical_rank':int(np.linalg.matrix_rank(Z-Z.mean(0))),'pca_last_evr':E[-1],
        'mse2_standardized':mse2,'expected_mse2':1-E[:2].sum(),
        'G001_score':score[0,0],'G001_top5_sum':contrib[top].sum(),'G001_other_sum':np.delete(contrib,top).sum(),
        'neighbor_summary':summary,'cv':cv,
        'versions':{p:md.version(p) for p in ['numpy','pandas','scipy','scikit-learn','umap-learn','numba','llvmlite','matplotlib','threadpoolctl']},'python':platform.python_version()}
    assert np.isclose(mse2,1-E[:2].sum())
    dump('results.json',result)
    (HERE/'requirements.txt').write_text('\n'.join(f'{k}=={v}' for k,v in result['versions'].items())+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2,default=float),flush=True)
    return result

if __name__=='__main__':
    run()
