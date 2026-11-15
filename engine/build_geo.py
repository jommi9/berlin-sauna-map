"""Draw a city's base map: its Overpass dumps and district outlines into geo.json.

    python3 engine/build_geo.py <city>

Needs the raw dumps in the city's folder (water.json, parks.json, roads.json,
rail.json, fetched with engine/fetch.sh or cut from an extract with
engine/osm_extract.py, and not committed) and its districts.geojson. The frame
is the bbox in the city's city.json, as [west, south, east, north]; the map is
always 1000 units wide.

The sea is drawn from the coastline (natural=coastline ways in water.json),
which OSM draws with the land on its left: the ways are joined, clipped to the
frame, and closed along the frame's edge into water polygons, with islands
left as holes. Map labels come from places.json (written by osm_extract.py)
when there is one; otherwise the labels already in geo.json are kept, because
Berlin's were placed by hand.
"""
import json, math, os, sys
import city
CITY = city.enter()
sys.setrecursionlimit(100000)

LON0, LAT0, LON1, LAT1 = CITY["bbox"]
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
# (osm_extract.py writes them as open boundary lines; Berlin's are polygons)
for f in (json.load(open('districts.geojson'))['features'] if os.path.exists('districts.geojson') else []):
    g = f['geometry']
    if g['type'] in ('LineString', 'MultiLineString'):
        lines = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
        ds = [p for line in lines if (p := mkpath([(c[0],c[1]) for c in line], 1.3))]
    else:
        polys = g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        ds = [p for poly in polys if (p := mkpath([(c[0],c[1]) for c in poly[0]], 1.3, True))]
    if ds: out['districts'].append({"d": " ".join(ds)})

# water
coast = []
for e in json.load(open('water.json'))['elements']:
    gm = e.get('geometry')
    if not gm: continue
    if e.get('tags', {}).get('natural') == 'coastline':
        coast.append([(p['lon'], p['lat']) for p in gm]); continue
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

