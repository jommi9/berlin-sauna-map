"""Encode img/card/*.webp into img/embed.json as data URIs, with attribution
from img/credits.json. Run after fetch_images.py, before assemble.py."""
import json, base64, os
c = json.load(open('img/credits.json', encoding='utf-8'))
emb = {}
for k, v in c.items():
    path = f'img/card/{k}.webp'
    if not os.path.exists(path):
        print(f"  ! missing {path}, skipping"); continue
    emb[k] = {"src": "data:image/webp;base64," + base64.b64encode(open(path,'rb').read()).decode(),
              "by": v["artist"], "lic": v["license"], "licurl": v.get("licurl",""),
              "page": v["page"], "title": v["title"]}
json.dump(emb, open('img/embed.json','w'), separators=(',',':'), ensure_ascii=True)
print(f"img/embed.json: {os.path.getsize('img/embed.json')/1024:.0f} KB, {len(emb)} images")
