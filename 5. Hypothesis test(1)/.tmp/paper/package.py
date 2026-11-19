from pathlib import Path
import shutil,json,zipfile,importlib.metadata
ROOT=Path(__file__).resolve().parents[2]; O=ROOT/'output/paper'
(O/'code').mkdir(exist_ok=True);(O/'source_data').mkdir(exist_ok=True)
shutil.copy2(ROOT/'V3/data/heart-disease-hypothesis.csv',O/'source_data/heart-disease-hypothesis.csv')
shutil.copy2(ROOT/'V3/data/README.md',O/'source_data/数据说明.md')
for name in ['analyze.py','figures.py']:
    s=(ROOT/'.tmp/paper'/name).read_text(encoding='utf8')
    s=s.replace("ROOT=Path(__file__).resolve().parents[2]","ROOT=Path(__file__).resolve().parents[1]")
    s=s.replace("ROOT/'output/paper/figures'","ROOT/'figures'")
    s=s.replace("ROOT/'output/paper'","ROOT")
    s=s.replace("ROOT/'V3/data/heart-disease-hypothesis.csv'","ROOT/'source_data/heart-disease-hypothesis.csv'")
    s=s.replace("sys.path.insert(0,'D:/codex/.codex/skills/nature-figure/scripts')","sys.path.insert(0,str(Path(__file__).resolve().parent))")
    (O/'code'/name).write_text(s,encoding='utf8')
shutil.copy2('D:/codex/.codex/skills/nature-figure/scripts/audit_panel_alignment.py',O/'code/audit_panel_alignment.py')
(O/'code/requirements.txt').write_text('\n'.join(f'{n}=={importlib.metadata.version(n)}' for n in ['numpy','pandas','scipy','statsmodels','matplotlib']),encoding='utf8')
(O/'使用说明.md').write_text('''# 课程论文交付说明

主文件为六页中文论文PDF，采用期刊文章的双栏正文、顺序编号引文和多面板图布局。它是课程作业，非正式期刊投稿文件。姓名与学号留空，提交前请填写并核对课程的AI使用规定。

## 内容

- `论文正文_可编辑.md`：可编辑全文，含图表引用和数学表达式。
- `figures/`：三幅原创数据图的PDF、SVG与PNG；SVG中文字可编辑。
- `analysis_results.json`、`model_results.csv`、`site_results.csv`：独立复算的统计结果。
- `source_data/`：原始课程数据的未修改副本及说明。
- `code/`：分析和绘图复现程序。

## 复现

Python 3.12环境中安装 `code/requirements.txt` 后依次运行：

```text
python code/analyze.py
python code/figures.py
```

程序以自身位置确定数据路径，重新生成结果与图表。均值差始终按疾病组减无疾病组计算，缺失终点记录保留在源数据中但不进入主要检验。预测模型和配对分析只回答方法选择，未伪称实际执行。

图1使用全部865名终点完整受试者；水平随机抖动只用于减少散点重叠，不生成观测值。图2是未经多重校正的探索性分析。图3是给定效应与方差的理论曲线，不是患者数据。

## 核查

主要结果已由Welch手工公式与统计计算相互核对；三个多面板图已通过对齐、文字大小和碰撞检查；六页PDF已逐页查看。图中文字不小于7 pt；PNG为400 dpi，另提供矢量PDF/SVG。未导出TIFF，因为交付用途为课程论文，不是期刊生产上传。

Science官方网站作者指南访问受限，因此本交付参照期刊视觉和论文结构，不声称逐条满足当前正式投稿规范。课程所需的五项任务及八项必备内容已在第6页列出对应位置。
''',encoding='utf8')
(O/'核查记录.md').write_text('''# 核查记录

主分析：920条记录；55条终点缺失；865条进入比较。疾病编码与num>0一致，record_id无重复。原始数据SHA-256见analysis_results.json。

图表：所有原始非缺失测量保留；55条缺失明确列出。静态检测的“随机数据”提示来自水平抖动，非模拟观测值。功效和多重比较图明确标为理论示例。图像叠放警告仅对应散点的栅格化图层，无内容遮盖。所有图对齐及最终PDF文字碰撞审查通过。

论文：6页逐页目视核查，修复了中文字体缺少负号、下标和数学重音的问题；公式用数学排版生成。无正文裁切或图注遮盖。姓名/学号尚待作者填写。

证据分配：主均值差为核心结果；协变量调整和中心差异限定解释；缺失模式属于结论边界；功效和方法矩阵用于作业教学要求。调整、分中心、年龄平方及秩检验均为探索性。

未执行：配对前后检验、临床预测验证、多重插补、因果推断。正文没有将这些计划写成实际结果。
''',encoding='utf8')
dest=ROOT/'output/课程论文_完整材料.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for f in O.rglob('*'):
        if f.is_file() and '__pycache__' not in str(f):z.write(f,f.relative_to(O))
print(dest)
