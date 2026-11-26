// Renders the daily seller Story (1080x1920) in the YardSwaps post look (brand/posts/kit.py, story()).
// Usage:  node render_story.js <photo.jpg|png> <machine> <out.jpg|png>
//
// Alan, 2026-11-26: "improve quality of post and imagery and branding ... looks like ai slop". Until then this
// Story was white type over an AI-made sunset yard. Now: a REAL listing photo (make_bg.py picks one the daily
// review approved), the YardSwaps tab, the headline with one blue line, and the link in a labelled box.
// Words follow MESSAGING.md (sellers: free listing first, then the AI, then no selling fee).
// The Graph API cannot add link stickers, so the link is printed, not tappable (Alan's pick, 2026-11-08).
// If <photo>.json sits next to the photo ({"credit": "Title · $1,200"}) the chip names the listing shown.
// This job checks out only stories/, so the look is drawn here in HTML; keep it in step with kit.py.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const [bg, machineRaw, out] = process.argv.slice(2);
if (!bg || !machineRaw || !out) {
  console.error('usage: node render_story.js <photo> <machine> <out.jpg|png>');
  process.exit(2);
}
const HEAD = ['Sitting idle?', '*List it free.'];
const BODY = 'Snap a photo and the AI writes the listing. No selling fee. Local pickup.';
const LABEL = 'List yours';
const URL_TEXT = 'yardswaps.com/sell-equipment';

let credit = '';
const side = bg.replace(/\.[a-z]+$/i, '.json');
if (fs.existsSync(side)) {
  try { credit = JSON.parse(fs.readFileSync(side, 'utf8')).credit || ''; } catch (e) { credit = ''; }
}
const ext = path.extname(bg).slice(1).replace('jpg', 'jpeg');
const bgData = `data:image/${ext};base64,${fs.readFileSync(bg).toString('base64')}`;
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const lines = HEAD.map((l) => (l.startsWith('*') ? `<span class="hl">${esc(l.slice(1))}</span>` : `<span>${esc(l)}</span>`)).join('');

const html = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700&family=Space+Grotesk:wght@700&display=block" rel="stylesheet">
<style>
  * { margin: 0; box-sizing: border-box; }
  body { width: 1080px; height: 1920px; overflow: hidden; background: #1A3353; color: #fff;
         font-family: 'Inter', sans-serif; position: relative; -webkit-font-smoothing: antialiased; }
  .photo { position: absolute; left: 0; top: 0; width: 100%; background: url(${bgData}) center 40%/cover no-repeat; }
  .melt { position: absolute; left: 0; width: 100%; height: 242px;
          background: linear-gradient(180deg, rgba(26,51,83,0) 0%, rgba(26,51,83,.78) 60%, #1A3353 100%); }
  .shade { position: absolute; left: 0; top: 0; width: 100%; height: 320px;
           background: linear-gradient(180deg, rgba(14,34,64,.6), rgba(14,34,64,0)); }
  /* nothing to read in the top 150 px or the bottom 340 px: Instagram's own buttons sit there */
  .tab { position: absolute; top: 150px; left: 56px; background: #fff; border-radius: 22px; padding: 17px 34px 15px;
         font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 54px; letter-spacing: -0.035em;
         line-height: 64px; color: #2563EB; box-shadow: 0 8px 28px rgba(10,24,48,.3); }
  .credit { position: absolute; top: 156px; right: 56px; max-width: 600px; background: #fff; color: #1A3353;
            border-radius: 18px; padding: 11px 22px 12px; text-align: right; font-weight: 700; font-size: 27px;
            line-height: 1.25; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .credit i { display: block; font-style: normal; font-family: 'Space Grotesk', sans-serif; font-size: 20px;
              letter-spacing: .12em; text-transform: uppercase; color: #2563EB; }
  .col { position: absolute; left: 56px; right: 56px; bottom: 370px; display: flex; flex-direction: column;
         align-items: flex-start; }
  h1 { font-family: 'Space Grotesk', sans-serif; font-weight: 700; text-transform: uppercase; line-height: 1.1;
       white-space: nowrap; }
  h1 span { display: block; width: max-content; }
  h1 span.hl { background: #2563EB; border-radius: 8px; padding: 0 .15em; margin-left: -.15em; line-height: 1.04;
               margin-top: .04em; }
  .body { margin-top: 30px; font-size: 46px; line-height: 1.34; font-weight: 600; color: #EEF3FB; }
  .label { margin-top: 32px; background: #2563EB; border-radius: 12px 12px 0 0; padding: 9px 22px 7px;
           font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 32px; letter-spacing: .1em;
           text-transform: uppercase; }
  .box { background: rgba(14,34,64,.92); border: 2px solid rgba(255,255,255,.18); border-radius: 0 18px 18px 18px;
         padding: 18px 28px 20px; font-size: 48px; font-weight: 600; }
</style></head><body>
<div class="photo"></div><div class="melt"></div><div class="shade"></div>
<div class="tab">YardSwaps</div>
${credit ? `<div class="credit"><i>On YardSwaps now</i>${esc(credit)}</div>` : ''}
<div class="col"><h1>${lines}</h1><p class="body">${esc(BODY)}</p>
<div class="label">${esc(LABEL)}</div><div class="box">${esc(URL_TEXT)}</div></div>
</body></html>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family));
  if (!fonts.some(f => f.includes('Space Grotesk'))) console.error('warning: Space Grotesk did not load');
  await page.evaluate(() => {
    // biggest headline that fits the column, then the photo fills the frame down to the words
    const h1 = document.querySelector('h1');
    let fs = 150;
    const wide = () => [...h1.children].some(e => e.getBoundingClientRect().right > 1080 - 56);
    h1.style.fontSize = fs + 'px';
    while (fs > 60 && wide()) { fs -= 2; h1.style.fontSize = fs + 'px'; }
    const top = document.querySelector('.col').getBoundingClientRect().top;
    document.querySelector('.photo').style.height = (top + 70) + 'px';
    document.querySelector('.melt').style.top = (top + 70 - 240) + 'px';
  });
  await page.screenshot(out.endsWith('.jpg') ? { path: out, type: 'jpeg', quality: 92 } : { path: out, type: 'png' });
  await browser.close();
  console.log(JSON.stringify({ out, machine: machineRaw, headline: HEAD.join(' ').replace('*', ''), body: BODY, cta: LABEL, url: URL_TEXT, credit }));
})();
