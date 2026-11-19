from pathlib import Path
import json, shutil, hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/HC3学习资料与参考文献'
TMP=ROOT/'.tmp/hc3_guide'
OUT.mkdir(parents=True,exist_ok=True); TMP.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('Song','C:/Windows/Fonts/simsun.ttc'))
pdfmetrics.registerFont(TTFont('Hei','C:/Windows/Fonts/simhei.ttf'))
pdfmetrics.registerFontFamily('Song',normal='Song',bold='Hei',italic='Song',boldItalic='Hei')
styles={
 'body':ParagraphStyle('body',fontName='Song',fontSize=11,leading=18,spaceAfter=9,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='Song',fontSize=9,leading=14,spaceAfter=6,wordWrap='CJK'),
 'h':ParagraphStyle('h',fontName='Hei',fontSize=15,leading=22,spaceBefore=10,spaceAfter=11),
 'title':ParagraphStyle('title',fontName='Hei',fontSize=24,leading=32,spaceAfter=15),
}
story=[]
def p(t,style='body'):story.append(Paragraph(t,styles[style]))
def formula(tex,width=430):
 fig=plt.figure(figsize=(8,0.65)); fig.text(.01,.5,'$'+tex+'$',fontsize=16,va='center')
 path=TMP/f'eq{len(list(TMP.glob("eq*.png")))}.png'
 fig.savefig(path,dpi=250,bbox_inches='tight',pad_inches=.08);plt.close(fig)
 from PIL import Image as PILImage
 with PILImage.open(path) as im:w,h=im.size
 target=min(width,w/250*72)
 story.append(Image(str(path),width=target,height=target*h/w,hAlign='LEFT'));story.append(Spacer(1,9))
