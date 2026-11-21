#!/usr/bin/env python3
"""How it works v3: 1920x1080 walkthrough from recorded app clips + Justin Case VO.

python3 build.py [--preview]   writes out/frames via ffmpeg pipe -> out/video-silent.mp4
and out/timeline.json (segment starts, VO starts) for the audio mix and captions.
"""
import json, os, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(HERE, '..', 'rec')
VO = os.environ.get('VO_DIR', '/home/user/yardswaps-media/narration/how-it-works-v3')
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1920, 1080, 30
PREVIEW = '--preview' in sys.argv

# Brand kit
BG = (246, 246, 248); SLATE = (26, 51, 83); BLUE = (37, 99, 235); BLUE_LIGHT = (229, 237, 253)
TEXT2 = (84, 84, 86); WHITE = (255, 255, 255); BORDER = (216, 216, 218)
FD = '/home/user/yardswaps-media/ads/parts-ad/source/fonts/'
FI = '/usr/share/fonts/opentype/inter/'
def font(path, size): return ImageFont.truetype(path, size)
F_HEAD = font(FD + 'SpaceGrotesk_700Bold.ttf', 68)
F_HEAD_L = font(FD + 'SpaceGrotesk_700Bold.ttf', 84)
F_TAG = font(FI + 'Inter-SemiBold.otf', 24)
F_SUB = font(FI + 'Inter-Regular.otf', 32)
F_SMALL = font(FI + 'Inter-Medium.otf', 22)

A = lambda n: Image.open(os.path.join(HERE, 'assets', n)).convert('RGBA')
WORDMARK = A('wordmark.png'); WORDMARK = WORDMARK.resize((int(WORDMARK.width * 44 / WORDMARK.height), 44), Image.LANCZOS)
HOTSY = Image.open(os.path.join(REC, 'img', 'hotsy.jpg')).convert('RGB')

# Phone geometry
SCR_H = 900; SCR_W = round(SCR_H * 1179 / 2334); BEZ = 16
PH_W, PH_H = SCR_W + 2 * BEZ, SCR_H + 2 * BEZ
PH_X = 1400 - PH_W // 2; PH_Y = (H - PH_H) // 2
CSS = SCR_W / 393  # css px -> screen px

def rounded_mask(size, r):
    m = Image.new('L', size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=255); return m
