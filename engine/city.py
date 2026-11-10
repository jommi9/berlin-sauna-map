#!/usr/bin/env python3
"""The one place the engine learns which city it is working on.

A city is a folder at the repo root that holds a city.json (berlin/ is the
first). Every engine script takes the city's folder name as its first argument
and then works inside that folder, so the file names the scripts use
(venues.json, geo.json, img/...) are the same for every city and nothing in
engine/ names a city.

    python3 engine/city.py          # list the cities, one per line
"""
import json, os, sys

ENGINE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ENGINE)

# The repository, for links to its issue forms and for the Pages address.
REPO = "jommi9/sauna-maps"
# The public home of the maps: the hub, with each city at HUB + "<slug>/".
HUB = "https://jommi.fi/sauna/"
UA = {"User-Agent": f"sauna-maps/1.0 (personal project; https://github.com/{REPO})"}

REQUIRED = ("name", "country", "timezone", "bbox", "lede", "notionIntro")


def slugs():
    return sorted(d for d in os.listdir(ROOT)
                  if os.path.isfile(os.path.join(ROOT, d, "city.json")))


def load(slug):
    cfg = json.load(open(os.path.join(ROOT, slug, "city.json"), encoding="utf-8"))
    missing = [k for k in REQUIRED if k not in cfg]
    if missing:
        raise SystemExit(f"{slug}/city.json is missing {', '.join(missing)}")
    cfg["slug"] = slug
    cfg["site"] = f"{HUB}{slug}/"
    return cfg


def enter():
    """Take the city off the command line, move into its folder, return its config.

    The city is removed from sys.argv, so whatever a script read from its
    arguments before (a --dry-run, an output name) is still where it was.
    """
    known = slugs()
    if len(sys.argv) < 2 or sys.argv[1] not in known:
        raise SystemExit(f"usage: {os.path.basename(sys.argv[0])} <city> ...   "
                         f"(cities: {', '.join(known) or 'none yet'})")
    slug = sys.argv.pop(1)
    os.chdir(os.path.join(ROOT, slug))
    sys.path.insert(0, os.getcwd())       # the city's own venues.py and sources.py
    sys.dont_write_bytecode = True        # no __pycache__ inside a folder Pages serves
    return load(slug)


if __name__ == "__main__":
    print("\n".join(slugs()))
