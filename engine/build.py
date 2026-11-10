#!/usr/bin/env python3
"""Rebuild a city's pages from its data, or every city's.

    python3 engine/build.py <city> [<city> ...]
    python3 engine/build.py                  # every city
    python3 engine/build.py --notion ...     # also regenerate <city>/notion_page.md

The steps, in the order they depend on each other:
    build_venues  <city>/venues.py            -> venues.json, meta.json
    declutter     overlapping pins nudged apart
    embed_images  img/card/*.webp             -> img/embed.json
    assemble      template.html + all of that -> index.html, artifact.html
"""
import os, subprocess, sys
import city

STEPS = ["build_venues.py", "declutter.py", "embed_images.py", "assemble.py"]
args = [a for a in sys.argv[1:] if a != "--notion"]
if "--notion" in sys.argv:
    STEPS.append("push_to_notion.py")
unknown = [a for a in args if a not in city.slugs()]
if unknown:
    raise SystemExit(f"no such city: {', '.join(unknown)}   (cities: {', '.join(city.slugs())})")

for slug in args or city.slugs():
    print(f"== {slug}")
    for step in STEPS:
        done = subprocess.run([sys.executable, os.path.join(city.ENGINE, step), slug])
        if done.returncode:
            raise SystemExit(f"{step} {slug} failed; stopped there")
