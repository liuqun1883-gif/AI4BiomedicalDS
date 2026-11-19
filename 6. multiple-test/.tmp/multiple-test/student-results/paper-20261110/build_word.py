from pathlib import Path
import re,html,json,copy
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT

R=Path(__file__).resolve().parent
OUT=R.parents[3]/'output/multiple-testing-paper/revised';OUT.mkdir(parents=True,exist_ok=True)
# Read the reviewed manuscript through its original structured authoring calls.
src=(R/'build_paper.py').read_text(encoding='utf-8')
prefix,body=src.split("\np('RESEARCH ARTICLE",1)
ns={'__file__':str(R/'build_paper.py')};exec(prefix,ns)
blocks=[]
ns.update(p=lambda text,style='body':blocks.append(['p',style,text]),
 h=lambda text:blocks.append(['p','h1',text]),sub=lambda text:blocks.append(['p','h2',text]),
 eq=lambda text:blocks.append(['eq',text]),page=lambda:blocks.append(['page']),
 table=lambda headers,rows,widths=None:blocks.append(['table',headers,rows,widths]),
 fig=lambda name,caption,height:blocks.append(['fig',name,caption,height]))
exec("p('RESEARCH ARTICLE"+body.split('\ndef header',1)[0],ns)

replacements={
 '从统计显著到可验证发现：<br/>白血病表达数据的多重检验控制':'白血病表达差异筛选中的多重检验控制',
 'From statistical significance to reproducible candidates:<br/>multiple-testing control in leukemia expression data':'Multiple-testing control in leukemia expression screening',
 '第 6 讲 · 多重检验校正　|　2026 年 11 月 10 日':'刘群　｜　学号 38720260158062<br/>生物医学数据科学　第 6 讲 多重检验校正　｜　2026 年 11 月 10 日',
 '显著结果数量不能直接代表真实发现':'显著结果数量不能直接代表真实差异的数量',
 '控制错误的检出力代价':'错误控制与检出力的权衡',
 '把偶然显著成为必然需要处理的问题':'使偶然显著成为需要处理的问题',
 '也使偶然显著成为必然需要处理的问题':'也增加了偶然显著结果被误当作可靠发现的风险',
 '这种算法计算错误':'一种算法计算错误',
 '全零模拟中，1,000 项检验平均产生 49.944 个原始显著结果；校正将其降至约 0.05 个。':'在 1,000 次全零模拟中，每次 1,000 项检验平均产生 49.944 个原始显著结果；Bonferroni 和 BH 校正后分别为 0.051 和 0.052 个。',
 '七项通过留出验证':'七项候选通过预定留出判据',
 '首次校正后 R=0 不能说明方法绝不出错':'首次模拟中校正后 R=0，不能说明方法绝不出错',
 '降至 0.0034':'降至 0.00335',
 '控制 FWER 的拒绝集合':'满足 FWER 控制规则的拒绝集合',
 '候选进入生物学研究仍需质控':'候选用于后续生物学研究仍需质控',
 '进入生物研究前仍需重新设计并预注册质控及注释方案':'开展新的生物学研究前，应另行预定质量控制和探针注释方案，不得追溯性改变本次家族以争取显著结果',
 '本例仅说明控制目标，不构成对某项临床试验设计的建议。':'这一例子说明，控制目标应由研究主张和错误代价决定，而不是由哪种方法得到更多显著结果决定。',
 '正错误发现率（pFDR）框架有关':'条件错误发现率框架有关，其中 pFDR=E(V/R｜R>0)',
 '常通过估计真实零假设比例 π₀ 形成自适应估计':'其常见估计方法通过估计真实零假设比例 π₀ 形成自适应结果',
 '不是前瞻性试验注册或新队列盲法':'不等同于前瞻性注册或对新队列实施盲法',
 '完整数值函数直接复用课程 Notebook':'数值计算直接复用课程 Notebook 中的函数',
 '它们解决的问题不同，不能彼此替代':'因此，显著性、效应、机制和可重复性应作为相互补充的证据分别报告',
}
def revise(x):
 for old,new in replacements.items():x=x.replace(old,new)
 return x
