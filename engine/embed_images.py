"""Encode img/card/*.webp into img/embed.json as data URIs, with attribution
from img/credits.json. Run after fetch_images.py, before assemble.py.

    python3 engine/embed_images.py <city>

A photo that did not come from Wikimedia Commons, one a visitor or reviewer sent in, has no
entry in credits.json. The city names it in PHOTOS in its venues.py, photo key to the name the
credit should carry (or None when it was sent without one), and its card is committed as
img/card/<key>.webp like the others.
"""
import json, base64, os
import city
city.enter()
import venues as data
c = json.load(open('img/credits.json', encoding='utf-8')) if os.path.exists('img/credits.json') else {}
emb = {}
for k, who in getattr(data, "PHOTOS", {}).items():
    path = f'img/card/{k}.webp'
    assert k not in c, f"{k} is both a Commons photo and a sent-in one"
    assert who is None or not set(who) & set('<>"\\`'), f"PHOTOS[{k!r}]: a credit is plain text"
    if not os.path.exists(path):
        print(f"  ! missing {path}, skipping"); continue
    emb[k] = {"src": "data:image/webp;base64," + base64.b64encode(open(path,'rb').read()).decode(),
              "by": who or "", "lic": "", "licurl": "", "page": "", "title": ""}
for k, v in c.items():
    path = f'img/card/{k}.webp'
    if not os.path.exists(path):
        print(f"  ! missing {path}, skipping"); continue
    emb[k] = {"src": "data:image/webp;base64," + base64.b64encode(open(path,'rb').read()).decode(),
              "by": v["artist"], "lic": v["license"], "licurl": v.get("licurl",""),
              "page": v["page"], "title": v["title"]}
json.dump(emb, open('img/embed.json','w'), separators=(',',':'), ensure_ascii=True)
print(f"img/embed.json: {os.path.getsize('img/embed.json')/1024:.0f} KB, {len(emb)} images")
