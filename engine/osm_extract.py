#!/usr/bin/env python3
"""Cut a city's base-map layers out of an OpenStreetMap .osm.pbf extract.

    python3 engine/osm_extract.py <city> <extract.osm.pbf> [<another.osm.pbf> ...]

A frame wider than one extract takes several: San Francisco with the East Bay is the
SanFrancisco and Berkeley extracts read together, and what both hold is kept once.

This stands in for engine/fetch.sh where Overpass cannot be reached (a cloud
session's network resets every Overpass connection). It writes the same files
fetch.sh would, in Overpass's "out geom" shape, so engine/build_geo.py reads
either: water.json, parks.json, roads.json, rail.json. It also writes
districts.geojson (boundary lines at city.json's "districtLevel", if any),
places.json (named suburbs and neighbourhoods, for the map's labels), and
candidates.json, every mapped place whose tags or name say sauna, banya or
bathhouse, which is where coordinates for a new venue come from and is never
evidence that the venue exists. All of them are inputs, gitignored but for
districts.geojson.

Extracts by city: https://download.bbbike.org/osm/bbbike/<Name>/<Name>.osm.pbf
(Helsinki, NewYork, SanFrancisco, Berlin ...). Only the city's bbox is kept.

The .pbf format is protobuf blocks; the message types are declared below by
hand, so nothing beyond the protobuf runtime and numpy is needed.
"""
import json, re, struct, sys, zlib
import numpy as np
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
import city

# ---------- the .osm.pbf message types (the fields this reads; the rest is skipped)
F = descriptor_pb2.FieldDescriptorProto
fdp = descriptor_pb2.FileDescriptorProto(name="osmpbf_min.proto", package="osm", syntax="proto2")
def message(name, *fields):
    m = fdp.message_type.add(name=name)
    for number, fname, ftype, label, type_name in fields:
        f = m.field.add(name=fname, number=number, type=ftype, label=label)
        if type_name:
            f.type_name = ".osm." + type_name
        if label == F.LABEL_REPEATED and ftype not in (F.TYPE_MESSAGE, F.TYPE_BYTES, F.TYPE_STRING):
            f.options.packed = True
OPT, REP = F.LABEL_OPTIONAL, F.LABEL_REPEATED
message("BlobHeader", (1, "type", F.TYPE_STRING, OPT, None), (3, "datasize", F.TYPE_INT32, OPT, None))
message("Blob", (1, "raw", F.TYPE_BYTES, OPT, None), (2, "raw_size", F.TYPE_INT32, OPT, None),
        (3, "zlib_data", F.TYPE_BYTES, OPT, None))
message("StringTable", (1, "s", F.TYPE_BYTES, REP, None))
message("Node", (1, "id", F.TYPE_SINT64, OPT, None), (2, "keys", F.TYPE_UINT32, REP, None),
        (3, "vals", F.TYPE_UINT32, REP, None), (8, "lat", F.TYPE_SINT64, OPT, None),
        (9, "lon", F.TYPE_SINT64, OPT, None))
message("DenseNodes", (1, "id", F.TYPE_SINT64, REP, None), (8, "lat", F.TYPE_SINT64, REP, None),
        (9, "lon", F.TYPE_SINT64, REP, None), (10, "keys_vals", F.TYPE_INT32, REP, None))
message("Way", (1, "id", F.TYPE_INT64, OPT, None), (2, "keys", F.TYPE_UINT32, REP, None),
        (3, "vals", F.TYPE_UINT32, REP, None), (8, "refs", F.TYPE_SINT64, REP, None))
message("Relation", (1, "id", F.TYPE_INT64, OPT, None), (2, "keys", F.TYPE_UINT32, REP, None),
        (3, "vals", F.TYPE_UINT32, REP, None), (8, "roles_sid", F.TYPE_INT32, REP, None),
        (9, "memids", F.TYPE_SINT64, REP, None), (10, "types", F.TYPE_INT32, REP, None))