captions={
 'fig1_simulation':'图 1　全零与部分真信号模拟中的错误控制及检出力。（a）全零情境下每轮原始显著数的分布，虚线为理论均值 50。（b）错误发现率 FDR。（c）家族错误率 FWER。（d）检出力。b、d 使用对数纵轴，以显示弱信号及低错误率区间；c 使用线性纵轴。点为 1,000 次重复均值，误差线为 ±1.96 个蒙特卡洛标准误，过短时可能被点遮盖；b、c 的水平点线为名义水平 0.05。每轮两组观测数为 27 和 11，δ 为 100 项真实信号的均值偏移。全零检出力无定义，未绘制。',
 'fig2_discovery':'图 2　完整检验家族内的证据分布与选择偏倚。（a）发现集 7,129 个探针的原始 p 值。（b）Cohen d 与 −log₁₀(p)；橙色为完整家族 BH≤0.05 的探针，灰色为其余探针。（c）相同数据与名义水平下的发现数，计数无重复误差线。（d）按原始 p 排序的前 20 项，分别采用完整家族校正及错误的选择后校正。所有散点均保留；标准化效应仅作描述，不等同于生物学重要性。',
 'fig3_validation':'图 3　全部锁定候选的效应与留出判据。（a、b）发现集和留出集的 AML−ALL 均值差及逐项 95% Welch 置信区间，两面板使用相同横轴尺度；组样本量依次为 AML/ALL=11/27 和 14/20。（c）留出检验在 10 项候选家族中的 Bonferroni adjusted p，竖虚线为 0.05。蓝色圆点表示方向一致且通过校正阈值，橙色方点表示未通过。逐项区间不具有家族同时覆盖或选择后覆盖保证，不能代替 c 中的判据。',
}
for b in blocks:
 if b[0]=='p':b[2]=revise(b[2])
 elif b[0]=='fig':b[2]=captions[b[1]]
# Add bridges without changing the scientific protocol.
for b in blocks:
 if b[0]=='p' and b[2].startswith('每种情境均有'):
  b[2]='上述错误率是重复研究的性质，不能由一次筛选直接观察。因此，先在真值已知的模拟中检验这些区别。'+b[2]
 if b[0]=='p' and b[2].startswith('发现集包含 ALL'):
  b[2]='模拟能够区分真、假发现，而真实表达数据中各项零假设的真值未知。以下分析因此报告发现数与效应证据，不将发现数解释为真阳性数。'+b[2]
 if b[0]=='p' and b[2].startswith('该探针在 AML 中的表达均值'):
  b[2]='该探针在 AML 中的平均表达低于 ALL。完整家族校正及留出结果支持其作为后续验证候选。其发现集效应绝对值较大，与筛选后效应可能被高估的现象相容，但也可能由抽样波动或样本构成差异造成，不能仅凭两个估计值证明选择偏倚。'
 if b[0]=='p' and b[2].startswith('ν 按 Welch'):
  b[2]='ν 为 Welch–Satterthwaite 近似自由度，由两组样本方差及样本量计算。Cohen d 的分母采用按自由度加权的合并组内标准差，仅作描述，不改变 Welch 检验允许不等方差的设定。本文的均值差均使用原表达尺度，不称为表达倍数变化；逐项区间不提供家族同时覆盖或筛选后覆盖保证。'
 if b[0]=='p' and b[2].startswith('run_analysis.py 复用'):
  b[2]='统计代码复用课程 Notebook 的数值函数，图表均由保存的结果表或原始表达数据绘制。修订图另提供 PDF、SVG 和高分辨率 PNG，Word 中的图可直接替换。正文、结果表和编号公式保留为可编辑对象。'
 if b[0]=='p' and b[2]=='稿件性质与使用说明':b[2]='作者与稿件说明'
 if b[0]=='p' and b[2].startswith('本稿采用研究论文的摘要'):
  b[2]='作者为刘群，学号 38720260158062。本稿为中文课程复现与再分析论文，采用学术论文结构及单栏排版。分析代码、文字润色和排版由 AI 辅助完成；统计图均来自真实计算结果，未用生成式图像替代数据。作者提交前应核对结果，并依课程规定披露 AI 使用情况。'
 if b[0]=='p' and b[2].startswith('原始数据未修改'):
  b[2]='原始数据与正式课程 Notebook 均未修改。完整分析表、锁定记录及原始复现脚本保存在随附复现材料中。此次修订只调整文字、图表表达与文档格式，没有改变发现家族、候选名单、验证判据或统计结果。'

