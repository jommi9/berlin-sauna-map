"""Join a city's tables (<city>/venues.py) into venues.json and meta.json.

    python3 engine/build_venues.py <city>

The facts live in the city's venues.py and nowhere else. What is here is what
every city shares: the projection onto the map, who-throws-the-water and the
sauna culture derived from it, and the joins. A table a city has no use for
(USC_TIERS in a city without Urban Sports Club, say) can simply be left out of
its venues.py.
"""
import datetime, json, math, os
import city
CITY = city.enter()
import venues as data

g = json.load(open('geo.json'))
LON0, LAT0, LON1, LAT1 = g['bbox']; SX = g['sx']; DM1 = g['dm1']
def proj(lon, lat):
    dm = math.degrees(math.log(math.tan(math.pi/4 + math.radians(lat)/2)))
    return round((lon-LON0)*SX, 1), round((DM1-dm)*SX, 1)

def table(name, default):
    return getattr(data, name, default)

V = data.V
IMG = table("IMG", {})
USC_TIERS = table("USC_TIERS", {})
OPEN = table("OPEN", {})
HOURS_TEXT = table("HOURS_TEXT", {})
GROUP_PRICED = table("GROUP_PRICED", set())
HEAT = table("HEAT", {})
HEAT_SOURCE = table("HEAT_SOURCE", None)
BANYA = table("BANYA", set())
FINNISH = table("FINNISH", {})
AUFGUSS_SCORE = table("AUFGUSS_SCORE", {})
PICKS = table("PICKS", [])
PRACTICAL = table("PRACTICAL", "")
TRAPS = table("TRAPS", [])
LAST_CHECKED = data.LAST_CHECKED
# The hero stamp wants the same date as dd.mm.yyyy; derived here so the two
# can never show different days.
LAST_CHECKED_STAMP = datetime.datetime.strptime(LAST_CHECKED, "%d %B %Y").strftime("%d.%m.%Y")


# --- Who actually throws the water. This is the distinction that decides
#     whether a place is a sauna or a warm room on a timetable, so it is derived
#     from the aufguss kind the venues themselves confirmed rather than typed
#     out a second time and left to drift.
#       staff   someone else throws and you sit and take it (Aufguss)
#       self    you throw your own loyly
#       machine a dispenser doses aroma; nobody throws anything
LOYLY_OF = {"scheduled": "staff", "request": "staff", "self": "self",
            "auto": "machine", "unknown": "unknown"}

# --- Which sauna culture a place belongs to, derived from who throws the water
#     and never typed separately: you throw your own (Finnish), a sauna master
#     throws the Aufguss (German), you throw your own in a banya (Russian), or a
#     machine doses it and nobody may (no loyly - a fake sauna by Finnish
#     standards). A banya is the one thing the loyly cannot tell apart, so each
#     city names its banyas in BANYA.
def style_of(name, loyly):
    if loyly == "self":
        return "russian" if name in BANYA else "finnish"
    return {"staff": "german", "machine": "none"}.get(loyly, "unknown")

LOYLY_TEXT = {
 "staff":   "Someone throws for you \u2014 Aufguss",
 "self":    "You throw your own l\u00f6yly",
 "machine": "Automatic dosing \u2014 nobody throws",
 "unknown": "Not known",
}


# --- Reviews. reviewers.json and reviews.json are written by the issue-ingest
#     workflow, never by hand: a reviewer is approved by labelling their
#     application issue, and a review is accepted only from an approved handle
#     for a venue that exists. Both are plain JSON so a bad ingest is a
#     reviewable diff rather than a silent database write. The panel is one
#     list for every city (reviewers.json at the repo root); a review belongs
#     to the city whose folder its reviews.json sits in.
REVIEWERS = json.load(open(os.path.join(city.ROOT, 'reviewers.json'), encoding='utf-8'))
REVIEWS = json.load(open('reviews.json', encoding='utf-8'))

def reviews_for(name):
    rs = [r for r in REVIEWS if r.get("venue") == name and r.get("reviewer") in REVIEWERS]
    rs.sort(key=lambda r: r.get("submitted", ""), reverse=True)
    for r in rs:
        who = REVIEWERS[r["reviewer"]]
        r["by"] = who.get("name") or r["reviewer"]
        r["handle"] = r["reviewer"]
    return rs

keys = ["name","lat","lon","kind","district","price","priceLabel","usc","uscLabel","sauna","pool","hours","bestFor","badge","flag","url"]
venues = []
for i, row in enumerate(V):
    d = dict(zip(keys, row))
    d["x"], d["y"] = proj(d["lon"], d["lat"])
    d["img"] = IMG.get(d["name"])
    d["uscTiers"] = USC_TIERS.get(d["name"], [])
    d["open"] = OPEN.get(d["name"])
    d["pricing"] = "group" if d["name"] in GROUP_PRICED else "person"
    t, a, note = HEAT.get(d["name"], (None, "unknown", None))
    if t: d["sauna"] = t
    d["aufguss"], d["aufgussNote"] = a, note
    d["loyly"] = LOYLY_OF[a]
    d["loylyText"] = LOYLY_TEXT[d["loyly"]]
    d["style"] = style_of(d["name"], d["loyly"])
    d["finnish"] = FINNISH.get(d["name"])
    if d["finnish"] is not None:
        assert d["finnish"] * 2 == int(d["finnish"] * 2) and 0 <= d["finnish"] <= 5, \
            f"{d['name']}: a Finnish score is 0-5 stars in halves, got {d['finnish']}"
    # An Aufguss score on a sauna where you throw your own would be rating
    # something that does not happen there.
    d["aufgussScore"] = AUFGUSS_SCORE.get(d["name"]) if d["loyly"] == "staff" else None
    d["heatSrc"] = HEAT_SOURCE if t else None
    d["reviews"] = reviews_for(d["name"])
    rated = [r["rating"] for r in d["reviews"] if isinstance(r.get("rating"), (int, float))]
    d["rating"] = round(sum(rated) / len(rated), 1) if rated else None
    d["hours"] = HOURS_TEXT.get(d["name"], d["hours"])
    # A closure has exactly one date, in OPEN. Writing the same date again as
    # prose is how "summer break through 31 Oct" outlived the venue shortening
    # its break to 30 Sep, so the sentence is generated from the date instead -
    # and the page regenerates it again at render time, so it goes stale for
    # hours rather than until the next build.
    if d["open"] and d["open"].get("closedUntil"):
        until = datetime.date.fromisoformat(d["open"]["closedUntil"])
        d["hours"] = f"Sauna closed until {until.day} {until:%B %Y}"
    d["id"] = i
    venues.append(d)
_names = {v["name"] for v in venues}
for _n in list(FINNISH) + list(AUFGUSS_SCORE) + list(BANYA):
    assert _n in _names, f"{_n!r} is scored or tagged but is not a venue name"
json.dump(venues, open('venues.json','w'), separators=(',',':'), ensure_ascii=False)
json.dump({"picks": [list(p) for p in PICKS], "practical": PRACTICAL, "lastChecked": LAST_CHECKED,
           "lastCheckedStamp": LAST_CHECKED_STAMP, "traps": [list(t) for t in TRAPS],
           "count": len(venues), "reviewers": REVIEWERS, "loylyText": LOYLY_TEXT},
          open('meta.json','w'), separators=(',',':'), ensure_ascii=False)
print(len(venues), "venues")
xs=[v['x'] for v in venues]; ys=[v['y'] for v in venues]
print("x range", min(xs), max(xs), "| y range", min(ys), max(ys), "| canvas", g['w'], g['h'])
