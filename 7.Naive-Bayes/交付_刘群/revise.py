from pathlib import Path
R=Path(__file__).resolve().parent
out=R.parent/'论文修订版_刘群';out.mkdir(exist_ok=True)
s=(R/'build.py').read_text(encoding='utf-8-sig')
s=s.replace("plt.rcParams.update({'font.family'", "plt.rcParams.update({'font.family'",1)
a=s.index("fig,ax=plt.subplots(figsize=(7,2.5))")
b=s.index('doc=Document()',a)
plots='''from matplotlib.patches import FancyBboxPatch
BLUE='#245B78';RED='#B65D46';GRAY='#637582'
plt.rcParams.update({'axes.labelcolor':'#243746','xtick.color':'#536570','ytick.color':'#536570','axes.edgecolor':'#A5B2BB','grid.color':'#E4EAF0','axes.axisbelow':True,'legend.frameon':False,'font.size':9})
fig,ax=plt.subplots(figsize=(7,2.5));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
for x,num,title,sub,count in [(.01,'01','训练集','估计先验与类内症状概率','72条  |  阴性37 · 阳性35'),(.35,'02','验证集','按预设规则选择阈值','24条  |  阴性12 · 阳性12'),(.69,'03','固定测试集','方案固定后进行最终评价','24条  |  阴性12 · 阳性12')]:
 ax.add_patch(FancyBboxPatch((x,.30),.29,.64,boxstyle='round,pad=.008,rounding_size=.018',facecolor='#F1F5F8',edgecolor='#D5DFE6',lw=.8))
 ax.text(x+.02,.82,num,color=BLUE,fontsize=10,weight='bold');ax.text(x+.02,.65,title,color='#233A4A',fontsize=13,weight='bold')
 ax.text(x+.02,.48,count,fontsize=8);ax.text(x+.02,.35,sub,fontsize=7.8,color=GRAY)
for x in [.317,.657]:ax.annotate('',xy=(x+.025,.60),xytext=(x-.012,.60),arrowprops={'arrowstyle':'->','color':GRAY,'lw':1.3})
ax.text(.5,.12,'六项症状  →  后验概率  →  阈值决策  →  分类指标与概率损失',ha='center',color=BLUE,fontsize=10)
save('fig1')
fig,ax=plt.subplots(figsize=(6.8,3.2));ax.set_facecolor('white');ax.grid(axis='y',lw=.6)
ax.axhspan(.9,1.05,color='#EEF5F4',zorder=0)
ax.plot(tt.threshold,tt.sensitivity,'o-',label='敏感度  TP / 12',color=BLUE,lw=1.6,ms=5)
ax.plot(tt.threshold,tt.specificity,'s-',label='特异度  TN / 12',color=RED,lw=1.6,ms=4.5)
ax.axvline(t,color='#83939F',ls='--',lw=1)
ax.text(.53,.73,'选定阈值 0.50\\n漏诊 0 · 误报 0',fontsize=9,color=BLUE)
ax.set(xlabel='决策阈值 t',ylabel='验证集比例',ylim=(-.04,1.08),xlim=(.02,.98),xticks=[.1,.3,.5,.7,.9]);ax.legend(loc='lower left',fontsize=9)
save('fig2')
fig,ax=plt.subplots(figsize=(6.8,3.2));ax.grid(lw=.5)
ax.axvspan(0,.5,alpha=.35,color='#F0F4F7');ax.axhspan(.5,1,alpha=.18,color='#F0F4F7')
ax.plot([0,1],[0,1],ls='--',lw=.9,color='#8B99A2');ax.axhline(.5,color='#AEB9C2',lw=.7);ax.axvline(.5,color='#AEB9C2',lw=.7)
g=pd.DataFrame({'p':p,'q':dp,'y':va.bladder_inflammation}).groupby(['p','q','y']).size().reset_index(name='n')
for y,col,marker,label in [(0,BLUE,'o','真实阴性'),(1,RED,'s','真实阳性')]:
 z=g[g.y==y];ax.scatter(z.p,z.q,s=28+15*z.n,c=col,marker=marker,edgecolors='white',linewidths=.7,label=label,zorder=4)
ax.text(.04,.90,'24条记录 · 按相同输出聚合',fontsize=8.5,color=GRAY)
ax.text(.59,.39,'6 / 24 条类别改变',fontsize=9,color=RED)
ax.set(xlabel='原模型阳性概率',ylabel='复制腰痛五次后的阳性概率',xlim=(-.04,1.04),ylim=(-.04,1.08))
ax.legend(loc='center left',bbox_to_anchor=(.02,.63),fontsize=8.5)
save('fig3')
fig,ax=plt.subplots(figsize=(6.8,3.0));ix=np.argsort(pt);yy=te.bladder_inflammation.to_numpy()[ix];rank=np.arange(1,25)
ax.grid(axis='y',lw=.6)
for label,col,marker,name in [(0,BLUE,'o','真实阴性 n=12'),(1,RED,'s','真实阳性 n=12')]:
 mask=yy==label;ax.vlines(rank[mask],0,pt[ix][mask],color=col,alpha=.22,lw=1.2);ax.scatter(rank[mask],pt[ix][mask],color=col,s=28,marker=marker,label=name,zorder=3)
ax.axhline(.5,color='#7A8B96',ls='--',lw=1);ax.text(1,.54,'决策阈值 0.50',fontsize=8,color=GRAY)
ax.set(xlabel='测试记录序号（按预测概率从低到高排列）',ylabel='阳性概率',ylim=(-.04,1.08),xlim=(.2,24.8),xticks=[1,6,12,18,24]);ax.legend(loc='center right',fontsize=8.5)
save('fig4')
'''
s=s[:a]+plots+s[b:]
s=s.replace("dpi=300","dpi=600")
s=s.replace("sec.top_margin=Cm(2)","sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=Cm(1.9)")
s=s.replace("doc.styles['Normal'].paragraph_format.line_spacing=1.08","doc.styles['Normal'].paragraph_format.line_spacing=1.12")
s=s.replace("doc.styles['Title'].font.size=Pt(22)","doc.styles['Title'].font.size=Pt(20)")
s=s.replace("def head(s):doc.add_heading(s,1)","""def head(s):
 major=['摘要','引言','材料与方法','结果','讨论','结论','数据与代码可用性','AI使用说明','参考文献','补充材料 七项工作单的计算与解释','任务6与7 分类指标与综合解释']
 doc.add_heading(s,1 if s in major else 2)""")
