#!/usr/bin/env python3
"""Turn a contributor's "New listing" or "New city" issue into changes ready for a pull request.

    python3 engine/propose.py <issue.json>

Run by .github/workflows/propose.yml. Only GitHub users named in contributors.json
may add listings or cities; anyone else's issue is answered and left alone. What
a contributor sends is still only a proposal: this script checks it, writes it
into the city's venues.py (or makes the new city's folder), rebuilds, and the
workflow opens a pull request that the owner reads and merges. Nothing reaches
the site without that merge.

A listing has to clear the same bar as one added by hand (CLAUDE.md, "Data
sourcing"): engine/verify_venue.py must find the venue's own site live and
talking about a sauna. OK and THIN go forward, THIN with a warning that the
page shows no prices or hours; BLOCKED goes forward marked for a human to read
the site; anything else is refused with the verdict.

Everything typed into the form ends up inside innerHTML on the page, so markup
characters are refused outright rather than cleaned up, and the text is written
into venues.py as JSON string literals, which are valid Python and cannot carry code.

Exit 0: files changed, the summary on stdout is the pull request's body.
Exit 1: refused, stdout says why. Exit 3: the author is not a contributor.
"""
import datetime, json, os, re, subprocess, sys, urllib.request, zoneinfo
import city
import verify_venue

issue = json.load(open(sys.argv[1], encoding="utf-8"))
author = issue["user"]["login"]
title = issue.get("title") or ""
body = issue.get("body") or ""
number = issue["number"]

def say(msg=""):
    print(msg)

def refuse(msg):
    say(f"REFUSED: {msg}")
    sys.exit(1)

def field(label, required=True, cap=400):
    """GitHub issue forms render as '### Label\\n\\nvalue'."""
    m = re.search(rf"^###\s+{re.escape(label)}\s*\n+(.*?)(?=\n###\s|\Z)", body, re.S | re.M)
    v = re.sub(r"\s+", " ", (m.group(1) if m else "")).strip()
    if v in ("_No response_", "_Keine Angabe_", "None"):
        v = ""
    if required and not v:
        refuse(f"'{label}' is empty")
    if len(v) > cap:
        refuse(f"'{label}' is longer than {cap} characters")
    bad = sorted(set(re.findall(r'[<>"`\\]', v)))
    if bad:
        refuse(f"'{label}' contains {' '.join(bad)} - plain text only, and use ' for quotes")
    return v

contributors = {k.lower() for k in json.load(open(os.path.join(city.ROOT, "contributors.json"), encoding="utf-8"))}
if author.lower() not in contributors:
    say(f"@{author} is not on the contributors list, so this was not turned into a pull request. "
        f"It stays open as a suggestion for a contributor to pick up.")
    sys.exit(3)

def engine(script, *args):
    done = subprocess.run([sys.executable, os.path.join(city.ENGINE, script), *args],
                          capture_output=True, text=True)
    if done.returncode:
        refuse(f"{script} failed:\n{(done.stdout + done.stderr)[-1500:]}")
    return done.stdout

def lit(value):
    """A Python literal for a string, a number or None."""
    if value is None:
        return "None"
    if isinstance(value, (int, float)):
        return repr(value)
    return json.dumps(value, ensure_ascii=False)

# ------------------------------------------------------------------ a new listing
LOYLY = {"I throw my own": "self", "Staff throw it (Aufguss)": "scheduled",
         "A machine doses it": "auto", "Not known": "unknown"}