def table(rows,widths):
 data=[[Paragraph(str(c),styles['small']) for c in row] for row in rows]
 t=Table(data,colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8EFF2')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#CBD4D9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
 story.append(t);story.append(Spacer(1,12))
def page():story.append(PageBreak())
def footer(c,d):
 c.setFont('Song',8);c.setFillColor(colors.HexColor('#596570'))
 c.drawString(48,813,'统计检验与假设设计  /  HC3 方法学习资料')
 c.drawString(48,27,'刘群  |  学号 38720260158062  |  整理日期 2026-11-05')
 c.drawRightString(547,27,str(d.page))

p('HC3 异方差稳健标准误','title')
p('简易理解、完整公式与课程数据实例','h')
p('HC3 用于估计回归系数的不确定性，并据此构建置信区间和计算 p 值。本资料围绕最大运动心率与心脏病证据的关联分析，说明 HC3 的作用、计算方式及适用条件。')
p('简易理解版','h')
p('模型依据疾病状态、年龄、性别和中心预测每个人的心率。实际值减去预测值，得到残差。若不同年龄、性别或中心的误差波动程度不同，就存在异方差。传统标准误依赖等方差设定，异方差稳健方法允许这些波动程度不同。[1]')
p('HC3 使用每个人的残差，同时按其杠杆值进行修正。杠杆值反映一个人的协变量组合在样本中有多特殊，以及其对自身拟合值的影响。高杠杆观测的残差可能因拟合而偏小，HC3 对这类观测作更强的修正。[2,5]')
table([['分析环节','在这篇论文中的作用'],['纳入年龄、性别和中心','估计在模型所规定的相同协变量条件下，疾病组与无疾病组的心率差异。'],['采用 HC3 标准误','评估系数估计的抽样不确定性，计算置信区间与 p 值。'],['加入年龄平方项','允许年龄与心率的平均关系出现曲率，检查模型设定的敏感性。']],[145,354])
p('实际数据中的变化','h')
p('在包含年龄平方项的同一个模型中，疾病系数为 -11.9789 次/分钟。普通标准误为 1.6659，HC3 标准误为 1.6999。本次 HC3 区间略宽，呈现的估计不确定性略高。结果来自 865 名终点完整者。')
p('普通标准误与 HC3 的相对大小依赖数据结构。选用 HC3 本身也无法证明本数据已经存在异方差。它提供对异方差较稳健的推断方式。[3,4]','small')
page()
p('完整版  模型与计算','title')
p('1  拟合回归并计算残差','h')
p('令 y 为心率向量，X 为包含截距与协变量的设计矩阵，β 为回归系数向量。普通最小二乘法先估计系数，再计算每个观测的残差。')
formula(r'y=X\beta+\varepsilon,\qquad \hat\beta=(X^{\top}X)^{-1}X^{\top}y')
formula(r'e_i=y_i-x_i^{\top}\hat\beta')
p('等方差设定令各人的误差方差相同。异方差设定允许 Var(ε<sub>i</sub> | X) 随观测改变。在误差间不相关及相应正则条件下，可使用三明治结构估计系数协方差。[1]')
p('2  计算杠杆值并构造 HC3','h')
formula(r'h_{ii}=x_i^{\top}(X^{\top}X)^{-1}x_i')
formula(r'\widehat{V}_{HC3}=(X^{\top}X)^{-1}X^{\top}\,\mathrm{diag}\!\left(\frac{e_i^2}{(1-h_{ii})^2}\right)X(X^{\top}X)^{-1}',490)
p('diag 表示把各观测的修正残差平方放到一个矩阵的对角线上。两侧的矩阵将这些误差信息转换成回归系数的协方差。第 j 个系数的标准误为该矩阵第 j 个对角元素的平方根。[5]')
formula(r'SE_{HC3}(\hat\beta_j)=\sqrt{[\widehat{V}_{HC3}]_{jj}}')
p('3  杠杆值修正如何起作用','h')
p('假设残差平方均为 100。杠杆值为 0.01 时，修正量约为 102.03。杠杆值为 0.20 时，修正量为 156.25。这是用于解释公式的假设例子。')
p('OLS 留一法中，删除第 i 个观测后对其预测的残差为 e<sub>i</sub>/(1-h<sub>ii</sub>)。HC3 使用这一量的平方，与 jackknife 协方差估计的近似构造有关。[2]')
page()
p('完整版  版本差异与适用条件','title')
p('HC0 到 HC3 的区别','h')
p('HC 表示异方差一致性。不同版本主要改变三明治矩阵中间部分的残差平方修正。下式中 n 为样本数，k 为包括截距在内的参数个数。[2,5]')
formula(r'HC0:\ e_i^2\qquad HC1:\ \frac{n}{n-k}e_i^2')
formula(r'HC2:\ \frac{e_i^2}{1-h_{ii}}\qquad HC3:\ \frac{e_i^2}{(1-h_{ii})^2}')
p('HC1 使用整体自由度修正。HC2 和 HC3 考虑各观测的杠杆值，HC3 修正更强。有限样本模拟是选择 HC3 的依据之一，其表现仍取决于样本结构、参数数量和极端杠杆值。[2,3]')
p('异方差与中心内相关','h')
table([['问题','关注的内容','分析中的处理'],['异方差','每个受试者的误差方差可能不同。','HC3 调整系数协方差估计。'],['中心平均差异','不同中心的平均心率或人群构成不同。','模型加入 C(site) 中心固定效应。'],['中心内残差相关','同中心受试者的残差可能共同变化。','需另行评估聚类结构与推断方法。']],[103,193,203])
p('中心固定效应调整中心之间的平均差异。剩余误差若在同一中心内相关，需要在协方差估计中考虑相关结构。本数据仅四个中心，常规依赖大量独立聚类的近似会面临困难。[4]')
p('解释结果时保留的条件','h')
p('本资料的回归解释以适当的均值模型、条件均值为零的误差设定及相应样本条件为基础。需关注模型形式、缺失机制、极端影响点和观测依赖性。用药、运动能力等未测量因素仍可能影响疾病系数。HC3 的稳健性主要针对异方差。')
p('稳健 t 推断使用近似参考分布。样本量较小、杠杆值极高或协变量相对过多时，应谨慎评估区间覆盖与检验表现。[2,4]')
page()
p('课程数据中的计算结果','title')
p('本页比较同一批 865 人、同一个含年龄平方项的模型。系数和标准误单位均为次/分钟。数值由课程 CSV 重算。')
table([['项目','普通标准误','HC3 标准误'],['疾病系数','-11.9789','-11.9789'],['标准误','1.6659','1.6999'],['95% 置信区间','[-15.25, -8.71]','[-15.32, -8.64]'],['双侧 p 值','1.41 × 10<super>-12</super>','3.76 × 10<super>-12</super>']],[155,172,172])
p('从标准误得到置信区间','h')
p('模型有 8 个参数，残差自由度为 865-8=857。程序显式指定 use_t=True，以 t 分布进行近似推断。')
formula(r'CI_{95\%}=\hat\beta_{disease}\pm t_{0.975,857}\,SE_{HC3}')
formula(r'-11.9789\pm1.9627\times1.6999=[-15.3153,-8.6425]')
p('相应的检验统计量为疾病系数除以 HC3 标准误，双侧 p 值取 t 参考分布两端的尾部概率。[6]')
formula(r't=\frac{-11.9789}{1.6999}\approx-7.047')
p('模型设定与复现','h')
p('使用 Python 的 statsmodels 公式接口。C(site) 将中心作为分类变量，I(age**2) 加入年龄平方项。下列代码中的 df 为读入课程数据后的数据表。','small')
code='''import statsmodels.formula.api as smf<br/>data = df.dropna(subset=["disease", "thalach"])<br/>formula = "thalach ~ disease + age + I(age**2) + sex + C(site)"<br/>result = smf.ols(formula, data=data).fit(<br/>&nbsp;&nbsp;&nbsp;&nbsp;cov_type="HC3", use_t=True)<br/>print(result.params["disease"])<br/>print(result.bse["disease"])<br/>print(result.conf_int().loc["disease"])'''
p(code,'small')
p('本次比较只改变标准误估计方式。报告中的协变量调整差异来自回归模型的变化。此前未调整系数约为 -20.54，调整年龄、性别和中心后约为 -12.17，再加入年龄平方项后约为 -11.98。','small')
page()
p('参考文献与文件阅读顺序','title')
refs=[
('1','White H. (1980). A Heteroskedasticity-Consistent Covariance Matrix Estimator and a Direct Test for Heteroskedasticity. Econometrica, 48(4), 817-838.','10.2307/1912934','HC3 理论基础。阅读异方差下系数协方差估计的基本问题。'),
('2','MacKinnon JG, White H. (1985). Some heteroskedasticity-consistent covariance matrix estimators with improved finite sample properties. Journal of Econometrics, 29(3), 305-325.','10.1016/0304-4076(85)90158-7','HC3 方法来源。了解有限样本修正与 jackknife 思路。下载件为公开工作论文修订稿。'),
('3','Long JS, Ervin LH. (2000). Using Heteroscedasticity Consistent Standard Errors in the Linear Regression Model. The American Statistician, 54(3), 217-224.','10.1080/00031305.2000.10474549','HC3 应用选择。比较 HC 版本并讨论实际使用。下载件为作者网站存档的 1999 年修订稿。'),
('4','Cameron AC, Miller DL. (2015). A Practitioner’s Guide to Cluster-Robust Inference. Journal of Human Resources, 50(2), 317-372.','10.3368/jhr.50.2.317','HC3 适用边界。理解中心内相关与少量聚类推断。下载件为作者公开稿。')]
for num,ref,doi,note in refs:
 p(f'[{num}] {ref}','small');p(note,'small');p(f'<link href="https://doi.org/{doi}" color="#245C78">https://doi.org/{doi}</link>','small');story.append(Spacer(1,5))
p('软件实现资料','h')
p('[5] statsmodels 官方 HC3_se 文档，提供 HC3 协方差与杠杆值公式。<br/><link href="https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.HC3_se.html" color="#245C78">打开 HC3_se 官方说明</link>','small')
p('[6] statsmodels 官方 get_robustcov_results 文档，说明稳健协方差与 use_t 推断设置。<br/><link href="https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html" color="#245C78">打开稳健协方差与推断设置说明</link>','small')
p('数据与版本记录','h')
p('课程数据为 V3/data/heart-disease-hypothesis.csv。讲解中的模型结果已用该数据重算。四篇文献按与 HC3 的关系命名。各文件的来源链接、版本、页数及获取状态记录在同目录的下载清单中。下载范围为论文正文。','small')
file=OUT/'00_HC3学习指南_简易理解与完整公式及数据实例.pdf'
SimpleDocTemplate(str(file),pagesize=(595,842),rightMargin=48,leftMargin=48,topMargin=55,bottomMargin=48,title='HC3 异方差稳健标准误',author='刘群').build(story,onFirstPage=footer,onLaterPages=footer)
d=pymupdf.open(file)
print('guide pages',len(d))
for i,pg in enumerate(d):pg.get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save(TMP/f'page-{i+1}.png')
