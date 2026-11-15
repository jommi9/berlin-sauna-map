// Take a city's share image, <city>/og.png: its map full-bleed at 1200x630 with the page's own hero
// laid over it as a frosted card, the way berlin/og.png is composed. Uses the Playwright that cloud
// sessions have preinstalled. Serve the repository first:
//
//   python3 -m http.server 8765 &
//   node engine/og.js helsinki nyc sf
//
// Retake it when the header or the venues change. Berlin's own og.png has a photo collage and was
// taken by hand; this does not reproduce that.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const city of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1, colorScheme: 'light' });
    await p.goto(`http://localhost:8765/${city}/`, { waitUntil: 'networkidle' });
    await p.waitForTimeout(400);
    await p.evaluate(() => {
      const wrap = document.getElementById('wrap');
      const map = document.getElementById('map').cloneNode(true);
      // venues fitted into the right-hand part of the image (x 660..1170), the card on the left
      const [ex, ey, ew, eh] = EXTENT;
      let u = Math.max(ew / 510, eh / 560) * 1.08;              // map units per image pixel
      u = Math.min(u, GEO.w / 1200, GEO.h / 630);                // never wider or taller than the map
      const w = 1200 * u, h = 630 * u;
      let x0 = ex + ew / 2 - 915 * u, y0 = ey + eh / 2 - 315 * u;
      x0 = Math.max(0, Math.min(GEO.w - w, x0)); y0 = Math.max(0, Math.min(GEO.h - h, y0));
      map.setAttribute('viewBox', `${x0} ${y0} ${w} ${h}`);
      const k = Math.max(1, u * 1.25);
      map.querySelectorAll('.blip').forEach(g => g.setAttribute('transform', g.getAttribute('transform').replace(/\s*scale\([^)]*\)/, '') + ` scale(${k})`));
      map.querySelectorAll('.callout, .scalebar').forEach(n => n.remove());
      Object.assign(map.style, { position: 'fixed', left: 0, top: 0, width: '1200px', height: '630px', background: 'var(--land)', borderRadius: 0 });
      const hero = document.querySelector('header.top');
      hero.querySelectorAll('.stats').forEach(n => n.remove());
      wrap.innerHTML = '';
      wrap.appendChild(map);
      const card = document.createElement('div');
      Object.assign(card.style, { position: 'fixed', left: '44px', top: '52px', width: '590px', boxSizing: 'border-box',
        padding: '44px 34px 40px', borderRadius: '22px', background: 'rgba(246,245,242,.86)',
        backdropFilter: 'blur(14px)', boxShadow: '0 18px 50px rgba(0,0,0,.12)' });
      card.appendChild(hero);
      hero.style.margin = '0'; hero.style.padding = '0'; hero.style.display = 'block';
      hero.querySelectorAll('.collage').forEach(n => n.remove());
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
