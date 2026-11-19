# 第 4 讲：降维、PCA 与 UMAP

负责人：zhang。主题：**如何把复杂高维数据压缩到可理解的低维空间？** 原安排“第 3 讲b”现独立为第 4 讲。高维数据与维度灾难已在 [第 3 讲](<../3. High-dimension/High-dimension.md>) 完成。本章继续使用 Golub 白血病表达数据：72 个样本、7,129 个探针。

## 课程材料

| 材料 | 用途 |
|---|---|
| [独立讲解稿](Dimension-reduction.md) | 课程目标、概念、课堂代码、常见错误与作业 |
| [PBL 说明 PPT](slides/dimension-reduction-pbl.pptx) | 25 页可编辑课件：术语概念、数据集、核心问题与实验设计 |
| [学生工作单](student-worksheet.md) | 四项任务：目的与流程、PCA、UMAP、证据结论 |
| [教师参考](teacher-reference.md) | 答案要点、实际结果、讲评与作业参考 |
| [教师复现脚本](scripts/teacher_analysis.py) | 标准化/原尺度 PCA、四种 UMAP 设置及训练部分交叉验证 |
| [数据说明](data/README.md) | 来源、字段、预处理及解释边界 |
| [课堂数据](data/leukemia/leukemia.csv) | 保留源表达值与原始划分 |
| [数据检查](data/inspection.json) | 类别计数、输入校验值和派生记录 |

## 教学与运行

建议课堂 45 分钟，课后实验与报告 60–90 分钟。课堂完成标准化→PCA→PC1/PC2→UMAP→图形比较；完整参数对照与可选预测验证在课后完成。数据已提供，无需重新下载。

在本章目录运行：

```powershell
python -m pip install -r scripts/teacher-requirements.txt
python scripts/teacher_analysis.py
```

教师提前运行 UMAP，首次编译可能较慢。程序按自身路径定位数据，输出统一写入项目根目录 `.tmp/dimension-reduction/teacher-results/`，不改写原始数据。历史合并版中间结果已移至 `.tmp/dimension-reduction/legacy-combined-teacher-results/` 保留。`assets/` 两张图是教师参考正式引用的教学插图；改变分析方案后需核对正文数值与插图再更新。

PPT 第 1–7 页说明问题与数据，第 8–15 页解释术语和方法，第 16–24 页说明任务、对照与结论要求，第 25 页为安排和提交清单。可按活动阶段穿插使用。作者脚本为 `scripts/build_slides.mjs`，使用 Codex artifact-tool 环境生成候选文件和预览至 `.tmp/dimension-reduction/slides/`；学生运行实验无需安装该工具。

## 本章边界

描述性降维在全部 72 个样本上拟合，标签仅作事后着色；可选建模对照只在原始 38 个训练样本内交叉验证，标准化、PCA 与分类器均放入每折 Pipeline。图形分离不等于预测性能，不等于真实亚型或疾病机制。解释率不等于诊断准确率，降维也不保证去噪或提高模型表现。

本章不再包含第 3 讲的逐维距离分布、逐维训练/测试分类、标签置换和多重检验任务。
