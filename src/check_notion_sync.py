#!/usr/bin/env python3
"""Diff the Notion source table against what the site actually ships.

Notion is the source of truth, but build_venues.py is a hand transcription of
it, so nothing stops the two drifting. This caught the InterContinental rates
sitting in Notion for a day while the site still showed only the day-visitor
price. Compares the numbers that matter - euro amounts and clock times - rather
than prose, since the site deliberately words things differently.

Refresh notion_snapshot.tsv from the Notion page, then:  python3 check_notion_sync.py
"""
import json, re, sys, unicodedata

def norm(s):
    s = unicodedata.normalize("NFKC", s).replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()

def euros(s):
    """Euro amounts only.

    Do NOT pre-strip clock times: "24.50" matches a time pattern, so stripping
    turned "€24.50" into "€ " and the preceding session length ("Urban Flow 120")
    was then read as 120 euros. Instead the number-before-euro form refuses a
    number preceded by a colon or dot (a clock time like "21:30 €20") and refuses
    a euro sign followed by a digit ("Short Escape 90 €22").
    """
    out = set()
    pat = r"€\s?(\d{1,4}(?:[.,]\d{1,2})?)|(?<![:.\d])(\d{1,4}(?:[.,]\d{1,2})?)\s?€(?!\s?\d)"
    for m in re.finditer(pat, norm(s)):
        v = (m.group(1) or m.group(2)).replace(",", ".")
        out.add(f"{float(v):g}")
    return out

def times(s):
    return {f"{int(h):02d}:{mi}" for h, mi in re.findall(r"(\d{1,2})[:.](\d{2})", norm(s))}

venues = {v["name"]: v for v in json.load(open("venues.json", encoding="utf-8"))}
rows = [l.rstrip("\n").split("\t") for l in open("notion_snapshot.tsv", encoding="utf-8") if l.strip()]

problems = 0
seen = set()
for name, cash, hours in rows:
    seen.add(name)
    v = venues.get(name)
    if not v:
        print(f"XX  in Notion but not on the site: {name}"); problems += 1; continue
    site_cash = v["priceLabel"]
    site_hours = v["hours"]
    miss_e = euros(cash) - euros(site_cash)
    miss_t = times(hours) - times(site_hours)
    if miss_e:
        print(f"!!  {name}\n      Notion prices missing from the site: {', '.join(sorted(miss_e, key=float))}")
        print(f"      notion: {norm(cash)[:96]}\n      site  : {norm(site_cash)[:96]}"); problems += 1
    if miss_t:
        print(f"!!  {name}\n      Notion times missing from the site: {', '.join(sorted(miss_t))}")
        print(f"      notion: {norm(hours)[:96]}\n      site  : {norm(site_hours)[:96]}"); problems += 1

for name in venues:
    if name not in seen:
        print(f"XX  on the site but not in the Notion snapshot: {name}"); problems += 1

print(f"\n{len(rows)} rows compared, {problems} drift{'' if problems == 1 else 's'} found")
sys.exit(1 if problems else 0)
