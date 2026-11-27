# Sauna Maps — working notes

## One engine, one folder per city

`engine/` is everything the cities share (build scripts, `template.html`, the self-updater,
the audit scripts) and names no city. A city is a folder at the repo root with a `city.json`:
`berlin/`, and since 15 November 2026 first, naive maps of `helsinki/`, `nyc/` and `sf/`. Its facts are `berlin/venues.py`, its settings
`berlin/city.json`, and its built pages sit beside them, because GitHub Pages serves the folder
as it is and the jommi.fi Worker passes `/sauna/berlin/` through to it.

- Every engine script takes the city first: `python3 engine/selfupdate.py berlin --dry-run`.
  `engine/build.py` rebuilds one city or all of them, and `engine/each.py <script>` runs a
  script over every city for the workflows.
- The city in each page's title is a switcher listing every city, so a new city, a renamed one,
  a new icon or a change to `"live"` alters every page: rebuild them all (`engine/build.py` with
  no city). On GitHub Pages every city in it is a link, because the folders sit side by side; on
  jommi.fi and in the artifact only live cities are links and the rest say "soon".
- Each city has its own app icon: `"icon"` in its `city.json` is the city's landmark as a few SVG
  shapes (Berlin's TV tower, Helsinki's cathedral), and `city.icon()` stands it between two curls
  of steam. A landmark too wide for that draws its own steam and says `"iconFull": true`, as San
  Francisco's Golden Gate Bridge does. It is the tab icon and the city's row in the switcher (the
  header no longer shows it, but its hidden SVG still holds the gradient the menu's icons use).
  A city without one gets the plain three curls, which is also the mark in the footer.
- A fact about one city never goes in `engine/`. If the template needs to say something that
  differs by city, it becomes a field in `city.json` and a placeholder (`__CITY__`, `__LEDE__`,
  `__TZ__`), and `assemble.py` fails the build on a placeholder left unfilled.
- `city.json` also says the currency sign (`"currency"`) and whether Urban Sports Club exists
  there (`"usc"`); without it the page drops the USC chip, figure, legend dot and card row. The
  price bands are the same numbers in every currency, which is rough but fine for euros and
  dollars. Filter chips that no venue in a city could match hide themselves.
- The other cities were built to the same sourcing rule as Berlin: every venue passed
  `verify_venue.py`, and every price and hour was read off its own site. Where a site renders
  prices with a script, or does not say who throws the water, the field is empty rather than
  guessed. San Francisco and Helsinki were re-read and filled out on 25 November 2026 and New
  York on the 26th. Finnish scores and picks are the editor's own, entered on the score desk (a
  private artifact, https://claude.ai/artifact/GaGofpEKqqdYqKFz9MT2QB: its `saunas` collection is
  the list and its `scores` collection is what the editor entered); outside Berlin only the
  saunas the editor has been to are scored.
- A day in `OPEN` is one window `[open, close]`, or a list of windows where a venue runs a morning
  turn and an evening one (Löyly, Kulttuurisauna: `[[540, 660], [780, 1320]]`), or `None`. The
  status and its countdown read every window (`spans`, `within`), so between two turns the tag
  says "closed now · opens in ...".
- Base maps for a new city come from an OpenStreetMap extract, not Overpass, which resets every
  connection from a cloud session: `engine/osm_extract.py <city> <extract.osm.pbf>` (BBBike has
  city extracts), then `engine/build_geo.py <city>`. It draws the sea from the coastline, which
  Berlin never needed. `engine/og.js` takes a city's share image.
- A frame wider than one extract takes several: `osm_extract.py` reads any number of them. San
  Francisco's frame runs from the city to Sausalito, Albany and Point San Pablo, and is the
  SanFrancisco and Berkeley extracts plus a strip neither covers (Tiburon to the Richmond shore),
  which `engine/osm_fill.py <W> <S> <E> <N> <out.osm.pbf>` fetched from OpenStreetMap's own API
  and saved in the same format. Where no extract reaches, no coastline is read and the land is
  drawn as open sea, so look at the whole base map after widening a frame. Geofabrik's downloads
  reset from a cloud session the way Overpass does.
- The base map is most of a page's weight, so `assemble.py` packs it on the way in (`pack_path`):
  every path becomes relative steps, and road pieces that meet end to end are joined into long
  strokes. `geo.json` stays as `build_geo.py` wrote it. The segments drawn are the same ones; a
  page went from about 500 KB to about 320 KB.
