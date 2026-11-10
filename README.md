# Sauna Maps

Public saunas and spas, priced and plotted one city at a time, with a Finn's notes on the löyly. Each city is a map designed like a phone app: the map with the list in a sheet over it, and a lowercase voice.

**Live: https://jommi.fi/sauna/** (the hub) and **https://jommi.fi/sauna/berlin/** (Berlin, twenty-one venues, the only city open so far).

The repository was called `berlin-sauna-map` while Berlin was the only city planned. GitHub
redirects the old repository address.

## How it is laid out

| Path | What it holds |
|---|---|
| `engine/` | Everything the cities share: the build scripts, the page template, the self-updater and the audit scripts. Nothing in here names a city. |
| `berlin/` | Everything about Berlin: its facts (`venues.py`), its settings (`city.json`), its base map, its photos, and the pages built from them. A second city is a second folder like it. |
| `reviewers.json` | The review panel, one list for every city. |
| `index.html` | A redirect to the hub, for anyone who lands on the root of the GitHub Pages copy. |

A city's folder is also what gets served. GitHub Pages serves the repository as it is, so
Berlin is at https://jommi9.github.io/sauna-maps/berlin/, and the jommi.fi Worker (repo
`jommi9/jommi-fi`) passes `/sauna/berlin/` through to that folder. There is one copy, and the
weekly self-update reaches both addresses. Canonical and share links point at jommi.fi. This is
why a city's page, its photos, its share image and its `venues.json` all sit in the one folder:
the page links them relatively, and the Worker only passes that folder through.

Berlin is also published as a private Claude Artifact:
https://claude.ai/code/artifact/79203c00-258e-4438-b918-bd671cd3db9c

## Hosting

GitHub Pages serves the repository from `main`. Note that a custom domain on the
account's *user* site (`jommi9.github.io`) is applied to every project site too — a
stale `CNAME` pointing at a non-resolving domain will take this page down along with
everything else on the account, returning a redirect into nowhere rather than a clear
error. If this URL ever 301s somewhere unexpected, check that repo's `CNAME` first.

Source of truth for a city's venue data is its `venues.py` (`berlin/venues.py`). The Notion page
**Personal Home / Projects / Berlin Sauna Guide / Saunas & Spas** is a *generated
view* of Berlin's — don't hand-edit that table, `push_to_notion.py` overwrites it. Each
city's page is a single static, self-contained HTML file with no keys and no build server.

## Files

In a city's folder (`berlin/`):

| File | What it is |
|---|---|
| `venues.py` | **The source of truth.** Every venue fact, as tables keyed by venue name: the venue rows, opening hours, cabin temperatures and Aufguss practice, the Finnish scores, the fast picks, the "two traps" box, the last-checked date. Edit content here; everything else is generated from it. |
| `city.json` | What makes the page this city's: its name, country, timezone, the map's bounding box (`[west, south, east, north]`), the second sentence of the lede, and the opening line of its Notion page. The folder's name is the city's slug and its address under `/sauna/`. |
| `sources.py` | Anchors for `selfupdate.py`: the regexes that pin one figure on a venue's own page to one figure in `venues.py`. |
| `reviews.json` | Reviews of this city's venues. Written by the ingest workflow, never by hand. |
| `index.html` | The built page (~400 KB). Its photos are served as files from `img/card/`, and it carries the canonical link, Open Graph tags and JSON-LD that the Artifact build leaves out. |
| `artifact.html` | The same page as one self-contained fragment with the photos inlined (~900 KB), for publishing as an Artifact. |
| `og.png` | The 1200x630 share image named in the Open Graph tags, and the picture on the city's card on the hub. Regenerate it by hand if the hero or the map changes. |
| `geo.json`, `venues.json`, `meta.json` | Derived map and venue data, committed so a rebuild needs no network. The jommi.fi Worker reads `venues.json` to know which venue names are real. |
| `districts.geojson` | District outlines, input to `build_geo.py`. |
| `img/card/*.webp`, `img/credits.json` | The photos and their Commons credits. |
| `notion_page.md` | The generated Notion page. |
| `roads.json` etc. | Raw Overpass dumps, gitignored (16 MB). Only needed if the map bbox changes; `fetch.sh` re-pulls them. |

