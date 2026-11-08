// Renders the daily "LIST IT FREE" Instagram Story (1080x1920) from a
// background photo. Usage:
//   node render_story.js <background.jpg|png> <machine> <out.png> [--preview]
// --preview draws a mock of where Instagram's link sticker goes; the file
// that gets published never contains a drawn sticker (the real one is added
// in Instagram, because the Graph API cannot add link stickers).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const [bg, machineRaw, out, flag] = process.argv.slice(2);
if (!bg || !machineRaw || !out) {
  console.error('usage: node render_story.js <bg> <machine> <out.png> [--preview]');
  process.exit(2);
}
const machine = machineRaw.toLowerCase();
const preview = flag === '--preview';

// Template texts: character-for-character, approved by Alan 2026-11-08.
const HEADLINE = 'LIST IT FREE';
const BODY = `That ${machine} in the yard is worth money. Snap a photo — AI drafts the listing.`;
const STICKER = 'List yours free on YardSwaps';
const FOOTER = 'No commission · Local pickup · yardswaps.com';

const ext = path.extname(bg).slice(1).replace('jpg', 'jpeg');
const bgData = `data:image/${ext};base64,${fs.readFileSync(bg).toString('base64')}`;
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

const html = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600&family=Space+Grotesk:wght@700&display=block" rel="stylesheet">
<style>
  * { margin: 0; box-sizing: border-box; }
  body { width: 1080px; height: 1920px; overflow: hidden; font-family: 'Inter', sans-serif; }
  .bg { position: absolute; inset: 0; background: url(${bgData}) center/cover; }
  .shade { position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(14,34,64,0.55) 0%, rgba(14,34,64,0.15) 38%,
      rgba(0,0,0,0) 55%, rgba(14,34,64,0.25) 75%, rgba(14,34,64,0.80) 100%); }
  .top { position: absolute; top: 250px; left: 80px; right: 80px; text-align: center; color: #fff; }
  h1 { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 164px; line-height: 0.95;
       letter-spacing: -2px; text-shadow: 0 6px 30px rgba(0,0,0,0.45); }
  .body { margin: 44px auto 0; max-width: 860px; font-size: 52px; line-height: 1.25; font-weight: 600;
          text-shadow: 0 3px 18px rgba(0,0,0,0.6); }
  .sticker { position: absolute; top: 1330px; left: 50%; transform: translateX(-50%);
             background: #fff; color: #2563EB; border-radius: 22px; padding: 26px 40px;
             font-size: 42px; font-weight: 600; white-space: nowrap; outline: 6px dashed #FFBE18; outline-offset: 10px; }
  .footer { position: absolute; bottom: 230px; left: 60px; right: 60px; text-align: center; color: #fff;
            font-size: 38px; font-weight: 500; text-shadow: 0 2px 12px rgba(0,0,0,0.7); }
</style></head><body>
<div class="bg"></div><div class="shade"></div>
<div class="top"><h1>${esc(HEADLINE)}</h1><p class="body">${esc(BODY)}</p></div>
${preview ? `<div class="sticker">\u{1F517} ${esc(STICKER)}</div>` : ''}
<div class="footer">${esc(FOOTER)}</div>
</body></html>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family));
  if (!fonts.some(f => f.includes('Space Grotesk'))) console.error('warning: Space Grotesk did not load');
  await page.screenshot({ path: out, type: 'png' });
  await browser.close();
  console.log(JSON.stringify({ out, machine, headline: HEADLINE, body: BODY, sticker: STICKER, footer: FOOTER, preview }));
})();
