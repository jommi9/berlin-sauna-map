import json, re, time, urllib.parse, urllib.request, html, os

PICK = {
 "hyatt":"File:2023 Grand Hyatt Hotel Berlin.jpg",
 "hilton":"File:MitteMohrenstraßeHotelHilton.jpg",
 "steigenberger":"File:2023 Steigenberger Hotel Berlin.jpg",
 "derome":"File:Hotel de Rome, Berlin (1X7A5173).jpg",
 "adlon":"File:Adlon Hotel Berlin Germany - 01.jpg",
 "palace":"File:Hotel Palace bei Nacht 20140726 5.jpg",
 "titanic":"File:2023 Hotel Titanic Berlin.jpg",
 "parkinn":"File:Park Inn by Radisson Alexanderplatz - Berlin.jpg",
 "intercon":"File:Berlin Hotel Intercontinental-20241207-RM-104709.jpg",
 "westin":"File:Westin Grand Berlin, 2024 (01).jpg",
 "neukoelln":"File:Stadtbad B-Neukoelln 07-2014.jpg",
 "liquidrom":"File:Tempodrom, Berlín, Alemania, 2016-04-22, DD 01-03 HDR.JPG",
}
UA = {"User-Agent":"berlin-sauna-map/1.0 (personal project; https://github.com/jommi9/berlin-sauna-map)"}
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
