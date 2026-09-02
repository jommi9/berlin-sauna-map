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
ven = json.dumps(json.load(open('venues.json', encoding='utf-8')), separators=(',', ':'), ensure_ascii=True)
img = json.dumps(json.load(open('img/embed.json', encoding='utf-8')), separators=(',', ':'), ensure_ascii=True)
doc = doc.replace('/*__GEO__*/', geo).replace('/*__VENUES__*/', ven).replace('/*__IMAGES__*/', img)
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
    page = ('<!doctype html>\n<html lang="en">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="theme-color" content="#0A0D0F">\n'
            '<meta name="description" content="Twenty Berlin saunas and spas, priced and plotted as an open-world game atlas.">\n'
            + head + sep + '\n</head>\n<body>\n' + body.lstrip() + '\n</body>\n</html>\n')
    open(OUT, 'w', encoding='ascii').write(page)
    doc = page
print(f"{TPL} -> {OUT}: {len(doc)/1024:.0f} KB, pure ASCII")
