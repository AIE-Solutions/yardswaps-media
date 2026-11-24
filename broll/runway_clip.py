#!/usr/bin/env python3
"""Make one Runway clip (or one image edit) and save it under broll/.

Runs in GitHub Actions (runway.yml). Reads RUNWAYML_API_SECRET from the
environment and never prints it. One run is one generation, so a bad run
costs at most one clip (25 credits for 5 s of Gen-4 Turbo).

Inputs (environment, set by the workflow):
  MODE      clip (default) | balance
  PHOTO     repo path (broll/in/...) or https URL of the start photo
  PROMPT    the motion / edit prompt (optional for seedream5.5_layers)
  MODEL     gen4_turbo (default) | gen4.5 | seedance2_5_flash | gen4_image | seedream5.5_layers
            seedream5.5_layers (Runway, Nov 12 2026) splits a real listing photo into
            transparent layers and broll/cutout_card.py builds brand covers from the
            item layer, only if the layer still matches the photo pixel for pixel.
  MAX_CREDITS  refuse to start when the estimate is above this (default 60)
  MAX_IMAGES   seedream5.5_layers only: images returned incl. the base (default 4)
  RATIO     720:1280 (default) | 1280:720 | 1104:832 | 832:1104 | 960:960 | 1584:672 | 1920:1080 | 1080:1920
  DURATION  5 (default) | 10   (video models only)
  SEED      optional integer
  SLUG      output name, e.g. forklift-yard -> broll/forklift-yard-720x1280.mp4
"""
import base64
import json
import mimetypes
import os
import random
import subprocess
import sys
import time
import urllib.error
import urllib.request

API = "https://api.dev.runwayml.com"
VERSION = "2024-11-06"
VIDEO_MODELS = {"gen4_turbo", "gen4.5", "seedance2_5_flash"}
IMAGE_MODELS = {"gen4_image"}
LAYER_MODELS = {"seedream5.5_layers"}
RATIOS = {"720:1280", "1280:720", "1104:832", "832:1104", "960:960", "1584:672",
          "1920:1080", "1080:1920", "480:854", "854:480"}
# Credits per output second (API changelog). seedance2_5_flash: 20/s at 720p, 13/s at
# 480p, 52 minimum, 4-30 s. Layers: 2 per returned image at 1k (4 at 2k) + 1 for the source.
PER_SECOND = {"gen4_turbo": 5, "gen4.5": 12, "seedance2_5_flash": 20}
TAGS = ""  # set in main(); sent as X-Runway-Tags so the Usage page splits spend by use
LOG = "broll/log.json"


def die(msg):
    print(f"runway: {msg}", file=sys.stderr)
    sys.exit(1)


