// Renders the daily seller Story (1080x1920) in the YardSwaps post look (brand/posts/kit.py, story(), look k2).
// Usage:  node render_story.js <photo.jpg|png> <machine> <out.jpg|png>
//
// Alan, 2026-11-26: "looks like ai slop", then "The white and blue is much cleaner than the blue in blue".
// The look: a REAL listing photo on top with nothing over it (make_bg.py picks one the daily review approved),
// then on WHITE the one blue tag, a one-line slate headline, one grey line of body, and the wordmark with the
// link. No pills, shadows, gradients or boxes. Under it a plain light panel, where Instagram's own buttons sit.
// Words follow MESSAGING.md (sellers: free listing first, then the AI, then no selling fee).
// The Graph API cannot add link stickers, so the link is printed, not tappable (Alan's pick, 2026-11-08).
// If <photo>.json sits next to the photo ({"credit": "Title · $1,200"}) a small line names the listing shown.
// This job checks out only stories/, so the look is drawn here in HTML; keep the numbers in step with kit.py.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const [bg, machineRaw, out] = process.argv.slice(2);
if (!bg || !machineRaw || !out) {
  console.error('usage: node render_story.js <photo> <machine> <out.jpg|png>');
  process.exit(2);
}
const TAG = 'List it free';
const HEAD = 'Sitting idle?';
const BODY = 'Snap a photo and the AI writes the listing. No selling fee. Local pickup.';
const URL_TEXT = 'yardswaps.com/sell-equipment';

let credit = '';
const side = bg.replace(/\.[a-z]+$/i, '.json');
if (fs.existsSync(side)) {
  try { credit = JSON.parse(fs.readFileSync(side, 'utf8')).credit || ''; } catch (e) { credit = ''; }
}
const ext = path.extname(bg).slice(1).replace('jpg', 'jpeg');
const bgData = `data:image/${ext};base64,${fs.readFileSync(bg).toString('base64')}`;
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

