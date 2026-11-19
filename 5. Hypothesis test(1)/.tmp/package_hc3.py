from pathlib import Path
import json,shutil,hashlib
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'output/HC3学习资料与参考文献'
items=[
 ('white','01_HC3理论基础_异方差一致协方差估计_White_1980_期刊版.pdf','10.2307/1912934','期刊扫描版','Heteroskedasticity-Consistent'),
 ('mackinnon','02_HC3方法来源_有限样本修正与Jackknife_MacKinnon_White_1985_工作论文修订稿.pdf','10.1016/0304-4076(85)90158-7','工作论文修订稿，原始工作论文1983年，1985年修订','Finite Sample'),
 ('long_archive','03_HC3应用选择_稳健标准误版本比较_Long_Ervin_2000_作者1999年修订稿.pdf','10.1080/00031305.2000.10474549','作者1999年修订稿，存档于原Indiana大学作者网站，期刊发表年2000','Long'),
 ('cameron','04_HC3适用边界_中心内相关与聚类推断_Cameron_Miller_2015_作者稿.pdf','10.3368/jhr.50.2.317','作者公开稿','Cluster-Robust'),
]
manifest=[]
for key,name,doi,version,check in items:
 folder=ROOT/'.tmp/hc3_download'/key
 src=next(folder.rglob('*.pdf'))
 raw=src.read_bytes();assert raw.startswith(b'%PDF')
 d=pymupdf.open(src);head=' '.join(p.get_text() for p in list(d)[:3]);assert check.lower() in head.lower()
 shutil.copy2(src,out/name)
 j=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
 # Preserve the original downloader manifest in the combined audit record.
 manifest.append({'filename':name,'doi':doi,'version':version,'pages':len(d),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'download_date':'2026-11-05','supporting_information':'not_requested','source_record':j})
(out/'下载清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
lines=['HC3 学习资料与参考文献','整理日期 2026-11-05','刘群  学号 38720260158062','','00 为五页中文讲解 PDF。01-04 为四篇参考文献正文。','按 HC3 理论基础、方法来源、应用选择、适用边界排序。','公开作者稿的排版、页数及措辞可能与正式期刊版不同。引用时使用期刊书目信息与 DOI。','']
for x in manifest:
 lines.extend([x['filename'],f"版本 {x['version']}",f"页数 {x['pages']}",f"DOI https://doi.org/{x['doi']}",''])
lines.extend(['每篇文献的原始来源和校验信息见下载清单.json。','软件公式说明 https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.HC3_se.html'])
(out/'阅读顺序与版本说明.txt').write_text('\n'.join(lines),encoding='utf8')
shutil.make_archive(str(ROOT/'output/HC3学习资料与参考文献'),'zip',root_dir=out.parent,base_dir=out.name)
print('Validated four references and packaged folder.')
print([(x['filename'],x['pages']) for x in manifest])
