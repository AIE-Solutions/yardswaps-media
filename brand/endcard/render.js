// Renders the end card PNGs from card.html. Run from this folder: node render.js
// Text lives in cards.json (one entry per audience). Re-run after any change and commit the PNGs.
const { chromium } = require('playwright');
const path = require('path');
const cards = require('./cards.json').cards;
const SIZES = { '9x16': [1080, 1920], '1x1': [1080, 1080], '4x5': [1080, 1350], '16x9': [1920, 1080] };
(async () => {
  const b = await chromium.launch();
  for (const [aud, c] of Object.entries(cards)) {
    for (const [ratio, [w, h]] of Object.entries(SIZES)) {
      const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
      const q = new URLSearchParams({ w, h, t1: c.line1, t2: c.line2, url: c.url });
      await p.goto('file://' + path.join(__dirname, 'card.html') + '?' + q);
      await p.evaluate(() => document.fonts.ready);
      await p.waitForTimeout(150);
      const out = path.join(__dirname, `endcard-${aud}-${ratio}.png`);
      await p.screenshot({ path: out });
      await p.close();
      console.log(out);
    }
  }
  await b.close();
})();
