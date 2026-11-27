"""Fill the template with one city's data and write its two pages.

    python3 engine/assemble.py <city>                  # <city>/index.html and <city>/artifact.html
    python3 engine/assemble.py <city> <template> <out> # one page from another template in engine/

Two outputs from one template, and they must not be merged:
  - the Artifact host supplies its own <head>, so artifact.html is a bare
    fragment (no doctype/html/head/body - those are rejected), with the photos
    inlined because it is one file;
  - a static host supplies nothing, so index.html is a real document. Without
    <meta name="viewport"> phones lay the page out at 980px and shrink-to-fit,
    which makes every bit of text unreadable.
"""
import base64, html, json, os, re, shutil, sys, unicodedata
import city
CITY = city.enter()
NAME = CITY['name']

def ent(s):   # HTML context: numeric character references
    return ''.join(c if ord(c) < 128 else f'&#{ord(c)};' for c in s)
def jsesc(s): # JS context: \uXXXX escapes (entities would NOT be decoded here)
    return ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in s)
def text(s):  # a city's own words, dropped into HTML text or a double-quoted attribute
    return ent(html.escape(s, quote=False).replace('"', '&quot;'))

# The base map is most of the page, so it is packed before it goes in. geo.json holds each layer
# as build_geo.py wrote it: absolute coordinates, and the roads as thousands of two-point pieces,
# one per stretch between junctions. Here every path is rewritten as relative steps in tenths of
# a unit, and the pieces of a line layer that meet end to end are joined into long strokes. The
# segments drawn are exactly the same ones (roads have round caps and joins, so a joined line
# looks as the pieces did); the text is under half the size.
LINE_LAYERS = ('motorway', 'primary', 'secondary', 'rail', 'river', 'canal')
def _n(t):
    s = ('-' if t < 0 else '') + (str(abs(t) // 10) if abs(t) >= 10 else '') + ('.' + str(abs(t) % 10) if abs(t) % 10 else '')
    return s if s not in ('', '-') else '0'
def _join(lines):
    """Join open lines that meet end to end. Only where exactly two ends meet: at a junction of
    three or more, which two to join would be a guess, and they are left as they are."""
    ends = {}
    for i, l in enumerate(lines):
        ends.setdefault(l[0], []).append(i); ends.setdefault(l[-1], []).append(i)
    used, out = [False] * len(lines), []
    for i, l in enumerate(lines):
        if used[i]:
            continue
        used[i] = True
        cur = list(l)
        for tail in (True, False):
            while True:
                pt = cur[-1] if tail else cur[0]
                free = [j for j in ends[pt] if not used[j]]
                if len(free) != 1 or len(ends[pt]) != 2:
                    break
                nxt = lines[free[0]]; used[free[0]] = True
                if tail: cur += nxt[1:] if nxt[0] == pt else nxt[-2::-1]
                else:    cur = (nxt[:-1] if nxt[-1] == pt else nxt[:0:-1]) + cur
        out.append(cur)
    return out
def pack_path(d, join):
    if not d or not re.fullmatch(r'[MZ0-9.,\- ]*', d):
        return d                       # not the plain M x,y x,y [Z] that build_geo.py writes
    subs = []
    for part in re.findall(r'M[^M]*', d):
        nums = re.findall(r'-?\d+(?:\.\d+)?', part)
        pts = [(round(float(nums[i]) * 10), round(float(nums[i + 1]) * 10)) for i in range(0, len(nums) - 1, 2)]
        if pts:
            subs.append((pts, 'Z' in part))
    if join:
        subs = [s for s in subs if s[1]] + [(p, False) for p in _join([p for p, z in subs if not z and len(p) > 1])]
    out = []
    for pts, closed in subs:
        s, prev = 'M' + _n(pts[0][0]) + ',' + _n(pts[0][1]), pts[0]
        for k, p in enumerate(pts[1:]):
            a, b = _n(p[0] - prev[0]), _n(p[1] - prev[1]); prev = p
            s += ('l' if k == 0 else '' if a[0] == '-' else ' ') + a + ('' if b[0] == '-' else ',') + b
        out.append(s + ('Z' if closed else ''))
    return ''.join(out)
geo = json.load(open('geo.json', encoding='utf-8'))
geo = json.dumps({k: pack_path(v, k in LINE_LAYERS) if isinstance(v, str) else v for k, v in geo.items()},
                 separators=(',', ':'), ensure_ascii=True)
venues = json.load(open('venues.json', encoding='utf-8'))
ven = json.dumps(venues, separators=(',', ':'), ensure_ascii=True)
embedded = json.load(open('img/embed.json', encoding='utf-8'))
meta = json.load(open('meta.json', encoding='utf-8'))
picks = json.dumps(meta['picks'], separators=(',', ':'), ensure_ascii=True)
# Every city the engine builds, for the switcher in the title. A new city changes this list on
# every page, so it means rebuilding them all.
cities = json.dumps([{"slug": s, "name": c["name"], "live": bool(c.get("live")), "icon": city.icon(c)}
                     for s, c in ((s, city.load(s)) for s in city.slugs())],
                    separators=(',', ':'), ensure_ascii=True)

# The two typefaces, both under the SIL Open Font License (engine/fonts). The website loads them
# from one fonts/ folder beside the cities (../fonts/ from a city's page), so no visitor's browser
# calls a font service and a visitor who swaps cities does not fetch them again; the Artifact is
# one file, so it carries them inline and leaves out the extended-Latin file it rarely needs.
LATIN = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,"
         "U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")
LATIN_EXT = ("U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,"
             "U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF")
FONTS = [("Inter Tight", "100 900", "inter-tight-latin-wght-normal.woff2", LATIN, True),
         ("Inter Tight", "100 900", "inter-tight-latin-ext-wght-normal.woff2", LATIN_EXT, False),
         ("IBM Plex Mono", "400", "ibm-plex-mono-latin-400-normal.woff2", LATIN, True),
         ("IBM Plex Mono", "500", "ibm-plex-mono-latin-500-normal.woff2", LATIN, True)]
def fontfaces(inline, up="../"):
    out = []
    for family, weight, name, span, core in FONTS:
        if inline and not core:
            continue
        path = os.path.join(city.ENGINE, "fonts", name)
        src = ("data:font/woff2;base64," + base64.b64encode(open(path, "rb").read()).decode()) if inline else f"{up}fonts/{name}"
        out.append(f"@font-face{{font-family:'{family}'; font-style:normal; font-weight:{weight}; font-display:swap; "
                   f"src:url({src}) format('woff2'); unicode-range:{span}}}")
    return "\n".join(out)
os.makedirs(os.path.join(city.ROOT, "fonts"), exist_ok=True)
for _family, _weight, _name, _span, _core in FONTS:
    shutil.copyfile(os.path.join(city.ENGINE, "fonts", _name), os.path.join(city.ROOT, "fonts", _name))
# The two files the first screen is set in, fetched before the stylesheet asks for them.
PRELOAD = ("inter-tight-latin-wght-normal.woff2", "ibm-plex-mono-latin-500-normal.woff2")

def slug_of(name):
    """A venue's name as its address, the same way slugOf() in the template makes it."""
    s = re.sub(r"[\u0300-\u036f]", "", unicodedata.normalize("NFD", name.lower()))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def stubs():
    """A small page per sauna, s/<slug>/index.html, for link previews.

    Whatever makes a preview (a chat app, a social network) fetches the address and reads its Open
    Graph tags without running any script and without ever seeing what follows a #. So a link to
    one sauna on the map cannot preview as that sauna. These pages can: each carries the sauna's
    name, a line about it and its picture (og/<slug>.jpg, drawn by engine/og.js --venues, or the
    city's own share image until that exists), and sends a person straight on to the map with the
    sauna picked. The page's "share" button hands out these addresses."""
    SITE, cur = CITY['site'], CITY.get('currency', '€')
    shutil.rmtree("s", ignore_errors=True)
    seen = {}
    for v in venues:
        slug = slug_of(v["name"])
        assert slug and slug not in seen, f"{v['name']} and {seen.get(slug)} would share the address {slug!r}"
        seen[slug] = v["name"]
        own = os.path.isfile(os.path.join("og", slug + ".jpg"))
        image = f"{SITE}og/{slug}.jpg" if own else f"{SITE}og.png"
        title = text(f"{v['name']} · Sauna Map {NAME}")
        line = f"{v['kind']} in {v['district']}" if v.get('district') else v['kind']
        if v.get('price') is not None:
            line += f", from {cur}{v['price']:g}"
        desc = text(f"{line}. Hours, prices and heat on the sauna map of {NAME}.")
        to = f"../../#{slug}"
        page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                f'<title>{title}</title>\n'
                f'<meta name="description" content="{desc}">\n'
                '<meta name="robots" content="noindex, follow">\n'
                f'<link rel="canonical" href="{SITE}">\n'
                '<meta property="og:type" content="website">\n'
                f'<meta property="og:site_name" content="{text("Sauna Map " + NAME)}">\n'
                f'<meta property="og:title" content="{title}">\n'
                f'<meta property="og:description" content="{desc}">\n'
                f'<meta property="og:url" content="{SITE}s/{slug}/">\n'
                f'<meta property="og:image" content="{image}">\n'
                '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
                '<meta name="twitter:card" content="summary_large_image">\n'
                f'<meta name="twitter:title" content="{title}">\n'
                f'<meta name="twitter:description" content="{desc}">\n'
                f'<meta name="twitter:image" content="{image}">\n'
                f'<script>location.replace("{to}")</script>\n'
                '</head>\n<body>\n'
                f'<p><a href="{to}">{text(v["name"])} on the sauna map of {text(NAME)}</a></p>\n'
                '</body>\n</html>\n')
        assert page.isascii()
        os.makedirs(os.path.join("s", slug), exist_ok=True)
        open(os.path.join("s", slug, "index.html"), "w", encoding="ascii").write(page)
    print(f"s/: {len(seen)} link-preview pages, {sum(os.path.isfile(os.path.join('og', s + '.jpg')) for s in seen)} with their own picture")

