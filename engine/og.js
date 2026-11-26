// Take a city's share image, <city>/og.png: its map full-bleed at 1200x630 with the page's own hero
// laid over it as a frosted card, the way berlin/og.png is composed. Uses the Playwright that cloud
// sessions have preinstalled. Serve the repository first:
//
//   python3 -m http.server 8765 &
//   node engine/og.js helsinki nyc sf
//
// Retake it when the header or the venues change. A city whose header has a photo collage (Berlin)
// gets a card the width of the image with the collage in it, and its venues in the strip below.
//
//   node engine/og.js --venues berlin sf
//
// draws a picture per sauna instead, <city>/og/<slug>.jpg, for the link-preview pages assemble.py
// writes (s/<slug>/): the sauna's name, kind and district beside its photograph, or beside the map
// around its pin where it has none. Run it after a venue is added or renamed, or gets a photo, and
// rebuild so the preview pages point at the new pictures. Nothing a self-update changes (a price,
// an opening hour) is in the picture, so it does not go stale between runs.
const { chromium } = require('playwright');
const fs = require('fs');

async function venues(b, city) {
  const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1, colorScheme: 'light' });
  await p.goto(`http://localhost:8765/${city}/`, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const list = await p.evaluate(() => V.map(v => ({ id: v.id, slug: slugOf(v) })));
  fs.mkdirSync(`${city}/og`, { recursive: true });
  for (const f of fs.readdirSync(`${city}/og`)) if (!list.some(v => v.slug + '.jpg' === f)) fs.unlinkSync(`${city}/og/${f}`);
  for (const { id, slug } of list) {
    await p.evaluate(id => {
      const v = V.find(x => x.id === id);
      if (sel !== id) choose(id, true);
      document.getElementById('og-card')?.remove();
      const card = document.createElement('div');
      card.id = 'og-card';
      Object.assign(card.style, { position: 'fixed', inset: 0, zIndex: 9999, background: 'var(--bg)', display: 'grid',
        gridTemplateColumns: '600px 600px', color: 'var(--label)', fontFamily: 'var(--font)' });
      const size = v.name.length <= 12 ? 104 : v.name.length <= 20 ? 84 : v.name.length <= 30 ? 68 : 56;
      const esc = t => String(t).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
      const mono = 'font:500 15px/1.5 var(--mono); letter-spacing:.14em; text-transform:uppercase';
      const heat = v.hot == null ? '' : `<span style="color:var(--hot)">${fmtT(v.hot)}</span>` + (v.plunge != null ? ` <span style="color:var(--label-3)">/</span> <span style="color:var(--cold)">${fmtT(v.plunge)}</span>` : '');
      card.innerHTML = `
        <div style="position:relative; padding:84px 44px 50px 56px; display:flex; flex-direction:column; min-width:0; background:var(--bg)">
          <div style="position:absolute; left:0; right:0; top:0; height:56px; background:var(--bark) repeat-x 0 -8px / auto 150px; opacity:.55; -webkit-mask-image:linear-gradient(#000 40%, transparent)"></div>
          <p style="margin:0; ${mono}; color:var(--label-2)">sauna map <span style="color:var(--label)">${esc(document.querySelector('.city-b').textContent.trim())}</span></p>
          <h1 style="margin:auto 0 22px; font:300 ${size}px/.96 var(--font-display); letter-spacing:-.035em; overflow-wrap:break-word">${esc(v.name)}</h1>
          <p style="margin:0; ${mono}">${esc(v.kind)}${v.district ? ' <span style="color:var(--label-3)">/</span> ' + esc(v.district) : ''}</p>
          <div style="margin-top:26px; height:3px; background:linear-gradient(90deg, var(--cold), var(--cool), var(--mild), var(--warm), var(--hot))"></div>
          <p style="margin:12px 0 0; display:flex; justify-content:space-between; ${mono}; color:var(--label-2)"><span>${heat || 'cold plunge'}</span><span>${heat ? '' : 'hot stones'}</span></p>
        </div>
        <div id="og-pic" style="position:relative; overflow:hidden; background:var(--land); border-left:1px solid var(--label)"></div>`;
      document.body.appendChild(card);
      const pic = card.querySelector('#og-pic'), img = v.img && IMG[v.img];
      if (img) {
        pic.innerHTML = `<img src="${img.src}" alt="" style="width:100%; height:100%; object-fit:cover; display:block">`;
      } else {
        const map = document.getElementById('map').cloneNode(true);
        map.removeAttribute('id');
        const u = Math.min(GEO.w * 0.34 / 600, GEO.w / 600, GEO.h / 630), w = 600 * u, h = 630 * u;
        const x0 = Math.max(0, Math.min(GEO.w - w, v.x - w / 2)), y0 = Math.max(0, Math.min(GEO.h - h, v.y - h / 2));
        map.setAttribute('viewBox', `${x0} ${y0} ${w} ${h}`);
        const k = Math.max(1, u * 1.5);
        map.querySelectorAll('.blip').forEach(g => {
          g.setAttribute('transform', g.getAttribute('transform').replace(/\s*scale\([^)]*\)/, '') + ` scale(${g.classList.contains('on') ? k * 1.5 : k})`);
          if (!g.classList.contains('on')) g.style.opacity = '.45';
        });
        map.querySelectorAll('.callout, .scalebar').forEach(n => n.remove());
        Object.assign(map.style, { position: 'absolute', inset: 0, width: '600px', height: '630px', background: 'var(--land)' });
        pic.appendChild(map);
      }
    }, id);
    await p.evaluate(() => Promise.all([...document.querySelectorAll('#og-card img')].map(i => i.decode().catch(() => {}))));
    await p.screenshot({ path: `${city}/og/${slug}.jpg`, type: 'jpeg', quality: 84 });
  }
  await p.close();
  console.log(`${city}/og: ${list.length} pictures`);
}