# ---------- the sea, from the coastline
def sea_path(ways):
    """Water polygons from coastline ways, as one SVG path drawn with fill-rule evenodd.

    Worked in y-up coordinates, where OSM's rule holds: land on the left of the
    way, water on the right. Each joined coastline is clipped to the frame (with
    PAD); a piece that enters and leaves it is followed, then the frame's edge is
    walked clockwise to the next piece's entry, until the polygon closes. Closed
    rings wholly inside the frame are islands and go in as holes. With no piece
    crossing the frame at all, the frame is open sea if it holds an island."""
    if not ways:
        return ""
    # join ways end to end on shared coordinates
    runs = []
    pool = [w for w in ways if len(w) > 1]
    while pool:
        cur = list(pool.pop()); grew = True
        while grew and cur[0] != cur[-1]:
            grew = False
            for i, w in enumerate(pool):
                if w[0] == cur[-1]: cur += w[1:]
                elif w[-1] == cur[0]: cur = w[:-1] + cur
                else: continue
                pool.pop(i); grew = True; break
        runs.append(cur)
    X0, X1, Y0, Y1 = -PAD, W + PAD, -(H + PAD), PAD       # the clip frame, y-up
    def up(lon, lat):
        x, y = proj(lon, lat); return (x, -y)
    def inside(p): return X0 <= p[0] <= X1 and Y0 <= p[1] <= Y1
    def clip(a, b):
        """Liang-Barsky: the part of segment a-b in the frame as (t0, t1), or None."""
        t0, t1 = 0.0, 1.0
        dx, dy = b[0] - a[0], b[1] - a[1]
        for p, q in ((-dx, a[0] - X0), (dx, X1 - a[0]), (-dy, a[1] - Y0), (dy, Y1 - a[1])):
            if p == 0:
                if q < 0: return None
                continue
            r = q / p
            if p < 0: t0 = max(t0, r)
            else: t1 = min(t1, r)
            if t0 > t1: return None
        return t0, t1
    at = lambda a, b, t: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    pieces, rings = [], []
    for run in runs:
        pts = [up(*p) for p in run]
        closed = run[0] == run[-1]
        if closed and all(inside(p) for p in pts):
            rings.append(pts); continue
        if closed:                              # start the walk outside the frame
            k = next(i for i, p in enumerate(pts) if not inside(p))
            pts = pts[k:-1] + pts[:k + 1]
        cur = [pts[0]] if inside(pts[0]) else None
        entered = False
        for a, b in zip(pts, pts[1:]):
            c = clip(a, b)
            if c is None:
                continue
            t0, t1 = c
            if t0 > 0:                          # enters the frame on this segment
                cur, entered = [at(a, b, t0)], True
            if cur is None:
                continue
            if t1 < 1:                          # leaves it
                cur.append(at(a, b, t1))
                if entered: pieces.append(cur)
                cur, entered = None, False
            else:
                cur.append(b)
        # a piece still open here ends inside the frame: the data runs out, so it is dropped
    perim = 2 * (X1 - X0) + 2 * (Y1 - Y0)
    def t_of(p):                                 # clockwise from the top-left corner
        x, y = p
        e = 1e-6 * perim
        if abs(y - Y1) < e: return x - X0
        if abs(x - X1) < e: return (X1 - X0) + (Y1 - y)
        if abs(y - Y0) < e: return (X1 - X0) + (Y1 - Y0) + (X1 - x)
        return 2 * (X1 - X0) + (Y1 - Y0) + (y - Y0)
    corners = [(0.0, (X0, Y1)), (X1 - X0, (X1, Y1)), ((X1 - X0) + (Y1 - Y0), (X1, Y0)),
               (2 * (X1 - X0) + (Y1 - Y0), (X0, Y0))]
    polys = []
    if pieces:
        entry = [t_of(p[0]) for p in pieces]
        used = [False] * len(pieces)
        for start in range(len(pieces)):
            if used[start]: continue
            poly, i = [], start
            for _ in range(len(pieces) + 1):
                used[i] = True
                poly += pieces[i]
                tx = t_of(pieces[i][-1])
                # the next entry met walking clockwise from this exit
                j = min(range(len(pieces)), key=lambda k: (entry[k] - tx) % perim or perim)
                gap = (entry[j] - tx) % perim
                for tc, xy in sorted(corners, key=lambda c: (c[0] - tx) % perim):
                    if 0 < (tc - tx) % perim < gap: poly.append(xy)
                if j == start or used[j]: break
                i = j
            polys.append(poly)
    elif rings:
        polys.append([(X0, Y1), (X1, Y1), (X1, Y0), (X0, Y0)])
    polys += rings
    out_d = []
    for poly in polys:
        pts = [(x, -y) for x, y in poly]
        if len(pts) > 3: pts = rdp(pts, 0.8)
        if len(pts) < 3: continue
        out_d.append("M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    print(f"sea: {len(runs)} coastlines, {len(pieces)} crossing the frame, {len(rings)} islands inside it")
    return " ".join(out_d)

# ---------- labels
def labels():
    """District names for the map: the city's suburbs from places.json, spaced so
    they do not collide; or, without places.json, whatever geo.json already has."""
    if not os.path.exists('places.json'):
        try: return json.load(open('geo.json'))['labels']
        except Exception: return []
    places = json.load(open('places.json', encoding='utf-8'))
    rank = {"borough": 0, "suburb": 1, "quarter": 2, "neighbourhood": 3}
    picked = []
    for kind in sorted(set(p["place"] for p in places), key=rank.get):
        if len(picked) >= 6: break
        for p in places:
            if p["place"] != kind: continue
            x, y = proj(p["lon"], p["lat"])
            if not (40 < x < W - 40 and 30 < y < H - 30): continue
            if all(math.hypot(x - q["x"], y - q["y"]) > 150 for q in picked):
                picked.append({"t": p["name"].upper(), "x": round(x, 1), "y": round(y, 1)})
    return picked[:14]

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
        "sea": sea_path(coast),
        "labels": labels()}
json.dump(flat, open('geo.json','w'), separators=(',',':'), ensure_ascii=True)
import os
print(f"canvas {W}x{H:.0f}")
print(f"districts {len(out['districts'])} | water {len(out['water'])} | rivers {len(out['rivers'])} | parks {len(out['parks'])}")
print(f"roads mtw {len(out['roads']['motorway'])} pri {len(out['roads']['primary'])} sec {len(out['roads']['secondary'])} | rail {len(out['rail'])}")
print(f"geo.json {os.path.getsize('geo.json')/1024:.0f} KB")
