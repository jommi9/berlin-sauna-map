#!/usr/bin/env python3
"""Fold an approved GitHub issue into reviewers.json or a city's reviews.json.

Run by the ingest workflow when a maintainer labels an issue `approved`.
Everything is validated before it is written, and a rejection exits non-zero so
the workflow comments on the issue rather than committing something wrong:

  * a review must name a venue that exists, spelled as the map spells it; the
    city it belongs to is the one whose map lists that name;
  * a review is only accepted from a handle already in reviewers.json;
  * ratings must be 1-5 and dates must be real ISO dates;
  * free text is length-capped and stripped of anything but plain text, because
    it lands in a page rendered with innerHTML.

The panel is one list for every city (reviewers.json at the repo root); reviews
are kept per city (<city>/reviews.json).

Usage: python3 engine/ingest_issue.py <issue.json>
"""
import datetime, html, json, os, re, sys
import city

REVIEWERS = os.path.join(city.ROOT, "reviewers.json")
def in_city(slug, name):
    return os.path.join(city.ROOT, slug, name)

issue = json.load(open(sys.argv[1], encoding="utf-8"))
labels = {l["name"] for l in issue.get("labels", [])}
handle = issue["user"]["login"]
body = issue.get("body") or ""

def field(label):
    """GitHub issue forms render as '### Label\\n\\nvalue'."""
    m = re.search(rf"^###\s+{re.escape(label)}\s*\n+(.*?)(?=\n###\s|\Z)", body, re.S | re.M)
    v = (m.group(1) if m else "").strip()
    return "" if v in ("_No response_", "_Keine Angabe_") else v

def clean(s, cap):
    s = re.sub(r"<[^>]*>", "", s)              # no markup reaches the page
    s = re.sub(r"\s+", " ", s).strip()
    return html.escape(s[:cap], quote=True)

def fail(msg):
    print(f"REJECTED: {msg}"); sys.exit(1)

if "reviewer-application" in labels:
    name = clean(field("Name to show on your reviews"), 60)
    bio = clean(field("One or two lines about you"), 220)
    if not name or not bio:
        fail("the application is missing a name or a bio")
    reviewers = json.load(open(REVIEWERS, encoding="utf-8"))
    if handle in reviewers:
        print(f"{handle} is already a reviewer; nothing to do"); sys.exit(0)
    reviewers[handle] = {"name": name, "bio": bio,
                         "joined": datetime.date.today().isoformat()}
    json.dump(dict(sorted(reviewers.items())), open(REVIEWERS, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print(f"added reviewer {handle} ({name})")

elif "review" in labels:
    reviewers = json.load(open(REVIEWERS, encoding="utf-8"))
    if handle not in reviewers:
        fail(f"@{handle} is not an approved reviewer yet - apply first")
    listed = {slug: {v["name"] for v in json.load(open(in_city(slug, "venues.json"), encoding="utf-8"))}
              for slug in city.slugs()}
    venue = field("Venue").strip()
    homes = [slug for slug, names in listed.items() if venue in names]
    if not homes:
        near = [n for names in listed.values() for n in names if venue.lower()[:8] in n.lower()]
        fail(f"no venue called {venue!r}." + (f" Did you mean: {', '.join(near)}?" if near else
             " Use the name exactly as the map spells it."))
    if len(homes) > 1:
        fail(f"{venue!r} is the name of a venue in more than one city ({', '.join(homes)}); "
             f"venue names have to be unique across the maps before this can be filed")
    home = homes[0]
    try:
        rating = int(field("Rating out of 5"))
        assert 1 <= rating <= 5
    except Exception:
        fail("rating must be a whole number from 1 to 5")
    try:
        visited = datetime.date.fromisoformat(field("When did you go?").strip()).isoformat()
    except Exception:
        fail("'when did you go' must be a real date like 2026-09-01")
    text = clean(field("Your review"), 900)
    if len(text) < 40:
        fail("the review is too short to be useful - a sentence or two at least")
    reviews = json.load(open(in_city(home, "reviews.json"), encoding="utf-8"))
    reviews = [r for r in reviews if not (r["venue"] == venue and r["reviewer"] == handle)]
    reviews.append({"venue": venue, "reviewer": handle, "rating": rating,
                    "visited": visited, "text": text,
                    "submitted": datetime.date.today().isoformat(),
                    "issue": issue["number"]})
    reviews.sort(key=lambda r: (r["venue"], r["submitted"]))
    json.dump(reviews, open(in_city(home, "reviews.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"added review of {venue} ({home}) by {handle} ({rating}/5)")
else:
    fail("issue carries neither the reviewer-application nor the review label")
