from pathlib import Path
import shutil,zipfile,importlib.metadata,json
ROOT=Path(__file__).resolve().parents[2]; O=ROOT/'output/paper_refined'
(O/'code').mkdir(exist_ok=True);(O/'source_data').mkdir(exist_ok=True)
shutil.copy2(ROOT/'V3/data/heart-disease-hypothesis.csv',O/'source_data/heart-disease-hypothesis.csv')
shutil.copy2(ROOT/'V3/data/README.md',O/'source_data/数据说明.md')
for source,target in [('analyze.py','analyze.py'),('figures_refined.py','figures.py'),('build_refined.py','build_pdf.py')]:
    s=(ROOT/'.tmp/paper'/source).read_text(encoding='utf8')
    s=s.replace("ROOT=Path(__file__).resolve().parents[2]","ROOT=Path(__file__).resolve().parents[1]")
    s=s.replace("ROOT/'output/paper_refined/figures'","ROOT/'figures'")
    s=s.replace("ROOT/'output/paper_refined'","ROOT")
    s=s.replace("ROOT/'output/paper'","ROOT")
    s=s.replace("ROOT/'V3/data/heart-disease-hypothesis.csv'","ROOT/'source_data/heart-disease-hypothesis.csv'")
    s=s.replace("sys.path.insert(0,'D:/codex/.codex/skills/nature-figure/scripts')","sys.path.insert(0,str(Path(__file__).resolve().parent))")
    s=s.replace("ROOT/'.tmp/paper/","ROOT/'code/.cache/")
    s=s.replace("ROOT/'.tmp/paper'","ROOT/'code/.cache'")
    if source=='build_refined.py':
        s=s.replace("r=json.loads(","(ROOT/'code/.cache').mkdir(parents=True,exist_ok=True)\nr=json.loads(",1)
    (O/'code'/target).write_text(s,encoding='utf8')
shutil.copy2('D:/codex/.codex/skills/nature-figure/scripts/audit_panel_alignment.py',O/'code/audit_panel_alignment.py')
packages=['numpy','pandas','scipy','statsmodels','matplotlib','reportlab','pymupdf','fonttools']
(O/'code/requirements.txt').write_text('\n'.join(f'{n}=={importlib.metadata.version(n)}' for n in packages),encoding='utf8')
(O/'使用说明.md').write_text('''# 刘群的课程论文：精修版

作者：刘群；学号：38720260157062。

主文件为六页中文论文PDF，采用双栏正文、顺序编号引文与四幅科研图。PDF中的曲线、森林图、文字和公式均以矢量形式嵌入；原始散点在图中采用高分辨率栅格图层。

## 文件

- `刘群_38720260157062_心脏病与最大运动心率.pdf`：精修论文。
- `论文正文_可编辑.md`：可编辑全文，含数学表达式及图表链接。
- `figures/`：四幅图的矢量PDF、可编辑文字SVG及600 dpi PNG。
- `analysis_results.json`、`model_results.csv`、`site_results.csv`：独立复算的数值结果。
- `source_data/`：原始课程数据的未修改副本与说明。
- `code/`：数据分析、绘图、论文排版程序及依赖版本。

## 复现

在Python 3.12环境中安装 `code/requirements.txt`，依次运行：

```text
python code/analyze.py
python code/figures.py
python code/build_pdf.py
```

前两步生成统计结果与图表。第三步在Windows中使用系统宋体、黑体生成PDF，同时更新可编辑正文；页面检查图位于自动创建的 `code/.cache/`。已有同名输出会被更新。

均值差均按“疾病组减无疾病组”计算。原始920条记录保留；55条终点缺失不进入主检验。图1的随机抖动只改变横向显示位置，不改变心率。核密度使用Scott带宽，左右两组各自按密度峰值归一化，宽度不表示样本人数。

图2为未经多重校正的探索性分析。右面板全部采用HC3稳健区间，包括未调整模型；该未调整区间与正文Welch区间有微小数值差别，图注已解释。图3为指定分布、效应和方差的理论曲线。图4为按原始中心总人数计算的缺失比例。

这是采用Science风格排版的中文课程论文，不是已通过正式投稿格式审查的期刊稿件。作者需按课程要求复核内容并披露AI辅助使用。
''',encoding='utf8')
(O/'精修说明与核查.md').write_text('''# 精修说明与核查

## 主要变化

1. 首页、页脚和PDF作者信息均填入刘群、38720260157062。
2. 图1改为半小提琴、全部观测散点、均值95%区间与经验累积分布；图2补充逐行效应估计和95%区间；图3标出80%功效对应样本量，并区分Bonferroni精确错误率与控制上界；图4新增来源中心缺失率。
3. 以矢量图和矢量公式替代原先嵌入的普通位图，保持细线与文字在放大时清晰。
4. 明确总体目标参数、完整病例估计和外推边界；澄清bootstrap不是离群点稳健化方法；说明组间或中心间显著性差异本身不能证明交互作用；避免将调整前后衰减比例解释为因果混杂比例。

## 数值与结构

原始920人；心率非缺失865人；疾病组474人、无疾病组391人。主要均值差−20.54次/分钟，Welch 95% CI［−23.73, −17.35］，p=1.30×10⁻³³。作者信息未从目录名推断，使用用户提供的学号38720260157062。

主结果与探索性调整结论未因美化而改变。正文保留全部作业要求，方法选择矩阵和四句话退出卡仍完整。新增图4替代讨论中重复罗列各中心缺失人数的文字；未扩大临床或因果主张。

## 图形与版面核查

四幅最终PDF的文字碰撞检查均无FAIL或WARN。前三幅多面板图通过1.5 pt容差的对齐检查；图4为单面板。原图最小字体7 pt，嵌入正文后仍高于5 pt。全部六页已逐页查看，姓名、学号、负号、下标、公式、图注及页脚均显示完整。

静态预检的三个提示已人工核查：缺失排除有明确920→865计数；随机数只用于原始点的横向抖动；仅交付600 dpi PNG及矢量PDF/SVG，没有期刊生产用途的TIFF。森林图的浅色行底纹是有意的阅读辅助，不遮盖线条或文字。

数据哈希记录在analysis_results.json。未执行配对实验、预测模型验证、多重插补或因果识别；论文没有将这些设计建议写成实际结果。
''',encoding='utf8')
dest=ROOT/'output/刘群_38720260157062_论文精修材料.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for f in O.rglob('*'):
        if f.is_file() and not any(x in f.parts for x in ['__pycache__','.cache']):z.write(f,f.relative_to(O))
with zipfile.ZipFile(dest) as z:assert z.testzip() is None
print('Refined package built and verified.')
