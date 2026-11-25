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

# Optional: "live" (true once the city is open on the hub at HUB + slug, so that copy is checked too),
# "currency" (the sign prices are written in, default "€"), "temp" ("F" to show
# temperatures in Fahrenheit; they are kept in Celsius), "usc" (true where Urban
# Sports Club exists and the venue rows say who takes it), "districtLevel" (the OSM admin_level
# osm_extract.py draws as district outlines), "icon" (the city's landmark for its app icon: SVG
# drawn in white on a 64 by 64 grid, standing on y=52 and no wider than x=20..44, written with
# single quotes; see icon() below), "iconFull" (true when the icon is the whole drawing, steam
# included, as San Francisco's bridge is: it is too wide to stand between two curls).
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


def icon(cfg):
    """What is drawn on a city's app icon, inside the 64 by 64 tile: steam rising either side of
    the city's own landmark. A city without one gets the plain icon, three curls of steam."""
    curl = lambda x: f"M{x} 43 q-4.6 -5.5 0 -11 q4.6 -5.5 0 -11"
    stones = "<path d='M15 52 h34' stroke='#fff' stroke-opacity='.6' stroke-width='4' stroke-linecap='round'/>"
    steam = lambda d: f"<path d='{d}' fill='none' stroke='#fff' stroke-width='4' stroke-linecap='round'/>"
    mark = cfg.get("icon")
    if not mark:
        return steam(f"{curl(21)} M32 45 q-5 -6.5 0 -13 q5 -6.5 0 -13 {curl(43)}") + stones
    if not mark.isascii() or '"' in mark or "\\" in mark or "<script" in mark.lower():
        raise SystemExit(f"{cfg['slug']}/city.json: the icon must be plain SVG shapes written with single quotes")
    if cfg.get("iconFull"):
        return mark + stones
    return steam(f"{curl(15.5)} {curl(48.5)}") + mark + stones


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
