from pathlib import Path
import re,html
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree
ROOT=Path(__file__).resolve().parents[2]; O=ROOT/'output/paper_refined'
doc=Document();sec=doc.sections[0]
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=sec.bottom_margin=Inches(.7);sec.left_margin=sec.right_margin=Inches(.75)
sec.header_distance=sec.footer_distance=Inches(.3)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Caption']:
    st=doc.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
    st._element.get_or_add_rPr().append(OxmlElement('w:rFonts'))
    st._element.rPr.rFonts.set(qn('w:eastAsia'),'宋体' if name in ['Normal','Caption'] else '黑体')
    st.paragraph_format.space_after=Pt(6)
doc.styles['Normal'].font.size=Pt(11)
doc.styles['Normal'].paragraph_format.line_spacing=1.18
doc.styles['Title'].font.size=Pt(22)
doc.styles['Subtitle'].font.size=Pt(13)
for name,size in [('Heading 1',14),('Heading 2',12)]:
    doc.styles[name].font.size=Pt(size);doc.styles[name].paragraph_format.space_before=Pt(10)
    doc.styles[name].paragraph_format.keep_with_next=True
doc.styles['Caption'].font.size=Pt(9)
doc.styles['Caption'].paragraph_format.line_spacing=1.08
doc.core_properties.author='刘群'
doc.core_properties.title='心脏病证据与最大运动心率的关联'
def runs(p,text,size=None):
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1 (\2)',text)
    root=etree.fromstring(('<root>'+text.replace('&','&amp;').replace('<sup>','<super>').replace('</sup>','</super>')+'</root>').encode())
    def add(t,sup=False,sub=False):
        if not t:return
        run=p.add_run(html.unescape(t));run.font.superscript=sup;run.font.subscript=sub
        if size:run.font.size=Pt(size)
    add(root.text)
    for e in root:
        add(e.text,e.tag=='super',e.tag=='sub');add(e.tail)
    return p
def para(text,style=None):return runs(doc.add_paragraph(style=style),text)
def m(tag,*children,**attrs):
    el=OxmlElement('m:'+tag)
    for k,v in attrs.items():el.set(qn('m:'+k),str(v))
    for ch in children:el.append(ch)
    return el
def mr(t):
    x=m('t');x.text=t;return m('r',x)
def sub(base,x):return m('sSub',m('e',base),m('sub',mr(x)))
def sup(base,x):return m('sSup',m('e',base),m('sup',mr(x)))
def frac(a,b):return m('f',m('num',*a),m('den',*b))
def accent(t,char):return m('acc',m('accPr',m('chr',val=char)),m('e',mr(t)))
def var(g):return sub(sup(mr('s'),'2'),g)
def n(g):return sub(mr('n'),g)
def term(g):return frac([var(g)],[n(g)])
def eq(number):
    p=doc.add_paragraph();p.paragraph_format.space_before=Pt(6);p.paragraph_format.space_after=Pt(9)
    om=m('oMath')
    hat=lambda:accent('Δ','̂')
    if number==1:
        nodes=[hat(),mr(' = '),sub(accent('y','̅'),'1'),mr(' − '),sub(accent('y','̅'),'0'),mr('，  SE = '),m('rad',m('radPr',m('degHide',val='1')),m('deg'),m('e',term('1'),mr(' + '),term('0'))),mr('，  t = '),frac([hat()],[mr('SE')])]
    elif number==2:
        summed=lambda:[term('1'),mr(' + '),term('0')]
        numerator=[sup(m('box',m('e',mr('('),*summed(),mr(')'))),'2')]
        ds=[]
        for g in ['1','0']:
            if ds:ds.append(mr(' + '))
            ds.append(frac([sup(m('box',m('e',mr('('),term(g),mr(')'))),'2')],[n(g),mr(' − 1')]))
        nodes=[mr('ν = '),frac(numerator,ds)]
    else:nodes=[mr('95% CI = '),hat(),mr(' ± '),sub(mr('t'),'ν,0.975'),mr(' SE')]
    for x in nodes:om.append(x)
    p._p.append(om);p.add_run(f'    ({number})')
    p.paragraph_format.keep_together=True

