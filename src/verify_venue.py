#!/usr/bin/env python3
"""Check venues against their OWN site, not aggregators.

Aggregator "best saunas in Berlin" lists carry venues that closed years ago
(Thermen am Europa-Center: insolvent since 2020, still listed everywhere).
So a candidate is never proposed on listing evidence alone - it has to clear
this first.

  python3 verify_venue.py                       # audit every venue in venues.json
  python3 verify_venue.py "Name" <url>          # check one candidate
"""
import json, re, sys, html, time, datetime, urllib.request, urllib.error

UA = {"User-Agent": "berlin-sauna-map/1.0 (personal project; https://github.com/jommi9/berlin-sauna-map)"}

DEAD = [r"dauerhaft geschlossen", r"permanently closed", r"insolven", r"betrieb eingestellt",
        r"endgültig geschlossen", r"dauerhaft schlie", r"hat geschlossen und"]
PAUSE = [r"vor(ü|ue)bergehend geschlossen", r"sommerpause", r"summer break", r"wegen umbau",
         r"renovier", r"wieder ab", r"temporarily closed"]

def text_of(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        raw = r.read(600_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
        code, final = r.status, r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:
        return 0, url, f"__ERR__{type(e).__name__}"
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
    return code, final, re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body)))

def check(name, url):
    code, final, txt = text_of(url)
    ev = {"name": name, "url": url, "http": code, "chars": len(txt)}
    if txt.startswith("__ERR__"):
        ev["verdict"], ev["why"] = "UNREACHABLE", txt[7:]; return ev
    if code in (401, 403, 405, 429):
        ev["verdict"], ev["why"] = "BLOCKED", f"HTTP {code} - bot protection, check by hand"; return ev
    if code != 200:
        ev["verdict"], ev["why"] = "UNREACHABLE", f"HTTP {code}"; return ev
    if len(txt) < 400:
        ev["verdict"], ev["why"] = "SUSPECT", f"page has only {len(txt)} chars of text"; return ev
    low = txt.lower()
    # German sites write "40€" - number first, no decimals - which a pattern
    # requiring "40,00 €" or "€40" misses entirely. Accept all three forms.
    ev["prices"] = sorted(set(
        m.group(0).strip() for m in re.finditer(
            r"(?:€\s?\d{1,4}(?:[.,]\d{2})?|\d{1,4}(?:[.,]\d{2})?\s?(?:€|EUR\b))", txt)))[:8]
    ev["hours"]  = sorted(set(re.findall(r"\d{1,2}[:.]\d{2}\s*[-–]\s*\d{1,2}[:.]\d{2}", txt)))[:4]
    ev["sauna_mentions"] = len(re.findall(r"sauna", low))
    ev["dead_flags"]  = [p for p in DEAD  if re.search(p, low)]
    # A closure banner carrying a date in the past is stale, not a live closure -
    # the Westin's USC page still said "closed until 31.05.2026" in September.
    ev["expired_notice"] = []
    today = datetime.date.today()
    for m in re.finditer(r"(\d{1,2})\.(\d{1,2})\.(20\d{2})", txt):
        ctx = low[max(0, m.start()-160):m.start()+40]
        if not re.search(r"geschlossen|closed|renovier|umbau|pause", ctx): continue
        try: d = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError: continue
        if d < today: ev["expired_notice"].append(m.group(0))
    ev["pause_flags"] = [p for p in PAUSE if re.search(p, low)]
    if ev["dead_flags"]:                      ev["verdict"], ev["why"] = "LIKELY CLOSED", ", ".join(ev["dead_flags"])
    elif ev["sauna_mentions"] == 0:           ev["verdict"], ev["why"] = "SUSPECT", "own site never says 'sauna'"
    elif ev["pause_flags"] and ev["expired_notice"]:
        ev["verdict"] = "STALE NOTICE"
        ev["why"] = f"closure banner expired {ev['expired_notice'][0]} but is still posted"
    elif ev["pause_flags"]:                   ev["verdict"], ev["why"] = "PAUSED", ", ".join(ev["pause_flags"])
    elif ev["prices"] or ev["hours"]:         ev["verdict"], ev["why"] = "OK", "live, mentions sauna, publishes prices/hours"
    else:                                     ev["verdict"], ev["why"] = "THIN", "live and mentions sauna, but no prices or hours found"
    return ev

def line(e):
    mark = {"OK":"ok ", "THIN":"?  ", "PAUSED":"~  ", "SUSPECT":"!  ", "BLOCKED":"-  ", "STALE NOTICE":"!! ",
            "LIKELY CLOSED":"XX ", "UNREACHABLE":"XX "}[e["verdict"]]
    extra = ""
    if e.get("prices"): extra += "  " + " ".join(e["prices"][:3])
    if e.get("hours"):  extra += "  " + e["hours"][0]
    return f"{mark}{e['verdict']:14} {e['name'][:34]:36}{extra}   {e['why'][:46]}"

if __name__ == "__main__":
    if len(sys.argv) == 3:
        print(json.dumps(check(sys.argv[1], sys.argv[2]), indent=1, ensure_ascii=False))
    else:
        vs = json.load(open("venues.json", encoding="utf-8"))
        bad = 0
        for v in vs:
            e = check(v["name"], v["url"]); print(line(e))
            if e["verdict"] in ("LIKELY CLOSED", "UNREACHABLE", "SUSPECT", "PAUSED", "STALE NOTICE"): bad += 1
            time.sleep(0.7)
        print(f"\n{len(vs)} venues checked, {bad} need a human look")
        # non-zero exit so CI can gate on it
        sys.exit(1 if bad else 0)
