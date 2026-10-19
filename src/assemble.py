import json, re, sys
TPL = sys.argv[1] if len(sys.argv) > 1 else 'tpl.html'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'berlin-sauna-map.html'
tpl = open(TPL, encoding='utf-8').read()

def ent(s):   # HTML context: numeric character references
    return ''.join(c if ord(c) < 128 else f'&#{ord(c)};' for c in s)
def jsesc(s): # JS context: \uXXXX escapes (entities would NOT be decoded here)
    return ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in s)

# split on <script> blocks so each half gets the right escaping
parts, out = re.split(r'(<script>.*?</script>)', tpl, flags=re.S), []
for p in parts:
    out.append(jsesc(p) if p.startswith('<script>') else ent(p))
doc = ''.join(out)

geo = json.dumps(json.load(open('geo.json', encoding='utf-8')), separators=(',', ':'), ensure_ascii=True)
venues = json.load(open('venues.json', encoding='utf-8'))
ven = json.dumps(venues, separators=(',', ':'), ensure_ascii=True)
images = json.load(open('img/embed.json', encoding='utf-8'))
meta = json.load(open('meta.json', encoding='utf-8'))
# The Artifact is one self-contained file, so it gets the photos inlined. The
# website has a file system, so there the same photos are served as files and
# the page shrinks from ~900 KB to ~500 KB; the <img> tags are already lazy.
if not OUT.endswith('artifact.html'):
    images = {k: dict(v, src=f'src/img/card/{k}.webp') for k, v in images.items()}
img = json.dumps(images, separators=(',', ':'), ensure_ascii=True)
picks = json.dumps(meta['picks'], separators=(',', ':'), ensure_ascii=True)
doc = (doc.replace('/*__GEO__*/', geo).replace('/*__VENUES__*/', ven)
          .replace('/*__IMAGES__*/', img).replace('/*__PICKS__*/', picks)
          .replace('/*__REVIEWERS__*/', json.dumps(meta['reviewers'], separators=(',', ':'), ensure_ascii=True))
          .replace('/*__TRAPS__*/', json.dumps(meta['traps'], separators=(',', ':'), ensure_ascii=True))
          .replace('__LAST_SCAN__', meta['lastCheckedStamp'])
          # PRACTICAL is one string in build_venues.py, shared with Notion; its
          # **bold** becomes <strong> here and its non-ASCII becomes entities.
          .replace('__PRACTICAL__', ent(re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', meta['practical'])))
          .replace('__COUNT__', str(meta['count'])))
for token in ('__LAST_SCAN__', '__COUNT__', '__PRACTICAL__', '/*__'):
    assert token not in doc, f"unfilled placeholder {token}"
assert doc.isascii(), "non-ascii survived"
# Two outputs from one template.
#   - the Artifact host supplies its own <head>, so it must get a bare fragment
#     (no doctype/html/head/body - those are rejected)
#   - a standalone static host supplies nothing, so index.html needs a real
#     document. Without <meta name="viewport"> phones lay the page out at 980px
#     and shrink-to-fit, which makes every bit of text unreadable.
if OUT.endswith('artifact.html'):
    open(OUT, 'w', encoding='ascii').write(doc)
else:
    head, sep, body = doc.partition('</style>')
    assert sep, "template must contain a </style> to split on"
    # The public address. GitHub Pages builds and serves the page; jommi.fi/sauna/ is the same
    # page passed through the jommi.fi Worker, and it is the one links and search should use.
    SITE = 'https://jommi.fi/sauna/berlin/'
    DESC = f"{meta['count']} Berlin saunas and spas, priced and plotted on one map, with a Finn's notes on the loyly."
    # The app icon from the header, as the tab icon: steam rising off the stones.
    icon = ('data:image/svg+xml,' +
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#E9A462"/><stop offset="1" stop-color="#B3502A"/></linearGradient></defs>'
            '<rect width="64" height="64" rx="15" fill="url(#g)"/>'
            '<path d="M21 43 q-4.6 -5.5 0 -11 q4.6 -5.5 0 -11 M32 45 q-5 -6.5 0 -13 q5 -6.5 0 -13 M43 43 q-4.6 -5.5 0 -11 q4.6 -5.5 0 -11" fill="none" stroke="#fff" stroke-width="4.6" stroke-linecap="round"/>'
            '<path d="M15 52 h34" stroke="#fff" stroke-opacity=".6" stroke-width="4.6" stroke-linecap="round"/>'
            '</svg>').replace('"', "'").replace('<', '%3C').replace('>', '%3E').replace('#', '%23')
    # Structured data: the list of places, so a search engine sees twenty named
    # venues with coordinates rather than one opaque page.
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "Berlin Sauna Map",
          "url": SITE, "description": DESC, "numberOfItems": meta['count'],
          "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "item": {
                  "@type": "Place", "name": v["name"],
                  "url": v.get("url") or SITE,
                  "address": {"@type": "PostalAddress", "addressLocality": "Berlin",
                              "addressCountry": "DE"},
                  "geo": {"@type": "GeoCoordinates", "latitude": v["lat"], "longitude": v["lon"]}}}
              for i, v in enumerate(venues)]}
    ldjson = json.dumps(ld, separators=(',', ':'), ensure_ascii=True).replace('</', '<\\/')
    page = ('<!doctype html>\n<html lang="en">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="theme-color" content="#F2F1EE" media="(prefers-color-scheme: light)">\n'
            '<meta name="theme-color" content="#0E0F11" media="(prefers-color-scheme: dark)">\n'
            '<meta name="color-scheme" content="light dark">\n'
            f'<meta name="description" content="{DESC}">\n'
            f'<link rel="canonical" href="{SITE}">\n'
            f'<link rel="icon" href="{icon}">\n'
            '<meta property="og:type" content="website">\n'
            '<meta property="og:site_name" content="Berlin Sauna Map">\n'
            '<meta property="og:title" content="Berlin Sauna Map">\n'
            f'<meta property="og:description" content="{DESC}">\n'
            f'<meta property="og:url" content="{SITE}">\n'
            f'<meta property="og:image" content="{SITE}og.png">\n'
            '<meta property="og:image:width" content="1200">\n'
            '<meta property="og:image:height" content="630">\n'
            '<meta property="og:image:alt" content="A map of central Berlin with sauna locations marked as flame blips">\n'
            '<meta property="og:locale" content="en_GB">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
            '<meta name="twitter:title" content="Berlin Sauna Map">\n'
            f'<meta name="twitter:description" content="{DESC}">\n'
            f'<meta name="twitter:image" content="{SITE}og.png">\n'
            + head + sep + '\n'
            f'<script type="application/ld+json">{ldjson}</script>\n'
            '</head>\n<body>\n' + body.lstrip() + '\n</body>\n</html>\n')
    open(OUT, 'w', encoding='ascii').write(page)
    doc = page
print(f"{TPL} -> {OUT}: {len(doc)/1024:.0f} KB, pure ASCII")
