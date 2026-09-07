# Berlin Sauna Map

Twenty Berlin saunas and spas drawn as an open-world game atlas.

**Live: https://jommi9.github.io/berlin-sauna-map/**

Also published as a private Claude Artifact:
https://claude.ai/code/artifact/79203c00-258e-4438-b918-bd671cd3db9c

## Hosting

GitHub Pages serves `index.html` from `main`. Note that a custom domain on the
account's *user* site (`jommi9.github.io`) is applied to every project site too — a
stale `CNAME` pointing at a non-resolving domain will take this page down along with
everything else on the account, returning a redirect into nowhere rather than a clear
error. If this URL ever 301s somewhere unexpected, check that repo's `CNAME` first.

Source of truth for the venue data is `src/build_venues.py`. The Notion page
**Personal Home / Projects / Berlin Sauna Guide / Saunas & Spas** is a *generated
view* of it — don't hand-edit that table, `push_to_notion.py` overwrites it. The
site is a single static, self-contained HTML file — no runtime API calls, no keys,
no build server.

## Files

| File | What it is |
|---|---|
| `index.html` | The built page (~900 KB, images inlined). This is what gets published, and what a static host serves at the site root. |
| `src/tpl2.html` | **Current design.** Template with `/*__GEO__*/` and `/*__VENUES__*/` placeholders. Edit look and feel here. |
| `src/tpl.html` | The previous, quieter atlas design, kept as a fallback. |
| `src/build_venues.py` | **The source of truth.** Every venue fact, the löyly/score tables, the fast picks, plus map projection. Edit content here; everything else is generated from it. |
| `src/declutter.py` | Nudges overlapping blips apart (currently ≤ 90 m displacement; a hairline tick shows the true spot when moved). |
| `src/build_geo2.py` | Projects and simplifies districts, water, parks, roads and rail into `geo.json`, collapsing each layer to one path so the SVG stays ~8 nodes instead of 9,400. |
| `src/assemble.py` | Inlines the JSON and writes the final ASCII-only HTML. Takes `<template> <output>`. |
| `src/push_to_notion.py` | Renders the Notion page from the repo into `notion_page.md`, ready to apply with `replace_content`. |
| `src/fetch.sh` | Overpass fetcher with mirror fallback and retries. Only needed to refresh the cached geodata. |
| `src/sources.py` | Anchors for `selfupdate.py`: the regexes that pin one figure on a venue's own page to one figure in our data. |
| `src/selfupdate.py` | Re-reads each venue's page and rewrites `build_venues.py` where a claim is provable. The only script allowed to write venue data. |
| `src/verify_venue.py` | Checks every venue against its own site: `OK` / `THIN` / `PAUSED` / `STALE NOTICE` / `BLOCKED` / `SUSPECT` / `LIKELY CLOSED` / `UNREACHABLE`. |
| `src/watch_changes.py` | Flags a venue whose own page no longer shows any price we list. Conservative by design — it reports, never edits. |
| `src/check_deployment.py` | Hashes the live page against `index.html`, warns on seasonal switches, and chases closures whose date has lapsed. `--wait <min>` to allow for a Pages deploy. |
| `src/ingest_issue.py` | Validates an approved reviewer application or review issue and folds it into the JSON. |
| `src/reviewers.json`, `src/reviews.json` | The review model. Written by the ingest workflow, never by hand. |
| `src/geo.json`, `src/venues.json`, `src/meta.json` | Derived map + venue data, committed so venue rebuilds need no network. |
| `src/bezirke.geojson` | District outlines, input to `build_geo2.py`. |
| `src/roads.json` etc. | Raw Overpass dumps, gitignored (16 MB). Only needed if the map bbox changes; `fetch.sh` re-pulls them. |

## Rebuilding after a data edit

1. Edit `src/build_venues.py` — it is the source, and Notion is generated from it.
   Never edit venue data with a bare `str.replace()`: assert the old string exists
   and is unique first, because a silent no-op replace is what once let a price
   reach Notion but not the site.
2. From `src/`:

   ```
   python3 build_venues.py && python3 declutter.py && python3 embed_images.py \
  && python3 assemble.py tpl2.html ../index.html \
  && python3 assemble.py tpl2.html ../artifact.html
   ```