s=s.replace("doc.styles['Heading 1'].paragraph_format.space_before=Pt(8)","""doc.styles['Heading 2'].font.size=Pt(11.5)
doc.styles['Heading 2'].font.bold=True
doc.styles['Heading 2'].paragraph_format.space_before=Pt(7)
doc.styles['Heading 2'].paragraph_format.space_after=Pt(4)
doc.styles['Caption'].font.size=Pt(9)
doc.styles['Caption'].font.bold=False
doc.styles['Caption'].paragraph_format.keep_with_next=False
doc.styles['Caption'].paragraph_format.line_spacing=1.05
doc.styles['Heading 1'].paragraph_format.space_before=Pt(8)""")
s=s.replace("def fig(n,caption):doc.add_picture(str(OUT/f'fig{n}.png'),width=Cm(14));doc.add_paragraph(caption,'Caption')", """def fig(n,caption):
 doc.add_picture(str(OUT/f'fig{n}.png'),width=Cm(15.5))
 doc.paragraphs[-1].alignment=1
 doc.paragraphs[-1].paragraph_format.keep_with_next=True
 doc.add_paragraph(caption,'Caption')""")
s=s.replace("tb.style='Light Shading'","tb.style='Light Shading'\n for c in tb.rows[0].cells:\n  sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E9EFF3');c._tc.get_or_add_tcPr().append(sh)")
replacements={
'概率损失显著低于先验基线的观测值':'平均对数损失低于先验基线',
'重复证据改变后验并损害分类':'重复特征改变后验及分类结果',
'本研究采用可复核的计数推导、阈值比较和重复特征干预，连接作业要求的七项知识点；教学手算数据与UCI记录始终分开。':'本实验首先通过计数推导核对后验概率，再比较阈值对错误类型的影响，最后通过复制特征检验模型对重复证据的敏感性，并在固定测试集上评价预测表现。独立设计的教学手算数据与UCI记录分别分析，不合并用于训练。',
'每行是一个sample；发热、恶心、腰痛、尿急、排尿痛、尿道灼痛分别为feature；bladder_inflammation为label。':'每行代表一条样本记录（sample）；六项特征（feature）依次为发热、恶心、腰痛、尿急、排尿痛和尿道灼痛；标签（label）为膀胱炎症（bladder_inflammation），1表示阳性，0表示阴性。',
'πc为先验，θcj为类内症状出现概率。':'πc为类别先验概率，θcj为给定类别c时第j项症状出现的概率；nc为类c的训练记录数，kcj为其中第j项症状出现的记录数，n=72。',
'六个二元症状有64种组合。':'理论上，六个二元症状有64种可能组合。',
'表2　训练、验证及固定测试的结果。':'表2　分类准确率、平均对数损失与混淆计数。',
'图2　验证集阈值与敏感度、特异度。全部点来自同一24条记录和固定概率；竖虚线标记预设规则选出的0.5。连线仅帮助追踪离散网格。':'图2　验证集上的阈值选择。敏感度和特异度分别以12条真实阳性、12条真实阴性为分母。浅绿色带标示比例≥0.90的区域，仅用于对照敏感度约束；竖虚线为选定阈值0.50。连线连接预设网格点，不表示连续估计。',
'图3　验证记录的重复特征干预。横轴为六输入概率，纵轴为额外复制五次腰痛后的概率；红色为真实阳性，蓝色为真实阴性，重合点表示相同输出。对角线为不变参考，横竖线为0.5阈值。':'图3　重复腰痛特征对验证后验的影响。24条记录按相同的原概率、复制后概率及真实类别聚合；点面积随记录数增加，未删除记录或添加抖动。蓝色圆点为阴性，赭色方点为阳性。对角虚线表示概率不变，横竖实线为0.50阈值；跨越决策边界的6条记录由正确变为错误。',
'图4　固定测试的24条概率输出。红色阳性、蓝色阴性；横轴为排序后记录序号，不表示时间。阈值0.5把两类正确分开。':'图4　固定测试集的逐记录概率。每个标记对应一条记录，按预测概率升序排列；竖线仅辅助读取概率高度。蓝色圆点为真实阴性，赭色方点为真实阳性。虚线为0.50阈值；序号不代表原始ID或测量时间。',
'可靠性分箱中，区间{rr["bin"]}含{rr.n}条验证记录':'为进一步检查概率幅度，在预设分箱[0, 0.2]中，共有{rr.n}条验证记录',
'独立乘积计算与程序输出之差':'按公式逐项计算的结果与模型接口输出之差',
'程序与独立手算一致':'按公式逐项计算的结果与模型接口输出一致',
'八条独立教学记录':'另行构造的八条教学记录',
'同源已见模式的新行':'来自同一数据源、具有已见症状模式的留出记录',
'而非对材料开发者完全盲法的外部验证':'不能视为对材料开发者保持盲态的测试，更不构成外部验证',
'其全部输入模式在训练出现':'其全部输入模式均在训练集中出现',
'概率表达模型的证据程度':'概率是在模型假设下对类别的概率估计',
'本页按新版工作单编号整理答案':'以下按新版工作单编号整理计算与解释',
'混淆矩阵把错误分为漏诊与误报':'混淆矩阵区分正确分类、漏诊与误报',
'本实验完成了同源教学数据上的建模闭环':'这一结论仅适用于本次固定划分下的教学记录',
}
for old,new in replacements.items():s=s.replace(old,new)
# Make three displayed formulas native Word equations with explicit scripts.
s=s.replace("def para(s):doc.add_paragraph(s)","""def para(s):
 if s.startswith(('πc =','wc(x) =','p(x) =')):
  p0=doc.add_paragraph();p0.alignment=1
  linear={'πc =':'π_c=n_c/n;  θ_(cj)=(k_(cj)+1)/(n_c+2)', 'wc(x) =':'w_c(x)=π_c ∏_(j=1)^6 θ_(cj)^(x_j) (1−θ_(cj))^(1−x_j)', 'p(x) =':'p(x)=w_1(x)/(w_0(x)+w_1(x));  ŷ=1[p(x)≥t]'}
  txt=next(v for k,v in linear.items() if s.startswith(k))
  math=OxmlElement('m:oMath');mr=OxmlElement('m:r');mt=OxmlElement('m:t');mt.text=txt;mr.append(mt);math.append(mr);p0._p.append(math)
 else:doc.add_paragraph(s)""")
s=s.replace("刘群_朴素贝叶斯课程论文.docx","刘群_朴素贝叶斯论文_精修版.docx")
(out/'build.py').write_text(s,encoding='utf8')
print(out)
