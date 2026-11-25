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
  Francisco's Golden Gate Bridge does. It is the header tile, the tab icon and the city's row in the switcher. A city
  without one gets the plain three curls, which is also the mark in the footer.
- A fact about one city never goes in `engine/`. If the template needs to say something that
  differs by city, it becomes a field in `city.json` and a placeholder (`__CITY__`, `__LEDE__`,
  `__TZ__`), and `assemble.py` fails the build on a placeholder left unfilled.
- `city.json` also says the currency sign (`"currency"`) and whether Urban Sports Club exists
  there (`"usc"`); without it the page drops the USC chip, figure, legend dot and card row. The
  price bands are the same numbers in every currency, which is rough but fine for euros and
  dollars. Filter chips that no venue in a city could match hide themselves.
- The naive cities were built to the same sourcing rule as Berlin: every venue passed
  `verify_venue.py`, and every price and hour was read off its own site. Where a site renders
  prices with a script, or does not say who throws the water, the field is empty rather than
  guessed. Who throws the water, the Finnish scores, picks and photos are still to do there.
- Base maps for a new city come from an OpenStreetMap extract, not Overpass, which resets every
  connection from a cloud session: `engine/osm_extract.py <city> <extract.osm.pbf>` (BBBike has
  city extracts), then `engine/build_geo.py <city>`. It draws the sea from the coastline, which
  Berlin never needed. `engine/og.js` takes a city's share image.
- The social layer on jommi.fi keys saved spots, visits and reviews by venue name alone, and
  works out the city from the name. So a venue's name must be unique across the cities, and
  `build_venues.py` refuses a name another city already uses. Each page asks for its own city's
  board (`/public?city=<slug>`).
- To open a city on jommi.fi: set `"live": true` in its `city.json` and rebuild every city, then
  in `jommi9/jommi-fi` add the slug to `SAUNA_LIVE` in `worker/sauna-api.js`, add its two paths to
  `run_worker_first` in `wrangler.jsonc`, and set its status to `live` in `src/lib/sauna.ts`.
  Berlin and San Francisco are open; Helsinki and New York are not yet.
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

- Corners are small and few: 4 to 6 px on surfaces (`--r-*`), 2 to 3 px on tags,
  photos flush to their card's edges. Full rounding is kept for things that are
  round by meaning: dots, the slider knob, the app icon.

- Every colour is a token at the top of `engine/template.html`'s `<style>`: light values on
  `:root`, the same names redefined for dark mode. A component never uses a
  literal colour, except over a photo.
- Two accents only. Lake blue (`--tint`) is anything you can tap; the warm
  `--ember` is heat, prices and picks. Pin colours are the price bands
  `--b0`..`--b4`.
- Pins are drawn by one function, `pin()`: a squircle (per person) or circle
  (per booking) with three curls of steam, because a sauna is about the löyly
  rising off the stones. The picked pin lifts a photo bubble (`showName`).
- The voice is lowercase for headings, labels and buttons; venue names and
  acronyms keep their case (`lower()` keeps USC).
- The header figures and the collage are computed in the browser from the
  venue data, so they cannot drift. The collage shows the venues named in
  `COVER`, and only those with a photograph.
- `og.png` is a screenshot of the hero over the map at 1200×630; retake it when
  the header changes (`node engine/og.js <city> ...`, which also does Berlin's collage).
- The city in the title is drawn as a button (tint text on `--tint-soft`, with a chevron) so it
  reads as something to tap. The footer carries the link to the repository with GitHub's mark.
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
  `index.html`, `og.png`, `venues.json` and `img/card/*.webp`, plus the root `index.html`, are
  published. A new kind of file a page needs has to be added there or it will 404 on jommi.fi
  while working on GitHub Pages.
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
  who approves it on the map's panel section. Reviews from the panel are served live by the
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

## Löyly, the Finnish score, and the Aufguss rating

Three related things, deliberately kept apart.

**Who throws the water** is derived, never typed twice: `LOYLY_OF` maps the
`aufguss` kind the venues confirmed by email onto `staff` (someone throws for
you), `self` (you throw your own) or `machine` (a dispenser doses aroma and
nobody throws anything). Hilton is the clearest `machine` — they wrote that
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
