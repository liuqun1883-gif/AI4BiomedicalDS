from pathlib import Path
import sys,json,io,contextlib,os,hashlib
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'.runtime'))
BASE=ROOT/'7. Naive-Bayes'; OUT=Path(__file__).parent
sys.path.insert(0,str(BASE/'scripts'))
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from lab_utils import *
from docx import Document
from docx.shared import Inches,Pt,Cm,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
tr=pd.read_csv(BASE/'data/student/train.csv'); va=pd.read_csv(BASE/'data/student/validation.csv')
model=fit_model(tr); p=model.predict_proba(va[FEATURES])[:,1]
tt=threshold_table(va.bladder_inflammation,p); t=choose_threshold(tt)
freeze={'author':'刘群','student_id':'38720260158062','date':'2026-11-18','target':'bladder_inflammation','features':FEATURES,'alpha':1,'threshold':t,'train_ids':tr.sample_id.tolist(),'train_sha256':hashlib.sha256((BASE/'data/student/train.csv').read_bytes()).hexdigest(),'rule':'validation sensitivity >= .90; maximize specificity; closest to .5; smaller threshold','refit':False}
(OUT/'固定方案.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2),encoding='utf8')
te=pd.read_csv(BASE/'data/student/locked-test-features.csv').merge(pd.read_csv(BASE/'data/teacher/locked-test-labels.csv'),on='sample_id',validate='one_to_one')
pt=model.predict_proba(te[FEATURES])[:,1]; ptr=model.predict_proba(tr[FEATURES])[:,1]
hand,w,hp=hand_calculation(tr,[0,0,0,1,1,1]); assert abs(hp-model.predict_proba(pd.DataFrame([[0,0,0,1,1,1]],columns=FEATURES))[0,1])<1e-12
stats=pd.DataFrame([dict(model=k,**scores(f.bladder_inflammation,pr,t)) for k,f,pr in [('NB train',tr,ptr),('NB validation',va,p),('Prior validation',va,np.full(len(va),tr.bladder_inflammation.mean())),('NB test',te,pt)]])
dup=[]; dp=None
for n in [0,1,5]:
 a=tr[FEATURES].copy(); b=va[FEATURES].copy()
 for i in range(n): a[f'copy{i}']=a.lumbar_pain;b[f'copy{i}']=b.lumbar_pain
 m=BernoulliNB(alpha=1,binarize=None).fit(a,tr.bladder_inflammation); z=m.predict_proba(b)[:,1]
 dup.append(dict(copies=n,**scores(va.bladder_inflammation,z)))
 if n==5: dp=z
dup=pd.DataFrame(dup); rel=reliability(va.bladder_inflammation,p)
for name,frame in [('metrics',stats),('thresholds',tt),('hand',hand),('duplicates',dup),('reliability',rel)]:frame.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
pd.DataFrame({'sample_id':te.sample_id,'y':te.bladder_inflammation,'p':pt,'prediction':(pt>=t).astype(int)}).to_csv(OUT/'test_predictions.csv',index=False)
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Microsoft YaHei','Arial'],'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
def save(name):
 plt.savefig(OUT/(name+'.png'),dpi=300,bbox_inches='tight');plt.savefig(OUT/(name+'.svg'),bbox_inches='tight');plt.savefig(OUT/(name+'.pdf'),bbox_inches='tight');plt.close()
fig,ax=plt.subplots(figsize=(7,2.5));ax.axis('off')
for x,title,sub in [(0.02,'训练 72 条','估计先验与症状概率'),(.36,'验证 24 条','按预设规则选择阈值'),(.70,'测试 24 条','方案固定后评价一次')]:
 ax.text(x,.65,title,fontsize=15,weight='bold',transform=ax.transAxes);ax.text(x,.38,sub,fontsize=10,transform=ax.transAxes)
ax.text(.29,.60,'→',fontsize=23,transform=ax.transAxes);ax.text(.63,.60,'→',fontsize=23,transform=ax.transAxes)
ax.text(.02,.06,'六项二元症状 → Bayes 后验概率 → 阈值类别 → 概率损失与分类指标',transform=ax.transAxes)
save('fig1')
fig,ax=plt.subplots(figsize=(6.5,3.2));ax.plot(tt.threshold,tt.sensitivity,'o-',label='敏感度',color='#205577');ax.plot(tt.threshold,tt.specificity,'s-',label='特异度',color='#b34b40');ax.axvline(t,color='gray',ls='--');ax.set(xlabel='验证集决策阈值',ylabel='比例',ylim=(-.04,1.09));ax.legend(loc='lower right');save('fig2')
fig,ax=plt.subplots(figsize=(6.5,3.2));ax.scatter(p,dp,c=va.bladder_inflammation,cmap='coolwarm',s=65,alpha=.8);ax.plot([0,1],[0,1],'--',color='gray');ax.axhline(.5,color='gray',lw=.6);ax.axvline(.5,color='gray',lw=.6);ax.set(xlabel='原六特征模型的阳性概率',ylabel='额外复制腰痛五次后的概率',xlim=(-.03,1.03),ylim=(-.03,1.03));save('fig3')
fig,ax=plt.subplots(figsize=(6.5,3.0));ix=np.argsort(pt);ax.scatter(np.arange(24),pt[ix],c=te.bladder_inflammation.to_numpy()[ix],cmap='coolwarm',s=55);ax.axhline(.5,color='gray',ls='--');ax.set(xlabel='按预测概率排序的测试记录',ylabel='阳性概率',ylim=(-.03,1.03));save('fig4')
doc=Document();sec=doc.sections[0];sec.top_margin=Cm(2);sec.bottom_margin=Cm(1.8);sec.left_margin=Cm(2.1);sec.right_margin=Cm(2.1)
for sn in ['Normal','Title','Heading 1','Heading 2','Caption']:
 st=doc.styles[sn];st.font.name='Times New Roman';st._element.rPr.rFonts.set(qn('w:eastAsia'),'宋体');st.font.color.rgb=RGBColor(0,0,0)
doc.styles['Normal'].font.size=Pt(10.5);doc.styles['Normal'].paragraph_format.line_spacing=1.08;doc.styles['Normal'].paragraph_format.space_after=Pt(4)
doc.styles['Title'].font.size=Pt(22);doc.styles['Heading 1'].font.size=Pt(14)
for st in doc.styles:
 for border in list(st.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
doc.styles['Heading 1'].paragraph_format.space_before=Pt(8);doc.styles['Heading 1'].paragraph_format.space_after=Pt(5)
footer=sec.footer.paragraphs[0];footer.alignment=2;footer.add_run('刘群  ·  38720260158062    ');field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
def para(s):doc.add_paragraph(s)
def head(s):doc.add_heading(s,1)
def fig(n,caption):doc.add_picture(str(OUT/f'fig{n}.png'),width=Cm(14));doc.add_paragraph(caption,'Caption')
def table(headers,rows):
 tb=doc.add_table(rows=1,cols=len(headers));tb.style='Light Shading'
 for c,s in zip(tb.rows[0].cells,headers):c.text=str(s)
 for row in rows:
  for c,s in zip(tb.add_row().cells,row):c.text=str(s)
def page():
 p=doc.add_paragraph();p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=Pt(1);r=p.add_run();r.font.size=Pt(1)
 from docx.enum.text import WD_BREAK
 r.add_break(WD_BREAK.PAGE)
doc.add_paragraph('朴素贝叶斯症状分类的概率解释与泛化边界','Title')
para('刘群　学号 38720260158062\n机器学习基础与朴素贝叶斯课程论文　2026年11月18日')
head('摘要')
para(f'分类正确并不充分说明概率预测可靠。本研究按照课程规定，对 UCI Acute Inflammations 的120条专家构造记录进行六症状二元编码，沿用72／24／24的训练、验证和测试划分。仅用训练集估计 Bernoulli 朴素贝叶斯参数，以验证集敏感度不低于0.90且特异度最大的预设规则选择阈值。选中阈值为{t:.2f}，验证与测试均正确分类24条记录，平均对数损失分别为{stats.iloc[1].log_loss:.6f}和{stats.iloc[3].log_loss:.6f}。额外复制腰痛五次后，验证准确率降至{dup.iloc[2].accuracy:.2f}，表明重复证据会改变后验。所有测试症状模式均在训练中出现，因此结果支持同源规则再现，不能据此推断跨患者或跨医院表现。')
para('关键词　Bernoulli朴素贝叶斯；条件独立；对数损失；分类评价；泛化')
head('引言')
para('医学预测模型需要把输入、概率和决策区别开来。一个模型可以给出正确类别，却仍对风险幅度表达不准；一个高准确率模型也可以遗漏全部少数类。本课程实验以六项症状预测膀胱炎症，研究数据如何转化为参数、参数如何产生后验，以及不同评价量分别回答什么问题。')
para('朴素贝叶斯以给定类别后的条件独立近似简化联合概率[2]。该近似允许用少量计数建模，也使重复输入可能被当作多次证据。本研究采用可复核的计数推导、阈值比较和重复特征干预，连接作业要求的七项知识点；教学手算数据与UCI记录始终分开。')
fig(1,'图1　实验流程与数据职责。训练估参、验证选阈值和最终测试各司其职；测试后不重训或更换阈值。')
page();head('材料与方法')
para('数据由Jacek Czerniak提供，采用CC BY 4.0许可[1]。120条记录由专家构造用于专家系统测试，不视为120名独立患者。每行是一个sample；发热、恶心、腰痛、尿急、排尿痛、尿道灼痛分别为feature；bladder_inflammation为label。体温≥38°C编码为发热。ID、原始体温和两个疾病标签均不进入六输入模型。')
para('沿用课程CSV的固定分层划分，两步拆分随机种子均为7。训练集72条，其中阴性37、阳性35；验证集24条，其中两类各12。三集合ID互不相交，不进行重复行删除。验证集24条的二元模式均在训练出现，故“新行”与“新组合”并不等同。')
head('参数估计与后验推导')
para('记类别为c∈{0,1}，症状为x∈{0,1}⁶。πc为先验，θcj为类内症状出现概率。训练过程由有标签记录估计以下参数；预测固定这些参数，不需要新记录的真实标签。')
para('πc = nc / n；　θcj = (kcj + 1) / (nc + 2)　　　　　　　　　(1)')
para('wc(x) = πc ∏ⱼ θcjˣʲ (1 − θcj)¹⁻ˣʲ　　　　　　　　　　　(2)')
para('p(x) = w1(x) / [w0(x) + w1(x)]；　ŷ = 1[p(x) ≥ t]　　　　(3)')
para('六个二元症状有64种组合。条件独立近似把联合似然转为六项乘积；假设针对同一类别内部，并非要求全体记录中症状独立。无症状时必须使用补概率。Laplace平滑α=1避免零计数产生零乘积，但不消除特征依赖。')
table(['症状','x','类0计数','类1计数','类0似然项','类1似然项'],[[f,int(hand.iloc[j].x),int(hand.iloc[j].count_one),int(hand.iloc[j+6].count_one),f'{hand.iloc[j].likelihood_term:.6f}',f'{hand.iloc[j+6].likelihood_term:.6f}'] for j,f in enumerate(['发热','恶心','腰痛','尿急','排尿痛','尿道灼痛'])])
para(f'表1　指定输入(0,0,0,1,1,1)的手算依据。π0=37/72，π1=35/72；w0={w[0]:.12f}，w1={w[1]:.12f}，故p={hp:.10f}，在t=0.5时判为阳性。独立乘积计算与程序输出之差小于10⁻¹²。')
head('评价方案')
para('阈值网格为0.05、0.10、0.20、0.30、0.50、0.70、0.80、0.90、0.95。先保留验证敏感度≥0.90的值，再最大化特异度；并列时取最接近0.5者，仍并列取较小者。方案写入固定方案.json后，读取已获准释放的测试标签；保持原训练集模型，不合并验证集重训。')
page();head('结果')
head('概率损失与类别判断提供互补证据')
para('平均对数损失L=−n⁻¹Σ[y ln p+(1−y)ln(1−p)]以自然对数计，越小越好[3]。NB采用计数估参；本实验并未用梯度下降最小化验证损失。先验基线对每条验证记录输出35/72，在0.5阈值下全部判阴性。')
table(['模型与集合','准确率','平均log loss','TN / FP / FN / TP'],[[r.model,f'{r.accuracy:.3f}',f'{r.log_loss:.6f}',f'{r.tn} / {r.fp} / {r.fn} / {r.tp}'] for _,r in stats.iterrows()])
para('表2　训练、验证及固定测试的结果。NB验证准确率为1，同时概率损失显著低于先验基线的观测值。验证损失略低于训练损失并不矛盾：不同样本集合的观测损失不必具有固定排序。本实验未进行差异显著性检验。')
head('阈值改变错误分布而不改变概率')
fig(2,'图2　验证集阈值与敏感度、特异度。全部点来自同一24条记录和固定概率；竖虚线标记预设规则选出的0.5。连线仅帮助追踪离散网格。')
para('阈值0.1时FP=5、FN=0，敏感度1、特异度7/12；阈值0.5时FP=FN=0；阈值0.9时FP=0、FN=2，敏感度10/12、特异度1。减少漏诊需要同时考察真实阳性的检出比例及误报负担，不能仅按accuracy选择。')
para('混淆矩阵以真实类别为行、预测类别为列。Accuracy=(TP+TN)/n；敏感度=TP/(TP+FN)；特异度=TN/(TN+FP)；精确率=TP/(TP+FP)；F1=2TP/(2TP+FP+FN)。敏感度以真实阳性为分母，精确率以预测阳性为分母。先验基线没有预测阳性，precision未定义，不能把NaN写成测得的零。')
page();head('重复证据改变后验并损害分类')
fig(3,'图3　验证记录的重复特征干预。横轴为六输入概率，纵轴为额外复制五次腰痛后的概率；红色为真实阳性，蓝色为真实阴性，重合点表示相同输出。对角线为不变参考，横竖线为0.5阈值。')
idx=int(np.argmax(abs(dp-p)))
para(f'记录{va.iloc[idx].sample_id}的概率从{p[idx]:.6f}变为{dp[idx]:.6f}。额外复制五次后，准确率由1降至{dup.iloc[2].accuracy:.2f}，log loss由{dup.iloc[0].log_loss:.6f}升至{dup.iloc[2].log_loss:.6f}。复制没有增加测量信息，却把腰痛的似然比重复相乘，改变了证据权重。一次复制的log loss为{dup.iloc[1].log_loss:.6f}，因此不能断言任何复制都必然使每项指标变差。')
rr=rel[rel.n>0].iloc[0]
para(f'可靠性分箱中，区间{rr["bin"]}含{rr.n}条验证记录，平均预测概率为{rr.mean_probability:.6f}，观察阳性比例为{rr.observed_fraction:.6f}。该比较检查概率幅度与观测频率是否一致；空箱没有信息，小样本非空箱也不足以证明总体校准。完整分箱表随实验输出保存。')
head('固定测试评价与泛化边界')
fig(4,'图4　固定测试的24条概率输出。红色阳性、蓝色阴性；横轴为排序后记录序号，不表示时间。阈值0.5把两类正确分开。')
para(f'测试TN=12、FP=0、FN=0、TP=12，accuracy为24/24，敏感度与特异度均为12/12。平均log loss为{stats.iloc[3].log_loss:.6f}，与验证结果的分类指标相同，但概率损失不同。测试有8种二元模式，24条记录的模式均在训练出现。其结果描述同源已见模式的新行，并不检验未见组合或跨医院迁移。')
page();head('讨论')
para('本实验的主要认识是分类、概率和泛化分别对应不同层次的问题。高准确率只描述给定阈值下的类别吻合；log loss进一步考虑模型分给真实类别的概率；分箱比较检查观测频率与概率幅度；划分与组合覆盖则界定评价对象。重复腰痛的实验把条件独立假设的后果显式化，使“模型从数据学习”具体落实到参数和证据权重。')
para('1000条记录中若只有10条阳性，全部预测阴性即可获得99%准确率，却检出0条阳性。此时敏感度0、特异度1、precision未定义。在早期筛查的假设用途下，漏掉需要进一步检查的对象是关键问题；同时误报也增加后续检查负担。这里的用途讨论用于解释指标，不构成该模型的临床部署建议。')
para('局限来自数据构造和评价范围。记录由专家设计，不能据行数推断独立患者数；二值化后输入支持集很小；课程材料编写者在早期探索中已查看过测试结果，因此该测试是模拟冻结流程的固定教学测试，而非对材料开发者完全盲法的外部验证。即使观察到零错误，有限样本仍不能保证未来永不出错。')
para('方法上的后续问题应针对这些局限展开：获得独立来源的数据，明确患者和测量单位，并考察未见症状组合及概率校准。当前结果不足以判断这种扩展后性能能否保持，也没有证据把重复模式的分类成功解释为新的疾病机制。')
head('结论')
para('六症状朴素贝叶斯通过训练计数、平滑和Bayes归一化获得可复核的概率预测。固定教学测试上的全部分类正确，与重复特征造成的性能下降并存。可靠评价必须同时解释错误分母、概率质量和输入覆盖范围；本实验完成了同源教学数据上的建模闭环。')
head('数据与代码可用性')
para('原始数据来源见文献[1]，课程进行了二元化和固定划分。本次交付包含可执行Notebook、固定方案、逐记录测试预测、指标表与图表源文件。分析仅使用课程提供的数据，不新增或伪造样本。')
head('AI使用说明')
para('AI协助梳理作业要求、执行代码、复核数值、制作图表和组织论文文字。本文不声称作者已经亲自完成尚未确认的手算核验；提交前应由刘群核对表1后验、教学混淆矩阵和log loss，并补充自己的初始预想与学习反思。')
head('参考文献')
para('[1] J. Czerniak. Acute Inflammations. UCI Machine Learning Repository (2009). DOI: 10.24432/C5V59S. CC BY 4.0. 数据来源与构造说明据课程data/README.md核对。')
para('[2] scikit-learn developers. Naive Bayes. https://scikit-learn.org/stable/modules/naive_bayes.html. 算法实现对应课程lab_utils.py。')
para('[3] scikit-learn developers. Model evaluation: quantifying the quality of predictions. https://scikit-learn.org/stable/modules/model_evaluation.html.')
page();head('补充材料 七项工作单的计算与解释')
para('本页按新版工作单编号整理答案，正文中的表1、图1—4和指标CSV提供实验依据。主观初始预想不能事后伪造，下述方法是可采用的方案，不代表作者实验前已有的想法。')
head('任务1与2 数据模型及学习')
para('1.1 可先按完全相同的症状组合统计阳性比例；需统计组合总数和阳性数。若找不到相同组合，可退回训练先验，并明确该规则的局限。1.2 一条记录是专家构造病例描述；每项症状是特征；膀胱炎症是标签。模型接收6个数，标签不能同时作输入，否则预测依赖待预测信息。p=0.8是模型概率，ŷ=1是阈值决策。只有症状清单尚未定义输入到输出的关系。')
para('2.1 八条独立教学记录：P̂(y=1|x=0)=1/3；P̂(y=1|x=1)=4/5=0.8。新输入x=1时预测阳性，不需预知y。2.2 加入(x=1,y=0)后重估得到4/6=2/3；固定模型仅预测时不更新频率。训练用(x,y)改变参数，预测用固定参数处理x，泛化评价用未参与开发的数据比较预测和真实标签。训练成绩不能代替泛化评价。')
head('任务3与4 数据职责与Bayes计算')
para('3.1 同一数据同时估参、选阈值和报告性能会偏向已见数据；看测试后挑阈值使测试成为开发数据。3.2 train估参、validation选阈值、test最终评价；测试后换特征也使其失去独立评价角色。train=72、validation=24，ID交集为空，验证24条模式均已见。新行可重复旧模式；新组合含未知输入；跨医院还可能改变人群与测量机制。')
para('4.1 教学数据P(Y=1)=5/8，P(x=1|Y=1)=4/5，P(x=1|Y=0)=1/3。后验=(4/5×5/8)/[(4/5×5/8)+(1/3×3/8)]=4/5，与直接频率一致。条件概率反向时条件集合和分母改变，不能直接互换。4.2 六二元输入有64种组合；有症状乘θ，无症状乘1−θ。条件独立针对给定Y后的类内关系。4.3 训练计数、权重和后验见表1，程序与独立手算一致。4.4 复制腰痛的记录及概率见图3正文，原值与复制值跨越0.5时类别改变；重复似然并不等于新增信息。')
head('任务5 损失计算')
para('5.1 教学模型A对a、b的类别分别为1、0，模型B亦为1、0，accuracy均为1。LA=−ln0.6=0.510826，LB=−ln0.9=0.105361。真实y=0时p=0.6和0.99均分错，损失分别为−ln0.4=0.916291与−ln0.01=4.605170，自信错误惩罚更大。5.2 单样本loss衡量一次概率误差，平均loss汇总全体；阈值错误数忽略概率幅度。NB学到先验和类内症状概率，不能把验证标签并入估参再称其未见。训练与验证对照见表2，NB在类别及概率两方面均优于先验基线。')
page();head('任务6与7 分类指标与综合解释')
para('6.1 八条教学预测在t=0.5时：TP=a,b；FN=c,d；FP=e；TN=f,g,h。矩阵[[3,1],[2,2]]，accuracy=5/8=0.625，敏感度2/4=0.5，特异度3/4=0.75，precision=2/3，F1=4/7。敏感度分母是a,b,c,d；precision分母是a,b,e。6.2 t=0.3时TP=3、FN=1、FP=3、TN=1，敏感度3/4，特异度1/4；g恰等于阈值也为阳性。概率不变，决策映射改变。')
table(['验证模型 t=0.5','TN','FP','FN','TP','Acc','Sens','Spec','Prec','F1'],[['Prior',12,0,12,0,.5,0,1,'未定义',0],['NB',12,0,0,12,1,1,1,1,1]])
para('6.3 三个要求阈值的错误计数见图2正文；选中0.5，它满足敏感度约束、达到最大特异度，且并列时距0.5最近。本验证集的优点是未观察到漏诊或误报；可能错误包括对未知输入的漏诊和概率偏差，验证全对不能排除这些错误。')
para('7.1 不平衡教学例子的accuracy=0.99、敏感度0、特异度1、precision未定义，检出0条阳性。7.2 全对的教学模型A、B仍有不同log loss；复制输入不增加信息却改变概率，说明类别正确并非概率可靠。可靠性非空箱的样本量、均值和观察比例见正文与reliability.csv。7.3 固定目标、六特征、α=1、阈值0.5和训练ID保存在固定方案.json，日期2026-11-18；测试计数及分母见图4正文。验证与测试分类指标相同而log loss不同。测试24条症状模式均已见，只回答同源保留行上的表现。')
head('一页综合说明')
para('数据模型规定输入与输出之间的可计算关系。本实验以六症状x为输入，用72条训练记录估计π和θ，再按Bayes公式计算p，最后用0.5阈值得到类别。以指定六位输入为例，p≈0.986576，因此判阳性；概率表达模型的证据程度，类别表达决策。')
para('训练改变参数，预测固定参数；新输入本身不会自动更新模型。验证集24条用于选择阈值，测试24条在方案冻结后才作评价。对照八条手算记录，训练加入一条阴性后概率由4/5变为2/3，清楚显示重新估参与单次预测的差别。')
para('Bayes后验把先验与似然结合后归一化。条件独立使六项似然可以相乘，但复制腰痛会重复计算同一证据。对数损失保留概率幅度：同为正确类别，0.9相对于0.6给真实类更高概率，损失从0.510826降为0.105361。')
para('混淆矩阵把错误分为漏诊与误报。八条教学例子在0.5阈值下敏感度2/4、精确率2/3，二者分母不同；在1000条极不平衡记录中，99%准确率仍可漏掉全部10条阳性。固定测试全对也只能说明当前数据的分类：其全部输入模式在训练出现，不能自动证明跨医院泛化。')
para('个人反思与亲自核验记录：由刘群本人补写实验前的原始想法、核算过程和仍未弄懂的问题；本报告不代造个人经历。')
doc.save(OUT/'刘群_朴素贝叶斯课程论文.docx')
(OUT/'复现结果.json').write_text(stats.to_json(orient='records',force_ascii=False,indent=2),encoding='utf8')
print(stats.to_string(index=False));print('DOCX saved')

