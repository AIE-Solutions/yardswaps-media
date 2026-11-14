#!/usr/bin/env python3
"""Dealer plan inventory videos: the render worker (dealer-videos/README.md).

Each Dealer plan on YardSwaps includes one short video a month of one of the
dealer's real listings. The app queues the job and writes the script from the
listing's own facts (Marketplace apps/web/lib/dealer-videos.ts); this worker:

  1. POST {APP_URL}/api/dealer-videos/worker/claim  -> one job or null
  2. downloads the listing's photos, drops any with a face and blurs
     number-like text (plates, phone numbers, street numbers),
  3. voices each script line with ElevenLabs text-to-speech,
  4. screenshots the dealer's public storefront for the end card,
  5. renders a 1080x1920 MP4: the whole item fitted over a blurred copy of
     the same photo (zoom never past 1.035), one caption per line in the
     brand colours, a storefront end card, our licensed music kept low,
  6. uploads it through a presigned POST from /worker/<id>/upload and
     reports to /worker/<id>/complete.

The repo is public, so the log names job and listing ids only, never a
dealer's contact details (the job carries none).

Local test without any service: python3 dealer-videos/render.py --sample DIR
renders DIR/*.jpg with a sample script and silent voice to dealer-videos/out/.
"""

import argparse
import glob
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "listings", "fonts")
MUSIC = os.path.join(ROOT, "music", "trend")
OUT = os.path.join(ROOT, "dealer-videos", "out")

APP_URL = (os.environ.get("APP_URL") or "https://www.yardswaps.com").rstrip("/")
SECRET = os.environ.get("DEALER_VIDEO_WORKER_SECRET", "")
XI_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("DEALER_VIDEO_VOICE_ID") or "DtQLDxHbTiQTpVVanTy1"  # "Justin Case"
# A generally available model: output we sell must not come from a beta model.
TTS_MODEL = os.environ.get("DEALER_VIDEO_TTS_MODEL") or "eleven_multilingual_v2"
UA = "yardswaps-dealer-videos/1.0 (https://github.com/AIE-Solutions/yardswaps-media)"

W, H, FPS = 1080, 1920, 30
BG = (246, 246, 248)
SLATE = (26, 51, 83)
BLUE = (37, 99, 235)
GRAY = (84, 84, 86)
WHITE = (255, 255, 255)
ZOOM_MAX = 1.035          # never more than this: the whole item stays in frame
LINE_PAD = 0.45           # seconds of air after each spoken line
END_HOLD = 1.6            # extra seconds on the end card
MUSIC_GAIN = 0.10


def log(msg):
    print(msg, flush=True)


# ---------- the app ----------

def api(path, body=None, timeout=60):
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        f"{APP_URL}{path}", data=data, method="POST",
        headers={"Authorization": f"Bearer {SECRET}", "Content-Type": "application/json", "User-Agent": UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read() or b"{}")
        except ValueError:
            payload = {}
        return e.code, payload


def upload(job_id, path):
    import requests
    code, res = api(f"/api/dealer-videos/worker/{job_id}/upload")
    if code != 200:
        raise RuntimeError(f"upload link refused: HTTP {code} {res.get('error', '')}")
    post = res["upload"]
    with open(path, "rb") as f:
        r = requests.post(post["url"], data=post["fields"], files={"file": ("video.mp4", f, "video/mp4")}, timeout=300)
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f"upload failed: HTTP {r.status_code} {r.text[:200]}")


# ---------- photos ----------

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def faces_in(img_bgr):
    import cv2
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    scale = 1000 / max(h, w) if max(h, w) > 1000 else 1.0
    if scale != 1.0:
        gray = cv2.resize(gray, (int(w * scale), int(h * scale)))
    found = 0
    for name in ("haarcascade_frontalface_default.xml", "haarcascade_profileface.xml"):
        cc = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, name))
        found += len(cc.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=8, minSize=(40, 40)))
    return found