message("PrimitiveGroup", (1, "nodes", F.TYPE_MESSAGE, REP, "Node"), (2, "dense", F.TYPE_MESSAGE, OPT, "DenseNodes"),
        (3, "ways", F.TYPE_MESSAGE, REP, "Way"), (4, "relations", F.TYPE_MESSAGE, REP, "Relation"))
message("PrimitiveBlock", (1, "stringtable", F.TYPE_MESSAGE, OPT, "StringTable"),
        (2, "primitivegroup", F.TYPE_MESSAGE, REP, "PrimitiveGroup"),
        (17, "granularity", F.TYPE_INT32, OPT, None), (19, "lat_offset", F.TYPE_INT64, OPT, None),
        (20, "lon_offset", F.TYPE_INT64, OPT, None))
pool = descriptor_pool.DescriptorPool()
pool.Add(fdp)
M = {n: message_factory.GetMessageClass(pool.FindMessageTypeByName("osm." + n))
     for n in ("BlobHeader", "Blob", "PrimitiveBlock")}

def blocks(paths):
    """Every PrimitiveBlock in the files, with its string table decoded."""
    for path in paths:
        with open(path, "rb") as f:
            while head := f.read(4):
                header = M["BlobHeader"].FromString(f.read(struct.unpack(">I", head)[0]))
                blob = M["Blob"].FromString(f.read(header.datasize))
                if header.type != "OSMData":
                    continue
                data = zlib.decompress(blob.zlib_data) if blob.HasField("zlib_data") else blob.raw
                block = M["PrimitiveBlock"].FromString(data)
                yield block, [s.decode("utf-8", "replace") for s in block.stringtable.s]

def tags(keys, vals, st):
    return {st[k]: st[v] for k, v in zip(keys, vals)}

# ---------- what to keep
ROAD = {"motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary"}
PARK_LEISURE = {"park", "garden", "nature_reserve"}
PARK_LANDUSE = {"forest", "grass", "meadow", "recreation_ground", "cemetery", "village_green"}
WATER = re.compile(r"^(water|bay|wetland)$")
SAUNA_NAME = re.compile(r"sauna|banya|bania|bathhouse|bath house|turkish bath|kylpyl|uimahalli|hammam|onsen|jjimjil", re.I)

def layer(t):
    """Which dump a tagged way belongs in, or None."""
    if t.get("natural") == "coastline":
        return "water"
    if t.get("waterway") in ("river", "canal", "riverbank") or t.get("natural") in ("water",) \
       or t.get("landuse") in ("reservoir", "basin"):
        return "water"
    if t.get("highway") in ROAD:
        return "roads"
    if t.get("railway") in ("rail", "light_rail") and t.get("tunnel") not in ("yes", "building_passage") \
       and t.get("service") is None:
        return "rail"
    if t.get("leisure") in PARK_LEISURE or t.get("landuse") in PARK_LANDUSE or t.get("natural") == "wood":
        return "parks"
    return None

def is_candidate(t):
    return (t.get("leisure") == "sauna" or t.get("amenity") in ("public_bath", "sauna")
            or t.get("sauna") in ("yes", "public") or bool(SAUNA_NAME.search(t.get("name", ""))))

