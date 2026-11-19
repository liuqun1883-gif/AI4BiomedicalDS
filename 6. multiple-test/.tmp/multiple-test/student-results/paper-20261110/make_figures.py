from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_panel_alignment import require_matplotlib_panel_alignment
OUT=Path(__file__).resolve().parent
FIG=OUT/'figures'; FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'Arial','font.size':8,'axes.titlesize':9,
 'axes.labelsize':8,'axes.spines.top':False,'axes.spines.right':False,
 'axes.linewidth':.6,'xtick.labelsize':7,'ytick.labelsize':7,
 'pdf.fonttype':42,'svg.fonttype':'none','legend.frameon':False})
colors=['#8A929A','#31688E','#D08A42']
methods=['raw','bonferroni','bh']; labels=['Raw','Bonferroni','BH']
def finish(fig,name):
    fig.canvas.draw()
    for i,ax in enumerate(fig.axes):
        ax.annotate(chr(97+i),xy=(0,1),xycoords='axes fraction',xytext=(-25,12),
            textcoords='offset points',fontweight='bold',fontsize=10,annotation_clip=False)
    require_matplotlib_panel_alignment(fig,json_out=FIG/f'{name}.alignment.json',strict=True)
    fig.savefig(FIG/f'{name}.pdf')
    fig.savefig(FIG/f'{name}.svg')
    fig.savefig(FIG/f'{name}.png',dpi=600)
    plt.close(fig)
s=pd.read_csv(OUT/'simulation-summary.csv')
n=pd.read_csv(OUT/'simulation-all-null.csv')
fig,axs=plt.subplots(2,2,figsize=(7.2,4.8))
fig.subplots_adjust(left=.1,right=.97,bottom=.11,top=.84,wspace=.35,hspace=.65)
ax=axs[0,0]
ax.hist(n.loc[n.method=='raw','R'],bins=np.arange(27.5,75.5,2),color=colors[0],edgecolor='white')
ax.axvline(50,color='black',lw=1,ls='--'); ax.set(title='All-null: unadjusted discoveries',xlabel='Discoveries per repetition',ylabel='Repetitions')
for ax,metric,title in [(axs[0,1],'FDR_estimate','False discovery rate'),(axs[1,0],'FWER_estimate','At least one false discovery'),(axs[1,1],'mean_power','Power among 100 true signals')]:
    scenarios=['all-null','signal-1.0','signal-0.5'] if metric!='mean_power' else ['signal-1.0','signal-0.5']
    for k,m in enumerate(methods):
        d=s.set_index(['scenario','method']).loc[[(c,m) for c in scenarios]]
        if metric=='mean_power':
            errs=[]
            for c in scenarios:
                r=pd.read_csv(OUT/f'simulation-{c}.csv')
                errs.append(1.96*r.loc[r.method==m,'power'].std()/np.sqrt(1000))
        else: errs=1.96*d[metric.replace('_estimate','_MCSE')].to_numpy()
        ax.errorbar(np.arange(len(scenarios))+(k-1)*.12,d[metric],yerr=errs,fmt=['o','s','^'][k],color=colors[k],ms=4,capsize=2,label=labels[k])
    ax.set_xticks(range(len(scenarios)),['All null','Strong','Weak'] if len(scenarios)==3 else ['Strong: delta = 1','Weak: delta = 0.5'])
    ax.set(title=title,ylabel='Rate',ylim=(-.04,1.07))
    if metric!='mean_power':ax.axhline(.05,color='black',ls=':',lw=.7)
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([0],[0],color=c,marker=m,ls='',label=l) for c,m,l in zip(colors,['o','s','^'],labels)],loc='upper center',ncol=3,bbox_to_anchor=(.54,1),fontsize=8)
finish(fig,'fig1_simulation')
t=pd.read_csv(OUT/'discovery.csv')
assert (t.raw > 0).all(), 'Log p-value axis requires strictly positive values'
b=pd.read_csv(OUT/'selection-bias.csv')
fig,axs=plt.subplots(2,2,figsize=(7.2,4.8))
fig.subplots_adjust(left=.1,right=.97,bottom=.11,top=.92,wspace=.36,hspace=.65)
axs[0,0].hist(t.raw,bins=np.linspace(0,1,31),color=colors[1]);axs[0,0].set(title='Full discovery family',xlabel='Raw p-value',ylabel='Probes')
ax=axs[0,1]
for mask,c,l in [(t.bh>.05,'#BFC4CA','BH > 0.05'),(t.bh<=.05,colors[2],'BH <= 0.05')]:
    ax.scatter(t.loc[mask,'cohen_d'],-np.log10(t.loc[mask,'raw']),s=5,c=c,alpha=.65,rasterized=True,label=l)
ax.set(title='Effect and evidence',xlabel="Cohen's d (AML minus ALL)",ylabel='-log10(raw p)')
ax=axs[1,0];vals=[int((t[m]<=.05).sum()) for m in methods]
ax.bar(labels,vals,color=colors,width=.58); ax.set(title='Different error-control targets',ylabel='Discoveries',ylim=(0,2000))
for i,v in enumerate(vals):ax.text(i,v+40,str(v),ha='center',fontsize=8)
ax=axs[1,1]
ax.plot(range(1,21),b.bh,marker='o',ms=3,color=colors[1],label='Full family: 7,129')
ax.plot(range(1,21),b.WRONG_bh_after_selecting_top20,marker='s',ms=3,color=colors[2],label='Selected family: 20 (invalid)')
ax.set(yscale='log',title='Post-selection correction is too small',xlabel='Raw-p rank in discovery set',ylabel='BH adjusted p');ax.legend(fontsize=6,loc='lower right')
ax.tick_params(axis='y',which='both',labelsize=9)
finish(fig,'fig2_discovery')
r=pd.read_csv(OUT/'replication.csv')
d=t.set_index('probe').loc[r.probe].reset_index()
fig,axs=plt.subplots(1,2,figsize=(7.2,4.3),sharey=True)
fig.subplots_adjust(left=.23,right=.97,bottom=.15,top=.86,wspace=.18)
for ax,df,title in zip(axs,[d,r],['Discovery: ALL 27, AML 11','Holdout: ALL 20, AML 14']):
    for i,row in df.iterrows():
        delta=row.delta_AML_minus_ALL
        ax.errorbar(delta,i,xerr=[[delta-row.ci95_low],[row.ci95_high-delta]],fmt='o' if r.iloc[i].replicated else 's',ms=4,color=colors[1] if r.iloc[i].replicated else colors[2],capsize=2)
    ax.axvline(0,color='#666666',ls=':',lw=.8)
    ax.set(title=title,xlabel='Mean difference (original scale)',xlim=(-6500,1900),xticks=[-6000,-3000,0])
axs[0].set_yticks(range(10),r.probe.str.strip());axs[0].invert_yaxis()
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([0],[0],color=colors[1],marker='o',ls='',label='Passed holdout rule'),Line2D([0],[0],color=colors[2],marker='s',ls='',label='Did not pass')],ncol=2,loc='upper center',fontsize=8)
finish(fig,'fig3_validation')
print('Saved three figures with alignment audits.')