3. `python3 push_to_notion.py`, then apply `notion_page.md` with `notion-update-page`
   / `replace_content`.
4. Commit and push — GitHub Pages serves `index.html`. A push succeeding is **not**
   the same as the site updating; confirm with `python3 check_deployment.py`.
5. Republish `artifact.html` to the same artifact URL (pass the URL so the link stays
   stable). Nothing in CI can do this step — the artifact is the one output that
   always needs a human.

`build_geo2.py` only needs re-running if you change the map's bounding box — it reads
the cached OSM files. To refresh those from Overpass, see the queries in `fetch.sh`.

## Keeping itself current

`.github/workflows/weekly-venue-audit.yml` runs Mondays 06:00 UTC, and does two
different jobs in order.

**It fixes what it can prove.** `selfupdate.py` re-reads each venue's own page and
rewrites `build_venues.py` where an anchor in `sources.py` matches exactly one value,
then rebuilds, regenerates Notion, commits and pushes. It caught Stadtbad Neukölln
shortening its 2026 summer break from 31 October to 30 September without telling
anyone.

It refuses to write when a figure would move below half or above double, when more
than four things change in one run, or when an edit target is not unique. Fourteen
anchors cover five venues; the other fifteen were **measured and rejected**, not
forgotten — they render prices in JavaScript or print bare amounts with no label
(`€14.50 €14.50 €29 €29`). No venue publishes JSON-LD opening hours (checked across
all twenty), so **hours are never written automatically**.

**It reports what it cannot.** `verify_venue.py`, `watch_changes.py` and
`check_deployment.py` then run, and anything needing a human becomes one issue.

Dated facts carry one date and no prose. `closedUntil` generates its own sentence at
build time *and again in the browser*, so a closure stops being claimed the day it
expires rather than at the next build.

## Reviews and scores

Reviews arrive as GitHub issues, never as edits. The forms are in
`.github/ISSUE_TEMPLATE/`; applying the `approved` label fires
`.github/workflows/ingest-reviews.yml`, which validates (venue must exist as the map
spells it, handle must already be approved, rating 1–5, real date, 40 characters
minimum), strips markup and HTML-escapes the body, rebuilds, commits and closes the
issue. The reviewer handle comes from the issue author, so nobody can post as someone
else. A rejection comments the reason and leaves the issue open.

Three separate judgements, deliberately kept apart:

- **Löyly** — who throws the water: someone else (`staff`, an Aufguss), you (`self`),
  or a machine that doses aroma and nobody throws (`machine`). Derived from the
  `aufguss` kind the venues confirmed by email, so there is no second table to drift.
- **Finnish score** — one Finn's rating of the place *as a sauna* out of 10: heat,
  löyly, whether you may throw water. Not the spa around it. `None` shows as `FIN –`,
  never a zero. Opinions, so `selfupdate.py` must never touch them.
- **Aufguss rating** — only rendered where `loyly == "staff"`, because rating the
  Aufguss at a self-serve sauna would be scoring something that does not happen there.

## Images

Twelve venues carry a real photo; the other eight carry a generated map tile.

That split is not a stylistic choice - it is what free licensing allows. Wikimedia
Commons has good, high-resolution photographs of every **hotel** on the list (the Adlon
alone is 7225x4912) and of Stadtbad Neukoelln and the Tempodrom that houses Liquidrom.
It has **nothing** for Vabali, KIEZ SAUNA, Olivin, Saunabad, Luetzow, ANTI SPA, sly or
Finnland Zentrum - searches for those return mineral crystals and 19th-century
magazines. The venues' own photographs are copyrighted marketing material and are not
reused here.

So the eight without a free photo get a zoomed crop of the atlas instead, centred on
their blip. Tiles cost almost nothing: they are `<svg>` elements whose `<use href="#atlas">`
points at the single map definition in `<defs>`, so the road geometry exists once in the
DOM rather than nine times.

Every photo is credited in place - photographer and licence, linking to the Commons file
page - as CC BY-SA and FAL require, and again in the Image credits block at the foot of
the page, which is generated from `img/credits.json` so it cannot drift from what is
actually embedded.

The eight venues without a freely licensed photo link straight to their own pictures
("See their photos") rather than carrying a copy of them.

