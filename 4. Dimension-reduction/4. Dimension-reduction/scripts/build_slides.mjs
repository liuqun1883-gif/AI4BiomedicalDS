import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const base=path.resolve(import.meta.dirname,'..');
const repo=path.resolve(base,'../../..');
const runtime=process.env.CODEX_ARTIFACT_RUNTIME||'C:/Users/rongs/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=runtime+'/node/node_modules';
const {Presentation,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const build=repo+'/.tmp/dimension-reduction/slides';
await fs.mkdir(build,{recursive:true});
const deck=Presentation.create({slideSize:{width:1280,height:720}});
const font='Microsoft YaHei', ink='#183A3C',teal='#087E80',gray='#526969',orange='#A4532B';
deck.theme.defaultFont=font;

const slides=[
{cover:true,title:'降维、PCA 与 UMAP',lead:'如何把复杂高维数据压缩到\n可理解的低维空间？',body:'第 4 讲 PBL 实验说明\nzhang',prompt:'概念、数据、问题与实验设计'},
{title:'本次 PBL 的驱动问题',lead:'二维图分得开，能支持什么结论？',body:'团队得到白血病表达数据，并画出一张 UMAP 图。\n同事说：“图上的簇证明了疾病机制，\n这个模型也能预测新患者。”\n你会接受吗？还需要哪些证据？',prompt:'先写初始判断、理由与信心（0–100），再开始实验。'},
{title:'需要回答的三个核心问题',lead:'每个问题都需要一项可检查的证据',rows:[['降维的目的','为了看清当前样本，还是预测未来样本？'],['方法的区别','PCA 与 UMAP 各保留什么、损失什么？'],['解释的边界','图上的分离、邻近与簇，能解释到哪一步？']],prompt:'最终用 PCA 结果和 UMAP 对照修订初始判断。'},
{title:'降维的五种用途',lead:'分析目标决定“有用”的评价标准',table:[['用途','需要什么证据'],['可视化','坐标清楚，图形对参数变化有说明'],['去噪','重复测量或下游验证更稳定'],['压缩特征','维数减少，同时报告重建误差或解释率'],['发现样本结构','候选模式经稳定性和外部信息检验'],['后续建模输入','完整流程在未参与拟合的数据上接受评价']],widths:[280,856],rowHeight:57,prompt:'降维可能去掉噪声，也可能丢掉重要信号。'},
{title:'数据矩阵的基本名称',lead:'一个样本对应一行，一个探针对应一列',rows:[['样本 sample','一份白血病样本的表达谱，n = 72。'],['特征 feature','探针表达值，p = 7,129。探针数不等于基因数。'],['标签 label','ALL：急性淋巴细胞白血病。\nAML：急性髓系白血病。仅作拟合后着色。']],prompt:'练习：指出 CSV 中哪些列属于输入，哪些属于元数据。'},
{title:'本课选择的数据集',lead:'Golub 白血病微阵列表达数据',table:[['项目','本课采用的版本'],['来源','OpenML leukemia，ID 1104，version 1'],['规模与类别','72 × 7,129，ALL 47，AML 25'],['原始划分','train 38，test 34'],['课堂文件','data/leukemia/leukemia.csv']],widths:[280,856],rowHeight:66,prompt:'选择理由：样本较少，可直接比较全部特征上的 PCA 与 UMAP。',notes:'数据来源：https://www.openml.org/d/1104 。原研究 Golub et al. (1999), Science 286:531–537, DOI 10.1126/science.286.5439.531。元数据 licence=Public，不等于明确的 CC BY 或 public domain。完整来源与转换规则见 data/README.md。'},
{title:'输入字段与数据边界',lead:'分析始终保留同一组样本和探针',body:'排除 sample_id、original_split、diagnosis 三列。\nsample_id 是教学编号，不能冒充原始患者 ID。\n表达矩阵含负值，不直接取 log 或 log1p。\n数据缺少患者重复、中心与批次字段。',prompt:'图形再清晰，也不能据此宣称已排除批次影响。'},
{title:'中心化与标准化',lead:'Centering 与 standardization 的区别',rows:[['中心化','每列减去均值，得到相对该列平均值的偏离。'],['标准化','再除以该列标准差：z = (x − μ) / s。'],['本课约定','StandardScaler 按列变换，标准差使用 ddof=0。']],prompt:'检查列均值约为 0、列标准差约为 1。本数据没有常量探针。'},
{title:'PCA 为什么对尺度敏感',lead:'PCA 寻找投影方差最大的方向',body:'原尺度下，变异很大的探针可能占据主要方向。\n标准化让每列按自身变异尺度参与比较。\n这会改变主成分，也可能放大低信噪比特征。\n本课同时做原尺度 PCA，观察这种改变。',prompt:'标准化不替代微阵列上游归一化，也不自动完成批次校正。'},
{title:'主成分与样本得分',lead:'PCA：Principal Component Analysis',rows:[['主成分方向','单位长度的线性方向。PC1 最大化投影方差。'],['后续主成分','PC2 与 PC1 正交，依次解释剩余方差。'],['得分 score','每个样本投影到该方向后的坐标。']],prompt:'PCA 不使用诊断标签。最大方差方向不一定最能区分疾病。'},
{title:'Loading：原特征如何组成 PC1',lead:'本课 loading = components_.T',body:'PC1 得分 = w₁z₁ + w₂z₂ + … + wₚzₚ\nw 是方向权重，z 是标准化后的探针值。\n绝对权重越大，该探针在这个方向上的系数越大。\n整体翻转权重与得分的符号，只改变坐标轴朝向。',prompt:'高 loading 不能直接解释为差异表达显著或致病证据。',notes:'本课采用单位特征向量权重。有的软件用乘以主成分标准差后的 loading，或变量与 PC 的相关系数，须注明定义。得分应理解为对中心化输入做投影，标准化矩阵在浮点精度内已中心化。'},
{title:'方差解释率',lead:'Explained variance ratio 衡量保留了多少变化',body:'某主成分解释率 = 该成分方差 / 输入的总方差。\n累计解释率 = 前 k 个主成分解释率之和。\nPC1–PC2 图要标注两轴各自的解释率。\n中心化后的 72 个样本至多有 71 个非零主成分。',prompt:'解释率不是分类准确率，也不是“生物学真相”的百分比。'},
{title:'UMAP 与局部邻域',lead:'Uniform Manifold Approximation and Projection',rows:[['邻域 neighborhood','先用高维输入中的近邻关系构建图。'],['嵌入 embedding','优化低维坐标，侧重保留局部邻域结构。'],['常见场景','单细胞与复杂表型的非线性结构探索。']],prompt:'UMAP1 / UMAP2 没有固定的基因或疾病单位。'},
{title:'UMAP 的参数名称',lead:'参数改变的是布局条件，结果需要对照',table:[['参数','含义','本课基线'],['n_neighbors','构建高维邻域时的邻居数','15'],['min_dist','低维点紧密堆积的限制参数','0.1'],['metric','高维相似性的距离度量','euclidean'],['random_state','控制随机过程的种子','42']],widths:[285,611,240],rowHeight:66,prompt:'固定 n_components=2、n_jobs=1。UMAP 没有与 PCA 等价的解释率。'},
{title:'PCA 与 UMAP 的比较',lead:'先说明保留的信息，再讨论图形差异',table:[['比较','PCA','UMAP'],['映射','线性投影','非线性嵌入'],['主要信息','正交方向上的方差','局部邻域关系'],['坐标解释','特征的线性组合','嵌入坐标'],['可报告的量','loading、方差解释率','参数、邻近关系与稳定性'],['主要限制','大方差可能来自技术变化','簇间距离与簇数容易误读']],widths:[220,448,468],rowHeight:57,prompt:'两种图都描述当前数据，单靠图形无法估计新患者预测性能。'},
{title:'四项任务与预期输出',lead:'每项任务都按“预测、观察、解释”完成',table:[['任务','操作','需要提交的证据'],['1 目的与流程','区分描述与预测','目标表及拟合范围'],['2 PCA','标准化及原尺度对照','散点图、解释率、权重表'],['3 UMAP','基线与三个单因素对照','比较图、参数、样本对应表'],['4 结论','回应初始主张','四句结论与额外验证方案']],widths:[230,410,496],rowHeight:66,prompt:'工作单任务 1–4 与本 PPT 一一对应。'},
{title:'任务 1：两种分析流程',lead:'关键区别是拟合范围与结论对象',rows:[['描述当前样本','全部 72 行拟合标准化与降维，再用诊断着色。'],['预测新样本','先划分。训练折拟合全部步骤，验证折只做变换。'],['需要回答','为什么“PCA 没用标签”仍不能消除信息泄露？']],prompt:'全数据均值、标准差和协方差都可能包含验证样本的信息。'},
{title:'任务 2：PCA 实验设计',lead:'只改变输入尺度，其余设置保持一致',table:[['项目','标准化方案','原尺度对照'],['输入','按探针 z-score','保留原值，仅由 PCA 中心化'],['固定条件','同一 72 × 7,129 矩阵','同一 72 × 7,129 矩阵'],['算法','PCA，完整 SVD','PCA，完整 SVD'],['记录','PC1/PC2、累计解释率','相同指标'],['比较','PC1 绝对权重前五名','名单与带符号权重']],widths:[230,448,458],rowHeight:57,prompt:'先预测：标准化会改变主成分吗？两种解释率能直接比“生物信息量”吗？'},
{title:'任务 2：PCA 图与权重的读法',lead:'解释一个方向，也说明它遗漏了什么',body:'画 PC1 vs PC2，轴标签写明各自解释率。\n画累计解释率曲线，观察两个坐标遗漏多少变化。\n列出前五个探针及带符号权重，解释一个系数。\n回答：PC1 是否是一个基因，或最佳诊断方向？',prompt:'整体符号相反可以正确。只写前五项不能代表完整 PC1 公式。'},
{title:'任务 3：UMAP 单因素对照',lead:'同一标准化矩阵，分别只改一个设置',table:[['条件','n_neighbors','min_dist','种子'],['基线','15','0.1','42'],['邻居数对照','5','0.1','42'],['紧密度对照','15','0.5','42'],['随机性对照','15','0.1','7']],widths:[320,272,272,272],rowHeight:66,prompt:'欧氏距离、二维输出、全部样本与探针保持不变，不先按诊断选列。'},
{title:'任务 3：需要观察什么',lead:'追踪同一个样本，避免只凭岛屿外观下结论',body:'保留 sample_id 与二维坐标的对应表。\n比较哪些样本在不同设置下仍然相邻。\n记录视觉聚集、岛屿间距和布局如何改变。\n并排比较 PCA 与 UMAP，保留全部参数对照。',prompt:'图中分离能证明疾病机制、真实亚型数量或预测性能吗？'},
{title:'可选实验：降维作为建模输入',lead:'只在原始 38 个训练样本内做三折交叉验证',rows:[['方案 A','StandardScaler 加 1 近邻分类器。'],['方案 B','StandardScaler、PCA(10) 加同一分类器。'],['固定与评价','相同分层三折，种子 42。报告 balanced accuracy。']],prompt:'每折拟合完整 Pipeline。PCA 用完整 SVD，不读取原始 test 标签评分。',notes:'StratifiedKFold(3, shuffle=True, random_state=42)。balanced accuracy 为 ALL 与 AML 两类召回率的平均。报告逐折分数和均值，不将三折当作独立临床样本计算结论。若第3讲已经看过同一测试集，不能重新称为未见过的确认性验证。'},
{title:'常见错误与对应修正',stack:true,lead:'三个检查点',rows:[['把 UMAP 簇当作生物学真相','比较参数稳定性，并提出独立信息或功能验证。'],['全数据降维后再交叉验证','标准化、PCA 与分类器全部在训练折内拟合。'],['忽略尺度直接做 PCA','报告预处理理由，并保留原尺度对照。']],prompt:'图形、模型验证与机制验证需要不同类型的证据。'},
{title:'任务 4：证据结论与作业',lead:'用自己的话回答，不以“图很漂亮”作结论',table:[['结论结构','填写内容'],['主张 Claim','是否接受初始主张？修订后的判断是什么？'],['证据 Evidence','一项 PCA 结果和一项 UMAP 参数对照'],['推理 Reasoning','这些结果如何支持你的判断？'],['边界 Boundary','尚不能推出什么？下一步如何验证？']],widths:[320,816],rowHeight:66,prompt:'作业：PC1 代表什么？为何通常标准化？UMAP 能说明和不能说明什么？'},
{title:'课堂安排与提交清单',lead:'45 分钟课堂，课后完成完整对照',rows:[['课堂前 25 分钟','初始判断与目的 5 分钟，标准化 5 分钟，PCA 15 分钟。'],['课堂最后 20 分钟','UMAP 12 分钟，泄露辨析 5 分钟，退出卡 3 分钟。'],['课后 60–90 分钟','提交含代码与结果的报告、参数记录、结论和三道作业。']],prompt:'评价重点：输入正确、对照可复现、拟合范围清楚、结论有边界。',notes:'配套入口 README.md；独立讲解稿 Dimension-reduction.md；student-worksheet.md；数据 data/leukemia/leukemia.csv。依赖 scripts/teacher-requirements.txt。教师提前运行 UMAP，避免首次编译占用课堂。中间输出统一在项目根目录 .tmp/dimension-reduction/。'},
];

function text(s,str,x,y,w,h,size=30,color=ink,bold=false){
 const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=str;sh.text.style={typeface:font,fontSize:size,color,bold,wrap:'square',insets:0,verticalAlignment:'top'};
}
const tableOwners=[];
for(let i=0;i<slides.length;i++){
 const d=slides[i],s=deck.slides.add();s.background.fill='#FAFBF8';
 if(d.cover){
  text(s,'生物医学数据科学',76,80,1120,50,28,teal,true);
  text(s,d.title,76,186,1120,90,60,ink,true);
  text(s,d.lead,76,312,1120,150,41,teal);
  text(s,d.body,76,510,1120,90,28,gray);
 }else{
  text(s,d.title,72,48,1136,68,43,ink,true);
  text(s,d.lead,72,142,1136,65,32,teal,true);
  if(d.table){
   tableOwners.push(i+1);
   const tb=s.tables.add({rows:d.table.length,columns:d.table[0].length,left:72,top:235,width:1136,height:d.table.length*d.rowHeight,values:d.table,columnWidths:d.widths});
   for(let r=0;r<d.table.length;r++)for(let c=0;c<d.table[0].length;c++){
    const cell=tb.getCell(r,c);cell.fill=r===0?'#E5EFEB':'#FFFFFF';
    cell.text.style={typeface:font,fontSize:25,bold:r===0,color:r===0?teal:ink,insets:10};
   }
  }else if(d.rows){
   d.rows.forEach(([label,body],j)=>{
    const wide=d.stack||label.length>15;
    if(wide){text(s,label,72,245+j*112,1136,40,29,teal,true);text(s,body,72,290+j*112,1136,55,28);}
    else {text(s,label,72,245+j*112,285,85,28,teal,true);text(s,body,380,245+j*112,828,88,30);}
   });
  }else text(s,d.body,72,245,1136,335,31);
 }
 text(s,d.prompt,72,625,1136,62,23,orange);
 text(s,String(i+1).padStart(2,'0'),1210,688,40,22,15,gray);
 s.speakerNotes.text=(d.notes||'请学生先预测，随后记录观察，再解释证据边界。')+'\n配套：第4讲 student-worksheet.md、teacher-reference.md、Dimension-reduction.md。\n数据：OpenML leukemia ID1104 version1，https://www.openml.org/d/1104 。原研究 DOI 10.1126/science.286.5439.531。\n方法来源：https://scikit-learn.org/stable/modules/decomposition.html#pca ; https://umap-learn.readthedocs.io/en/latest/parameters.html ; https://scikit-learn.org/stable/common_pitfalls.html#data-leakage 。';
}
await fs.writeFile(build+'/content.json',JSON.stringify(slides,null,2));
await fs.writeFile(build+'/table-owners.json',JSON.stringify(tableOwners));
await (await PresentationFile.exportPptx(deck)).save(build+'/candidate.pptx');
for(let i=0;i<deck.slides.items.length;i++){
 const png=await deck.export({slide:deck.slides.items[i],format:'png',scale:1});
 await fs.writeFile(build+`/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await png.arrayBuffer()));
}
console.log('Rendered '+slides.length+' slides to '+build);
