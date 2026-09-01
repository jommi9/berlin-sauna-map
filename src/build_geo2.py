import json, math, sys
sys.setrecursionlimit(100000)

LON0, LON1 = 13.300, 13.490
LAT0, LAT1 = 52.462, 52.547
W = 1000.0
def dmerc(lat): return math.degrees(math.log(math.tan(math.pi/4 + math.radians(lat)/2)))
SX = W/(LON1-LON0); DM0, DM1 = dmerc(LAT0), dmerc(LAT1); H = (DM1-DM0)*SX
def proj(lon, lat): return ((lon-LON0)*SX, (DM1-dmerc(lat))*SX)

PAD = 40.0
def inbox(pts): return any(-PAD<=x<=W+PAD and -PAD<=y<=H+PAD for x,y in pts)

def rdp(pts, eps):
    stack, keep = [(0, len(pts)-1)], [False]*len(pts)
    keep[0] = keep[-1] = True
    while stack:
        i, j = stack.pop()
        if j <= i+1: continue
        x0,y0 = pts[i]; x1,y1 = pts[j]
        dx,dy = x1-x0, y1-y0; n = math.hypot(dx,dy)
        imax, dmax = -1, eps
        for k in range(i+1, j):
            px,py = pts[k]
            d = abs(dx*(y0-py)-(x0-px)*dy)/n if n else math.hypot(px-x0, py-y0)
            if d > dmax: imax, dmax = k, d
        if imax > 0:
            keep[imax] = True; stack.append((i,imax)); stack.append((imax,j))
    return [p for p,k in zip(pts, keep) if k]

def mkpath(lonlat, eps, close=False):
    pts = [proj(a,b) for a,b in lonlat]
    if not inbox(pts): return None
    if len(pts) > 2: pts = rdp(pts, eps)
    if len(pts) < 2: return None
    d = "M" + " ".join(f"{x:.1f},{y:.1f}" for x,y in pts)
    return d + ("Z" if close else "")

out = {"w": round(W,1), "h": round(H,1), "bbox":[LON0,LAT0,LON1,LAT1], "sx": round(SX,4), "dm1": DM1,
       "districts": [], "water": [], "rivers": [], "parks": [], "roads": {"motorway":[],"primary":[],"secondary":[]}, "rail": []}

# districts -> boundary lines only
for f in json.load(open('bezirke.geojson'))['features']:
    g = f['geometry']; polys = g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    ds = [p for poly in polys if (p := mkpath([(c[0],c[1]) for c in poly[0]], 1.3, True))]
    if ds: out['districts'].append({"n": f['properties'].get('spatial_alias'), "d": " ".join(ds)})

# water
for e in json.load(open('water.json'))['elements']:
    gm = e.get('geometry')
    if not gm: continue
    ll = [(p['lon'],p['lat']) for p in gm if p]
    if len(ll) < 2: continue
    ww = e.get('tags',{}).get('waterway')
    pts = [proj(*p) for p in ll]
    span = max(max(x for x,_ in pts)-min(x for x,_ in pts), max(y for _,y in pts)-min(y for _,y in pts))
    if ww in ('river','canal'):
        if span > 4 and (d := mkpath(ll, 0.7)): out['rivers'].append({"d": d, "c": ww})
    elif span >= 6:
        if d := mkpath(ll, 0.9, ll[0]==ll[-1]): out['water'].append(d)

# parks / green
for e in json.load(open('parks.json'))['elements']:
    gm = e.get('geometry')
    if not gm or len(gm) < 4: continue
    ll = [(p['lon'],p['lat']) for p in gm]
    pts = [proj(*p) for p in ll]
    area = abs(sum(pts[i][0]*pts[i-1][1]-pts[i-1][0]*pts[i][1] for i in range(len(pts))))/2
    if area < 280: continue
    if d := mkpath(ll, 1.1, True): out['parks'].append(d)

# roads
CLS = {"motorway":"motorway","motorway_link":"motorway","trunk":"motorway","primary":"primary","secondary":"secondary"}
EPS = {"motorway":0.6,"primary":0.8,"secondary":1.1}
for e in json.load(open('roads.json'))['elements']:
    gm = e.get('geometry')
    if not gm or len(gm) < 2: continue
    c = CLS.get(e['tags'].get('highway'))
    if not c: continue
    if d := mkpath([(p['lon'],p['lat']) for p in gm], EPS[c]): out['roads'][c].append(d)

# rail
for e in json.load(open('rail.json'))['elements']:
    gm = e.get('geometry')
    if not gm or len(gm) < 2: continue
    if d := mkpath([(p['lon'],p['lat']) for p in gm], 1.0): out['rail'].append(d)

# collapse each layer to a single path string: 9k DOM nodes -> ~8
flat = {"w": out["w"], "h": out["h"], "bbox": out["bbox"], "sx": out["sx"], "dm1": out["dm1"],
        "districts": " ".join(d["d"] for d in out["districts"]),
        "water": " ".join(out["water"]),
        "river": " ".join(r["d"] for r in out["rivers"] if r["c"] == "river"),
        "canal": " ".join(r["d"] for r in out["rivers"] if r["c"] == "canal"),
        "parks": " ".join(out["parks"]),
        "motorway": " ".join(out["roads"]["motorway"]),
        "primary": " ".join(out["roads"]["primary"]),
        "secondary": " ".join(out["roads"]["secondary"]),
        "rail": " ".join(out["rail"]),
        "labels": []}
json.dump(flat, open('geo.json','w'), separators=(',',':'), ensure_ascii=True)
import os
print(f"canvas {W}x{H:.0f}")
print(f"districts {len(out['districts'])} | water {len(out['water'])} | rivers {len(out['rivers'])} | parks {len(out['parks'])}")
print(f"roads mtw {len(out['roads']['motorway'])} pri {len(out['roads']['primary'])} sec {len(out['roads']['secondary'])} | rail {len(out['rail'])}")
print(f"geo.json {os.path.getsize('geo.json')/1024:.0f} KB")