def new_listing():
    slug = field("City").lower()
    if slug not in city.slugs():
        refuse(f"no city called {slug!r}; the cities are {', '.join(city.slugs())}. "
               f"A new city needs the 'New city' form first.")
    cfg = city.load(slug)
    name = field("Name", cap=70)
    url = field("Official website", cap=300)
    if not re.fullmatch(r"https://[^\s'<>\"]+\.[^\s'<>\"]+", url):
        refuse("the website has to be an https:// address on the venue's own site")
    if re.search(r"(facebook|instagram|tripadvisor|yelp|google|urbansportsclub)\.", url):
        refuse("the website has to be the venue's own site, not a listing or a social page")
    m = re.fullmatch(r"\s*(-?\d{1,3}\.\d{3,8})\s*[, ]\s*(-?\d{1,3}\.\d{3,8})\s*", field("Coordinates"))
    if not m:
        refuse("coordinates look like '60.18651, 24.95734': latitude, then longitude, at least three decimals")
    lat, lon = float(m.group(1)), float(m.group(2))
    w, s, e, n = cfg["bbox"]
    if not (s <= lat <= n and w <= lon <= e):
        refuse(f"{lat}, {lon} is outside the {cfg['name']} map, which covers latitude {s} to {n} and "
               f"longitude {w} to {e}. Check the two numbers are the right way round.")
    price_text = field("Cheapest entry", required=False, cap=12).replace(",", ".")
    price = None
    if price_text:
        pm = re.fullmatch(r"[^\d]{0,3}(\d{1,4}(?:\.\d{1,2})?)[^\d]{0,3}", price_text)
        if not pm:
            refuse("the cheapest entry is one number, like 18 or 27.50; leave it empty if their site gives none")
        price = float(pm.group(1))
        price = int(price) if price == int(price) else price
    loyly = field("Who throws the water?", required=False) or "Not known"
    if loyly not in LOYLY:
        refuse(f"'Who throws the water?' should be one of: {', '.join(LOYLY)}")
    row = [name, lat, lon, field("Kind", cap=50), field("Neighbourhood", cap=50), price,
           field("Prices in words", cap=220),
           "no", "Not checked for Urban Sports Club" if cfg.get("usc") else "",
           field("Sauna", cap=260), field("Pool or cold water", cap=160), field("Opening hours", cap=220),
           field("Best for", cap=70), None, field("Heads up", required=False, cap=260) or None, url]

    # the name is the key everywhere, including the social layer, so it is unique across cities
    for other in city.slugs():
        names = {v["name"].lower() for v in json.load(open(os.path.join(city.ROOT, other, "venues.json"), encoding="utf-8"))}
        if name.lower() in names:
            refuse(f"{name!r} is already listed in {other}")

    e = verify_venue.check(name, url)
    verdict = e["verdict"]
    if verdict not in ("OK", "THIN", "BLOCKED"):
        refuse(f"the venue's own site did not pass the check: {verdict} ({e.get('why', '')}). "
               f"Only a live site that mentions a sauna can be listed. Checked {url}")

    path = os.path.join(city.ROOT, slug, "venues.py")
    src = open(path, encoding="utf-8").read()
    start = re.search(r"^V = \[\n", src, re.M)
    if not start or len(re.findall(r"^V = \[\n", src, re.M)) != 1:
        refuse(f"could not find the one venue list in {slug}/venues.py")
    end = src.find("\n]\n", start.end() - 1)
    if end < 0:
        refuse(f"could not find the end of the venue list in {slug}/venues.py")
    text = (f" # Proposed by @{author} in #{number}; verify_venue.py said {verdict} on "
            f"{datetime.date.today().isoformat()}.\n"
            f" [{', '.join(lit(x) for x in row[:9])},\n"
            f"  {', '.join(lit(x) for x in row[9:15])},\n"
            f"  {lit(row[15])}],")
    src = src[:end] + "\n" + text + src[end:]
    kind = LOYLY[loyly]
    if kind != "unknown":
        entry = f" {lit(name)}: (None, {lit(kind)}, None),"
        heat = re.search(r"^HEAT = \{\n", src, re.M)
        if heat:
            close = src.find("\n}\n", heat.end() - 1)
            src = src[:close] + "\n" + entry + src[close:]
        else:
            stamp = re.search(r"^LAST_CHECKED = ", src, re.M)
            block = ("# --- Who throws the water, as the contributor who added the venue reported it.\n"
                     "HEAT = {\n" + entry + "\n}\n\n")
            src = src[:stamp.start()] + block + src[stamp.start():]
    open(path, "w", encoding="utf-8").write(src)
    engine("build.py", slug)

    say(f"Adds **{name}** to the {cfg['name']} map, proposed by @{author} in #{number}.")
    say()
    say(f"- Their site: {url}")
    say(f"- `verify_venue.py`: **{verdict}**, {e.get('why', '')}")
    if e.get("prices"):
        say(f"- Prices the check saw on the page: {', '.join(e['prices'])}")
    if e.get("hours"):
        say(f"- Hours the check saw on the page: {', '.join(e['hours'])}")
    if verdict == "THIN":
        say("- **The page shows no prices or hours.** Ask where the figures in this row came from before merging.")
    if verdict == "BLOCKED":
        say("- **Their site blocks automated reads**, so nothing was checked. Read it by hand before merging.")
    say(f"- Entry: {row[6]}" + (f" (from {price:g})" if price is not None else " (no figure given)"))
    say(f"- Hours as typed: {row[11]}")
    say(f"- Who throws the water: {loyly}")
    say()
    say("Before merging: read the prices and hours off the venue's own page, and add structured hours "
        f"to `OPEN` in `{slug}/venues.py` if the card should say open or closed. Merging closes #{number}.")

# ------------------------------------------------------------------ a new city
RESERVED = {"engine", "src", "img", "api", "sauna", "docs", "test", "tests"}