def blur_digit_text(img_bgr):
    """Blur every OCR word containing a digit (plates, phone and street numbers)."""
    import cv2
    if not shutil.which("tesseract"):
        return img_bgr
    import pytesseract
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    data = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT, config="--psm 11")
    out = img_bgr.copy()
    for i, word in enumerate(data["text"]):
        word = (word or "").strip()
        try:
            conf = float(data["conf"][i])
        except ValueError:
            conf = -1
        if conf < 40 or not word or not any(ch.isdigit() for ch in word):
            continue
        x, y, w, h = (data[k][i] for k in ("left", "top", "width", "height"))
        pad = max(6, h // 2)
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(out.shape[1], x + w + pad), min(out.shape[0], y + h + pad)
        roi = out[y0:y1, x0:x1]
        if roi.size:
            k = max(15, (max(roi.shape[:2]) // 2) * 2 + 1)
            out[y0:y1, x0:x1] = cv2.GaussianBlur(roi, (k, k), 0)
    return out


def usable_photos(sources):
    """PIL images of the photos we may show: no faces, number text blurred."""
    import cv2
    import numpy as np
    from PIL import Image
    out = []
    for src in sources:
        try:
            raw = fetch(src) if src.startswith("http") else open(src, "rb").read()
            img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:  # noqa: BLE001
            log(f"  photo skipped (download): {type(e).__name__}")
            continue
        if img is None or min(img.shape[:2]) < 300:
            continue
        if faces_in(img):
            log("  photo skipped (a face)")
            continue
        img = blur_digit_text(img)
        out.append(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
    return out


# ---------- voice ----------

def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip() or 0)


def tts(text, out_path):
    body = json.dumps({"text": text, "model_id": TTS_MODEL, "language_code": "en"}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128",
        data=body, method="POST",
        headers={"xi-api-key": XI_KEY, "Content-Type": "application/json", "User-Agent": UA},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                open(out_path, "wb").write(r.read())
            return
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            raise RuntimeError(f"TTS HTTP {e.code}") from None


def silent(seconds, out_path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-t", f"{seconds:.2f}", out_path], check=True)


# ---------- storefront ----------

def storefront_shot(url, out_path):
    """Phone-size screenshot of the public storefront, or None."""
    if not url:
        return None
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": 390, "height": 760}, device_scale_factor=2, user_agent=UA)
            page.goto(url, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(1200)
            # The cookie banner and app banners are not part of the storefront.
            page.add_style_tag(content=".cookie-banner,[class*='CookieBanner'],[class*='get-app'],[class*='GetApp']{display:none!important}")
            page.screenshot(path=out_path)
            b.close()
        return out_path
    except Exception as e:  # noqa: BLE001
        log(f"  storefront screenshot skipped: {type(e).__name__}")
        return None


# ---------- drawing ----------

def font(name, size, weight):
    from PIL import ImageFont
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    try:
        f.set_variation_by_name(weight)
    except Exception:  # noqa: BLE001
        pass
    return f


def wrap(draw, text, f, width, max_lines):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while draw.textlength(lines[-1] + "…", font=f) > width and " " in lines[-1]:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] = lines[-1].rstrip(",;:-") + "…"
    return lines


def backdrop(photo):
    """The same photo, cover-scaled, blurred and lightened, behind the fitted one."""
    from PIL import Image, ImageFilter
    s = max(W / photo.width, H / photo.height)
    bg = photo.resize((int(photo.width * s) + 1, int(photo.height * s) + 1), Image.BILINEAR)
    left, top = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(40))
    return Image.blend(bg, Image.new("RGB", (W, H), BG), 0.45)


def caption_layer(text, accent=False):
    """Transparent overlay: wordmark at the top, the spoken line in a card."""
    from PIL import Image, ImageDraw
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    mark = font("SpaceGrotesk.ttf", 52, "Bold")
    d.rounded_rectangle((48, 96, 48 + d.textlength("YardSwaps", font=mark) + 56, 96 + 92), 46, fill=WHITE + (235,))
    d.text((76, 110), "YardSwaps", font=mark, fill=SLATE)
    f = font("SpaceGrotesk.ttf", 68, "Bold")
    lines = wrap(d, text, f, W - 2 * 112, 3)
    lh = 84
    box_h = lh * len(lines) + 88
    y0 = H - 300 - box_h
    d.rounded_rectangle((64, y0, W - 64, y0 + box_h), 36, fill=WHITE + (245,))
    if accent:
        d.rounded_rectangle((64, y0, 64 + 14, y0 + box_h), 7, fill=BLUE + (255,))
    for i, ln in enumerate(lines):
        d.text((112, y0 + 44 + i * lh), ln, font=f, fill=BLUE if accent else SLATE)
    return layer


def photo_frames(photo, text, seconds, accent=False):
    """Frames for one line: the whole photo fitted, a slow push in to ZOOM_MAX."""
    from PIL import Image
    bg = backdrop(photo)
    cap = caption_layer(text, accent)
    box_w, box_h = W - 2 * 40, int(H * 0.56)
    s = min(box_w / photo.width, box_h / photo.height)
    base_w, base_h = photo.width * s, photo.height * s
    cy = 300 + box_h / 2
    n = max(1, int(round(seconds * FPS)))
    for i in range(n):
        z = 1.0 + (ZOOM_MAX - 1.0) * (i / max(1, n - 1))
        w, h = int(base_w * z), int(base_h * z)
        frame = bg.copy()
        frame.paste(photo.resize((w, h), Image.BILINEAR), ((W - w) // 2, int(cy - h / 2)))
        frame.paste(cap, (0, 0), cap)
        yield frame


def end_frame(dealer, storefront_url, shot_path):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    big = font("SpaceGrotesk.ttf", 72, "Bold")
    small = font("Inter.ttf", 44, "Medium")
    y = 150 if shot_path else 720
    title = f"See more from {dealer}" if dealer else "See it on YardSwaps"
    for ln in wrap(d, title, big, W - 160, 2):
        d.text(((W - d.textlength(ln, font=big)) / 2, y), ln, font=big, fill=SLATE)
        y += 88
    if shot_path:
        shot = Image.open(shot_path).convert("RGB")
        pw = 600
        ph = int(shot.height * pw / shot.width)
        ph = min(ph, 1140)
        shot = shot.resize((pw, int(shot.height * pw / shot.width)), Image.LANCZOS).crop((0, 0, pw, ph))
        fx, fy = (W - pw) // 2 - 22, y + 40
        d.rounded_rectangle((fx, fy, fx + pw + 44, fy + ph + 44), 64, fill=SLATE)
        mask = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw, ph), 44, fill=255)
        img.paste(shot, (fx + 22, fy + 22), mask)
        y = fy + ph + 44 + 56
    else:
        y += 40
    link = storefront_url.replace("https://", "").replace("www.", "") if storefront_url else "yardswaps.com"
    for ln in wrap(d, link, small, W - 160, 2):
        d.text(((W - d.textlength(ln, font=small)) / 2, y), ln, font=small, fill=BLUE)
        y += 58
    d.text(((W - d.textlength("YardSwaps", font=big)) / 2, H - 200), "YardSwaps", font=big, fill=SLATE)
    return img


# ---------- assembly ----------

def render(job, workdir, out_path, voice=True):
    lines = [ln.strip() for ln in job["script"].split("\n") if ln.strip()]
    if len(lines) < 2:
        raise RuntimeError("script too short")
    photos = usable_photos(job["listing"]["photoUrls"])
    if len(photos) < 2:
        raise RuntimeError(f"only {len(photos)} usable photos")
    log(f"  {len(photos)} photos, {len(lines)} lines")

    # Voice: one clip per line, so each caption is timed to its own words.
    clips = []
    for i, text in enumerate(lines):
        p = os.path.join(workdir, f"line{i}.mp3")
        if voice:
            tts(text, p)
        else:
            silent(max(1.6, len(text) / 14), p)
        clips.append((p, duration(p)))

    shot = storefront_shot(job["dealer"].get("storefrontUrl"), os.path.join(workdir, "store.png"))

    # Scenes: every line but the last on a photo (the first photo opens the
    # video, so the real item is on screen from the first frame); the last
    # line ("See more from ...") on the storefront end card.
    seg_wavs, total = [], 0.0
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
         os.path.join(workdir, "video.mp4")],
        stdin=subprocess.PIPE,
    )
    try:
        for i, (clip, dur) in enumerate(clips):
            last = i == len(clips) - 1
            seconds = dur + LINE_PAD + (END_HOLD if last else 0)
            n = int(round(seconds * FPS))
            seconds = n / FPS
            if last:
                frame = end_frame(job["dealer"].get("name", ""), job["dealer"].get("storefrontUrl"), shot).tobytes()
                for _ in range(n):
                    ff.stdin.write(frame)
            else:
                accent = lines[i].startswith(("Asking $", "Make an offer"))
                for fr in photo_frames(photos[i % len(photos)], lines[i], seconds, accent):
                    ff.stdin.write(fr.tobytes())
            wav = os.path.join(workdir, f"seg{i}.wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", clip, "-af", f"apad=whole_dur={seconds:.3f}",
                            "-t", f"{seconds:.3f}", "-ar", "44100", "-ac", "2", wav], check=True)
            seg_wavs.append(wav)
            total += seconds
    finally:
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError("video encode failed")

    concat = os.path.join(workdir, "voice.txt")
    with open(concat, "w") as f:
        f.writelines(f"file '{w}'\n" for w in seg_wavs)
    voice_wav = os.path.join(workdir, "voice.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", voice_wav], check=True)

    tracks = sorted(glob.glob(os.path.join(MUSIC, "*lofi*.mp3"))) or sorted(glob.glob(os.path.join(MUSIC, "*.mp3")))
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", os.path.join(workdir, "video.mp4"), "-i", voice_wav]
    if tracks:
        cmd += ["-stream_loop", "-1", "-i", random.Random(job["id"]).choice(tracks)]
        cmd += ["-filter_complex",
                f"[2:a]volume={MUSIC_GAIN},atrim=0:{total:.3f},afade=t=out:st={max(0, total - 1.2):.3f}:d=1.2[m];"
                "[1:a][m]amix=inputs=2:duration=first:normalize=0[a]",
                "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a"]
    cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", out_path]
    subprocess.run(cmd, check=True)
    return total