- The social layer on jommi.fi keys saved spots, visits and reviews by venue name alone, and
  works out the city from the name. So a venue's name must be unique across the cities, and
  `build_venues.py` refuses a name another city already uses. Each page asks for its own city's
  board (`/public?city=<slug>`).
- To open a city on jommi.fi: set `"live": true` in its `city.json` and rebuild every city, then
  in `jommi9/jommi-fi` add the slug to `SAUNA_LIVE` in `worker/sauna-api.js`, add its two paths to
  `run_worker_first` in `wrangler.jsonc`, and set its status to `live` in `src/lib/sauna.ts`.
  Berlin, San Francisco, Helsinki and New York are open.
- The repository was `berlin-sauna-map` until November 2026. `check_deployment.py` reads the
  repository's name from Actions, so the Pages address follows a rename by itself; `REPO` in
  `engine/city.py` is the one place the name is written down.

## Who can add what

Anyone can use the maps: save a sauna, log a visit, apply to review. Adding a listing or a city
is for the GitHub users named in `contributors.json` (jommi9 and Jaamuru so far), and even they
only propose:

- The way in is two issue forms, "Add a sauna" and "Open a new city".
  `.github/workflows/propose.yml` runs `engine/propose.py` on them. It checks the issue's author
  against `contributors.json`, refuses markup and malformed input, runs `verify_venue.py` on the
  venue's own site, writes the row into the city's `venues.py` (or draws a new city's base map
  from a BBBike extract), rebuilds, and opens a pull request. **Nothing reaches the site until
  the owner merges that pull request.** From anyone else the issue stays open as a suggestion.
- To add a contributor, add their GitHub login to `contributors.json`. That is the whole grant:
  they do not need to be a collaborator on the repository, and the page lists them.
- A row written by the form is marked with a comment naming the issue and the verifier's
  verdict. THIN and BLOCKED go forward with a warning in the pull request; read the venue's
  page before merging, as for any venue.