def assemble(TPL, OUT):
    artifact = OUT.endswith('artifact.html')
    tpl = open(os.path.join(city.ENGINE, TPL), encoding='utf-8').read()

    # split on <script> blocks so each half gets the right escaping
    parts, out = re.split(r'(<script>.*?</script>)', tpl, flags=re.S), []
    for p in parts:
        out.append(jsesc(p) if p.startswith('<script>') else ent(p))
    doc = ''.join(out)

    # The Artifact is one self-contained file, so it gets the photos inlined. The
    # website has a file system, so there the same photos are served as files and
    # the page shrinks from ~900 KB to ~500 KB; the <img> tags are already lazy.
    images = embedded if artifact else {k: dict(v, src=f'img/card/{k}.webp') for k, v in embedded.items()}
    img = json.dumps(images, separators=(',', ':'), ensure_ascii=True)
    doc = (doc.replace('/*__GEO__*/', geo).replace('/*__VENUES__*/', ven)
              .replace('/*__IMAGES__*/', img).replace('/*__PICKS__*/', picks)
              .replace('/*__REVIEWERS__*/', json.dumps(meta['reviewers'], separators=(',', ':'), ensure_ascii=True))
              .replace('/*__TRAPS__*/', json.dumps(meta['traps'], separators=(',', ':'), ensure_ascii=True))
              .replace('__LAST_SCAN__', meta['lastCheckedStamp'])
              # PRACTICAL is one string in the city's venues.py, shared with Notion; its
              # **bold** becomes <strong> here and its non-ASCII becomes entities.
              .replace('__PRACTICAL__', ent(re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', meta['practical'])))
              .replace('__COUNT__', str(meta['count']))
              # What makes this page one city's and not another's (city.json).
              .replace('__CITY_LC__', text(NAME.lower())).replace('__CITY__', text(NAME))
              .replace('__LEDE__', text(CITY['lede']))
              .replace('__TZ__', CITY['timezone'])
              .replace('__CUR__', jsesc(CITY.get('currency', '€')))
              .replace('__USC__', 'true' if CITY.get('usc') else 'false')
              .replace('__TU__', 'F' if CITY.get('temp') == 'F' else 'C')
              .replace('/*__COVER__*/', json.dumps(meta['cover'], separators=(',', ':'), ensure_ascii=True))
              .replace('/*__FONTFACES__*/', fontfaces(artifact))
              .replace('__APPICON__', city.icon(CITY)).replace('/*__CITIES__*/', cities).replace('__SLUG__', CITY['slug'])
              .replace('__SIBLINGS__', 'false' if artifact else 'true')
              # The about page sits beside the map on the website; the Artifact is one file, so
              # there the link goes out to the published one.
              .replace('__ABOUT__', f'href="{CITY["site"]}about/" target="_blank" rel="noopener noreferrer"' if artifact else 'href="about/"')
              .replace('/*__CONTRIBUTORS__*/', json.dumps(meta['contributors'], separators=(',', ':'), ensure_ascii=True))
              .replace('__HUB__', city.HUB).replace('__REPO__', city.REPO))
    for token in ('__LAST_SCAN__', '__COUNT__', '__PRACTICAL__', '__CITY', '__LEDE__', '__TZ__', '__CUR__', '__USC__', '__TU__',
                  '__HUB__', '__REPO__', '__SLUG__', '__SIBLINGS__', '__ABOUT__', '__APPICON__', '/*__'):
        assert token not in doc, f"unfilled placeholder {token}"
    assert doc.isascii(), "non-ascii survived"
    if not artifact:
        doc = document(doc)
    open(OUT, 'w', encoding='ascii').write(doc)
    print(f"{TPL} -> {CITY['slug']}/{OUT}: {len(doc)/1024:.0f} KB, pure ASCII")

def tab_icon():
    """The app icon from the header, as the tab icon: steam rising beside the city's landmark."""
    return ('data:image/svg+xml,' +
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#E9A462"/><stop offset="1" stop-color="#B3502A"/></linearGradient></defs>'
            '<rect width="64" height="64" rx="15" fill="url(#g)"/>'
            + city.icon(CITY) +
            '</svg>').replace('"', "'").replace('<', '%3C').replace('>', '%3E').replace('#', '%23')

def about():
    """about/index.html: everything the map page does not need to say itself.

    Whose guide this is, where the data and the map come from, the city's own notes and traps,
    who adds listings, and the photo credits. The map page links here from its footer and keeps
    one line of attribution. The colours are the template's own tokens, cut out of it here, so
    the two pages cannot drift apart."""
    tpl = open(os.path.join(city.ENGINE, 'template.html'), encoding='utf-8').read()
    tokens = tpl[tpl.index(':root{'):tpl.index('*{box-sizing:border-box}')]
    bold = lambda t: re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html.escape(t, quote=False))
    by_name = {v['name']: v for v in venues}
    notes, script = '', ''
    if meta['practical'].strip() or meta['traps']:
        ps = [f"<p>{bold(meta['practical'])}</p>"] if meta['practical'].strip() else []
        for name, said in meta['traps']:
            v = by_name.get(name)
            if not v:
                continue
            # A closure date is never prose: the browser adds it while it is in force (see TRAPS).
            until = (v.get('open') or {}).get('closedUntil')
            ps.append(f"<p{f' data-until={chr(34)}{until}{chr(34)}' if until else ''}><strong>{html.escape(name)}</strong>"
                      f"{'' if said.startswith(chr(0x2019)) else ' '}{html.escape(said, quote=False)}</p>")
        notes = f"    <div><dt>before you go</dt><dd>{''.join(ps)}</dd></div>\n"
        script = ('<script>\n(() => { const today = new Intl.DateTimeFormat("en-CA", { timeZone: "' + CITY['timezone'] + '" }).format(new Date());\n'
                  '  const M = ["January","February","March","April","May","June","July","August","September","October","November","December"];\n'
                  '  document.querySelectorAll("[data-until]").forEach(p => { const u = p.dataset.until, [y, m, d] = u.split("-").map(Number);\n'
                  '    if (today <= u) p.append(` It is on break until ${d} ${M[m - 1]} ${y}.`); }); })();\n</script>\n')
    credits = ''
    for v in venues:
        im = embedded.get(v.get('img') or '')
        if not im:
            continue
        credits += (f"        <li><b>{html.escape(v['name'])}</b>, photo by {html.escape(im['by'])}, "
                    f"<a href=\"{html.escape(im['page'])}\" target=\"_blank\" rel=\"noopener noreferrer\">{html.escape(im['lic'])}</a></li>\n"
                    if im.get('lic') else
                    f"        <li><b>{html.escape(v['name'])}</b>, sent in by {html.escape(im.get('by') or 'a visitor')}</li>\n")
    people = ', '.join(f'<a href="https://github.com/{h}" target="_blank" rel="noopener noreferrer">@{html.escape(h)}</a>' for h in meta['contributors'])
    doc = open(os.path.join(city.ENGINE, 'about.html'), encoding='utf-8').read()
    for k, val in (('/*__FONTFACES__*/', fontfaces(False, '../../')), ('/*__TOKENS__*/', tokens),
                   ('__NOTES__', notes), ('__CREDITS__', credits), ('__SCRIPT__', script), ('__CONTRIBUTORS__', people),
                   ('__USC_TERMS__', ' and Urban Sports Club term' if CITY.get('usc') else ''),
                   ('__LAST_SCAN__', meta['lastCheckedStamp']), ('__ICON__', tab_icon()), ('__SITE__', CITY['site']),
                   ('__CITY_LC__', text(NAME.lower())), ('__CITY__', text(NAME)), ('__HUB__', city.HUB), ('__REPO__', city.REPO)):
        doc = doc.replace(k, val)
    doc = ent(doc)
    assert '__' not in re.sub(r'data:[^"\')]+', '', doc), "unfilled placeholder in about.html"
    assert doc.isascii()
    os.makedirs('about', exist_ok=True)
    open(os.path.join('about', 'index.html'), 'w', encoding='ascii').write(doc)
    print(f"about.html -> {CITY['slug']}/about/index.html: {len(doc)/1024:.0f} KB")

def document(doc):
    head, sep, body = doc.partition('</style>')
    assert sep, "template must contain a </style> to split on"
    # The public address. GitHub Pages builds and serves the page; jommi.fi/sauna/<city>/ is the
    # same page passed through the jommi.fi Worker, and it is the one links and search should use.
    SITE = CITY['site']
    TITLE = text(f"Sauna Map {NAME}")
    PLAIN = f"{meta['count']} {NAME} saunas and spas, priced and plotted on one map, with a Finn's notes on the loyly."
    DESC = text(PLAIN)
    icon = tab_icon()
    # Structured data: the list of places, so a search engine sees twenty named
    # venues with coordinates rather than one opaque page.
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": f"Sauna Map {NAME}",
          "url": SITE, "description": PLAIN, "numberOfItems": meta['count'],
          "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "item": {
                  "@type": "Place", "name": v["name"],
                  "url": v.get("url") or SITE,
                  "address": {"@type": "PostalAddress", "addressLocality": NAME,
                              "addressCountry": CITY['country']},
                  "geo": {"@type": "GeoCoordinates", "latitude": v["lat"], "longitude": v["lon"]}}}
              for i, v in enumerate(venues)]}
    ldjson = json.dumps(ld, separators=(',', ':'), ensure_ascii=True).replace('</', '<\\/')
    return ('<!doctype html>\n<html lang="en">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="theme-color" content="#F2F1EE" media="(prefers-color-scheme: light)">\n'
            '<meta name="theme-color" content="#0E0F11" media="(prefers-color-scheme: dark)">\n'
            '<meta name="color-scheme" content="light dark">\n'
            f'<meta name="description" content="{DESC}">\n'
            f'<link rel="canonical" href="{SITE}">\n'
            f'<link rel="icon" href="{icon}">\n'
            + ''.join(f'<link rel="preload" href="../fonts/{f}" as="font" type="font/woff2" crossorigin>\n' for f in PRELOAD) +
            '<meta property="og:type" content="website">\n'
            f'<meta property="og:site_name" content="{TITLE}">\n'
            f'<meta property="og:title" content="{TITLE}">\n'
            f'<meta property="og:description" content="{DESC}">\n'
            f'<meta property="og:url" content="{SITE}">\n'
            f'<meta property="og:image" content="{SITE}og.png">\n'
            '<meta property="og:image:width" content="1200">\n'
            '<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="A map of central {text(NAME)} with sauna locations marked as flame blips">\n'
            '<meta property="og:locale" content="en_GB">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:title" content="{TITLE}">\n'
            f'<meta name="twitter:description" content="{DESC}">\n'
            f'<meta name="twitter:image" content="{SITE}og.png">\n'
            + head + sep + '\n'
            f'<script type="application/ld+json">{ldjson}</script>\n'
            '</head>\n<body>\n' + body.lstrip() + '\n</body>\n</html>\n')

if len(sys.argv) == 3:
    assemble(sys.argv[1], sys.argv[2])
elif len(sys.argv) == 1:
    assemble('template.html', 'index.html')
    assemble('template.html', 'artifact.html')
    stubs()
    about()
else:
    raise SystemExit("usage: assemble.py <city> [<template> <out>]")
