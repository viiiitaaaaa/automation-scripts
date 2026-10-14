# Публикуемая копия панели: содержимое каждой книги из «Все приёмы» — в отдельный файл books/N.html,
# подгружается при раскрытии книги. Локальная news_panel.html не меняется.
import re, os, sys
SRC = r"C:\Users\User\tg_monitor\news_panel.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "publish")  # 14.10: панель 22 МБ > лимита Artifact 16 МБ
s = open(SRC, encoding="utf-8").read()
os.makedirs(os.path.join(OUT, "books"), exist_ok=True)
res, pos, n = [], 0, 0
tag = re.compile(r"<details\b|</details>")
for m in re.finditer(r'<details class="bkf-book">', s):
    if m.start() < pos: continue
    so = s.index("</summary>", m.start()) + len("</summary>")
    depth, k = 1, m.end()
    for t in tag.finditer(s, m.end()):
        depth += 1 if t.group() == "<details" else -1
        if depth == 0: k = t.start(); break
    n += 1
    open(os.path.join(OUT, "books", f"{n}.html"), "w", encoding="utf-8").write(s[so:k].replace("�", "&#xFFFD;"))
    res.append(s[pos:so]); res.append(f'<div class="bkf-lazy" data-src="books/{n}.html">Загружаю…</div>')
    pos = k
res.append(s[pos:])
js = """<script>document.addEventListener('toggle',e=>{const d=e.target;if(!d.classList||!d.classList.contains('bkf-book')||!d.open)return;
const z=d.querySelector(':scope>.bkf-lazy');if(!z||z.dataset.done)return;z.dataset.done=1;
fetch(z.dataset.src).then(r=>r.text()).then(h=>{z.outerHTML=h}).catch(()=>{z.textContent='Не загрузилось — откройте локальную панель'})},true);</script>"""
out = ("".join(res) + js).replace("�", "&#xFFFD;")
open(os.path.join(OUT, "news_panel.html"), "w", encoding="utf-8").write(out)
print("книг", n, "страница", round(len(out.encode()) / 1e6, 1), "МБ")
