import sys, urllib.request as u, io, concurrent.futures as cf
from PIL import Image, ImageDraw, ImageFont
src,dst=sys.argv[1],sys.argv[2]
rows=[l.split('|') for l in open(src,encoding='utf-8').read().split('\n') if l]
def get(r):
    k=r[4] if r[4].endswith('.jpg') else r[4]+'-0-cib.jpg'
    try: return Image.open(io.BytesIO(u.urlopen(u.Request('https://cbu01.alicdn.com/img/ibank/'+k+'_300x300.jpg',headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read())).convert('RGB')
    except Exception: return Image.new('RGB',(300,300),'gray')
ims=list(cf.ThreadPoolExecutor(12).map(get,rows))
C=9;S=260;F=ImageFont.truetype('arial.ttf',19)
sh=Image.new('RGB',(C*S,((len(ims)+C-1)//C)*(S+26)),'white');d=ImageDraw.Draw(sh)
for k,(im,r) in enumerate(zip(ims,rows)):
    x,y=(k%C)*S,(k//C)*(S+26); im.thumbnail((S-4,S-4)); sh.paste(im,(x+2,y+26)); d.text((x+4,y+2),f"#{k+1} {r[1]}¥ {r[2]}% s{r[3]}",fill='red',font=F)
sh.save(dst,quality=80)