(async () => {
  const b = await chromium.launch();
  const args = process.argv.slice(2);
  if (args[0] === '--venues') {
    for (const city of args.slice(1)) await venues(b, city);
    await b.close();
    return;
  }
  for (const city of args) {
    const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1, colorScheme: 'light' });
    await p.goto(`http://localhost:8765/${city}/`, { waitUntil: 'networkidle' });
    // The page keeps its header short so the map starts on the first screen. A share image has no
    // map to make room for, so it gets the header at full size, photographs included.
    await p.addStyleTag({ content: `
      .title{font-size:clamp(54px,9.6vw,150px) !important; margin-top:10px !important}
      .intro{grid-template-columns:minmax(0,1fr) minmax(0,1.1fr) !important; gap:10px 48px !important}
      .intro .brand{grid-column:1 / -1 !important; grid-row:auto !important}
      .lede{display:block !important; grid-column:auto !important; grid-row:auto !important; font-size:17px !important; max-width:44ch !important; margin:18px 0 0 !important}
      .collage{display:block !important}` });
    await p.waitForTimeout(400);
    await p.evaluate(() => {
      const wrap = document.getElementById('wrap');
      const map = document.getElementById('map').cloneNode(true);
      const photos = document.querySelectorAll('header.top .collage .snap').length > 0;
      // venues fitted into the right-hand part of the image (x 660..1170), the card on the left;
      // with a collage the card is the full width, so they go in the strip under it (y 380..610)
      let [ex, ey, ew, eh] = EXTENT;
      const most = Math.min(GEO.w / 1200, GEO.h / 630);          // never wider or taller than the map
      const need = () => (photos ? Math.max(ew / 1100, eh / 230) : Math.max(ew / 510, eh / 560)) * 1.08;   // map units per image pixel
      const far = !photos && need() > most * 2;
      if (far) {
        // The venues are spread over more than twice the map that fits beside the card (a tall
        // frame, as San Francisco's is with the East Bay in it), so a slice of the whole would be
        // mostly empty. Show where most of them are: the six in ten nearest the middle one.
        const mid = a => a.slice().sort((p, q) => p - q)[Math.floor(a.length / 2)];
        const mx = mid(V.map(v => v.x)), my = mid(V.map(v => v.y));
        const core = V.slice().sort((a, b) => Math.hypot(a.x - mx, a.y - my) - Math.hypot(b.x - mx, b.y - my)).slice(0, Math.ceil(V.length * 0.6));
        ex = Math.min(...core.map(v => v.x)); ey = Math.min(...core.map(v => v.y));
        ew = Math.max(...core.map(v => v.x)) - ex; eh = Math.max(...core.map(v => v.y)) - ey;
      }
      const u = Math.min(need(), most);
      const w = 1200 * u, h = 630 * u;
      const clampX = x => Math.max(0, Math.min(GEO.w - w, x));
      // The card is on the left with the venues to its right. Where that would leave them under the
      // card (they sit near the map's left edge, and the picture cannot show what is west of the
      // map), the card goes on the right if that hides less.
      const hidden = (x0, from, to) => V.filter(v => { const px = (v.x - x0) / u; return px > from && px < to; }).length;
      const xl = clampX(ex + ew / 2 - 915 * u), xr = clampX(ex + ew / 2 - 285 * u);
      const right = far && hidden(xr, 566, 1156) < hidden(xl, 44, 634);
      let x0 = photos ? clampX(ex + ew / 2 - 600 * u) : right ? xr : xl, y0 = ey + eh / 2 - (photos ? 495 : 315) * u;
      y0 = Math.max(0, Math.min(GEO.h - h, y0));
      map.setAttribute('viewBox', `${x0} ${y0} ${w} ${h}`);
      const k = Math.max(1, u * 1.25);
      map.querySelectorAll('.blip').forEach(g => g.setAttribute('transform', g.getAttribute('transform').replace(/\s*scale\([^)]*\)/, '') + ` scale(${k})`));
      map.querySelectorAll('.callout, .scalebar').forEach(n => n.remove());
      Object.assign(map.style, { position: 'fixed', left: 0, top: 0, width: '1200px', height: '630px', background: 'var(--land)', borderRadius: 0 });
      const hero = document.querySelector('header.top');
      hero.querySelectorAll('.stats').forEach(n => n.remove());
      hero.querySelectorAll('.city-m').forEach(n => n.remove());                // a picture has no switcher,
      hero.querySelectorAll('.city-b').forEach(b => b.replaceWith(b.textContent));   // so the city is plain text
      wrap.innerHTML = '';
      wrap.appendChild(map);
      const card = document.createElement('div');
      Object.assign(card.style, { position: 'fixed', left: right ? '566px' : '44px', top: '52px', width: photos ? '1112px' : '590px', boxSizing: 'border-box',
        padding: photos ? '30px 34px 30px' : '44px 34px 40px', borderRadius: '0', background: 'rgba(255,255,255,.9)',
        backdropFilter: 'blur(14px)', boxShadow: '0 18px 50px rgba(0,0,0,.12)' });
      card.appendChild(hero);
      hero.style.margin = '0'; hero.style.padding = '0';
      if (photos) hero.style.gridTemplateColumns = 'minmax(0,1fr) 410px';
      else { hero.style.display = 'block'; hero.querySelectorAll('.collage').forEach(n => n.remove()); }
      hero.querySelectorAll('.intro, .lede').forEach(n => { n.style.maxWidth = 'none'; n.style.width = '100%'; });
      wrap.appendChild(card);
      document.querySelectorAll('.eyebrow .crumb').forEach(a => { a.nextSibling.textContent = a.nextSibling.textContent.replace(/^\s*\/\s*/, ''); a.remove(); });
      document.body.style.overflow = 'hidden';
    });
    await p.waitForTimeout(200);
    await p.screenshot({ path: `${city}/og.png` });
    await p.close();
  }
  await b.close();
})();
