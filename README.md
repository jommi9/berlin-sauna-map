# Berlin Sauna Map

Nineteen Berlin saunas and spas drawn as an open-world game atlas.

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
| `index.html` | The built page (~339 KB). This is what gets published, and what a static host serves at the site root. |
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
   python3 build_venues.py && python3 declutter.py && python3 assemble.py tpl2.html ../index.html
   ```

3. Republish `index.html` to the same artifact URL (pass the URL so the link stays stable).

`build_geo2.py` only needs re-running if you change the map's bounding box — it reads
the cached OSM files. To refresh those from Overpass, see the queries in `fetch.sh`.

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
