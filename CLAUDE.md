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

`python3 src/verify_venue.py` with no arguments re-checks every listed venue against its
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

`PICKS`, `PRACTICAL`, `TRAPS` and `LAST_CHECKED` are defined once in `build_venues.py` and
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

`index.html` (full document, has the viewport meta) is for GitHub Pages.
`artifact.html` (bare fragment) is for publishing as an Artifact, which rejects
`<html>`/`<head>`/`<body>` and supplies its own head. The Artifact also gets the twelve
photos inlined as data URIs, because it is one file; the website gets them as
`src/img/card/*.webp`, which halves the page. `og.png` at the repo root is the share
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

- Every colour is a token at the top of `tpl2.html`'s `<style>`: light values on
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
  the header changes.
- A place is a compact row (thumbnail, name, status) until it is picked; only
  the picked one opens into the full card. That keeps several places in view,
  which is what shows the list scrolls; a soft fade at its bottom edge and a
  visible scrollbar back it up (`updateMore`). No floating buttons over the list.
  The list-and-map panel is sized so it fits one screen under the filter row.

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
serves it at https://jommi9.github.io/berlin-sauna-map/, and the jommi.fi Worker passes
https://jommi.fi/sauna/berlin/ through to it, which is the address canonical and share links use;
jommi.fi/sauna/ is the hub of all the sauna maps, and the eyebrow links up to it).

## The social layer lives on jommi.fi, behind X

Signing in, saved spots, logged visits, the leaderboard and the review panel are not in
this repo's data. They are an API in the jommi.fi Worker (repo `jommi9/jommi-fi`,
`worker/sauna-api.js`, under `/sauna/api/`) with its own D1 database, on the same origin
as the map so a session cookie works. The page asks `/sauna/api/me` on load and shows
none of it unless the answer is `on: true`, and only asks at all under a `/sauna/` path,
so the github.io copy and the artifact have no sign-in, no board and the GitHub review
links instead. The code is the last block of `tpl2.html`'s script ("the social layer").

- Sign-in goes through the shared `accounts` Worker (game `sauna`), the one Termination
  uses; nothing here sees an X token. It turns itself on once that Worker lists the game,
  and `SAUNA_SIGNIN = "off"` in jommi-fi's `wrangler.jsonc` keeps it off.
- A visit is a person's own word. The board counts distinct saunas, one visit per sauna per
  day, so it is slow to pad and not proof of anything.
- Becoming a reviewer is an application read by the editor (`SAUNA_ADMINS`, an X handle),
  who approves it on the map's panel section. Reviews from the panel are served live by the
  API and render under each card's "reviews"; they never enter `reviews.json`.
- Everything people type is escaped with `esc()` before it touches `innerHTML`. Keep it so.

## Reviews baked into the build come through GitHub issues, never by hand

This is the older path, and the only one a copy without the API can show. On jommi.fi the
panel above replaces it.

Two files hold the whole model: `src/reviewers.json` (approved handles) and
`src/reviews.json` (a flat list, each keyed to a venue `name` and a `reviewer`
handle). `build_venues.py` joins them onto venues as `reviews` and a rounded
`rating`; a review whose `reviewer` is not in `reviewers.json` is silently
dropped, so revoking someone is a one-line delete.

The path in is `.github/ISSUE_TEMPLATE/reviewer-application.yml` and `review.yml`.
Applying the `approved` label fires `.github/workflows/ingest-reviews.yml`, which
runs `src/ingest_issue.py` (validates venue name, handle, rating, date, length;
strips markup and HTML-escapes, because review text lands in `innerHTML`),
rebuilds both outputs, commits, then comments on the issue and closes it. A
rejection exits non-zero, comments the reason and leaves the issue open.

Never write review text yourself, not even to test rendering. Build with a
`PLACEHOLDER`-marked body, check the layout, then reset `reviews.json` to `[]`
and rebuild before committing.

## The map updates itself where it can prove the change

`src/selfupdate.py` re-reads each venue's own page weekly and rewrites
`build_venues.py` where a claim is provable, then the workflow rebuilds, pushes
and regenerates Notion. Nothing else in the repo is allowed to write venue data.

Proof means an anchor in `src/sources.py` matching one value on the operator's
own page. Repetition is fine — a price in a summary box and again in a table is
the same claim twice — but two *different* values under one label is not proof
and is left alone.

Three refusals, and none of them should be relaxed:

| | |
|---|---|
| a figure moving below half or above double | a misparse fails loudly instead of writing €6 over €22 |
| more than four changes in one run | five venues do not all reprice on the same Monday; a broken parser looks exactly like that |
| an edit target that is not unique | the same rule CLAUDE.md already imposes by hand |

Only five venues are anchored, and the others were **measured and rejected**,
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
immediately beside the figure, add the anchor to `sources.py`, and check it
matches exactly once with `python3 selfupdate.py --dry-run`.

## Löyly, the Finnish score, and the Aufguss rating

Three related things, deliberately kept apart.

**Who throws the water** is derived, never typed twice: `LOYLY_OF` maps the
`aufguss` kind the venues confirmed by email onto `staff` (someone throws for
you), `self` (you throw your own) or `machine` (a dispenser doses aroma and
nobody throws anything). Hilton is the clearest `machine` — they wrote that
pouring your own is *not allowed*. Change the kind in `HEAT` and the löyly
follows; there is no second dict to keep in step.

**Which sauna culture** a place belongs to is derived from the löyly too
(`style_of` in `build_venues.py`) and shown as the flag badge on each card:
you throw your own is **Finnish**, a sauna master's Aufguss is **German**, a
machine dosing it with nobody allowed to throw is **no löyly** (a fake sauna by
Finnish standards). A **banya** throws its own like a Finnish sauna, which the
löyly cannot tell apart, so banyas are named in `BANYA`; none is listed yet.

**`FINNISH`** is one Finn's score of the place *as a sauna*, in stars out of 5
(halves allowed) — heat, löyly, and whether you may throw water — not of the spa
around it. A venue missing from the table is not scored yet and its card shows
no score, never a zero; a scored card shows it on the flag badge ("4.5★").
These are opinions, so they are only ever written by hand: `selfupdate.py` must
never touch them, and nothing in the build second-guesses them.

**`AUFGUSS_SCORE`** only renders where `loyly == "staff"`. Rating the Aufguss
at a self-serve sauna would be scoring something that does not happen there,
so `build_venues.py` drops it rather than trusting the caller.

The filter chip that used to say "Aufguss" is now two chips, because the two
are opposites and a Finn is usually looking for one or the other.
