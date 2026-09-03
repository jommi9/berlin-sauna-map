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

**Sync findings back.** Verification turns up corrections the table does not have, and
if they only ever live in `build_venues.py` then Notion silently stops being the source
of truth and the next rebuild from it undoes the fixes. Push anything verified back into
the table (`notion-update-page` with `update_content` does surgical find-and-replace),
and say where it came from — "from Gezer Spa's own shop", "(OpenStreetMap)". Watch two
things when writing: identical cell text repeats across rows, so match on a neighbouring
cell for uniqueness, and Notion auto-links bare domains, which mangles surrounding bold
markers — keep URLs out of emphasised runs.

## Checking Notion and the site actually agree

`build_venues.py` is a hand transcription, so nothing stops it drifting from the
Notion table. Three drifts were found this way, each after a sync I believed was
complete: the InterContinental hotel-guest rates, Olivin's full price ladder and
Liquidrom's tiered admission all sat in Notion while the site showed older text.

    cd src
    # refresh notion_snapshot.tsv from the Notion page (name / cash / hours per row)
    python3 check_notion_sync.py

It compares euro amounts and clock times rather than prose, since the site words
things deliberately differently, and exits non-zero on drift. Run it after every
Notion edit. Two parsing traps are already handled and should not be "simplified"
away: a decimal price like `24.50` matches a clock-time pattern, and a session
length like `Urban Flow 120 €24.50` reads as 120 euros unless the euro sign is
required not to be followed by a digit.

Never use a bare `str.replace()` to edit venue data. Assert the old string exists
and is unique first — a silent no-op replace is what let the InterContinental rates
reach Notion but not the site.

## Two build outputs — do not merge them

`index.html` (full document, has the viewport meta) is for GitHub Pages.
`artifact.html` (bare fragment) is for publishing as an Artifact, which rejects
`<html>`/`<head>`/`<body>` and supplies its own head. Serving the fragment as a
website makes phones lay it out at 980 px and shrink to fit — the bug that made the
site unreadable on mobile while looking fine in scaled screenshots.

When checking mobile, assert `innerWidth` is what you set. If it reports 980, the
viewport meta is missing and everything measured after that is meaningless.

## Rebuild

```
cd src
python3 build_venues.py && python3 declutter.py && python3 embed_images.py \
  && python3 assemble.py tpl2.html ../index.html \
  && python3 assemble.py tpl2.html ../artifact.html
```

Then republish `index.html` to the existing artifact URL, and push (GitHub Pages
serves it at https://jommi9.github.io/berlin-sauna-map/).
