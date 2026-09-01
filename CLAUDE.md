# Berlin Sauna Map — working notes

## Data sourcing: primary source first, always

Never propose or add a venue on the strength of a "best saunas in Berlin" listicle,
Yelp roundup, or similar aggregator. Those lists are badly stale. Verified failures
from one afternoon of checking:

- **Thermen am Europa-Center** — operator insolvent, shut since March 2020. Still
  appears on 2026 "best of" lists.
- **Badeschiff** — the *Winterbadeschiff* sauna conversion is no longer operated.
  Aggregators still describe it as "a pool that becomes a sauna in winter".
- **Stadtbad Charlottenburg** — has no sauna at all; neither hall's page mentions one.
- **Gewölbe Sauna** — directories give address, phone and hours, but the venue's own
  site returns HTTP 500, so nothing about it is confirmed.

The correct order is:

1. Run `python3 src/verify_venue.py "<name>" <official-url>`.
2. Only if it comes back `OK` (live, mentions sauna, publishes prices or hours) is the
   venue a candidate.
3. Read the prices and hours off the venue's own page — never off the aggregator.
4. Anything short of that goes in flagged as unverified, the way sly Berlin and
   Park Inn are, or does not go in at all.

Aggregators are fine for *discovering names to check*. They are never evidence.

## Auditing what is already listed

`python3 src/verify_venue.py` with no arguments re-checks all 20 venues against their
own sites. Verdicts:

| | Meaning |
|---|---|
| `OK` | live, mentions sauna, publishes prices or hours |
| `THIN` | live and mentions sauna, but no prices/hours found — normal for hotel spa pages |
| `PAUSED` | a current closure or seasonal-break notice |
| `STALE NOTICE` | a closure banner whose date has already passed — needs a human |
| `BLOCKED` | HTTP 401/403/429 bot protection; check by hand, not a closure |
| `SUSPECT` / `LIKELY CLOSED` / `UNREACHABLE` | investigate before trusting the row |

Re-run it before any refresh of the guide. It found the Westin's renovation banner,
which had expired three months earlier and was still posted.

## Notion is the source of truth

Venue facts live in the Notion page *Personal Home / Projects / Berlin Sauna Guide /
Saunas & Spas*. `src/build_venues.py` is a transcription of that table — edit Notion
first, then mirror it here. Do not invent prices.

## Rebuild

```
cd src
python3 build_venues.py && python3 declutter.py && python3 embed_images.py \
  && python3 assemble.py tpl2.html ../index.html
```

Then republish `index.html` to the existing artifact URL, and push (GitHub Pages
serves it at https://jommi9.github.io/berlin-sauna-map/).
