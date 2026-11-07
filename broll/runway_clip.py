#!/usr/bin/env python3
"""Make one Runway clip (or one image edit) and save it under broll/.

Runs in GitHub Actions (runway.yml). Reads RUNWAYML_API_SECRET from the
environment and never prints it. One run is one generation, so a bad run
costs at most one clip (25 credits for 5 s of Gen-4 Turbo).

Inputs (environment, set by the workflow):
  MODE      clip (default) | balance | fetch (TASK = id of a task whose run timed out)
  PHOTO     repo path (broll/in/...) or https URL of the start photo
  PROMPT    the motion / edit prompt
  MODEL     gen4_turbo (default) | gen4.5 | gen4_image | product_ad
  RATIO     720:1280 (default) | 1280:720 | 1104:832 | 832:1104 | 960:960 | 1584:672
            product_ad also takes 1080:1920 | 1920:1080 | 1440:1440 | 834:1112 | 1248:1664 (1080p costs more)
  DURATION  5 (default) | 10 for video models; 4 to 15 for product_ad
  STYLE     product_ad only: comma-separated style/ambience photos (up to 4)
  INFO      product_ad only: product description (max 2,500 characters)
  AUDIO     product_ad only: 1 to let Runway add sound (default off; we add our own music)
  product_ad: PHOTO may list up to 10 comma-separated product photos, the first is the main one.
  Cost (Nov 2026 pricing guide): 720p 200 credits for 4 s + 36/s after; 1080p 216 + 40/s.
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
VIDEO_MODELS = {"gen4_turbo", "gen4.5"}
IMAGE_MODELS = {"gen4_image"}
RECIPES = {"product_ad"}          # POST /v1/recipes/product_ad: product photos + style photos + concept -> finished ad
RATIOS = {"720:1280", "1280:720", "1104:832", "832:1104", "960:960", "1584:672"}
RECIPE_RATIOS = {"1280:720", "720:1280", "960:960", "834:1112", "1920:1080", "1080:1920", "1440:1440", "1248:1664"}
RECIPE_VERSION = "2026-07"
LOG = "broll/log.json"


def die(msg):
    print(f"runway: {msg}", file=sys.stderr)
    sys.exit(1)


def req(method, path, key, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(API + path, data=data, method=method)
    r.add_header("Authorization", f"Bearer {key}")
    r.add_header("X-Runway-Version", VERSION)
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


def wait(task_id, key, limit=900):
    print(f"  task {task_id} (if this run times out, GET /v1/tasks/{task_id} still has the output)")
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
        if time.time() - t0 > limit:
            die(f"gave up after {limit // 60} minutes; task {task_id} may still finish, check the Runway portal")


def download(url, out):
    with urllib.request.urlopen(url, timeout=300) as resp, open(out, "wb") as f:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    print(f"saved {out} ({os.path.getsize(out) // 1024} KB)")


def main():
    key = os.environ.get("RUNWAYML_API_SECRET", "").strip()
    if not key:
        die("RUNWAYML_API_SECRET not set yet; nothing was spent")
    mode = os.environ.get("MODE", "clip").strip() or "clip"
    if mode == "balance":
        balance(key)
        return
    if mode == "fetch":   # download a finished task by id (a run that timed out), no new spend
        tid = os.environ.get("TASK", "").strip()
        slug = os.environ.get("SLUG", "").strip() or "fetched"
        if not tid or not all(c.isalnum() or c in "-_" for c in tid + slug):
            die("fetch needs TASK (a task id) and a plain SLUG")
        task = wait(tid, key, limit=2700)
        os.makedirs("broll", exist_ok=True)
        for i, u in enumerate(task["output"], 1):
            download(u, f"broll/{slug}{'' if i == 1 else f'-{i}'}.mp4")
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
    allowed = VIDEO_MODELS | IMAGE_MODELS | RECIPES
    if model not in allowed:
        die(f"model {model} is not on the allow list {sorted(allowed)}")
    ratios = RECIPE_RATIOS if model in RECIPES else RATIOS
    if ratio not in ratios:
        die(f"ratio {ratio} is not on the allow list {sorted(ratios)}")
    if model in VIDEO_MODELS and duration not in (5, 10):
        die("duration must be 5 or 10")
    if model in RECIPES and not 4 <= duration <= 15:
        die("product_ad duration must be 4 to 15 seconds")
    if not all(c.isalnum() or c in "-_" for c in slug):
        die("slug may only use letters, digits, - and _")

    before = balance(key)
    tag = ratio.replace(":", "x")
    os.makedirs("broll", exist_ok=True)

    if model in RECIPES:
        products = [x.strip() for x in photo.split(",") if x.strip()][:10]
        styles = [x.strip() for x in os.environ.get("STYLE", "").split(",") if x.strip()][:4]
        info = os.environ.get("INFO", "").strip()[:2500]
        body = {"version": RECIPE_VERSION, "productImages": [{"uri": photo_input(x)} for x in products],
                "userConcept": prompt[:3500], "ratio": ratio, "duration": duration,
                "audio": os.environ.get("AUDIO", "").strip() in ("1", "true", "yes")}
        if styles:
            body["styleImages"] = [{"uri": photo_input(x)} for x in styles]
        if info:
            body["productInfo"] = info
        print(f"recipe {model} {ratio} {duration}s products={len(products)} styles={len(styles)} slug={slug}")
        task = req("POST", f"/v1/recipes/{model}", key, body)
        task = wait(task["id"], key, limit=2700)
        out = f"broll/{slug}-{tag}.mp4"
        download(task["output"][0], out)
        if len(task["output"]) > 1:
            for i, u in enumerate(task["output"][1:], 2):
                download(u, f"broll/{slug}-{tag}-{i}.mp4")
    elif model in VIDEO_MODELS:
        image = photo_input(photo)
        body = {"model": model, "promptImage": image, "promptText": prompt,
                "ratio": ratio, "duration": duration}
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
        image = photo_input(photo)
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
             "model": model, "ratio": ratio, "duration": duration if model in VIDEO_MODELS | RECIPES else None,
             "photo": ",".join(x if x.startswith("https://") else os.path.basename(x) for x in photo.split(",")),
             "prompt": prompt, "seed": seed or None, "file": out,
             "credits": (before - after) if (before is not None and after is not None) else None}
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