def new_city():
    name = field("City name", cap=40)
    slug = field("Short name for the address", cap=24).lower()
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,23}", slug) or slug in RESERVED:
        refuse("the short name is lowercase letters, digits and hyphens, like 'tampere'")
    if slug in city.slugs() or os.path.exists(os.path.join(city.ROOT, slug)):
        refuse(f"there is already a '{slug}'")
    country = field("Country code", cap=2).upper()
    if not re.fullmatch(r"[A-Z]{2}", country):
        refuse("the country code is two letters, like FI")
    tz = field("Timezone", cap=40)
    try:
        zoneinfo.ZoneInfo(tz)
    except Exception:
        refuse(f"{tz!r} is not a timezone name; they look like Europe/Helsinki")
    nums = re.findall(r"-?\d{1,3}(?:\.\d+)?", field("Map frame", cap=80))
    if len(nums) != 4:
        refuse("the map frame is four numbers: west, south, east, north")
    w, s, e, n = (float(x) for x in nums)
    if not (-180 <= w < e <= 180 and -85 <= s < n <= 85):
        refuse("the map frame is west, south, east, north, with west below east and south below north")
    if e - w > 0.6 or n - s > 0.4 or e - w < 0.03 or n - s < 0.02:
        refuse("the map frame should cover a city: between 0.03 and 0.6 degrees wide and 0.02 and 0.4 tall. "
               "Berlin's is 0.19 wide and 0.085 tall.")
    extract = field("OpenStreetMap extract", cap=40)
    if not re.fullmatch(r"[A-Za-z]{3,40}", extract):
        refuse("the extract is BBBike's name for the city, letters only, like Helsinki or NewYork")
    currency = field("Currency sign", cap=3)
    temp = "F" if field("Temperatures", required=False).startswith("Fahrenheit") else "C"
    lede = field("One line about the city's saunas", cap=160)

    folder = os.path.join(city.ROOT, slug)
    pbf = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), f"{extract}.osm.pbf")
    source = f"https://download.bbbike.org/osm/bbbike/{extract}/{extract}.osm.pbf"
    try:
        with urllib.request.urlopen(urllib.request.Request(source, headers=city.UA), timeout=600) as r, open(pbf, "wb") as out:
            while chunk := r.read(1 << 20):
                out.write(chunk)
    except Exception as err:
        refuse(f"could not download {source} ({type(err).__name__}). The names are listed at "
               f"https://download.bbbike.org/osm/bbbike/")
    os.makedirs(os.path.join(folder, "img", "card"))
    cfg = {"name": name, "country": country, "timezone": tz, "bbox": [w, s, e, n], "lede": lede,
           "notionIntro": f"{name} sauna shortlist.", "currency": currency, "temp": temp, "usc": False}
    text = json.dumps(cfg, indent=2, ensure_ascii=False)
    text = re.sub(r'"bbox": \[\s*([^\]]+?)\s*\]', lambda m: '"bbox": [' + ", ".join(x.strip() for x in m.group(1).split(",")) + "]", text)
    open(os.path.join(folder, "city.json"), "w", encoding="utf-8").write(text + "\n")
    today = datetime.date.today().strftime("%-d %B %Y")
    open(os.path.join(folder, "venues.py"), "w", encoding="utf-8").write(
        f'# -*- coding: utf-8 -*-\n"""{name}: every fact about its venues. This file is the source of truth.\n\n'
        f'Opened by @{author} in #{number}. Listings arrive one at a time through the\n'
        f'"New listing" form, each checked against the venue\'s own site.\n"""\n\n'
        f"# name, lat, lon, kind, district, price(from|None), priceLabel, usc, uscLabel,\n"
        f"# sauna, pool, hours, bestFor, badge, flag, url\nV = [\n]\n\n"
        f'LAST_CHECKED = "{today}"\n')
    open(os.path.join(folder, "reviews.json"), "w").write("[]\n")
    open(os.path.join(folder, "img", "credits.json"), "w").write("{}\n")
    open(os.path.join(folder, "img", "card", ".gitkeep"), "w").write("")
    out = engine("osm_extract.py", slug, pbf) + engine("build_geo.py", slug)
    engine("build.py")            # every city: each page's switcher lists the new one
    geo = json.load(open(os.path.join(folder, "geo.json")))
    drawn = sum(len(geo.get(k) or "") for k in ("primary", "secondary", "motorway"))
    if drawn < 2000:
        refuse(f"the map frame holds almost no roads in the {extract} extract. Either the frame is not "
               f"inside that city, or the numbers are in the wrong order (west, south, east, north).")

    say(f"Opens **{name}** as `{slug}/`, proposed by @{author} in #{number}. It has a base map and no listings yet.")
    say()
    say(f"- Map frame: west {w}, south {s}, east {e}, north {n}, drawn from BBBike's `{extract}` extract")
    say(f"- {tz}, prices in {currency}, temperatures in °{temp}")
    say("- " + " · ".join(l for l in out.splitlines() if l.startswith(("canvas", "sea:", "roads mtw"))))
    say()
    say(f"Before merging: look at `{slug}/index.html` to check the frame shows the right part of the city. "
        f"After merging: add listings with the 'New listing' form, take the share image with "
        f"`node engine/og.js {slug}`, and open the city on jommi.fi (the hub's city list and the Worker's "
        f"live cities, both in `jommi9/jommi-fi`). Merging closes #{number}.")

if title.lower().startswith("new listing"):
    new_listing()
elif title.lower().startswith("new city"):
    new_city()
else:
    refuse("the issue title has to start with 'New listing:' or 'New city:', as the forms set it")