hp=sec.header.paragraphs[0];runs(hp,'BIOMEDICAL DATA SCIENCE  |  统计检验与假设设计',8)
fp=sec.footer.paragraphs[0];runs(fp,'刘群 · 38720260157062',8)
fp.add_run('\t');fp.paragraph_format.tab_stops.add_tab_stop(Inches(6.9),WD_ALIGN_PARAGRAPH.RIGHT)
for typ,text in [('begin',None),(None,' PAGE '),('end',None)]:
    rr=OxmlElement('w:r');e=OxmlElement('w:fldChar' if typ else 'w:instrText')
    if typ:e.set(qn('w:fldCharType'),typ)
    else:e.text=text
    rr.append(e);fp._p.append(rr)
lines=(O/'论文正文_可编辑.md').read_text(encoding='utf8').splitlines();i=0;eqn=0
major={'摘要','结果：组间差异在协变量调整后缩小','材料与方法','统计推断的误差控制','讨论：关联的强度与证据边界','结论：主张—证据—推理—边界','作业要求对照','参考文献与注释','数据、代码与制作说明'}
while i<len(lines):
    line=lines[i].strip();i+=1
    if not line or line=='---':continue
    if i==1:para(line,'Title');continue
    if line.startswith('## 四中心'):para(line[3:],'Subtitle');continue
    if line.startswith('## '):
        t=line[3:];heading=para(t,'Heading 1' if t in major else 'Heading 2');heading.paragraph_format.page_break_before=t.startswith('结论：');continue
    if line.startswith('!['):
        path=re.search(r'\((.*?)\)',line).group(1)
        p=doc.add_paragraph();p.add_run().add_picture(str(O/path),width=Inches(6.9))
        p.paragraph_format.keep_with_next=True;p.paragraph_format.space_after=Pt(4)
        continue
    if line.startswith('$'):
        eqn+=1;eq(eqn);continue
    if line.startswith('|'):
        rows=[line]
        while i<len(lines) and lines[i].strip().startswith('|'):rows.append(lines[i].strip());i+=1
        rows=[x for x in rows if not re.match(r'^\|\s*---',x)]
        vals=[[html.unescape(x.strip()) for x in row.strip('|').split('|')] for row in rows]
        if vals[0][0]=='必须覆盖的内容':
            locs=['引言与科学问题','材料与方法；表2','统计推断的误差控制；图3','结果；表1','混杂控制与模型边界；多重比较','讨论；结论']
            for row,loc in zip(vals[1:],locs):row[1]=loc
        tab=doc.add_table(rows=0,cols=len(vals[0]));tab.autofit=False
        widths={2:[4.7,2.2],3:([3.15,1.875,1.875] if vals[0][0].startswith('表1') else [1.55,2.5,2.85])}[len(vals[0])]
        for col,w in zip(tab.columns,widths):col.width=Inches(w)
        for j,row in enumerate(vals):
            cells=tab.add_row().cells
            for cell,text,w in zip(cells,row,widths):
                cell.width=Inches(w);p=cell.paragraphs[0]
                p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(3);p.paragraph_format.line_spacing=1.08
                runs(p,text.replace('<','&lt;').replace('>','&gt;'),9)
                if j==0:
                    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EAF0F3');cell._tc.get_or_add_tcPr().append(sh)
                    for rr in p.runs:rr.bold=True
            trpr=tab.rows[-1]._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
            if j==0:trpr.append(OxmlElement('w:tblHeader'))
        borders=OxmlElement('w:tblBorders')
        for edge in ['top','left','bottom','right','insideH','insideV']:
            x=OxmlElement('w:'+edge);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'D9D9D9');borders.append(x)
        tab._tbl.tblPr.append(borders);doc.add_paragraph().paragraph_format.space_after=Pt(0)
        continue
    # Preserve text except format-specific statements, which must describe this Word edition.
    line=line.replace('图表以矢量格式嵌入','Word版保留高清图表，正文、表格和公式可编辑')
    line=line.replace('本文为采用Science风格排版的中文课程论文','本文为中文课程论文；Word版采用便于修改的单栏排版')
    if line.startswith('图') and '｜' in line:
        p=para(line,'Caption');p.paragraph_format.keep_together=True
    else:
        p=para(line.replace('num>0','num&gt;0'))
        if line.startswith(('Heart disease','刘群')):
            for rr in p.runs:rr.font.size=Pt(10)
        if re.match(r'^\d\. ',line):
            for rr in p.runs:rr.font.size=Pt(9)
    p.paragraph_format.widow_control=True
file=O/'刘群_38720260157062_心脏病与最大运动心率_可编辑.docx'
doc.save(file)
print(file)