# Insert a distinct raw-observation view immediately after the validation section.
idx=next(i for i,b in enumerate(blocks) if b[:2]==['p','h1'] and b[2].startswith('6　'))
extra=[['p','h1','5.1　从原始观测理解验证结果'],
 ['p','body','为使均值差及区间能够回到原始观测，图 4 展示排序首位的 U22376_cds2_s_at，以及排序末位、未通过留出判据的 X74262_at。两者仅用于说明样本分布，不参与重新选择候选或修改判据。'],
 ['fig','fig4_samples','图 4　通过与未通过留出判据候选的原始表达分布。（a、b）U22376_cds2_s_at 的发现集与留出集；（c、d）X74262_at 的对应分布。每个散点是一份表达样本，横向抖动仅为避免重叠；未删除离群观测。箱体为第 25–75 百分位数，箱内横线为中位数，须延伸至 1.5 倍四分位距范围内的最远观测；所有须外观测仍由散点显示。同一探针两面板共享纵轴尺度。图中不添加新的显著性检验，正式验证判据见图 3。',350],
 ['p','body','X74262_at 的留出均值差仍与发现方向一致，但差异幅度减小，且候选家族 Bonferroni adjusted p=0.260，未达到预定阈值。这说明方向一致本身不等于通过验证；同时，未通过阈值也不能直接证明该探针没有真实差异。两类候选均需结合个体差异、样本构成与后续独立证据评价。'],['page']]
blocks[idx:idx]=extra

doc=Document();sec=doc.sections[0]
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=Inches(.7);sec.bottom_margin=Inches(.65);sec.left_margin=Inches(.8);sec.right_margin=Inches(.8)
sec.header_distance=Inches(.28);sec.footer_distance=Inches(.28)
def setfont(style,latin,cjk,size,bold=False):
 st=doc.styles[style];st.font.name=latin;st.font.size=Pt(size);st.font.bold=bold;st.font.color.rgb=RGBColor(0,0,0)
 st.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),cjk)
setfont('Normal','Times New Roman','宋体',11)
setfont('Title','Times New Roman','黑体',22,True)
setfont('Subtitle','Times New Roman','宋体',12)
setfont('Heading 1','Times New Roman','黑体',15,True)
setfont('Heading 2','Times New Roman','黑体',11.5,True)
setfont('Caption','Times New Roman','宋体',8.5)
normal=doc.styles['Normal'].paragraph_format
normal.line_spacing=Pt(16);normal.space_after=Pt(6);normal.widow_control=True
for sty in ['Heading 1','Heading 2']:
 pf=doc.styles[sty].paragraph_format;pf.space_before=Pt(7);pf.space_after=Pt(7);pf.keep_with_next=True
doc.styles['Caption'].paragraph_format.line_spacing=Pt(12)
doc.styles['Caption'].paragraph_format.space_after=Pt(7)
doc.core_properties.author='刘群';doc.core_properties.title='白血病表达差异筛选中的多重检验控制'
doc.core_properties.subject='学号 38720260158062 | 多重检验校正课程论文'
hp=sec.header.paragraphs[0];hp.text='多重检验控制与白血病表达差异';hp.style='Caption'
hp.runs[0].font.color.rgb=RGBColor.from_string('666666')
fp=sec.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
fr=fp.add_run('刘群  ·  38720260158062    |    ');fr.font.size=Pt(8)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');fp._p.append(field)

def inline(par,text,size=None):
 # Preserve emphasis and ordinary super/subscripts as editable Word runs.
 bold=False;sup=False;sub=False
 for token in re.split(r'(<[^>]+>)',text):
  if token=='<b>':bold=True
  elif token=='</b>':bold=False
  elif token in ['<super>','<sup>']:sup=True
  elif token in ['</super>','</sup>']:sup=False
  elif token=='<sub>':sub=True
  elif token=='</sub>':sub=False
  elif token.startswith('<br'):par.add_run().add_break()
  elif not token.startswith('<'):
   run=par.add_run(html.unescape(token));run.bold=bold;run.font.superscript=sup;run.font.subscript=sub
   if size:run.font.size=Pt(size)
 return par
def mathrun(text):
 r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);return r
def mathscripts(text,tag):
 el=OxmlElement('m:'+tag);base=OxmlElement('m:e');base.append(mathrun(text[0]));el.append(base)
 slot=OxmlElement('m:sub' if tag=='sSub' else 'm:sup');slot.append(mathrun(text[1]));el.append(slot);return el
