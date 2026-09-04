#!/usr/bin/env python3
"""Spot numbers that appeared at a venue's own site but are missing from our data.

verify_venue.py answers "is this venue still alive". This answers the next
question: "has the price or the opening time changed since we wrote it down".
It reports numbers, never prose - a venue rewording its facilities blurb is
noise, a venue changing 22 EUR to 25 EUR is not.

Two extraction traps, both hit for real:
  * German sites write whole euros as "40EUR" - number first, no decimals.
  * A decimal price like 24.50 matches a clock-time pattern, so times must be
    matched by lookbehind rather than stripped first.
Deliberately conservative: it flags candidates for a human, it never edits.
"""
import json, re, sys, time, unicodedata, urllib.request

UA = {"User-Agent": "berlin-sauna-map/1.0 (personal project; https://github.com/jommi9/berlin-sauna-map)"}
EURO = r"€\s?(\d{1,4}(?:[.,]\d{1,2})?)|(?<![:.\d])(\d{1,4}(?:[.,]\d{1,2})?)\s?(?:€|EUR\b)(?!\s?\d)"
TIME = r"(?<!\d)(\d{1,2})[:.](\d{2})(?!\d)"

def norm(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s).replace("–", "-").replace("—", "-"))

def euros(s):
    out = set()
    for m in re.finditer(EURO, norm(s)):
        v = (m.group(1) or m.group(2)).replace(",", ".")
        f = float(v)
        if 1 <= f <= 500:                      # ignore years, phone fragments, huge memberships
            out.add(f"{f:g}")
    return out

def times(s):
    return {f"{int(h):02d}:{mi}" for h, mi in re.findall(TIME, norm(s)) if int(h) <= 24}

def page_text(url):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40)\
            .read(700_000).decode("utf-8", "replace")
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
    return norm(re.sub(r"<[^>]+>", " ", body))

venues = json.load(open("venues.json", encoding="utf-8"))
findings = 0
checked = 0
for v in venues:
    # Only the venue's own site. Facebook, Urban Sports Club and visitBerlin
    # would compare our data against someone else's page.
    if not v.get("url") or re.search(r"facebook\.com|urbansportsclub\.com|visitberlin\.de", v["url"]):
        continue
    try:
        txt = page_text(v["url"])
    except Exception:
        continue                                # verify_venue.py already reports reachability
    site_e = euros(txt)

    # Only compare when the page is demonstrably a price page. Many venue sites
    # render prices with JavaScript, so a raw fetch sees a shell - treating that
    # as "the price vanished" made this flag 10 of 14 venues on its first run.
    if len(site_e) < 3:
        continue
    ours = euros(v["priceLabel"])
    if not ours:
        continue
    checked += 1
    # A single missing figure usually means the page restructured. Every one of
    # our figures missing, on a page that clearly lists prices, is a real signal.
    if ours and not (ours & site_e):
        findings += 1
        print(f"!!  {v['name'][:34]:36} none of our prices appear on its own page")
        print(f"      we list : {', '.join(sorted(ours, key=float))}")
        print(f"      page has: {', '.join(sorted(site_e, key=float)[:10])}")
        print(f"      {v['url']}")

print(f"\n{checked} venue(s) with a readable price page compared, {findings} where every "
      f"price we list has disappeared from it")
print("Hours are not compared: German pages write '15 bis 24 Uhr' as often as '15:00',")
print("and seasonal switches are handled separately by check_deployment.py.")
sys.exit(1 if findings else 0)
