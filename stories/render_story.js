// Renders the daily "LIST IT FREE" Instagram Story (1080x1920) from a
// background photo. Usage:
//   node render_story.js <background.jpg|png> <machine> <out.png>
// The Graph API cannot add link stickers, so (Alan's pick, 2026-11-08) the
// sticker line is printed on the image with the URL under it, not tappable.
// Writes JPEG when <out> ends in .jpg (Instagram's image_url needs JPEG).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const [bg, machineRaw, out] = process.argv.slice(2);
if (!bg || !machineRaw || !out) {
  console.error('usage: node render_story.js <bg> <machine> <out.jpg|png>');
  process.exit(2);
}
const machine = machineRaw.toLowerCase();

// Template texts: character-for-character, approved by Alan 2026-11-08.
const HEADLINE = 'LIST IT FREE';
const BODY = `That ${machine} in the yard is worth money. Snap a photo — AI drafts the listing.`;
const STICKER = 'List yours free on YardSwaps';
const URL_TEXT = 'yardswaps.com/sell-equipment';
const FOOTER = 'No commission · Local pickup · yardswaps.com';

const ext = path.extname(bg).slice(1).replace('jpg', 'jpeg');
const bgData = `data:image/${ext};base64,${fs.readFileSync(bg).toString('base64')}`;
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

const html = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600&family=Space+Grotesk:wght@700&display=block" rel="stylesheet">
<style>
  * { margin: 0; box-sizing: border-box; }
  body { width: 1080px; height: 1920px; overflow: hidden; font-family: 'Inter', sans-serif; background: #1A3353; }
  /* Backdrop: the same photo, blurred, so the frame is full without zooming into the machine. */
  .bg { position: absolute; inset: -60px; background: url(${bgData}) center/cover; filter: blur(36px); transform: scale(1.08); }
  .shade { position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(14,34,64,0.70) 0%, rgba(14,34,64,0.45) 40%,
      rgba(14,34,64,0.45) 70%, rgba(14,34,64,0.80) 100%); }
  .top { position: absolute; top: 190px; left: 70px; right: 70px; text-align: center; color: #fff; }
  h1 { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 140px; line-height: 0.95;
       letter-spacing: -2px; text-shadow: 0 6px 30px rgba(0,0,0,0.45); }
  .body { margin: 28px auto 0; max-width: 900px; font-size: 46px; line-height: 1.22; font-weight: 600;
          text-shadow: 0 3px 18px rgba(0,0,0,0.6); }
  /* The machine: the whole photo below the empty sky, never cropped at the sides, never under text. */
  .card { position: absolute; left: 50%; transform: translateX(-50%); border-radius: 28px; overflow: hidden;
          box-shadow: 0 24px 60px rgba(0,0,0,0.45); border: 4px solid rgba(255,255,255,0.9); }
  .card img { display: block; position: absolute; left: 0; width: 100%; }
  .cta { position: absolute; left: 70px; right: 70px; text-align: center; color: #fff;
         padding: 22px 24px; border-radius: 28px; background: rgba(14,34,64,0.80);
         text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
  .cta-1 { font-size: 50px; font-weight: 600; }
  .cta-2 { margin-top: 6px; font-size: 44px; font-weight: 600; color: #FFBE18; }
  .footer { position: absolute; left: 60px; right: 60px; text-align: center; color: #fff;
            font-size: 36px; font-weight: 500; text-shadow: 0 2px 12px rgba(0,0,0,0.7); }
</style></head><body>
<div class="bg"></div><div class="shade"></div>
<div class="top"><h1>${esc(HEADLINE)}</h1><p class="body">${esc(BODY)}</p></div>
<div class="card"><img src="${bgData}"></div>
<div class="cta"><div class="cta-1">${esc(STICKER)}</div><div class="cta-2">${esc(URL_TEXT)}</div></div>
<div class="footer">${esc(FOOTER)}</div>
</body></html>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  // Fit the photo card between the text and the link box (Nov 9: Alan saw machines cut off and
  // the link box sitting on the machine). The card shows the photo at full width from 15% down
  // (the bank prompt keeps the top third as empty sky; the tallest machine in the bank starts at
  // 20%) to the bottom, so nothing at the sides, top or bottom of the machine is cropped.
  const box = await page.evaluate(async () => {
    const img = document.querySelector('.card img');
    await img.decode();
    const top = 0.15, bottom = 0.98;
    const textBottom = document.querySelector('.top').getBoundingClientRect().bottom;
    const y0 = textBottom + 36, ctaH = document.querySelector('.cta').offsetHeight;
    const footH = document.querySelector('.footer').offsetHeight;
    const yMax = 1715 - footH - 18 - ctaH - 30;   // footer must end above Instagram's reply bar
    const maxH = yMax - y0, maxW = 960;
    const aspect = img.naturalWidth / (img.naturalHeight * (bottom - top));
    let h = maxH, w = h * aspect;
    if (w > maxW) { w = maxW; h = w / aspect; }
    const card = document.querySelector('.card');
    Object.assign(card.style, { top: y0 + (maxH - h) / 2 + 'px', width: w + 'px', height: h + 'px' });
    Object.assign(img.style, { top: (-top * img.naturalHeight * w / img.naturalWidth) + 'px' });
    const cardBottom = y0 + (maxH - h) / 2 + h;
    const cta = document.querySelector('.cta'); cta.style.top = cardBottom + 30 + 'px';
    const foot = document.querySelector('.footer'); foot.style.top = cardBottom + 30 + ctaH + 18 + 'px';
    return { top, w: Math.round(w), h: Math.round(h) };
  });
  console.error('photo card', JSON.stringify(box));
  const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family));
  if (!fonts.some(f => f.includes('Space Grotesk'))) console.error('warning: Space Grotesk did not load');
  await page.screenshot(out.endsWith('.jpg') ? { path: out, type: 'jpeg', quality: 92 } : { path: out, type: 'png' });
  await browser.close();
  console.log(JSON.stringify({ out, machine, headline: HEADLINE, body: BODY, cta: STICKER, url: URL_TEXT, footer: FOOTER }));
})();
