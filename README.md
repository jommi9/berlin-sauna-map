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

Source of truth for the venue data is the Notion page **Personal Home / Projects /
Berlin Sauna Guide / Saunas & Spas**. The site is a single static, self-contained
HTML file — no runtime API calls, no keys, no build server.

## Files

| File | What it is |
|---|---|
| `index.html` | The built page (~858 KB, images inlined). This is what gets published, and what a static host serves at the site root. |
| `src/tpl2.html` | **Current design.** Template with `/*__GEO__*/` and `/*__VENUES__*/` placeholders. Edit look and feel here. |
| `src/tpl.html` | The previous, quieter atlas design, kept as a fallback. |
| `src/build_venues.py` | The venue table transcribed from Notion, plus map projection. **Edit content here.** |
| `src/declutter.py` | Nudges overlapping blips apart (currently ≤ 90 m displacement; a hairline tick shows the true spot when moved). |
| `src/build_geo2.py` | Projects and simplifies districts, water, parks, roads and rail into `geo.json`, collapsing each layer to one path so the SVG stays ~8 nodes instead of 9,400. |
| `src/assemble.py` | Inlines the JSON and writes the final ASCII-only HTML. Takes `<template> <output>`. |
| `src/fetch.sh` | Overpass fetcher with mirror fallback and retries. Only needed to refresh the cached geodata. |
| `src/geo.json`, `src/venues.json` | Derived map + venue data, committed so venue rebuilds need no network. |
| `src/roads.json` etc. | Raw Overpass dumps, gitignored (16 MB). Only needed if the map bbox changes; `fetch.sh` re-pulls them. |

## Rebuilding after a Notion edit

1. Update the `V` list in `src/build_venues.py` to match the Notion table.
2. From `src/`:

   ```
   python3 build_venues.py && python3 declutter.py && python3 embed_images.py \
  && python3 assemble.py tpl2.html ../index.html \
  && python3 assemble.py tpl2.html ../artifact.html
   ```

3. Republish `index.html` to the same artifact URL (pass the URL so the link stays stable).

`build_geo2.py` only needs re-running if you change the map's bounding box — it reads
the cached OSM files. To refresh those from Overpass, see the queries in `fetch.sh`.

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
