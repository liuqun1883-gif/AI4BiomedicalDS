from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import LogLocator, NullFormatter
from audit_panel_alignment import require_matplotlib_panel_alignment

R=Path(__file__).resolve().parent
F=R.parents[3]/'output/multiple-testing-paper/revised/figures'
F.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'Arial','font.size':9,'axes.titlesize':10,'axes.labelsize':9,
 'xtick.labelsize':8,'ytick.labelsize':8,'axes.spines.top':False,'axes.spines.right':False,
 'axes.linewidth':.7,'pdf.fonttype':42,'svg.fonttype':'none','legend.frameon':False,
 'axes.titlepad':12,'xtick.major.size':3,'ytick.major.size':3})
C=['#818A93','#245D81','#C47B36'];M=['raw','bonferroni','bh'];L=['Unadjusted','Bonferroni','BH']
def save(fig,name):
 for i,ax in enumerate(fig.axes):
  ax.annotate(chr(97+i),xy=(0,1),xycoords='axes fraction',xytext=(-25,14),textcoords='offset points',fontsize=11,fontweight='bold',annotation_clip=False)
  ax.set_axisbelow(True)
 fig.canvas.draw()
 require_matplotlib_panel_alignment(fig,json_out=F/f'{name}.alignment.json',strict=True)
 fig.savefig(F/f'{name}.pdf');fig.savefig(F/f'{name}.svg');fig.savefig(F/f'{name}.png',dpi=600)
 plt.close(fig)
s=pd.read_csv(R/'simulation-summary.csv');null=pd.read_csv(R/'simulation-all-null.csv')
fig,ax=plt.subplots(2,2,figsize=(7.2,5.1))
fig.subplots_adjust(left=.11,right=.97,bottom=.11,top=.83,wspace=.42,hspace=.72)
vals=null.loc[null.method=='raw','R']
ax[0,0].hist(vals,bins=np.arange(vals.min()-.5,vals.max()+1.5),color='#AAB7C1',edgecolor='white',linewidth=.3)
ax[0,0].axvline(50,c=C[1],ls='--',lw=1)
ax[0,0].set(title='All-null discovery counts',xlabel='Discoveries per repetition',ylabel='Repetitions')
for a,metric,title in [(ax[0,1],'FDR_estimate','Expected false-discovery proportion'),(ax[1,0],'FWER_estimate','Risk of any false discovery'),(ax[1,1],'mean_power','Power under weaker signals')]:
 scenarios=['all-null','signal-1.0','signal-0.5'] if metric!='mean_power' else ['signal-1.0','signal-0.5']
 for k,m in enumerate(M):
  z=s.set_index(['scenario','method']).loc[[(c,m) for c in scenarios]]
  if metric=='mean_power':
   se=[]
   for scenario in scenarios:
    rr=pd.read_csv(R/f'simulation-{scenario}.csv');se.append(rr.loc[rr.method==m,'power'].std()/np.sqrt(1000))
   se=np.array(se)
  else:se=z[metric.replace('_estimate','_MCSE')].to_numpy()
  a.errorbar(np.arange(len(scenarios))+(k-1)*.12,z[metric],yerr=1.96*se,fmt=['o','s','^'][k],color=C[k],ms=4.5,capsize=2,lw=1)
 a.set_xticks(range(len(scenarios)),['All null','δ = 1','δ = 0.5'] if len(scenarios)==3 else ['δ = 1','δ = 0.5'])
 a.set(title=title,ylabel='Rate (log scale)' if metric!='FWER_estimate' else 'Probability')
 if metric!='FWER_estimate':
  a.set_yscale('log');a.set_ylim((.004,1.5) if metric=='FDR_estimate' else (.001,1.4))
  ticks=[.01,.05,.1,1] if metric=='FDR_estimate' else [.001,.01,.1,1]
  a.set_yticks(ticks,[str(v) for v in ticks]);a.yaxis.set_minor_formatter(NullFormatter())
 else:a.set_ylim(-.035,1.08)
 a.grid(axis='y',color='#E4E8EA',linewidth=.5)
 if metric!='mean_power':a.axhline(.05,color='#333333',lw=.8,ls=':')
