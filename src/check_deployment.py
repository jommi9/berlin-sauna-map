#!/usr/bin/env python3
"""Check the published site actually matches the repo, and warn about seasonal switches.

A `git push` succeeding is not the same as the site updating. On 4 Sep 2026 the
Pages deploy failed on an OIDC token timeout while the push reported success, so
the site quietly served stale content until someone hashed it. Nothing noticed.

Also warns when a seasonal hours switch has just passed, since three venues
change opening times on 1 October and back on 31 March, and those dates are
hard-coded from what the venues said months earlier.
"""
import datetime, hashlib, json, re, sys, time, urllib.request

SITE = "https://jommi9.github.io/berlin-sauna-map/"
UA = {"User-Agent": "berlin-sauna-map-selfcheck/1.0"}
problems = []

# Pages takes a minute or two to publish, so when this runs straight after a
# push --wait <minutes> keeps re-checking rather than reporting a deploy that
# simply has not finished yet.
m = re.search(r"--wait[= ](\d+)", " ".join(sys.argv))
deadline = time.time() + (int(m.group(1)) * 60 if m else 0)

# --- is the live page the page we built?
local = hashlib.sha256(open("../index.html", "rb").read()).hexdigest()
while True:
    try:
        live_bytes = urllib.request.urlopen(
            urllib.request.Request(SITE + "?cachebust=" + str(datetime.datetime.now().timestamp()),
                                   headers=UA), timeout=60).read()
        live = hashlib.sha256(live_bytes).hexdigest()
        if live == local:
            print(f"ok  live site matches the repo ({local[:12]})")
            break
        err = (f"live site does NOT match the repo\n"
               f"      repo {local[:12]}\n      live {live[:12]}\n"
               f"      A push can succeed while the Pages deploy fails. "
               f"Re-run the latest 'pages build and deployment' run.")
    except Exception as e:
        err = f"could not fetch the live site: {type(e).__name__} {e}"
    if time.time() >= deadline:
        problems.append(err)
        break
    print("..  live site not updated yet, waiting 45s")
    time.sleep(45)

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

# --- has a dated closure lapsed without anyone recording the new hours?
#     The card stops claiming "closed" by itself on the day, but it then has no
#     hours at all, so somebody has to go and read them off the venue's page.
for v in json.load(open("venues.json", encoding="utf-8")):
    o = v.get("open") or {}
    if not o.get("closedUntil") or o.get("weekly"):
        continue
    ended = datetime.date.fromisoformat(o["closedUntil"])
    if ended < today:
        problems.append(f"{v['name']} reopened on {ended} ({(today - ended).days} day(s) ago) "
                        f"and we still have no opening hours for it: {v['url']}")

for p in problems:
    print(f"!!  {p}")
print(f"\n{'deployment and season checks passed' if not problems else str(len(problems)) + ' issue(s)'}")
sys.exit(1 if problems else 0)
