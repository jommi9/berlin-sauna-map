import json, math
vs = json.load(open('venues.json'))
MIN = 27.0          # min centre-to-centre distance (blips are 22 units wide)
for v in vs: v['px'], v['py'] = v['x'], v['y']
for _ in range(400):
    moved = 0.0
    for i in range(len(vs)):
        for j in range(i+1, len(vs)):
            a, b = vs[i], vs[j]
            dx, dy = b['px']-a['px'], b['py']-a['py']
            d = math.hypot(dx, dy)
            if d < 1e-6: dx, dy, d = 0.6, -0.4, 0.72
            if d < MIN:
                push = (MIN - d) / 2 * 0.55
                ux, uy = dx/d, dy/d
                a['px'] -= ux*push; a['py'] -= uy*push
                b['px'] += ux*push; b['py'] += uy*push
                moved += push
    # spring back toward true location so pins stay honest
    for v in vs:
        v['px'] += (v['x']-v['px'])*0.06
        v['py'] += (v['y']-v['py'])*0.06
    if moved < 0.01: break

worst = 0
for v in vs:
    v['px'] = round(v['px'],1); v['py'] = round(v['py'],1)
    off = math.hypot(v['px']-v['x'], v['py']-v['y'])
    v['off'] = round(off,1)
    worst = max(worst, off)
mind = min(math.hypot(a['px']-b['px'], a['py']-b['py']) for i,a in enumerate(vs) for b in vs[i+1:])
print(f"max displacement {worst:.1f} units (~{worst/1000*100:.1f}% of map width) | min pin gap {mind:.1f}")
for v in sorted(vs, key=lambda v:-v['off'])[:5]: print(f"  {v['off']:5.1f}  {v['name']}")
json.dump(vs, open('venues.json','w'), separators=(',',':'), ensure_ascii=False)