fig.legend(handles=[Line2D([0],[0],c=c,marker=m,ls='',label=l) for c,m,l in zip(C,['o','s','^'],L)],ncol=3,loc='upper center',bbox_to_anchor=(.54,1),fontsize=9)
save(fig,'fig1_simulation')
t=pd.read_csv(R/'discovery.csv');b=pd.read_csv(R/'selection-bias.csv')
assert (t.raw>0).all()
fig,ax=plt.subplots(2,2,figsize=(7.2,5.1));fig.subplots_adjust(left=.11,right=.97,bottom=.11,top=.9,wspace=.42,hspace=.72)
ax[0,0].hist(t.raw,bins=np.linspace(0,1,31),color=C[1],edgecolor='white',lw=.3)
ax[0,0].set(title='Discovery family · 7,129 probes',xlabel='Unadjusted p-value',ylabel='Probe count')
for mask,col in [(t.bh>.05,'#C9D0D5'),(t.bh<=.05,C[2])]:ax[0,1].scatter(t.loc[mask,'cohen_d'],-np.log10(t.loc[mask,'raw']),s=6,c=col,alpha=.65,rasterized=True,edgecolors='none')
ax[0,1].set(title='Effect size and statistical evidence',xlabel="Cohen's d · AML minus ALL",ylabel='−log10(p)')
counts=[(t[m]<=.05).sum() for m in M]
ax[1,0].barh(range(3),counts,color=C,height=.55)
ax[1,0].set_yticks(range(3),L);ax[1,0].invert_yaxis();ax[1,0].set(xlim=(0,2100),xlabel='Discoveries',title='Same family, different error targets')
for i,x in enumerate(counts):ax[1,0].text(x+45,i,f'{x:,}',va='center',fontsize=9)
ax[1,0].grid(axis='x',c='#E4E8EA',lw=.5)
for field,col,lab,marker in [('bh',C[1],'All 7,129 probes','o'),('WRONG_bh_after_selecting_top20',C[2],'Selected 20 only (invalid)','s')]:
 ax[1,1].plot(np.arange(1,21),b[field],color=col,label=lab,marker=marker,ms=3,lw=1)
ax[1,1].set(yscale='log',xlabel='Rank among the selected 20',ylabel='BH adjusted p',title='Selection changes the denominator')
ax[1,1].tick_params(axis='y',labelsize=9);ax[1,1].set_xticks([1,5,10,15,20]);ax[1,1].legend(loc='lower right',fontsize=7)
save(fig,'fig2_discovery')
r=pd.read_csv(R/'replication.csv');d=t.set_index('probe').loc[r.probe].reset_index()
fig,axs=plt.subplots(1,3,figsize=(7.2,4.6),sharey=True)
fig.subplots_adjust(left=.22,right=.98,bottom=.18,top=.82,wspace=.25)
for a,df,title in zip(axs[:2],[d,r],['Discovery','Holdout']):
 for i,row in df.iterrows():
  col=C[1] if r.iloc[i].replicated else C[2];mark='o' if r.iloc[i].replicated else 's';delta=row.delta_AML_minus_ALL
  a.errorbar(delta,i,xerr=[[delta-row.ci95_low],[row.ci95_high-delta]],fmt=mark,c=col,ms=4,capsize=2,lw=1)
 a.axvline(0,c='#777777',ls=':',lw=.8);a.set(xlim=(-6500,1800),xticks=[-6000,-3000,0],xlabel='Mean difference',title=title)
for i,row in r.iterrows():axs[2].scatter(row.bonferroni,i,s=22,c=C[1] if row.replicated else C[2],marker='o' if row.replicated else 's')
axs[2].set(xscale='log',xlim=(1e-5,1),xticks=[1e-4,.01,1],xlabel='Adjusted p (log)',title='Holdout Bonferroni')
axs[2].tick_params(axis='x',labelsize=9);axs[2].axvline(.05,c='#555555',ls='--',lw=.8)
axs[0].set_yticks(range(10),r.probe.str.strip());axs[0].invert_yaxis()
for a in axs:
 a.grid(axis='y',c='#E9ECEF',lw=.5)
fig.legend(handles=[Line2D([0],[0],c=C[1],marker='o',ls='',label='Passed prespecified rule'),Line2D([0],[0],c=C[2],marker='s',ls='',label='Did not pass')],ncol=2,loc='upper center',fontsize=9)
save(fig,'fig3_validation')
data=pd.read_csv(R.parents[3]/'6. multiple-test/data/leukemia.csv')
probes=[r.probe.iloc[0],r.probe.iloc[-1]]
fig,axs=plt.subplots(2,2,figsize=(7.2,5.1))
fig.subplots_adjust(left=.12,right=.97,bottom=.11,top=.88,wspace=.36,hspace=.76)
rng=np.random.default_rng(602)
for row,probe in enumerate(probes):
 for col,split in enumerate(['train','test']):
  a=axs[row,col];dd=data[data.original_split==split]
  arrays=[dd.loc[dd.diagnosis==g,probe].to_numpy() for g in ['ALL','AML']]
  bp=a.boxplot(arrays,positions=[0,1],widths=.38,patch_artist=True,showfliers=False,medianprops={'color':'#333333','linewidth':1})
  for box,c in zip(bp['boxes'],['#D7E5ED','#F0DFCC']):box.set_facecolor(c);box.set_edgecolor('#888888')
  for j,ys in enumerate(arrays):a.scatter(j+rng.uniform(-.16,.16,len(ys)),ys,s=13,color=C[1] if j==0 else C[2],alpha=.7,zorder=3,edgecolors='none')
  a.set_xticks([0,1],[f'ALL (n={len(arrays[0])})',f'AML (n={len(arrays[1])})'])
  a.set(title=f'{probe.strip()} · '+('Discovery' if split=='train' else 'Holdout'),ylabel='Expression (original scale)')
  a.grid(axis='y',color='#E9ECEF',lw=.5)
 lo=min(axs[row,0].get_ylim()[0],axs[row,1].get_ylim()[0]);hi=max(axs[row,0].get_ylim()[1],axs[row,1].get_ylim()[1])
 for a in axs[row]:a.set_ylim(lo,hi)
save(fig,'fig4_samples')
print('Four revised figures saved:',F)
