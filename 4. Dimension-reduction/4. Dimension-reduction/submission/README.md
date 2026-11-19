# 白血病降维工作单：提交说明

本包对应 **72份白血病样本、7,129个探针的Markdown工作单**。

## 提交文件

- `白血病降维分析_数学论文式作业.pdf`：13页完整报告，覆盖任务1—4、退出卡和三道作业；含摘要、数学命题与证明、5组图、数值表、代码及参考文献。
- `作业正文.md`：可编辑文字源稿（数学公式使用LaTeX语法）。
- `analysis.py`：完整、可复现的分析代码。
- `requirements.txt`：锁定本次实际使用的数值分析依赖。
- `build_report.py`：PDF排版源程序，使用Windows宋体、黑体和Consolas；重建PDF另需reportlab、PyMuPDF、Pillow。
- `audit_panel_alignment.py`：科研绘图技能提供的版面对齐检查辅助脚本，不参与数值分析。

## 运行

解压后进入 `course` 目录，执行：

```powershell
python -m pip install -r submission/requirements.txt
python submission/analysis.py
```

默认数据位于 `course/data/leukemia/leukemia.csv`。输出写入包根目录 `.tmp/dimension-reduction/student-results/`。若文件管理器隐藏 `.tmp`，可直接在地址栏输入该相对目录。

## 可追踪结果

- `results.json`：主要数值、校验值和软件版本。
- `sample-coordinates.csv`：72例样本对应PCA、原尺度PCA及四组UMAP坐标。
- `pc1-loadings.csv`、`G001-contributions.csv`：方向权重与样本贡献示例。
- `explained-variance.csv`：逐成分及累计解释率。
- `neighbors-by-sample.csv`、`stable-neighbors.csv`、`neighbor-summary.csv`：完整邻域核查。
- `cv-results.csv`、`cv-predictions.csv`、`cv-fit-audit.json`：固定原始38例训练集内的三折验证。
- `protocol.json`、`umap-settings.json`及`umap-*-all-params.json`：预期、拟合范围及参数。
- `fig*.png/pdf/svg`：可追踪图稿；PDF与SVG保留图内可编辑文本。

未对原始34例测试样本计算预测评分。描述性分析使用全部72例，诊断标签仅用于拟合后着色。

AI使用及结论边界已在正文披露；文稿未编造姓名、学号或个人课堂经历。若课程要求身份信息，请在提交平台或封面补充。