def main():
    cfg = city.enter()
    if len(sys.argv) < 2:
        raise SystemExit("usage: osm_extract.py <city> <extract.osm.pbf> [<another.osm.pbf> ...]")
    path = sys.argv[1:]
    W, S, E, N = cfg["bbox"]
    # a margin, so a road or a coast that leaves the frame and comes back is kept whole
    mx, my = (E - W) * 0.08, (N - S) * 0.08
    BW, BS, BE, BN = W - mx, S - my, E + mx, N + my
    level = cfg.get("districtLevel")

    # pass 1: relations. District boundaries and multipolygon water name the ways they need.
    want_ways = {}            # way id -> layer for untagged member ways
    mp_water = []             # relations whose outer ways make a water area
    for block, st in blocks(path):
        for group in block.primitivegroup:
            for r in group.relations:
                t = tags(r.keys, r.vals, st)
                mem = np.cumsum(np.array(r.memids, dtype=np.int64))
                ways = [int(m) for m, ty in zip(mem, r.types) if ty == 1]
                if level and t.get("boundary") == "administrative" and t.get("admin_level") == str(level):
                    for w in ways:
                        want_ways.setdefault(w, "districts")
                elif t.get("type") == "multipolygon" and layer(t) == "water" and t.get("natural") != "coastline":
                    outer = [int(m) for m, ty, role in zip(mem, r.types, r.roles_sid) if ty == 1 and st[role] in ("outer", "")]
                    mp_water.append(outer)
                    for w in outer:
                        want_ways.setdefault(w, "mpwater")
                elif t.get("type") == "multipolygon" and layer(t) == "parks":
                    for m, ty, role in zip(mem, r.types, r.roles_sid):
                        if ty == 1 and st[role] in ("outer", ""):
                            want_ways.setdefault(int(m), "parks")
                elif is_candidate(t):
                    pass                       # a sauna mapped as a relation is rare; skipped
    mp_water = [list(o) for o in dict.fromkeys(tuple(o) for o in mp_water)]      # a relation in two extracts, once
    print(f"pass 1: {len(want_ways)} member ways wanted, {len(mp_water)} water relations")

    # pass 2: ways
    kept = {}                 # way id -> (layer, tags, refs)
    for block, st in blocks(path):
        for group in block.primitivegroup:
            for w in group.ways:
                t = tags(w.keys, w.vals, st)
                lay = layer(t) if t else None
                if lay is None and is_candidate(t):
                    lay = "candidates"
                if lay is None:
                    lay = want_ways.get(w.id)
                elif w.id in want_ways and want_ways[w.id] == "districts":
                    kept[-w.id] = ("districts", {}, None)   # also a boundary; noted below
                if lay is None:
                    continue
                kept[w.id] = (lay, t, np.cumsum(np.array(w.refs, dtype=np.int64)))
    need = np.unique(np.concatenate([v[2] for v in kept.values() if v[2] is not None]))
    print(f"pass 2: {len(kept)} ways kept, {len(need)} nodes to place")

    # pass 3: nodes. Coordinates for every kept way, plus tagged places and saunas.
    coord = {}
    places, cand = [], []
    for block, st in blocks(path):
        g, lato, lono = block.granularity or 100, block.lat_offset, block.lon_offset
        for group in block.primitivegroup:
            d = group.dense
            if len(d.id):
                ids = np.cumsum(np.array(d.id, dtype=np.int64))
                lat = (lato + g * np.cumsum(np.array(d.lat, dtype=np.int64))) * 1e-9
                lon = (lono + g * np.cumsum(np.array(d.lon, dtype=np.int64))) * 1e-9
                hit = np.isin(ids, need, assume_unique=True)
                for i, la, lo in zip(ids[hit], lat[hit], lon[hit]):
                    coord[int(i)] = (round(float(la), 7), round(float(lo), 7))
                kv = d.keys_vals
                if len(kv) > len(ids):        # some node in this group has tags
                    inbox = (lat > BS) & (lat < BN) & (lon > BW) & (lon < BE)
                    j = 0
                    for n in range(len(ids)):
                        t = {}
                        while kv[j] != 0:
                            t[st[kv[j]]] = st[kv[j + 1]]; j += 2
                        j += 1
                        if t and inbox[n]:
                            pt = (round(float(lat[n]), 6), round(float(lon[n]), 6))
                            if t.get("place") in ("suburb", "quarter", "neighbourhood", "borough") and t.get("name"):
                                places.append({"name": t["name"], "place": t["place"], "lat": pt[0], "lon": pt[1]})
                            if is_candidate(t):
                                cand.append({"osm": f"node/{ids[n]}", "lat": pt[0], "lon": pt[1], "tags": t})
            for n in group.nodes:             # plain (non-dense) nodes, rare in extracts
                la, lo = (lato + g * n.lat) * 1e-9, (lono + g * n.lon) * 1e-9
                if n.id in need:
                    coord[n.id] = (round(la, 7), round(lo, 7))
    places = list({(p["name"], p["lat"], p["lon"]): p for p in places}.values())   # a node in two extracts, once
    cand = list({c["osm"]: c for c in cand}.values())
    print(f"pass 3: {len(coord)} nodes placed, {len(places)} place names, {len(cand)} candidate nodes")

    def geometry(refs):
        return [{"lat": coord[r][0], "lon": coord[r][1]} for r in refs if int(r) in coord]
    def touches(geom):
        return any(BS < p["lat"] < BN and BW < p["lon"] < BE for p in geom)

    dumps = {k: [] for k in ("water", "parks", "roads", "rail")}
    lines = []
    for wid, (lay, t, refs) in kept.items():
        if refs is None:
            continue
        geom = geometry(refs)
        if len(geom) < 2 or not touches(geom):
            continue
        if lay in dumps:
            dumps[lay].append({"type": "way", "id": wid, "tags": t, "geometry": geom})
        elif lay == "mpwater":
            pass                                  # assembled below
        elif lay == "districts":
            lines.append([[p["lon"], p["lat"]] for p in geom])
        elif lay == "candidates":
            la = sum(p["lat"] for p in geom) / len(geom); lo = sum(p["lon"] for p in geom) / len(geom)
            cand.append({"osm": f"way/{wid}", "lat": round(la, 6), "lon": round(lo, 6), "tags": t})
        if -wid in kept:                          # a tagged way that is also a district boundary
            lines.append([[p["lon"], p["lat"]] for p in geom])
    # Multipolygon water: chain the outer ways into rings, so a lake drawn in pieces fills.
    for outer in mp_water:
        for ring in chains([list(kept[w][2]) for w in outer if w in kept and kept[w][2] is not None]):
            geom = geometry(ring)
            if len(geom) > 3 and touches(geom) and ring[0] == ring[-1]:
                dumps["water"].append({"type": "way", "id": 0, "tags": {"natural": "water"}, "geometry": geom})
    for name, elements in dumps.items():
        json.dump({"elements": elements}, open(f"{name}.json", "w"), separators=(",", ":"))
        print(f"{name}.json: {len(elements)} ways")
    if level:
        json.dump({"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {}, "geometry": {"type": "MultiLineString", "coordinates": lines}}]},
            open("districts.geojson", "w"), separators=(",", ":"))
        print(f"districts.geojson: {len(lines)} boundary lines at admin_level {level}")
    json.dump(places, open("places.json", "w"), ensure_ascii=False, indent=0)
    json.dump(cand, open("candidates.json", "w"), ensure_ascii=False, indent=1)
    print(f"places.json: {len(places)}  candidates.json: {len(cand)}")

def chains(ways):
    """Join ways that share end nodes into the longest runs possible (rings where they close)."""
    ways = [list(w) for w in ways if len(w) > 1]
    out = []
    while ways:
        cur = ways.pop()
        grew = True
        while grew and cur[0] != cur[-1]:
            grew = False
            for i, w in enumerate(ways):
                if w[0] == cur[-1]:   cur += w[1:]
                elif w[-1] == cur[-1]: cur += w[-2::-1]
                elif w[-1] == cur[0]:  cur = w[:-1] + cur
                elif w[0] == cur[0]:   cur = w[:0:-1] + cur
                else: continue
                ways.pop(i); grew = True; break
        out.append(cur)
    return out

if __name__ == "__main__":
    main()