def run_jobs(max_jobs):
    if not SECRET:
        log("DEALER_VIDEO_WORKER_SECRET is not set: nothing to do")
        return 0
    done = 0
    for _ in range(max_jobs):
        code, res = api("/api/dealer-videos/worker/claim")
        if code == 503:
            log("Dealer videos are switched off in the app")
            break
        if code != 200:
            raise SystemExit(f"claim failed: HTTP {code} {res.get('error', '')}")
        if res.get("queued"):
            log(f"queued {res['queued']} new video(s)")
        job = res.get("job")
        if not job:
            log("no job waiting")
            break
        log(f"job {job['id']} (listing {job['listing']['id']}, attempt {job['attempt']})")
        workdir = tempfile.mkdtemp(prefix="dv-")
        out_path = os.path.join(workdir, "out.mp4")
        try:
            if not XI_KEY:
                raise RuntimeError("ELEVENLABS_API_KEY is not set")
            total = render(job, workdir, out_path, voice=True)
            upload(job["id"], out_path)
            code, res = api(f"/api/dealer-videos/worker/{job['id']}/complete", {"ok": True, "durationSec": round(total)})
            log(f"  complete: HTTP {code} {res.get('status', res.get('error', ''))}")
            done += 1 if code == 200 and res.get("ok") else 0
        except Exception as e:  # noqa: BLE001
            msg = f"{type(e).__name__}: {e}"[:300]
            log(f"  failed: {msg}")
            api(f"/api/dealer-videos/worker/{job['id']}/complete", {"ok": False, "error": msg})
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
    return done


