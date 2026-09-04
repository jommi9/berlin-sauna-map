#!/usr/bin/env python3
"""Check the published site actually matches the repo, and warn about seasonal switches.

A `git push` succeeding is not the same as the site updating. On 4 Sep 2026 the
Pages deploy failed on an OIDC token timeout while the push reported success, so
the site quietly served stale content until someone hashed it. Nothing noticed.

Also warns when a seasonal hours switch has just passed, since three venues
change opening times on 1 October and back on 31 March, and those dates are
hard-coded from what the venues said months earlier.
"""
import datetime, hashlib, json, sys, urllib.request

SITE = "https://jommi9.github.io/berlin-sauna-map/"
UA = {"User-Agent": "berlin-sauna-map-selfcheck/1.0"}
problems = []

# --- is the live page the page we built?
local = hashlib.sha256(open("../index.html", "rb").read()).hexdigest()
try:
    live_bytes = urllib.request.urlopen(
        urllib.request.Request(SITE + "?cachebust=" + str(datetime.datetime.now().timestamp()),
                               headers=UA), timeout=60).read()
    live = hashlib.sha256(live_bytes).hexdigest()
    if live == local:
        print(f"ok  live site matches the repo ({local[:12]})")
    else:
        problems.append(f"live site does NOT match the repo\n"
                        f"      repo {local[:12]}\n      live {live[:12]}\n"
                        f"      A push can succeed while the Pages deploy fails. "
                        f"Re-run the latest 'pages build and deployment' run.")
except Exception as e:
    problems.append(f"could not fetch the live site: {type(e).__name__} {e}")

# --- did a seasonal switch just happen?
today = datetime.date.today()
for label, month, day in (("winter hours", 10, 1), ("summer hours", 3, 31)):
    switch = datetime.date(today.year, month, day)
    days = (today - switch).days
    if 0 <= days <= 21:
        seasonal = [v["name"] for v in json.load(open("venues.json", encoding="utf-8"))
                    if (v.get("open") or {}).get("seasons")]
        problems.append(f"{label} began {days} day(s) ago ({switch}). Re-check at source: "
                        + ", ".join(seasonal))

for p in problems:
    print(f"!!  {p}")
print(f"\n{'deployment and season checks passed' if not problems else str(len(problems)) + ' issue(s)'}")
sys.exit(1 if problems else 0)