In `engine/` (every script takes the city as its first argument, for example `python3 engine/selfupdate.py berlin`):

| File | What it is |
|---|---|
| `build.py` | The whole rebuild in one command, for one city or for all of them. |
| `city.py` | Finds the cities and reads `city.json`. Also holds the repository name and the hub address, the two things the engine knows about where it is published. |
| `each.py` | Runs one script for every city in turn, for the workflows. |
| `template.html` | **Current design.** Template with `/*__GEO__*/` and `/*__VENUES__*/` placeholders, and `__CITY__`, `__LEDE__` and `__TZ__` for what comes from `city.json`. Edit look and feel here; the colour tokens sit at the top of its `<style>`, light first with a dark set. |
| `template_atlas.html` | The previous, quieter atlas design, kept as a fallback. It still assembles (`assemble.py berlin template_atlas.html out.html`) but was written for Berlin and says so in its text. |
| `build_venues.py` | Joins a city's tables into `venues.json` and `meta.json`: the map projection, who throws the water and the sauna culture derived from it, reviews and scores. |
| `declutter.py` | Nudges overlapping blips apart (currently ≤ 90 m displacement in Berlin; a hairline tick shows the true spot when moved). |
| `build_geo.py` | Projects and simplifies districts, water, parks, roads and rail into `geo.json`, collapsing each layer to one path so the SVG stays ~8 nodes instead of 9,400. |
| `assemble.py` | Inlines the JSON and writes the final ASCII-only `index.html` and `artifact.html`. |
| `push_to_notion.py` | Renders a city's Notion page into `notion_page.md`, ready to apply with `replace_content`. |
| `fetch.sh` | Overpass fetcher with mirror fallback and retries. Only needed to refresh the cached geodata. |
| `selfupdate.py` | Re-reads each venue's page and rewrites the city's `venues.py` where a claim is provable. The only script allowed to write venue data. |
| `verify_venue.py` | Checks every venue against its own site: `OK` / `THIN` / `PAUSED` / `STALE NOTICE` / `BLOCKED` / `SUSPECT` / `LIKELY CLOSED` / `UNREACHABLE`. With no argument it audits every city; with a name and a URL it checks one candidate. |
| `watch_changes.py` | Flags a venue whose own page no longer shows any price we list. Conservative by design — it reports, never edits. |
| `check_deployment.py` | Hashes a city's live page against its `index.html`, warns on seasonal switches, and chases closures whose date has lapsed. `--wait <min>` to allow for a Pages deploy. |
| `ingest_issue.py` | Validates an approved reviewer application or review issue and folds it into the JSON. A review goes to the city whose map lists the venue. |

## Rebuilding after a data edit

1. Edit the city's `venues.py` — it is the source, and Notion is generated from it.
   Never edit venue data with a bare `str.replace()`: assert the old string exists
   and is unique first, because a silent no-op replace is what once let a price
   reach Notion but not the site.
2. From the repository root:

   ```
   python3 engine/build.py berlin
   ```

3. `python3 engine/push_to_notion.py berlin`, then apply `berlin/notion_page.md` with
   `notion-update-page` / `replace_content`.
4. Commit and push — GitHub Pages serves `berlin/index.html`. A push succeeding is **not**
   the same as the site updating; confirm with `python3 engine/check_deployment.py berlin`.
5. Republish `berlin/artifact.html` to the same artifact URL (pass the URL so the link stays
   stable). Nothing in CI can do this step — the artifact is the one output that
   always needs a human.

`build_geo.py` only needs re-running if you change the map's bounding box — it reads
the cached OSM files. To refresh those from Overpass, see the queries in `fetch.sh`.

## Opening a new city

1. Make its folder, named for its slug (`helsinki/`), with a `city.json` like Berlin's.
2. Draw its base map: fetch the Overpass dumps for its bounding box with `engine/fetch.sh`, add
   a `districts.geojson`, and run `python3 engine/build_geo.py helsinki`.
