import json
import re
import base64
import io
from PIL import Image

with open('trend_radar_dashboard.html', encoding='utf-8') as f:
    content = f.read()

start = content.index('const DATA = [') + len('const DATA = ')
depth = 0
i = start
in_str = False
esc = False
while i < len(content):
    c = content[i]
    if in_str:
        if esc:
            esc = False
        elif c == '\\':
            esc = True
        elif c == '"':
            in_str = False
    else:
        if c == '"':
            in_str = True
        elif c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                i += 1
                break
    i += 1

raw = content[start:i]
data = json.loads(raw)

for row in data:
    for p in row.get("products", []):
        img = p["image"]
        b64 = img.split(",", 1)[1]
        raw_bytes = base64.b64decode(b64)
        im = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        # compute average brightness
        small = im.resize((16, 16))
        pixels = list(small.getdata())
        avg = sum(sum(px) for px in pixels) / (len(pixels) * 3)
        if avg < 15:
            print(row["keyword"], "-- DARK image, avg:", round(avg, 1), p["title"][:60], p["url"])