SCR_MASK = rounded_mask((SCR_W, SCR_H), 46)
def phone_base():
    im = Image.new('RGBA', (PH_W + 80, PH_H + 80), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    d.rounded_rectangle([40, 52, 40 + PH_W, 52 + PH_H], 62, fill=(14, 34, 64, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(22)); im.alpha_composite(sh)
    ImageDraw.Draw(im).rounded_rectangle([40, 40, 40 + PH_W, 40 + PH_H], 62, fill=(17, 20, 26, 255))
    return im
PHONE = phone_base()

def wrap(d, text, f, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

# ---- segments --------------------------------------------------------------
# clip: recorded folder; ranges: list of (start,end) frames played in order at 1x
# (end exclusive, None = to the end); hold0: seconds to hold the first frame;
# callout: (x0,y0,x1,y1) in css px of the 393-wide screen, from frame index (output-local).
SEGS = [
    dict(id='open', vo='hiw3-01-open', kind='open', tag='', head='How to use YardSwaps',
         sub='One pressure washer, from photos to a live listing, then the buyer side.'),
    dict(id='tips', vo='hiw3-02-tips', clip='wt-tips', tag='SELL  ·  STEP 1', head='Open Photo tips before you shoot',
         sub='Whole item in the frame, plus the label up close.', callout=(10, 486, 330, 570), co_from=70),
    dict(id='scan', vo='hiw3-03-scan', clip='wt-scan', tag='SELL  ·  STEP 2', head='Add photos. AI fills in the listing',
         sub='One of the whole washer, one of the label.', callout=(0, 362, 393, 585), co_from=262),
    dict(id='specs', vo='hiw3-04-specs', clip='wt-specs', tag='SELL  ·  STEP 3', head='Check what it read from the label',
         sub='Brand: Hotsy, read off the decal.', callout=(0, 262, 393, 392), co_from=150),
    dict(id='price', vo='hiw3-05-price', clip='wt-price', tag='SELL  ·  STEP 4', head='Use the suggested price, or your own',
         sub='Condition and description are already written.', callout=(4, 236, 393, 352), co_from=0),
    dict(id='publish', vo='hiw3-06-publish', clip='wt-pub', ranges=[(0, 40), (165, None)], tag='SELL  ·  STEP 5', head='Publish. Listing is free',
         sub='It shows up in the feed and in search.'),
    dict(id='search', vo='hiw3-07-search', clip='wt-search', ranges=[(0, 300), (360, 480)], tag='BUY  ·  STEP 6', head='Search and open a listing',
         sub='Photos, details and what to check before you buy.'),
    dict(id='offer', vo='hiw3-08-offer', clip='wt-offer', tag='BUY  ·  STEP 7', head='Make an offer',
         sub='The seller can accept it or counter.'),
    dict(id='chat', vo='hiw3-09-chat', clip='wt-chat', tag='BUY  ·  STEP 8', head='Message the seller and meet up',
         sub='Local pickup. Run it, then pay when you are satisfied.'),
    dict(id='store', vo='hiw3-10-store', clip='wt-store', ranges=[(0, 300), (620, None)], tag='FOR BUSINESSES',
         head='Sell as a business with a storefront', sub='Your company name, hours, service area and one link to share.',
         callout=(0, 152, 393, 262), co_from=0, co_to=150),
    dict(id='plans', vo='hiw3-11-plans', clip='wt-plans', ranges=[(0, 150)], hold0=2.5, tag='STOREFRONT PLAN',
         head='30 days free, then $29/mo for 3 months', sub='Founding price for the first 100 storefronts. Then $49/mo.',
         callout=(12, 64, 393, 192), co_from=0),
    dict(id='end', vo='hiw3-12-end', kind='end'),
]

def vo_len(name):
    p = os.path.join(VO, name + '.mp3')
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))

def clip_frames(seg):
    d = os.path.join(REC, 'raw', seg['clip'])
    fs = sorted(f for f in os.listdir(d) if f.endswith('.jpg'))
    taps = json.load(open(os.path.join(d, 'taps.json')))
    out, tapl = [], []
    for k in range(int(seg.get('hold0', 0) * FPS)): out.append(fs[0])
    for a, b in seg.get('ranges', [(0, None)]):
        b = len(fs) if b is None else b
        base = len(out)
        for t in taps:
            if a <= t['f'] < b: tapl.append((base + t['f'] - a, t['x'], t['y']))
        out += fs[a:b]
    return [os.path.join(d, f) for f in out], tapl

LEAD = 0.45; TAIL = 0.7
timeline = []; t = 0.0
for s in SEGS:
    s['vo_len'] = vo_len(s['vo'])
    if 'clip' in s:
        s['frames'], s['taps'] = clip_frames(s)
        clen = len(s['frames']) / FPS
    else:
        clen = 0
    base = {'open': 4.2, 'end': 6.0}.get(s.get('kind'), 0)
    s['dur'] = max(clen, LEAD + s['vo_len'] + TAIL, base)
    s['start'] = t; s['vo_start'] = t + LEAD
    timeline.append(dict(id=s['id'], start=round(t, 3), dur=round(s['dur'], 3), vo=s['vo'], vo_start=round(t + LEAD, 3),
                         vo_len=round(s['vo_len'], 3), head=s.get('head', ''), tag=s.get('tag', '')))
    t += s['dur']
TOTAL = t
json.dump(dict(total=round(TOTAL, 3), segments=timeline), open(os.path.join(OUT, 'timeline.json'), 'w'), indent=1)
print('total', round(TOTAL, 2), 's')
for x in timeline: print(f"{x['id']:8s} {x['start']:7.2f} {x['dur']:6.2f} vo {x['vo_len']:5.2f}")

# ---- drawing ----------------------------------------------------------------
def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3

def draw_left(c, s, lt):
    d = ImageDraw.Draw(c)
    a = ease(lt / 0.5)
    x0 = 150; y = 230 - int((1 - a) * 20)
    if s['tag']:
        tw = d.textlength(s['tag'], font=F_TAG)
        d.rounded_rectangle([x0, y, x0 + tw + 36, y + 46], 23, fill=BLUE_LIGHT)
        d.text((x0 + 18, y + 9), s['tag'], font=F_TAG, fill=BLUE)
        y += 76
    for ln in wrap(d, s['head'], F_HEAD, 820):
        d.text((x0, y), ln, font=F_HEAD, fill=SLATE); y += 80
    y += 14
    for ln in wrap(d, s['sub'], F_SUB, 800):
        d.text((x0, y), ln, font=F_SUB, fill=TEXT2); y += 44
    return y

def screen_frame(path):
    im = Image.open(path).convert('RGB')
    return im

def draw_callout(c, src, box, y, alpha):
    x0, y0, x1, y1 = [v * 3 for v in box]
    crop = src.crop((x0, y0, x1, y1))
    cw = 720; ch = round(crop.height * cw / crop.width)
    maxh = H - 80 - y
    if ch > maxh: ch = maxh; cw = round(crop.width * ch / crop.height)
    crop = crop.resize((cw, ch), Image.LANCZOS)
    card = Image.new('RGBA', (cw + 16, ch + 16), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle([0, 0, cw + 15, ch + 15], 22, fill=BLUE + (255,))
    m = rounded_mask((cw, ch), 16); card.paste(crop, (8, 8), m)
    if alpha < 1:
        card.putalpha(card.getchannel('A').point(lambda v: int(v * alpha)))
    dy = int((1 - alpha) * 16)
    sh = Image.new('RGBA', c.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([150, y + 18 + dy, 150 + cw + 16, y + ch + 34 + dy], 22, fill=(14, 34, 64, int(50 * alpha)))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    c.alpha_composite(card, (150, y + dy))
    # connector dot on the phone edge
    return

def draw_phone(c, src, taps, fi):
    c.alpha_composite(PHONE, (PH_X - 40, PH_Y - 40))
    scr = src.resize((SCR_W, SCR_H), Image.LANCZOS)
    c.paste(scr, (PH_X + BEZ, PH_Y + BEZ), SCR_MASK)
    ov = Image.new('RGBA', c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for tf, tx, ty in taps:
        k = fi - tf
        if -6 <= k < 22:
            cx = PH_X + BEZ + tx * CSS; cy = PH_Y + BEZ + ty * CSS
            if k < 0:  # finger approaching: soft dot
                r = 26; al = int(120 * (1 + k / 6))
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE + (al,))
            else:
                p = k / 22; r = 26 + 46 * ease(p); al = int(170 * (1 - p))
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE + (al,), width=6)
                if k < 8:
                    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=BLUE + (int(120 * (1 - k / 8)),))
    c.alpha_composite(ov)

def bg():
    c = Image.new('RGBA', (W, H), BG + (255,))
    d = ImageDraw.Draw(c)
    d.ellipse([1400 - 620, 540 - 620, 1400 + 620, 540 + 620], fill=(235, 241, 253, 255))
    c = c.filter(ImageFilter.GaussianBlur(60)) if False else c
    c.alpha_composite(WORDMARK, (150, 80))
    return c
BG_IMG = bg()

def fit(im, bw, bh):
    r = min(bw / im.width, bh / im.height); return im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)