// Every number below is kit.py's, moved down 200 px (kit.STORY_OFF) so Instagram's own header sits on the light
// strip, not on the photo: margin 64, photo 200..920, tag top 948 (162 tall, 118 px type), title baseline 1211
// (86 px, one line), body baselines 1277 and 1327 (40 px), wordmark baseline 1405 (46 px), light panel from 1440.
// Nothing to read in the top 200 px or the bottom 340 px.
const html = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600&family=Space+Grotesk:wght@700&display=block" rel="stylesheet">
<style>
  * { margin: 0; box-sizing: border-box; }
  body { width: 1080px; height: 1920px; overflow: hidden; background: #EEF2F8; color: #1A3353;
         font-family: 'Inter', sans-serif; position: relative; -webkit-font-smoothing: antialiased; }
  .photo { position: absolute; left: 0; top: 200px; width: 1080px; height: 720px; background: #EEF2F8; overflow: hidden; }
  .photo img { position: absolute; }
  .band { position: absolute; left: 0; top: 920px; width: 1080px; height: 520px; background: #fff; }
  .t { position: absolute; left: 64px; white-space: nowrap; line-height: 1; }
  .t i { display: inline-block; width: 0; height: 0; }
  .sg { font-family: 'Space Grotesk', sans-serif; font-weight: 700; }
  .tag { position: absolute; left: 64px; top: 948px; height: 162px; padding: 0 30px; background: #2563EB;
         border-radius: 10px; color: #fff; font-size: 118px; letter-spacing: -0.02em; text-transform: uppercase;
         white-space: nowrap; line-height: 162px; }
  .title { font-size: 86px; letter-spacing: -0.025em; text-transform: uppercase; }
  .body { font-size: 40px; font-weight: 500; color: #4A5568; }
  .wm { font-size: 46px; letter-spacing: -0.02em; }
  .wm b { color: #2563EB; font-weight: 700; }
  .url { left: auto; right: 64px; font-size: 36px; font-weight: 500; color: #4A5568; }
  .credit { font-size: 32px; font-weight: 500; color: #4A5568; max-width: 952px; overflow: hidden; text-overflow: clip; }
</style></head><body>
<div class="photo"><img id="ph" src="${bgData}"></div>
<div class="band"></div>
<div class="tag sg" id="tag"><i></i>${esc(TAG)}</div>
<div class="t sg title" data-base="1211"><i></i>${esc(HEAD)}</div>
<div class="t body" data-base="1277" id="b1"><i></i></div>
<div class="t body" data-base="1327" id="b2"><i></i></div>
<div class="t sg wm" data-base="1405"><i></i>Yard<b>Swaps</b></div>
<div class="t url" data-base="1405"><i></i>${esc(URL_TEXT)}</div>
${credit ? `<div class="t credit" data-base="1506"><i></i>Shown: ${esc(credit)}</div>` : ''}
</body></html>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family));
  if (!fonts.some(f => f.includes('Space Grotesk'))) console.error('warning: Space Grotesk did not load');
  const fit = await page.evaluate((BODY) => {
    // the photo: fill the 1080x720 slot when that trims 6% or less off each side, else show the WHOLE photo
    // sitting on the light panel (Alan, 11-09: fit the whole item, never zoom into it)
    const im = document.getElementById('ph');
    const W = 1080, H = 720, w = im.naturalWidth, h = im.naturalHeight;
    const cover = Math.max(W / w, H / h), trim = Math.max(w * cover - W, h * cover - H) / 2 / Math.max(w * cover, h * cover);
    const k = trim <= 0.06 ? cover : Math.min(W / w, H / h);
    im.style.width = w * k + 'px'; im.style.height = h * k + 'px';
    im.style.left = (W - w * k) / 2 + 'px';
    im.style.top = (trim <= 0.06 ? (H - h * k) * 0.4 : H - h * k) + 'px';
    // tag and headline: one line each, stepping the size down until they fit the 952 px column
    const shrink = (el, size, floor, pad) => {
      el.style.fontSize = size + 'px';
      while (size > floor && el.getBoundingClientRect().width > 952) { size -= 2; el.style.fontSize = size + 'px'; }
      return size;
    };
    const tag = document.getElementById('tag');
    const ts = shrink(tag, 118, 60);
    tag.style.height = tag.style.lineHeight = Math.round(162 * ts / 118) + 'px';
    const title = document.querySelector('.title');
    const hs = shrink(title, 86, 64);
    // body: at most two lines, 900 px wide, whole words
    const probe = document.createElement('span');
    probe.className = 'body'; probe.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap';
    document.body.appendChild(probe);
    const lines = []; let cur = '';
    for (const word of BODY.split(' ')) {
      probe.textContent = (cur + ' ' + word).trim();
      if (probe.getBoundingClientRect().width <= 900 || !cur) cur = probe.textContent;
      else { lines.push(cur); cur = word; }
    }
    lines.push(cur); probe.remove();
    document.getElementById('b1').append(lines[0] || '');
    document.getElementById('b2').append(lines[1] || '');
    // sit every text line on its baseline (the empty <i> marks the baseline)
    for (const el of document.querySelectorAll('[data-base]')) {
      el.style.top = '0px';
      const base = el.querySelector('i').getBoundingClientRect().bottom;
      el.style.top = (Number(el.dataset.base) - base) + 'px';
    }
    return { tag: ts, title: hs, lines: lines.length, whole: trim > 0.06 };
  }, BODY);
  if (fit.lines > 2) { console.error('body does not fit two lines'); process.exit(1); }
  await page.screenshot(out.endsWith('.jpg') ? { path: out, type: 'jpeg', quality: 92 } : { path: out, type: 'png' });
  await browser.close();
  console.log(JSON.stringify({ out, machine: machineRaw, headline: HEAD, tag: TAG, body: BODY, url: URL_TEXT, credit, look: 'k2' }));
})();