def run_sample(photo_dir):
    """Render a local sample with a made-up script and silent voice."""
    os.makedirs(OUT, exist_ok=True)
    photos = sorted(glob.glob(os.path.join(photo_dir, "*.jpg")) + glob.glob(os.path.join(photo_dir, "*.png")))
    job = {
        "id": "sample",
        "script": "2016 Ford F-550 service truck.\n142,000 miles.\nAsking $38,500.\n"
                  "Located in Tulsa, Oklahoma.\nSee more from Red River Equipment on YardSwaps.",
        "attempt": 1,
        "dealer": {"name": "Red River Equipment", "slug": None, "storefrontUrl": None},
        "listing": {"id": "sample", "title": "sample", "photoUrls": photos},
    }
    workdir = tempfile.mkdtemp(prefix="dv-")
    out_path = os.path.join(OUT, "sample.mp4")
    try:
        total = render(job, workdir, out_path, voice=bool(XI_KEY))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    log(f"wrote {out_path} ({total:.1f} s)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", help="render the photos in this folder instead of claiming jobs")
    ap.add_argument("--max-jobs", type=int, default=int(os.environ.get("MAX_JOBS") or 10))
    a = ap.parse_args()
    if a.sample:
        run_sample(a.sample)
    else:
        n = run_jobs(a.max_jobs)
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a") as f:
                f.write(f"Dealer videos made this run: {n}\n")
        sys.exit(0)