def equation(text):
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(8)
 p.paragraph_format.line_spacing=1.2
 omp=OxmlElement('m:oMathPara');pr=OxmlElement('m:oMathParaPr');jc=OxmlElement('m:jc');jc.set(qn('m:val'),'center');pr.append(jc);omp.append(pr)
 om=OxmlElement('m:oMath')
 def slot(tag,items):
  x=OxmlElement('m:'+tag)
  for y in items:x.append(mathrun(y) if isinstance(y,str) else y)
  return x
 def script(base,index,super=False):
  return slot('sSup' if super else 'sSub',[slot('e',[base]),slot('sup' if super else 'sub',[index])])
 def frac(num,den):return slot('f',[slot('num',num),slot('den',den)])
 def rad(items):
  z=OxmlElement('m:rad');pr=OxmlElement('m:radPr');dh=OxmlElement('m:degHide');dh.set(qn('m:val'),'1');pr.append(dh);z.append(pr);z.append(OxmlElement('m:deg'));z.append(slot('e',items));return z
 if '(2)' in text:
  items=['FWER = P(V ≥ 1) = 1 − ',script('(1 − α)','m',True),'     (2)']
 elif '(3)' in text:
  items=['FDP = ',frac(['V'],['max(R, 1)']),',    FDR = E(FDP),    FWER = P(V ≥ 1)     (3)']
 elif '(4)' in text:
  items=['Δ = ',script('x̄','AML'),' − ',script('x̄','ALL'),',    SE = ',rad([frac([script(script('s','AML'),'2',True)],[script('n','AML')]),' + ',frac([script(script('s','ALL'),'2',True)],[script('n','ALL')])]),'     (4)']
 elif '(5)' in text:
  items=['95% CI = Δ ± ',script('t','0.975,ν'),' SE,    d = ',frac(['Δ'],[script('s','pooled')]),'     (5)']
 else:items=[html.unescape(re.sub('<[^>]+>','',text)).replace('。','')]
 for item in items:om.append(mathrun(item) if isinstance(item,str) else item)
 omp.append(om);p._p.append(omp)
def make_table(headers,rows,widths):
 tb=doc.add_table(rows=1,cols=len(headers));tb.alignment=WD_TABLE_ALIGNMENT.CENTER;tb.autofit=False
 widths=widths or [492/len(headers)]*len(headers)
 for col,w in zip(tb.columns,widths):col.width=Inches(w/492*6.9)
 for row_idx,vals in enumerate([headers]+rows):
  row=tb.rows[0] if row_idx==0 else tb.add_row()
  if row_idx==0:
   trpr=row._tr.get_or_add_trPr();rep=OxmlElement('w:tblHeader');trpr.append(rep)
  trpr=row._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trpr.append(cant)
  for j,(cell,val) in enumerate(zip(row.cells,vals)):
   cell.width=Inches(widths[j]/492*6.9);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   pp=cell.paragraphs[0];pp.paragraph_format.line_spacing=Pt(10.5);pp.paragraph_format.space_after=Pt(0);pp.paragraph_format.space_before=Pt(0)
   pp.alignment=WD_ALIGN_PARAGRAPH.LEFT if j==0 or len(str(val))>22 else WD_ALIGN_PARAGRAPH.CENTER
   inline(pp,str(val),8.3)
   tcpr=cell._tc.get_or_add_tcPr();mar=OxmlElement('w:tcMar')
   for side,n in [('top',55),('bottom',55),('left',75),('right',75)]:
    e=OxmlElement('w:'+side);e.set(qn('w:w'),str(n));e.set(qn('w:type'),'dxa');mar.append(e)
   tcpr.append(mar)
   borders=OxmlElement('w:tcBorders')
   for side in ['top','bottom','left','right']:
    e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
   tcpr.append(borders)
   shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EFF3' if row_idx==0 else ('F7F9FA' if row_idx%2==0 else 'FFFFFF'));tcpr.append(shade)
   if row_idx==0:
    for rr in pp.runs:rr.bold=True
 doc.add_paragraph().paragraph_format.space_after=Pt(0)

for b in blocks:
 if b[0]=='page':doc.add_page_break()
 elif b[0]=='p':
  sty={'title':'Title','en':'Subtitle','h1':'Heading 1','h2':'Heading 2','small':'Caption'}.get(b[1],'Normal')
  par=doc.add_paragraph(style=sty);inline(par,b[2]);
  if b[1]=='title':par.paragraph_format.space_after=Pt(9)
  if b[1]=='en':par.paragraph_format.space_after=Pt(9)
 elif b[0]=='eq':equation(b[1])
 elif b[0]=='table':make_table(b[1],b[2],b[3])
 elif b[0]=='fig':
  par=doc.add_paragraph();par.alignment=WD_ALIGN_PARAGRAPH.CENTER;par.paragraph_format.keep_with_next=True;par.paragraph_format.space_after=Pt(3)
  par.paragraph_format.line_spacing=1.0
  par.add_run().add_picture(str(OUT/'figures'/f'{b[1]}.png'),width=Inches(6.1))
  cp=doc.add_paragraph(style='Caption');inline(cp,b[2]);cp.paragraph_format.keep_together=True

for node in list(doc.styles.element.iter(qn('w:pBdr')))+list(doc.element.iter(qn('w:pBdr'))):
 node.getparent().remove(node)
doc.save(OUT/'刘群_38720260158062_多重检验论文_修订版.docx')
(OUT/'revised-content.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2),encoding='utf-8')
print('Word saved',OUT)
