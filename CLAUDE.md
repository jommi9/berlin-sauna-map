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

## The repo is the source of truth; Notion is generated

Direction of travel was flipped on 3 September 2026. Venue facts live in
`src/build_venues.py`. The Notion page *Personal Home / Projects / Berlin Sauna
Guide / Saunas & Spas* is a **generated view** of it — do not hand-edit that
table, the next push overwrites it. The callout at the top of the page says so.

Why: `build_venues.py` used to be a hand transcription of Notion, and the two
drifted three times in two days (the InterContinental hotel-guest rates, Olivin's
price ladder, Liquidrom's tiered admission) — each time after a sync that looked
complete. One direction of travel makes that class of bug impossible, so the
old `check_notion_sync.py` drift checker is gone with it.

To publish the table after a data change:

    cd src && python3 push_to_notion.py      # writes notion_page.md

then apply it with `notion-update-page`, command `replace_content`, passing the
file's contents. Two Notion quirks are handled in the generator and should not be
"simplified" away: bare domains get auto-linked and wreck surrounding bold markers,
so they are wrapped in backticks; a table cell containing a newline breaks the row,
so every cell is whitespace-collapsed; and a code span inside a bold run collides
into `****`, so notes are written as a bold **Heads up:** label followed by
unbolded text rather than bolding the whole sentence.

`PICKS`, `PRACTICAL` and `LAST_CHECKED` are defined once in `build_venues.py` and
injected into both the site template and the Notion page, so the fast-picks list
cannot say two different things.

Never edit venue data with a bare `str.replace()`. Assert the old string exists
and is unique first — a silent no-op replace is what let the InterContinental
rates reach Notion but not the site.

## Two build outputs — do not merge them

`index.html` (full document, has the viewport meta) is for GitHub Pages.
`artifact.html` (bare fragment) is for publishing as an Artifact, which rejects
`<html>`/`<head>`/`<body>` and supplies its own head. Serving the fragment as a
website makes phones lay it out at 980 px and shrink to fit — the bug that made the
site unreadable on mobile while looking fine in scaled screenshots.

When checking mobile, assert `innerWidth` is what you set. If it reports 980, the
viewport meta is missing and everything measured after that is meaningless.

## After pushing, confirm the site actually changed

A `git push` succeeding is not the same as the site updating. On 4 September 2026
the Pages deploy failed on an OIDC token timeout while the push reported success,
and the site quietly served stale content. `src/check_deployment.py` hashes the
live page against `index.html` and also warns when a seasonal hours switch has just
passed; it runs in the weekly audit. If it reports a mismatch, re-run the latest
"pages build and deployment" workflow run — the build almost always succeeded and
only the deploy step failed.

## Rebuild

```
cd src
python3 build_venues.py && python3 declutter.py && python3 embed_images.py \
  && python3 assemble.py tpl2.html ../index.html \
  && python3 assemble.py tpl2.html ../artifact.html
```

Then republish `index.html` to the existing artifact URL, and push (GitHub Pages
serves it at https://jommi9.github.io/berlin-sauna-map/).