3. Write its `venues.py`, one venue at a time, each checked first with
   `python3 engine/verify_venue.py "<name>" <official-url>` and read off the venue's own page.
   Only `V` and `LAST_CHECKED` are required; leave out any table the city has no use for.
   Add an empty `reviews.json` (`[]`), and a `sources.py` once a venue has a price that can be
   anchored.
4. `python3 engine/build.py helsinki`, then take its `og.png`.
5. In `jommi9/jommi-fi`: add the slug to the live cities in `worker/index.js` and
   `worker/sauna-api.js`, add its path to `run_worker_first` in `wrangler.jsonc`, and set it to
   `live` in that repository's city list (`sauna.ts`).

The workflows pick a new city up by themselves, because they run over every folder that has a
`city.json`.

Two parts of the engine still assume Berlin, and each needs a decision that only a real second
city can settle. Urban Sports Club is a column in every venue row and has its own filter, legend
dot and header figure in the template. Prices are written and banded in euros.

## Keeping itself current

`.github/workflows/weekly-venue-audit.yml` runs Mondays 06:00 UTC, and does two
different jobs in order.

**It fixes what it can prove.** For every city, `selfupdate.py` re-reads each venue's own page
and rewrites the city's `venues.py` where an anchor in its `sources.py` matches exactly one value,
then rebuilds, regenerates Notion, commits and pushes. It caught Stadtbad Neukölln
shortening its 2026 summer break from 31 October to 30 September without telling
anyone.

It refuses to write when a figure would move below half or above double, when more
than four things change in one city in one run, or when an edit target is not unique. In
Berlin fourteen anchors cover five venues; the other fifteen were **measured and rejected**, not
forgotten — they render prices in JavaScript or print bare amounts with no label
(`€14.50 €14.50 €29 €29`). No venue publishes JSON-LD opening hours (checked across
all twenty), so **hours are never written automatically**.

**It reports what it cannot.** `verify_venue.py`, `watch_changes.py` and
`check_deployment.py` then run, and anything needing a human becomes one issue.

Dated facts carry one date and no prose. `closedUntil` generates its own sentence at
build time *and again in the browser*, so a closure stops being claimed the day it
expires rather than at the next build.

## Reviews and scores

On jommi.fi, people sign in with X to save spots, log visits and climb the leaderboard,
and apply to join the review panel; the editor approves them on the page, and their
reviews are served live by the jommi.fi Worker (`jommi9/jommi-fi`, `worker/sauna-api.js`).
None of that is in this repo, and none of it shows on a copy served anywhere else. It does not
know about cities yet: a saved spot or a visit is keyed by the venue's name alone, which has to
change before a second city opens.

Reviews baked into the build arrive as GitHub issues, never as edits. The forms are in
`.github/ISSUE_TEMPLATE/`; applying the `approved` label fires
`.github/workflows/ingest-reviews.yml`, which validates (venue must exist as the map
spells it, handle must already be approved, rating 1–5, real date, 40 characters
minimum), strips markup and HTML-escapes the body, rebuilds, commits and closes the
issue. A review is filed under the city whose map lists the venue. The reviewer handle comes from the issue author, so nobody can post as someone
else. A rejection comments the reason and leaves the issue open.

Three separate judgements, deliberately kept apart:

- **Löyly** — who throws the water: someone else (`staff`, an Aufguss), you (`self`),
  or a machine that doses aroma and nobody throws (`machine`). Derived from the
  `aufguss` kind the venues confirmed by email, so there is no second table to drift.
- **Finnish score** — one Finn's rating of the place *as a sauna* in stars out of 5,
  halves allowed: heat, löyly, whether you may throw water. Not the spa around it. A
  venue without one shows no score, never a zero. Opinions, so `selfupdate.py` must
  never touch them.
- **Aufguss rating** — only rendered where `loyly == "staff"`, because rating the
  Aufguss at a self-serve sauna would be scoring something that does not happen there.

## Images

In Berlin, twelve venues carry a real photo; the other eight carry a generated map tile.

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
| `engine/fetch_images.py` | Pulls the Commons files named in the city's `COMMONS` table at 900 px plus their licence metadata into `img/credits.json`. |
| `engine/embed_images.py` | Encodes `img/card/*.webp` into `img/embed.json` as data URIs. |

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
