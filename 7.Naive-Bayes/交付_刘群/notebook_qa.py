from pathlib import Path
import sys,os,io,contextlib,base64,json
ROOT=Path(__file__).resolve().parent.parent;OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'.runtime'))
import nbformat,fitz
from PIL import Image,ImageOps,ImageDraw
nb=nbformat.v4.new_notebook();nb.cells=[nbformat.v4.new_markdown_cell('# 刘群 38720260158062\n第7讲核心任务可复现实验。对应2026-10-21新版工作单；测试标签已获准释放。先固定方案，再打开测试标签。不执行另需冻结的换目标拓展。')]
codes=[('A 数据与职责',"""from pathlib import Path
import sys, json
import numpy as np, pandas as pd
BASE=next(p for p in [Path.cwd()/'7. Naive-Bayes',Path.cwd().parent/'7. Naive-Bayes'] if (p/'scripts/lab_utils.py').exists())
sys.path.insert(0,str(BASE/'scripts'))
from lab_utils import *
train=pd.read_csv(BASE/'data/student/train.csv')
val=pd.read_csv(BASE/'data/student/validation.csv')
print('特征',FEATURES)
for name,f in [('train',train),('validation',val)]:
 print(name,len(f),f.bladder_inflammation.value_counts().to_dict(),'缺失',f.isna().sum().sum())
assert not set(train.sample_id)&set(val.sample_id)
profiles=set(map(tuple,train[FEATURES].to_numpy()))
print('验证已见模式记录数',sum(tuple(x) in profiles for x in val[FEATURES].to_numpy()))
"""),('A2 估参和后验手算',"""model=fit_model(train)
hand,weights,posterior=hand_calculation(train,[0,0,0,1,1,1])
print(hand.to_string(index=False));print('权重',weights,'后验',posterior)
program=model.predict_proba(pd.DataFrame([[0,0,0,1,1,1]],columns=FEATURES))[0,1]
print('手算与程序差',abs(program-posterior))
assert abs(program-posterior)<1e-12
"""),('B 损失与阈值',"""p=model.predict_proba(val[FEATURES])[:,1]
for name,f,prob in [('train',train,model.predict_proba(train[FEATURES])[:,1]),('validation',val,p),('prior',val,np.full(len(val),train.bladder_inflammation.mean()))]:
 print(name,scores(f.bladder_inflammation,prob))
thresholds=threshold_table(val.bladder_inflammation,p)
chosen=choose_threshold(thresholds)
print(thresholds.to_string(index=False));print('选定阈值',chosen)
print('教学log loss',-np.log(.6),-np.log(.9),-np.log(.4),-np.log(.01))
"""),('C 条件独立与概率质量',"""print(reliability(val.bladder_inflammation,p).to_string(index=False))
for copies in [0,1,5]:
 a=train[FEATURES].copy();b=val[FEATURES].copy()
 for i in range(copies):a[f'copy{i}']=a.lumbar_pain;b[f'copy{i}']=b.lumbar_pain
 m=BernoulliNB(alpha=1,binarize=None).fit(a,train.bladder_inflammation)
 pp=m.predict_proba(b)[:,1]
 print('额外腰痛副本',copies,scores(val.bladder_inflammation,pp))
 if copies==5:print(pd.DataFrame({'ID':val.sample_id,'原概率':p,'复制后':pp}).to_string(index=False))
"""),('D1 固定方案',"""freeze=dict(name='刘群',student_id='38720260158062',target='bladder_inflammation',features=FEATURES,alpha=1,threshold=chosen,train_ids=train.sample_id.tolist(),date='2026-11-18',refit=False)
print(json.dumps(freeze,ensure_ascii=False,indent=2))
FREEZE_CONFIRMED=True
OPEN_LOCKED_TEST=True # 用户已确认教师允许最终评价
"""),('D2 固定测试',"""assert FREEZE_CONFIRMED and OPEN_LOCKED_TEST
test=pd.read_csv(BASE/'data/student/locked-test-features.csv').merge(pd.read_csv(BASE/'data/teacher/locked-test-labels.csv'),on='sample_id',validate='one_to_one')
assert not set(test.sample_id)&(set(train.sample_id)|set(val.sample_id))
tp=model.predict_proba(test[FEATURES])[:,1]
print(scores(test.bladder_inflammation,tp,chosen))
print('已见模式记录数',sum(tuple(x) in profiles for x in test[FEATURES].to_numpy()))
print('测试不同模式数',len(test[FEATURES].drop_duplicates()))
print(pd.DataFrame({'ID':test.sample_id,'y':test.bladder_inflammation,'p':tp}).to_string(index=False))
""")]
env={};os.chdir(ROOT)
for i,(title,code) in enumerate(codes,1):
 nb.cells.append(nbformat.v4.new_markdown_cell('## '+title));buf=io.StringIO()
 with contextlib.redirect_stdout(buf):exec(compile(code,'<notebook>','exec'),env)
 cell=nbformat.v4.new_code_cell(code,execution_count=i,outputs=[nbformat.v4.new_output('stream',name='stdout',text=buf.getvalue())]);nb.cells.append(cell)
for i in range(1,5):
 nb.cells.append(nbformat.v4.new_markdown_cell(f'### 图{i}（由build.py生成，与上述分析同源）'))
 nb.cells.append(nbformat.v4.new_markdown_cell(f'![Figure {i}](attachment:fig{i}.png)',attachments={f'fig{i}.png':{'image/png':base64.b64encode((OUT/f'fig{i}.png').read_bytes()).decode()}}))
nb.metadata.kernelspec={'display_name':'Python 3','language':'python','name':'python3'}
nbformat.write(nb,OUT/'刘群_核心任务_已运行.ipynb')
pdf=OUT/'刘群_朴素贝叶斯课程论文.pdf'
if pdf.exists():
 qa=OUT/'qa';qa.mkdir(exist_ok=True);d=fitz.open(pdf);thumbs=[]
 for i,p in enumerate(d):
  pix=p.get_pixmap(matrix=fitz.Matrix(1.4,1.4));pix.save(qa/f'page-{i+1}.png');im=Image.open(qa/f'page-{i+1}.png');im.thumbnail((330,467));thumbs.append(im.copy());print(i+1,len(p.get_text()),p.get_text()[:35])
 sheet=Image.new('RGB',(330*3,500*((len(thumbs)+2)//3)),'#dddddd')
 for i,im in enumerate(thumbs):sheet.paste(im,((i%3)*330,(i//3)*500))
 sheet.save(qa/'contact.png')
