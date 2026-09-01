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
open(OUT, 'w', encoding='ascii').write(doc)
print(f"{TPL} -> {OUT}: {len(doc)/1024:.0f} KB, pure ASCII")
