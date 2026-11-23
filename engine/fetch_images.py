"""Read the credits for a city's photos off Wikimedia Commons into img/credits.json.

    python3 engine/fetch_images.py <city>

Which Commons file stands behind which photo key is the city's own table,
COMMONS in its venues.py.
"""
import json, re, time, urllib.parse, urllib.request, html, os
import city
city.enter()
from venues import COMMONS as PICK

UA = city.UA
def strip(h_):
    return re.sub(r'\s+',' ', html.unescape(re.sub(r'<[^>]+>','',h_ or ''))).strip()

out={}
for k,title in PICK.items():
    u=("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo"
       f"&titles={urllib.parse.quote(title)}&iiprop=url|size|extmetadata&iiurlwidth=900")
    for a in range(4):
        try:
            r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40)); break
        except Exception as e:
            if a==3: r=None
            time.sleep(4*(a+1))
    if not r: print("FAIL",k); continue
    pg=list(r["query"]["pages"].values())[0]
    if "imageinfo" not in pg: print("MISSING",k,title); continue
    ii=pg["imageinfo"][0]; md=ii.get("extmetadata",{})
    g=lambda f: strip((md.get(f) or {}).get("value",""))
    out[k]={"title":pg["title"][5:],"thumb":ii["thumburl"],"w":ii["width"],"h":ii["height"],
            "artist":g("Artist"),"license":g("LicenseShortName"),"licurl":g("LicenseUrl"),
            "page":ii["descriptionurl"],"desc":g("ImageDescription")[:110]}
    print(f"{k:14} {ii['width']}x{ii['height']:<6} {out[k]['license'][:16]:18} {out[k]['artist'][:34]:36} {out[k]['desc'][:40]}")
    time.sleep(1.2)
json.dump(out, open('img/credits.json','w'), indent=1, ensure_ascii=False)
print("\nwrote credits for", len(out), "images")