OPEN_PHOTO = fit(HOTSY, 760, 860)
def draw_open(lt):
    c = BG_IMG.copy(); d = ImageDraw.Draw(c)
    a = ease(lt / 0.8)
    ph = OPEN_PHOTO; px = 1400 - ph.width // 2; py = (H - ph.height) // 2 + int((1 - a) * 24)
    card = Image.new('RGBA', (ph.width + 20, ph.height + 20), (255, 255, 255, 255))
    card.paste(ph, (10, 10))
    m = rounded_mask(card.size, 24)
    sh = Image.new('RGBA', c.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([px - 10, py + 8, px + ph.width + 10, py + ph.height + 28], 24, fill=(14, 34, 64, 60))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    c.paste(card, (px - 10, py - 10), m)
    y = 380
    for ln in wrap(d, 'How to use YardSwaps', F_HEAD_L, 800):
        d.text((150, y), ln, font=F_HEAD_L, fill=SLATE); y += 100
    y += 20
    for ln in wrap(d, 'List equipment from a few photos, buy locally, and open a storefront for your business.', F_SUB, 760):
        d.text((150, y), ln, font=F_SUB, fill=TEXT2); y += 46
    return c

APPST = fit(A('appstore.png'), 1000, 72); PLAY = fit(A('play.png'), 1000, 72)
QRI = fit(A('qr-ios.png'), 200, 200); QRP = fit(A('qr-play.png'), 200, 200)
BIGMARK = A('wordmark.png'); BIGMARK = BIGMARK.resize((int(BIGMARK.width * 110 / BIGMARK.height), 110), Image.LANCZOS)
def draw_end(lt):
    c = Image.new('RGBA', (W, H), BG + (255,)); d = ImageDraw.Draw(c)
    a = ease(lt / 0.7)
    c.alpha_composite(BIGMARK, ((W - BIGMARK.width) // 2, 150 + int((1 - a) * 16)))
    t1 = 'Get YardSwaps free'
    d.text(((W - d.textlength(t1, font=F_HEAD)) // 2, 320), t1, font=F_HEAD, fill=SLATE)
    # two columns: badge over QR
    cols = [(APPST, QRI, 'iPhone'), (PLAY, QRP, 'Android')]
    gx = [W // 2 - 300, W // 2 + 300]
    for (badge, qr, lab), cx in zip(cols, gx):
        c.alpha_composite(badge, (cx - badge.width // 2, 450))
        card = Image.new('RGBA', (qr.width + 28, qr.height + 28), (255, 255, 255, 255))
        card.alpha_composite(qr, (14, 14))
        c.paste(card, (cx - card.width // 2, 560), rounded_mask(card.size, 18))
        d.text((cx - d.textlength(lab, font=F_SMALL) / 2, 800), lab, font=F_SMALL, fill=TEXT2)
    t2 = 'yardswaps.com'
    f2 = font(FD + 'SpaceGrotesk_700Bold.ttf', 52)
    d.text(((W - d.textlength(t2, font=f2)) // 2, 870), t2, font=f2, fill=BLUE)
    t3 = 'Demo listings and accounts shown.'
    d.text(((W - d.textlength(t3, font=F_SMALL)) // 2, 1000), t3, font=F_SMALL, fill=(120, 120, 124))
    return c

def render_seg(s, lt):
    if s.get('kind') == 'open': return draw_open(lt)
    if s.get('kind') == 'end': return draw_end(lt)
    c = BG_IMG.copy()
    lf = int(lt * FPS)
    fi = min(lf, len(s['frames']) - 1)
    src = screen_frame(s['frames'][fi])
    y = draw_left(c, s, lt)
    draw_phone(c, src, s['taps'], lf)
    cf = s.get('co_from', 0)
    if s.get('callout') and cf <= fi < s.get('co_to', 10 ** 9):
        k = lt - 0.3 if cf == 0 else (lf - cf) / FPS
        al = ease(k / 0.45)
        if s.get('co_to') and fi > s['co_to'] - 10: al = min(al, (s['co_to'] - fi) / 10)
        if al > 0: draw_callout(c, src, s['callout'], y + 26, al)
    return c

XF = 9
def render(gf):
    tt = gf / FPS
    for i, s in enumerate(SEGS):
        if tt < s['start'] + s['dur'] or i == len(SEGS) - 1: break
    lt = tt - s['start']
    c = render_seg(s, lt)
    if i > 0 and lt * FPS < XF:
        pv = SEGS[i - 1]
        a = Image.blend(render_seg(pv, pv['dur'] - 1 / FPS).convert('RGB'), c.convert('RGB'), (lt * FPS + 1) / (XF + 1))
        return a
    return c

def main():
    n = int(math.ceil(TOTAL * FPS))
    if PREVIEW:
        for s in SEGS:
            for frac in (0.15, 0.85):
                gf = int((s['start'] + s['dur'] * frac) * FPS)
                render(gf).convert('RGB').save(os.path.join(OUT, f"pv-{s['id']}-{int(frac*100)}.jpg"), quality=85)
        return
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
           os.path.join(OUT, 'video-silent.mp4')]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for gf in range(n):
        p.stdin.write(render(gf).convert('RGB').tobytes())
        if gf % 600 == 0: print('frame', gf, '/', n, flush=True)
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    main()