- The forms are recognised by their title ("New listing: ", "New city: "), not by a label.
- Form text lands in `innerHTML` unescaped, like all venue data, so `propose.py` refuses
  `< > " \` and backticks outright. Keep that if the forms gain fields.
- With Settings > Actions > General > "Allow GitHub Actions to create and approve pull
  requests" ticked, the workflow opens the pull request itself. Without it the proposal is
  still pushed to its `proposal-<issue>` branch and the issue gets a link that opens the pull
  request in one click, so the forms work either way.

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

1. Run `python3 engine/verify_venue.py "<name>" <official-url>`.
2. Only if it comes back `OK` (live, mentions sauna, publishes prices or hours) is the
   venue a candidate.
3. Read the prices and hours off the venue's own page — never off the aggregator.
4. Anything short of that goes in flagged as unverified, the way sly Berlin and
   Park Inn are, or does not go in at all.

Aggregators are fine for *discovering names to check*. They are never evidence.

## Auditing what is already listed

`python3 engine/verify_venue.py` with no arguments re-checks every listed venue in every city
against its own sites (`verify_venue.py berlin` for one city). Verdicts:

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

Direction of travel was flipped on 3 September 2026. Venue facts live in the city's
`venues.py` (`berlin/venues.py`; until November 2026 they were the top half of
`build_venues.py`, which is why older notes name that file). The Notion page *Personal Home / Projects / Berlin Sauna
Guide / Saunas & Spas* is a **generated view** of it — do not hand-edit that
table, the next push overwrites it. The callout at the top of the page says so.

Why: the venue data used to be a hand transcription of Notion, and the two
drifted three times in two days (the InterContinental hotel-guest rates, Olivin's
price ladder, Liquidrom's tiered admission) — each time after a sync that looked
complete. One direction of travel makes that class of bug impossible, so the
old `check_notion_sync.py` drift checker is gone with it.

To publish the table after a data change:

    python3 engine/push_to_notion.py berlin      # writes berlin/notion_page.md

then apply it with `notion-update-page`, command `replace_content`, passing the
file's contents. Two Notion quirks are handled in the generator and should not be
"simplified" away: bare domains get auto-linked and wreck surrounding bold markers,
so they are wrapped in backticks; a table cell containing a newline breaks the row,
so every cell is whitespace-collapsed; and a code span inside a bold run collides
into `****`, so notes are written as a bold **Heads up:** label followed by
unbolded text rather than bolding the whole sentence.

`PICKS`, `PRACTICAL`, `TRAPS` and `LAST_CHECKED` are defined once in the city's `venues.py` and
injected into both the site template and the Notion page (the traps as a "Two traps"
list under the table), so the fast-picks list cannot say two different things. The hero stamp ("Last scan dd.mm.yyyy") is derived from
`LAST_CHECKED`, so bump that one string when you re-verify the venues. A trap is one
sentence with no dates in it; when the venue has a `closedUntil` in force the browser
appends the date itself, the same way the card's hours line is composed. Never write a
closure date as prose in the template or in `TRAPS`.

Never edit venue data with a bare `str.replace()`. Assert the old string exists
and is unique first — a silent no-op replace is what let the InterContinental
rates reach Notion but not the site.

## Two build outputs — do not merge them

In each city's folder, `index.html` (full document, has the viewport meta) is for GitHub Pages.
`artifact.html` (bare fragment) is for publishing as an Artifact, which rejects
`<html>`/`<head>`/`<body>` and supplies its own head. The Artifact also gets the twelve
photos inlined as data URIs, because it is one file; the website gets them as
`img/card/*.webp`, which halves the page. `og.png` in the city's folder is the share
image the website's Open Graph tags point at. Serving the fragment as a
website makes phones lay it out at 980 px and shrink to fit — the bug that made the
site unreadable on mobile while looking fine in scaled screenshots.

When checking mobile, assert `innerWidth` is what you set. If it reports 980, the
viewport meta is missing and everything measured after that is meaningless.

## Design

The page is built like a places app. Search and filters are one row above
everything; under it, on a computer, the list sits in a sidebar beside the map,
and on a phone the map fills a framed screen with the list riding up over it as
a sheet that collapses to its handle and the place count. Rules that keep it
coherent:

- The look is an index: white and ink, one light sans (Inter Tight) set very large for the
  title, monospaced capitals (IBM Plex Mono) for every label, tag, chip and button, hairlines in
  place of boxes. No rounded corners (`--r-*` are 0) and no shadows; menus and dialogs get a
  1 px ink line instead. Rounding is kept for things round by meaning: dots, the slider knob,
  avatars.
- The site is called "sauna map" and the city comes after it: the title reads "sauna map
  berlin", and so do the page title and share title ("Sauna Map Berlin").
- **The list and the map start on the first screen.** The header is short on purpose: the title
  on one line at about two thirds of its old size with the figures beside it, no collage above
  the map (`.collage` is hidden on the page), and one row of filters with the kind and USC-tier
  groups behind "more filters" on a computer. On a phone the lede is hidden and the figures are
  one slim row. On a 1440 by 900 laptop the map starts about 320 px down; do not add anything
  above the filter bar without checking that. The share image is the exception: `og.js` puts the
  header back at full size, collage included, because a picture has no map to make room for.
- The sauna is in three marks and no more. Birch bark fades in from the top of the page
  (`--bark`), the title thins toward its top edge like steam (`--title-fade`), and a
  thermometer line runs under the header from "cold plunge" to "hot stones" (`--cold`,
  `--cool`, `--mild`, `--warm`, `--hot`). The hottest figure is `--hot` and plunge
  temperatures are `--cold`.
- Both typefaces are under the SIL Open Font License and live in `engine/fonts` with their
  licences. `assemble.py` copies them into one `fonts/` folder at the repo root, beside the
  cities, and every page loads them from `../fonts/`, so no visitor's browser calls a font
  service and swapping cities does not fetch them twice; the Artifact carries them inline. On
  jommi.fi that folder is `/sauna/fonts/`, which the jommi.fi Worker passes through like a city.

- Every colour is a token at the top of `engine/template.html`'s `<style>`: light values on
  `:root`, the same names redefined for dark mode. A component never uses a
  literal colour, except over a photo.
- Ink is what you can tap: `--tint` is the ink colour, a pressed chip is filled with it, and
  links are underlined or outlined. Red (`--ember`, `--hot`) is heat, prices and picks. Pin
  colours are the price bands `--b0`..`--b4`, greys that darken to ink as the price rises.
- Pins are drawn by one function, `pin()`: a squircle (per person) or circle
  (per booking) with three curls of steam, because a sauna is about the löyly
  rising off the stones. The picked pin lifts a photo bubble (`showName`).
- The voice is lowercase for headings, labels and buttons; venue names and
  acronyms keep their case (`lower()` keeps USC).
- The header figures and the collage are computed in the browser from the
  venue data, so they cannot drift. The collage shows the venues named in
  `COVER`, and only those with a photograph; since 26 November 2026 it is drawn only in the
  share image.
- A photo is either from Wikimedia Commons (the city's `COMMONS`, credited with photographer and
  licence by `fetch_images.py`) or one a visitor or reviewer sent in (the city's `PHOTOS`, photo
  key to the name to credit, or `None`; its card is committed as `img/card/<key>.webp`, 640×400).
  `embed_images.py` joins the two, and the card and the credits list say "sent in by a visitor"
  for the second kind, with a line on how to ask for a credit or a take-down. Sent-in photos
  arrive through the photo desk, a private artifact (https://claude.ai/artifact/SHbPacgFe3q3xTeDJSrRQg):
  its `wanted` collection is the venues without a photo and its `photos` collection is what was
  sent, each pointing at an uploaded asset.
- **Photo rights are settled.** The owner is in contact with the venues, and the venues have
  cleared the maps to use their photos (the owner's word, 26 November 2026). A photo that comes
  through the photo desk goes on the map: do not ask where it is from, whether it is licensed or
  whether people in it agreed, and do not attach caveats about rights to the report. Size and
  sharpness are still worth a line.
- `og.png` is a screenshot of the hero over the map at 1200×630; retake it when
  the header changes (`node engine/og.js <city> ...`, which also does Berlin's collage).
- The city in the title is the switcher: underlined, with a red chevron after it. The footer
  carries the link to the repository with GitHub's mark.
- The disclaimer and the data credit (OpenStreetMap's attribution among it) are small print
  under the footer at the bottom right (`.fine`), not cards. "before you go" holds only the
  city's own notes, benchmarks and traps, and is hidden in a city that has neither.
- The °C / °F switch stands at the right end of the filter bar, in line with the map's right
  edge, on a computer and on a phone.
- A picked sauna has its own address, the page's with `#<name-as-a-slug>` after it (`slugOf`).
  Picking one writes it to the address bar and opening such a link picks that sauna.
- A card's first button is "directions": a Google Maps link to the sauna's coordinates, which
  opens the visitor's maps app. "hours & booking" goes to the venue's own site and shows its
  host. There is no street address on a card yet, because the data has districts and
  coordinates only.
- The account stands in the top right corner of the page (`#acct` in `header.top`, not in the
  filter bar): an outlined "sign in" when signed out, the avatar and handle when signed in, with
  its menu hanging from the right edge. On a phone the line above the title makes room for it.
- The panel is a dialog (`#panel-d`), opened by "the panel" in the footer and by the panel line
  in the account menu (`openPanel`). It is one panel for every city, so no page carries it as a
  section; the owner asked for that on 27 November 2026. The line about who adds listings is in
  the small print.
- Signing in is quiet and asked for where it earns something. A signed-out card offers "save" and "i've been here", and either
  opens the sign-in dialog with the reason in its heading (`signIn(why)`, from `data-why`).
- Two things the owner tried and rejected on 26 November 2026, so do not bring them back
  unasked: a key above the list explaining the badges (with the pick chip reworded to "editor's
  pick"), and hiding the stove and löyly rows and the "not known" badge where nothing is known.
  The J chip, the unknown badge and the "Not known" rows stay.
- "share" on a card hands out a different address, `<city>/s/<slug>/`: a small page `assemble.py`
  writes per sauna (`stubs()`), because whatever draws a link preview never sees what follows a
  `#`. That page carries the sauna's name, a line about it and its picture in Open Graph tags, and
  its one line of script sends a person on to the map with the sauna picked. The picture is
  `<city>/og/<slug>.jpg`, drawn by `node engine/og.js --venues <city> ...` (name, kind, district
  and heat beside the photograph, or beside the map around its pin); without one the page falls
  back to the city's `og.png`. Run that after adding or renaming a venue or giving it a photo,
  then rebuild. `slug_of` in `assemble.py` and `slugOf` in the template must stay the same rule.
  The artifact has no such pages, so there "share" copies the `#` address.
- Until the script at the foot of the page has run there is no list and no map, so the page shows
  a loading state: steam rising where the map will be and ghost rows in the list (`.loading`,
  and `.wrap.ready` once `run()` is done). Do not make the first screen depend on the script.
- Swapping cities is a new page. When the pointer nears the switcher or it opens, the other
  cities are prefetched (`fetchAhead`), and Chrome prerenders one as its row is pressed
  (speculation rules).
- "open now" and "closed now" are as of this minute in the city's own time, so their dot
  pulses. When the change is three hours away or less the tag adds "closes in 50 min" or "opens
  in 2 h 30 min" (`statusText`), worked out from the same weekly hours. A window that ends at
  last entry therefore counts down to last entry.
- A place is a compact row (thumbnail, name, status) until it is picked; only
  the picked one opens into the full card. That keeps several places in view,
  which is what shows the list scrolls; a soft fade at its bottom edge and a
  visible scrollbar back it up (`updateMore`). No floating buttons over the list.
  The list-and-map panel is sized so it fits one screen under the filter row.

## Where the pages are served from

Two copies are published from `main`, and neither needs a build step because the pages are
built and committed here.

- **Cloudflare, for jommi.fi.** `wrangler.jsonc` makes this repository an assets-only Worker,
  `sauna-maps`, deployed by Cloudflare's Git connection on each push to `main`. It has no
  address of its own: the jommi.fi Worker reaches it through a service binding and serves each
  live city at `jommi.fi/sauna/<city>/`. `.assetsignore` is an allowlist: only each city's
  `index.html`, `og.png`, `venues.json`, `img/card/*.webp`, `og/*.jpg` and `s/*/index.html`, plus
  the root `index.html` and `fonts/*.woff2`, are published. A new kind of file a page needs has
  to be added there or it will 404 on jommi.fi while working on GitHub Pages. The jommi.fi Worker
  sets how long a browser keeps each kind (`saunaCache` in `worker/index.js`): the typefaces for a
  year, pictures for a day, a page for a minute and stale for ten more while it refreshes.
- **GitHub Pages**, at `jommi9.github.io/<repo>/<city>/`, which is where a city that is not yet
  open on the hub can be looked at.

A city is open on the hub when its `city.json` says `"live": true` (and the jommi.fi Worker lists
it); `check_deployment.py` then checks the jommi.fi copy as well as the Pages one. It ignores
the analytics tag Cloudflare adds to pages on jommi.fi.

## After pushing, confirm the site actually changed

A `git push` succeeding is not the same as the site updating. On 4 September 2026
the Pages deploy failed on an OIDC token timeout while the push reported success,
and the site quietly served stale content. `engine/check_deployment.py <city>` hashes the
city's live page against its `index.html` and also warns when a seasonal hours switch has just
passed; it runs in the weekly audit. If it reports a mismatch on the Pages copy, re-run the
latest "pages build and deployment" workflow run — the build almost always succeeded and
only the deploy step failed. A mismatch on the jommi.fi copy means Cloudflare did not deploy
the last push: retry the latest build under Workers & Pages > sauna-maps > Deployments. Watch
for this after the weekly self-update in particular, since that commit is made by a workflow.

## Rebuild

```
python3 engine/build.py berlin        # or no city, for all of them
```

That runs `build_venues.py`, `declutter.py`, `embed_images.py` and `assemble.py` for the city,
in that order. Then republish `berlin/artifact.html` to the existing artifact URL, and push
(GitHub Pages serves it at https://jommi9.github.io/sauna-maps/berlin/, and the jommi.fi Worker
passes https://jommi.fi/sauna/berlin/ through to it, which is the address canonical and share links use;
jommi.fi/sauna/ is the hub of all the sauna maps, and the eyebrow links up to it).

## The social layer lives on jommi.fi, behind X

Signing in, saved spots, logged visits, the leaderboard and the review panel are not in
this repo's data. They are an API in the jommi.fi Worker (repo `jommi9/jommi-fi`,
`worker/sauna-api.js`, under `/sauna/api/`) with its own D1 database, on the same origin
as the map so a session cookie works. The page asks `/sauna/api/me` on load and shows
none of it unless the answer is `on: true`, and only asks at all under a `/sauna/` path,
so the github.io copy and the artifact have no sign-in, no board and the GitHub review
links instead. The code is the last block of `engine/template.html`'s script ("the social layer").

- Sign-in goes through the shared `accounts` Worker (site `sauna`), the one Termination
  uses; nothing here sees a provider's token. `SAUNA_SIGNIN` in jommi-fi's `wrangler.jsonc` is
  the switch. People sign in with X or GitHub: the page asks which when both are offered
  (`SOC.providers`, from `/me`). The two are separate accounts, and a person is a handle *and*
  where it is from (`via`): profile links, the "you" row on the board and the editor's approve
  buttons all use both, because @sam on X and @sam on GitHub can be two people. Signing in with
  GitHub is not what lets someone add listings; `contributors.json` is. A signed-in GitHub
  contributor just gets a shortcut to the form in their menu.
- A visit is a person's own word. The board counts distinct saunas, one visit per sauna per
  day, so it is slow to pad and not proof of anything.
- Becoming a reviewer is an application read by the editor (`SAUNA_ADMINS`, an X handle),
  who approves it in the panel dialog. Reviews from the panel are served live by the
  API and render under each card's "reviews"; they never enter `reviews.json`.
- Everything people type is escaped with `esc()` before it touches `innerHTML`. Keep it so.
- A logged visit can carry a line of text and the temperatures the person saw (`POST /visit` with
  `log`). The page shows them under each card as "from visitors", with which visit it was for
  that person and the latest reported sauna and plunge figures. **A visitor's number is their
  word, not a venue fact**: it never goes into `venues.py`, never feeds the row's temperature tag
  or the sorts, and people who keep off the board are left out of it.
- The public feed also counts saves per sauna, so each row shows "N saved · N visits" and the
  list can be sorted by either. Like the rest of the layer, none of this exists off jommi.fi.

## Reviews baked into the build come through GitHub issues, never by hand

This is the older path, and the only one a copy without the API can show. On jommi.fi the
panel above replaces it.

Two files hold the whole model: `reviewers.json` at the repo root (approved handles, one panel
for every city) and the city's `reviews.json` (a flat list, each keyed to a venue `name` and a `reviewer`
handle). `build_venues.py` joins them onto venues as `reviews` and a rounded
`rating`; a review whose `reviewer` is not in `reviewers.json` is silently
dropped, so revoking someone is a one-line delete.

The path in is `.github/ISSUE_TEMPLATE/reviewer-application.yml` and `review.yml`.
Applying the `approved` label fires `.github/workflows/ingest-reviews.yml`, which
runs `engine/ingest_issue.py` (finds the city whose map lists the venue; validates venue name,
handle, rating, date, length; a rating is 0.5 to 5 in halves, here and on the jommi.fi panel;
strips markup and HTML-escapes, because review text lands in `innerHTML`),
rebuilds every city, commits, then comments on the issue and closes it. A
rejection exits non-zero, comments the reason and leaves the issue open.

Never write review text yourself, not even to test rendering. Build with a
`PLACEHOLDER`-marked body, check the layout, then reset `reviews.json` to `[]`
and rebuild before committing.

## The map updates itself where it can prove the change

`engine/selfupdate.py <city>` re-reads each venue's own page weekly and rewrites the city's
`venues.py` where a claim is provable, then the workflow rebuilds, pushes
and regenerates Notion. Nothing else in the repo is allowed to write venue data.

Proof means an anchor in the city's `sources.py` matching one value on the operator's
own page. Repetition is fine — a price in a summary box and again in a table is
the same claim twice — but two *different* values under one label is not proof
and is left alone.

Three refusals, and none of them should be relaxed:

| | |
|---|---|
| a figure moving below half or above double | a misparse fails loudly instead of writing €6 over €22 |
| more than four changes in one city in one run | five venues do not all reprice on the same Monday; a broken parser looks exactly like that |
| an edit target that is not unique | the same rule CLAUDE.md already imposes by hand |

In Berlin only five venues are anchored, and the others were **measured and rejected**,
not forgotten: KIEZ SAUNA, Lützow, Palace, Titanic and ANTI SPA either render
prices with JavaScript or print bare amounts with no label beside them
(`€14.50 €14.50 €29 €29`), so no anchor can tell one tariff from another. No
venue publishes JSON-LD opening hours — that was checked across all 20 — so
hours are never written automatically.

Dated facts carry one date and no prose. `closedUntil` generates its own
sentence at build time *and again in the browser*, so the day a closure expires
the card stops claiming the sauna is shut without waiting for a rebuild; it
then says the hours are unverified, and `check_deployment.py` chases it.
Stadtbad shortened its 2026 summer break from 31 Oct to 30 Sep without telling
anyone — that drift is what this is for.

To add a venue to the self-updater: read its page, find a label that sits
immediately beside the figure, add the anchor to the city's `sources.py`, and check it
matches exactly once with `python3 engine/selfupdate.py berlin --dry-run`.

## Temperatures are numbers, kept in °C

Each venue has `hot`, the hottest cabin, and `plunge`, the cold plunge, shown on its row the
way Sauna Ikitai shows them ("90° / 14°") and offered as sorts. `hot` is derived at build time
from the highest temperature the venue's own heat text names, so the number and the prose
cannot disagree. `plunge` is the city's `PLUNGE` table, filled only where a venue states a
figure; Lützow's 14°C is the only one in Berlin so far. A city with `"temp": "F"` in its
`city.json` shows both in Fahrenheit first, and everything is stored in °C (a Fahrenheit figure
keeps one decimal there, so 220°F comes back as 220 and not 219).

The °C / °F switch beside the search overrides the city's unit on that device, for every city
(`localStorage`, key `sauna.unit`). It changes the row tags, the hottest figure, visitors'
figures and the note form, and it rewrites the temperatures inside a venue's own prose
(`tempText`), so write those with the degree sign and the unit letter ("190°F", "80–100°C"). A
bare number in prose ("ranging from 180 to 200") cannot be converted, so avoid it.

## The stove

Every card has a "stove" row: what heats the sauna and, where it is known, who made the stove.
It comes from the city's `STOVE` table, `name: (fuel, brand, note, source)`. Fuel is `wood`,
`smoke`, `pellet`, `electric`, `gas` or `infrared`, or `None`; brand is the maker (IKI, Harvia)
or `None`. A venue missing from the table shows "not known", which is the honest state for most
of them. Source is `"venue"` for what its own site says and `"editor"` for the owner's own
knowledge of the place, and the card says which. Alchemy Springs' two gas stoves are the
editor's word: its site does not mention them. The "wood-fired" chip matches `wood` and
`smoke`. Never guess a fuel from the kind of place.

## Löyly, the Finnish score, and the Aufguss rating

Three related things, deliberately kept apart.

**Who throws the water** is derived, never typed twice: `LOYLY_OF` maps the
`aufguss` kind the venues confirmed by email onto `staff` (someone throws for
you), `self` (you throw your own), `machine` (a dispenser doses aroma and
nobody throws anything) or `dry` (kind `"dry"`: the venue asks that no water goes
on the stones at all, as Good Hot does; it gets the same "no löyly" badge). Hilton is the clearest `machine` — they wrote that
pouring your own is *not allowed*. Change the kind in `HEAT` and the löyly
follows; there is no second dict to keep in step.

**Which sauna culture** a place belongs to is derived from the löyly too
(`style_of` in `engine/build_venues.py`) and shown as the flag badge on each card:
you throw your own is **Finnish**, a sauna master's Aufguss is **German**, a
machine dosing it with nobody allowed to throw is **no löyly** (a fake sauna by
Finnish standards). A **banya** throws its own like a Finnish sauna, which the
löyly cannot tell apart, so banyas are named in the city's `BANYA`; none is listed yet.

**`FINNISH`** is one Finn's score of the place *as a sauna*, in stars out of 5
(halves allowed) — heat, löyly, and whether you may throw water — not of the spa
around it. A venue missing from the table is not scored yet and its card shows
no score, never a zero; a scored card shows it on the flag badge ("4.5★").
These are opinions, so they are only ever written by hand: `selfupdate.py` must
never touch them, and nothing in the build second-guesses them.

**`AUFGUSS_SCORE`** only renders where `loyly == "staff"`. Rating the Aufguss
at a self-serve sauna would be scoring something that does not happen there,
so `engine/build_venues.py` drops it rather than trusting the caller.

The filter chip that used to say "Aufguss" is now two chips, because the two
are opposites and a Finn is usually looking for one or the other.
