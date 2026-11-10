#!/usr/bin/env python3
"""Run one engine script for every city in turn.

    python3 engine/each.py selfupdate.py [--dry-run]
    python3 engine/each.py check_deployment.py --wait 6

Every city is run even when an earlier one fails, and the exit status is
non-zero if any of them was, so a workflow step can gate on the whole round.
"""
import os, subprocess, sys
import city

if len(sys.argv) < 2 or not os.path.isfile(os.path.join(city.ENGINE, sys.argv[1])):
    raise SystemExit("usage: each.py <script in engine/> [arguments for it]")
worst = 0
for slug in city.slugs():
    print(f"== {slug}", flush=True)
    done = subprocess.run([sys.executable, os.path.join(city.ENGINE, sys.argv[1]), slug, *sys.argv[2:]])
    worst = max(worst, done.returncode)
sys.exit(worst)
