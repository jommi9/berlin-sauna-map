#!/usr/bin/env python3
"""Fetch a small box of OpenStreetMap from its own API and save it as an .osm.pbf.

    python3 engine/osm_fill.py <W> <S> <E> <N> <out.osm.pbf>

For the holes between city extracts. A frame that reaches past every extract BBBike
publishes has land the base map would draw as open sea, because no coastline was read
there. This fetches that strip tile by tile from api.openstreetmap.org (the "map" call,
which returns every way that touches a box, whole) and writes it in the same format, so
engine/osm_extract.py takes it as one more extract beside the others.

The API is for editors, not for bulk downloads: keep the box to the hole. A tile the
API refuses as too large is cut in four and tried again.
"""
import struct, sys, time, urllib.request, zlib
import xml.etree.ElementTree as ET
import osm_extract as X

STEP = 0.025
AGENT = "sauna-maps-build/1.0 (base map fill; github.com/jommi9/sauna-maps)"
Block = X.M["PrimitiveBlock"]
Header = X.M["BlobHeader"]
Blob = X.M["Blob"]

def fetch(w, s, e, n, depth=0):
    """The API's XML for one box, as a list of roots; a refused box is quartered."""
    url = f"https://api.openstreetmap.org/api/0.6/map?bbox={w:.5f},{s:.5f},{e:.5f},{n:.5f}"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENT})
            with urllib.request.urlopen(req, timeout=180) as r:
                return [ET.fromstring(r.read())]
        except urllib.error.HTTPError as err:
            if err.code in (400, 509) and depth < 4:      # too many nodes in the box
                mx, my = (w + e) / 2, (s + n) / 2
                out = []
                for box in ((w, s, mx, my), (mx, s, e, my), (w, my, mx, n), (mx, my, e, n)):
                    out += fetch(*box, depth + 1)
                return out
            if err.code not in (429, 500, 502, 503, 504):
                raise
        except OSError:
            pass
        time.sleep(5 * (attempt + 1))
    raise SystemExit(f"could not fetch {url}")

def main():
    if len(sys.argv) != 6:
        raise SystemExit("usage: osm_fill.py <W> <S> <E> <N> <out.osm.pbf>")
    W, S, E, N = map(float, sys.argv[1:5])
    nodes, ways, rels = {}, {}, {}
    y = S
    while y < N - 1e-9:
        x = W
        while x < E - 1e-9:
            for root in fetch(x, y, min(x + STEP, E), min(y + STEP, N)):
                for el in root:
                    t = {c.get("k"): c.get("v") for c in el.iter("tag")}
                    i = int(el.get("id", 0))
                    if el.tag == "node" and el.get("lat"):
                        nodes[i] = (float(el.get("lat")), float(el.get("lon")), t)
                    elif el.tag == "way":
                        ways[i] = ([int(c.get("ref")) for c in el.iter("nd")], t)
                    elif el.tag == "relation":
                        rels[i] = ([(c.get("type"), int(c.get("ref")), c.get("role") or "") for c in el.iter("member")], t)
            print(f"  {x:.3f},{y:.3f}: {len(nodes)} nodes, {len(ways)} ways, {len(rels)} relations so far", flush=True)
            time.sleep(1)
            x += STEP
        y += STEP

    out = open(sys.argv[5], "wb")
    def write(block):
        data = block.SerializeToString()
        blob = Blob(raw_size=len(data), zlib_data=zlib.compress(data)).SerializeToString()
        head = Header(type="OSMData", datasize=len(blob)).SerializeToString()
        out.write(struct.pack(">I", len(head)) + head + blob)
    def start():
        block, table = Block(), {"": 0}
        block.stringtable.s.append(b"")
        def sid(text):
            if text not in table:
                table[text] = len(table)
                block.stringtable.s.append(text.encode("utf-8"))
            return table[text]
        return block, sid
    def delta(values):
        last, out_ = 0, []
        for v in values:
            out_.append(v - last); last = v
        return out_

    ids = sorted(nodes)
    for a in range(0, len(ids), 8000):
        block, sid = start()
        part = ids[a:a + 8000]
        d = block.primitivegroup.add().dense
        d.id.extend(delta(part))
        d.lat.extend(delta([round(nodes[i][0] * 1e7) for i in part]))
        d.lon.extend(delta([round(nodes[i][1] * 1e7) for i in part]))
        for i in part:
            for k, v in nodes[i][2].items():
                d.keys_vals.extend((sid(k), sid(v)))
            d.keys_vals.append(0)
        write(block)
    wids = sorted(ways)
    for a in range(0, len(wids), 8000):
        block, sid = start()
        g = block.primitivegroup.add()
        for i in wids[a:a + 8000]:
            refs, t = ways[i]
            w = g.ways.add(id=i)
            w.keys.extend(sid(k) for k in t); w.vals.extend(sid(v) for v in t.values())
            w.refs.extend(delta(refs))
        write(block)
    rids = sorted(rels)
    for a in range(0, len(rids), 2000):
        block, sid = start()
        g = block.primitivegroup.add()
        for i in rids[a:a + 2000]:
            mem, t = rels[i]
            r = g.relations.add(id=i)
            r.keys.extend(sid(k) for k in t); r.vals.extend(sid(v) for v in t.values())
            r.roles_sid.extend(sid(role) for _, _, role in mem)
            r.memids.extend(delta([ref for _, ref, _ in mem]))
            r.types.extend({"node": 0, "way": 1, "relation": 2}[ty] for ty, _, _ in mem)
        write(block)
    out.close()
    print(f"wrote {sys.argv[5]}: {len(nodes)} nodes, {len(ways)} ways, {len(rels)} relations")

if __name__ == "__main__":
    main()
