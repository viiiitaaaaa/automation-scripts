# Сходство фото товаров 1688 (items.json) с юбками Pinduoduo (cj\sverka\pdd_pics\<лист>_<№>.jpg) через CLIP.
import json, os, io, glob, urllib.request as u, concurrent.futures as cf
import torch, open_clip
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); PICS = os.path.join(D, 'pics'); os.makedirs(PICS, exist_ok=True)
items = json.load(open(os.path.join(D, 'items.json'), encoding='utf-8'))

def dl(it):
    p = os.path.join(PICS, it['offer'] + '.jpg')
    if not os.path.exists(p):
        try:
            b = u.urlopen(u.Request(it['pic'] + '_400x400.jpg', headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read()
            Image.open(io.BytesIO(b)).convert('RGB').save(p)
        except Exception: return None
    return p
list(cf.ThreadPoolExecutor(12).map(dl, items))

model, _, prep = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k'); model.eval()
def emb(paths):
    out = []
    with torch.no_grad():
        for i in range(0, len(paths), 32):
            x = torch.stack([prep(Image.open(p).convert('RGB')) for p in paths[i:i + 32]])
            e = model.encode_image(x); out.append(e / e.norm(dim=-1, keepdim=True))
    return torch.cat(out)
pdd = sorted(glob.glob(r'C:\Users\User\cj\sverka\pdd_pics\*.jpg'))
ali = [os.path.join(PICS, it['offer'] + '.jpg') for it in items if os.path.exists(os.path.join(PICS, it['offer'] + '.jpg'))]
S = emb(ali) @ emb(pdd).T
res = {}
for i, p in enumerate(ali):
    v, k = S[i].topk(3)
    res[os.path.basename(p)[:-4]] = [(os.path.basename(pdd[j])[:-4], round(float(s), 3)) for s, j in zip(v, k)]
json.dump(res, open(os.path.join(D, 'match.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(ali), 'товаров 1688 ×', len(pdd), 'юбок PDD')
for o, m in sorted(res.items(), key=lambda x: -x[1][0][1])[:15]: print(o, m)