| Script | Does |
|---|---|
| `src/fetch_images.py` | Pulls the chosen Commons files at 900 px plus their licence metadata into `img/credits.json`. |
| `src/embed_images.py` | Encodes `img/card/*.webp` into `img/embed.json` as data URIs. |

Card images are committed as 640x400 WebP (409 KB total). They are inlined as data URIs
rather than linked so the page stays a single self-contained file that also works as an
Artifact, where the CSP blocks external images.

## Mobile

Two things matter and neither is obvious:

- **The site build must be a full document.** The Artifact host supplies its own
  `<head>`, so the template is authored as a fragment — but a fragment served by a
  static host has no `<meta name="viewport">`, and phones then lay the page out at
  980 px and shrink it to fit. `assemble.py` wraps the fragment for `index.html` and
  leaves `artifact.html` bare. Do not "simplify" this back to one output.
- **The map reframes itself.** Below 520 px of map width the viewBox crops to the
  venue bounding box (`EXTENT`), district labels and the scale bar are hidden because
  they would render at ~4 px, and blips scale up to a ~17 px touch target. Scaling
  blips breaks the build-time spacing, so `spread()` re-runs the same relaxation at
  runtime against the size actually drawn; displaced blips get a hairline back to
  their true position (currently 4 blips, max ~200 m).

Verified at 320, 375, 768 and 1440 px: no horizontal overflow at any width.

## Mobile explorer

Below 1000px the map/list split becomes a map-first explorer rather than a short map
with twenty long cards stacked under it:

- the map fills an 82dvh section, and `frameFor()` fits the venue extent to the
  container's own aspect ratio, so a portrait phone gets a portrait frame with no
  letterboxing;
- selecting a venue raises a **peek card** over the map (thumbnail, name, type,
  district, price) with a close button;
- the list is a **bottom sheet** you can drag or tap open, labelled with the current
  match count.

Two traps worth remembering. `.mapcol .inner` is `position:sticky; top:70px` on desktop;
the mobile rule must reset `top:auto` or the map is pushed 70px down and overflows the
section. And the scrollport differs by breakpoint - `.listcol` on desktop, `.cards`
inside the sheet on mobile - so `revealCard()` walks up to find the real scroller
instead of assuming, otherwise it scrolls the window and drags the page out from under
the map.

## Design notes

- **Single committed theme.** A game HUD reads as one fixed world, so the page does
  not follow the viewer's light/dark setting; every colour is painted explicitly.
- **Type.** Rockstar sets the GTA logo in **Pricedown** (Ray Larabie, based on the
  *Price Is Right* logo, used on every title since GTA III) and the interface in
  **Chalet 1960** / **Chalet Comprime 1960** (House Industries). Pricedown's free
  licence is desktop-only and explicitly excludes web embedding, so the page uses the
  closest Google Fonts stand-ins instead: **Anton** for the wordmark and big numbers,
  **Oswald** for HUD labels and map type (an Alternate Gothic revival, the usual
  Chalet Comprime substitute), **Archivo** for body copy. The wordmark's six-step
  offset `text-shadow` is what gives it the extruded game-logo slab.
- **Group hire is a different unit.** A EUR 40 booking for up to four people is not
  comparable to a EUR 12.50 entry, so venues priced per booking are drawn as **circles**
  rather than squares, carry a "priced per booking" tag, have their own filter chip, and
  are excluded from the cheapest-per-person figure. Shape was the free channel: fill
  already carries the price band and the corner dot already carries USC.
- **Blips** are rounded squares filled by price band (€18 → €90, gold to deep ember)
  with a white flame glyph; a cyan corner dot means the venue is on Urban Sports Club;
  a pale blip with a dark flame means the price is unpublished or the sauna is closed.
  The card list uses the same blip so the two views read as one system.
- **The map** is real OSM geometry — motorways in amber, primary and secondary streets
  in white over a warm casing, parks in olive, water in slate, S-Bahn dashed. Scale bar
  is exact: 1 map unit = 12.88 m at this latitude.
- The whole file is pure ASCII (non-ASCII becomes HTML entities in markup and `\uXXXX`
  escapes in script), so it renders correctly whatever charset a host declares.
- Geodata © OpenStreetMap contributors, ODbL.