def req(method, path, key, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(API + path, data=data, method=method)
    r.add_header("Authorization", f"Bearer {key}")
    r.add_header("X-Runway-Version", VERSION)
    if TAGS and method == "POST":
        r.add_header("X-Runway-Tags", TAGS)
    if data is not None:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        text = e.read().decode(errors="replace")[:600]
        die(f"{method} {path} -> HTTP {e.code}: {text}")


def balance(key):
    org = req("GET", "/v1/organization", key)
    credits = org.get("creditBalance")
    print(f"credit balance: {credits} (about ${(credits or 0) / 100:.2f})")
    usage = org.get("usage")
    if usage:
        print(json.dumps(usage, indent=1)[:1500])
    return credits


def photo_input(photo):
    if photo.startswith("https://"):
        return photo
    if not os.path.isfile(photo):
        die(f"photo not found: {photo}")
    size = os.path.getsize(photo)
    if size > 16 * 1024 * 1024:
        die(f"photo is {size // 1024 // 1024} MB; the API limit is 16 MB")
    mime = mimetypes.guess_type(photo)[0] or "image/jpeg"
    try:
        from PIL import Image  # available on ubuntu-latest; aspect check only
        w, h = Image.open(photo).size
        if not (0.5 <= w / h <= 2.0):
            die(f"photo aspect {w}x{h} is outside the 1:2 to 2:1 range the API accepts")
    except ImportError:
        pass
    with open(photo, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def wait(task_id, key):
    t0 = time.time()
    while True:
        time.sleep(10 + random.random() * 3)
        task = req("GET", f"/v1/tasks/{task_id}", key)
        status = task.get("status")
        print(f"  {int(time.time() - t0)}s {status}")
        if status == "SUCCEEDED":
            return task
        if status in ("FAILED", "CANCELLED"):
            die(f"task {status}: {task.get('failure') or task.get('failureCode') or task}")
        if time.time() - t0 > 900:
            die("gave up after 15 minutes; the task may still finish, check the Runway portal")


def download(url, out):
    with urllib.request.urlopen(url, timeout=300) as resp, open(out, "wb") as f:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    print(f"saved {out} ({os.path.getsize(out) // 1024} KB)")


def estimate(model, ratio, duration, max_images):
    if model in LAYER_MODELS:
        return 2 * max_images + 1
    if model == "seedance2_5_flash":
        per = 13 if ratio in ("480:854", "854:480") else 20
        return max(52, per * duration)
    if model in PER_SECOND:
        return PER_SECOND[model] * duration
    return 8


def layers(key, image, slug, prompt, max_images):
    """seedream5.5_layers: the base image plus transparent PNG layers -> broll/layers/<slug>/."""
    body = {"model": "seedream5.5_layers", "referenceImages": [{"uri": image}],
            "resolution": "1k", "outputFormat": "png", "maxImages": max_images}
    if prompt:
        body["promptText"] = prompt
    print(f"text_to_image seedream5.5_layers maxImages={max_images} slug={slug}")
    task = req("POST", "/v1/text_to_image", key, body)
    task = wait(task["id"], key)
    out_dir = f"broll/layers/{slug}"
    os.makedirs(out_dir, exist_ok=True)
    meta = task.get("layers") or []
    rows = []
    for i, url in enumerate(task.get("output") or []):
        out = f"{out_dir}/{i:02d}.png"
        download(url, out)
        m = next((x for x in meta if x.get("uri") == url), meta[i] if i < len(meta) else {})
        rows.append({"file": out, "name": m.get("name"), "zIndex": m.get("zIndex"),
                     "boundingBox": m.get("boundingBox")})
    with open(f"{out_dir}/layers.json", "w") as f:
        json.dump(rows, f, indent=1)
    return out_dir


def main():
    global TAGS
    key = os.environ.get("RUNWAYML_API_SECRET", "").strip()
    if not key:
        die("RUNWAYML_API_SECRET not set yet; nothing was spent")
    mode = os.environ.get("MODE", "clip").strip() or "clip"
    if mode == "balance":
        balance(key)
        return

    photo = os.environ.get("PHOTO", "").strip()
    prompt = os.environ.get("PROMPT", "").strip()
    model = os.environ.get("MODEL", "gen4_turbo").strip() or "gen4_turbo"
    ratio = os.environ.get("RATIO", "720:1280").strip() or "720:1280"
    duration = int(os.environ.get("DURATION", "5") or 5)
    seed = os.environ.get("SEED", "").strip()
    slug = os.environ.get("SLUG", "").strip()
    if not photo or not prompt or not slug:
        die("PHOTO, PROMPT and SLUG are required")
    max_images = int(os.environ.get("MAX_IMAGES", "4") or 4)
    max_credits = int(os.environ.get("MAX_CREDITS", "60") or 60)
    allowed = VIDEO_MODELS | IMAGE_MODELS | LAYER_MODELS
    if model not in allowed:
        die(f"model {model} is not on the allow list {sorted(allowed)}")
    if model in LAYER_MODELS:
        if not photo or not slug:
            die("PHOTO and SLUG are required")
        if not 2 <= max_images <= 8:
            die("MAX_IMAGES must be 2 to 8 (base + item + a few background pieces)")
    elif not prompt:
        die("PROMPT is required")
    if ratio not in RATIOS:
        die(f"ratio {ratio} is not on the allow list {sorted(RATIOS)}")
    if model == "seedance2_5_flash":
        if not 4 <= duration <= 30:
            die("seedance2_5_flash duration must be 4 to 30")
        if ratio not in ("720:1280", "1280:720", "480:854", "854:480"):
            die("seedance2_5_flash: use 720:1280 / 1280:720 (720p) or 480:854 / 854:480")
    elif model in VIDEO_MODELS and duration not in (5, 10):
        die("duration must be 5 or 10")
    if not all(c.isalnum() or c in "-_" for c in slug):
        die("slug may only use letters, digits, - and _")
    TAGS = f"yardswaps,organic,model:{model},slug:{slug[:58]}".lower()

    cost = estimate(model, ratio, duration, max_images)
    before = balance(key)
    if cost > max_credits:
        die(f"estimate {cost} credits is above MAX_CREDITS={max_credits}; nothing was spent")
    if before is not None and cost > before:
        die(f"estimate {cost} credits but the balance is {before}; nothing was spent "
            "(we never buy credits without Alan's OK)")
    image = photo_input(photo)
    tag = ratio.replace(":", "x")
    os.makedirs("broll", exist_ok=True)

    if model in LAYER_MODELS:
        if photo.startswith("https://"):
            local = f"broll/in/{slug}-source.jpg"
            download(photo, local)  # the cover takes its pixels from this real photo
            photo = local
        out = layers(key, image, slug, prompt, max_images)
        try:
            cmd = [sys.executable, "broll/cutout_card.py", "--photo", photo,
                   "--layers", out, "--slug", slug]
            for flag, env in (("--title", "TITLE"), ("--price", "PRICE")):
                if os.environ.get(env, "").strip():
                    cmd += [flag, os.environ[env].strip()]
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"cutout_card refused the layers ({e}); layers kept for review")
    elif model in VIDEO_MODELS:
        body = {"model": model, "promptImage": image, "promptText": prompt,
                "ratio": ratio, "duration": duration}
        if model == "seedance2_5_flash":
            body["outputFormat"] = "mp4"
        if seed:
            body["seed"] = int(seed)
        print(f"image_to_video {model} {ratio} {duration}s slug={slug}")
        task = req("POST", "/v1/image_to_video", key, body)
        task = wait(task["id"], key)
        out = f"broll/{slug}-{tag}.mp4"
        download(task["output"][0], out)
        rev = f"broll/{slug}-{tag}-rev.mp4"
        try:
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", out, "-vf", "reverse",
                            "-an", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", rev],
                           check=True)
            print(f"saved {rev} (plays backwards, ends on the photo: use this one in the opener)")
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"no reversed copy ({e}); reverse it in the render step")
    else:
        body = {"model": model, "promptText": prompt, "ratio": ratio,
                "referenceImages": [{"uri": image, "tag": "photo"}]}
        if seed:
            body["seed"] = int(seed)
        print(f"text_to_image {model} {ratio} slug={slug}")
        task = req("POST", "/v1/text_to_image", key, body)
        task = wait(task["id"], key)
        out = f"broll/{slug}-{tag}.png"
        download(task["output"][0], out)

    after = balance(key)
    entry = {"when": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), "slug": slug,
             "model": model, "ratio": ratio, "duration": duration if model in VIDEO_MODELS else None,
             "photo": photo if photo.startswith("https://") else os.path.basename(photo),
             "prompt": prompt, "seed": seed or None, "file": out,
             "credits": (before - after) if (before is not None and after is not None) else None,
             "estimate": cost, "tags": TAGS}
    log = []
    if os.path.isfile(LOG):
        with open(LOG) as f:
            log = json.load(f)
    log.append(entry)
    with open(LOG, "w") as f:
        json.dump(log, f, indent=1)
    print(json.dumps(entry, indent=1))


if __name__ == "__main__":
    main()
