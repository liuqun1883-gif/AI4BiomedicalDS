from pathlib import Path
import pymupdf
from PIL import Image
r=Path('论文修订版_刘群');q=r/'qa';q.mkdir(exist_ok=True)
d=pymupdf.open(r/'预览.pdf');thumbs=[]
for i,p in enumerate(d):
 p.get_pixmap(matrix=pymupdf.Matrix(1.4,1.4)).save(q/f'page-{i+1}.png')
 im=Image.open(q/f'page-{i+1}.png');im.thumbnail((300,430));thumbs.append(im.copy());print(i+1,len(p.get_text()))
s=Image.new('RGB',(900,450*((len(d)+2)//3)),'#ddd')
for i,im in enumerate(thumbs):s.paste(im,((i%3)*300,(i//3)*450))
s.save(q/'contact.png')
