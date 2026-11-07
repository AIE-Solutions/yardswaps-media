#!/usr/bin/env python3
"""Make Runway clips, stills or ads and save them under broll/.

Runs in GitHub Actions (runway.yml). Reads RUNWAYML_API_SECRET from the
environment and never prints it. Every run prints the credit balance before
and after, and logs what it spent to broll/log.json.

Modes (MODE):
  clip     one generation from the inputs below (default)
  batch    every job in a shot list (SHOTS = broll/shots/<name>.json), several
           takes each, submitted together; ONLY = comma-separated job ids to run
           a subset; BUDGET = the most credits this run may spend (required).
           The run estimates the cost first and spends nothing if the estimate
           is over BUDGET or over the balance.
  estimate price a shot list (SHOTS, ONLY) without spending anything
  balance  print the credit balance only
  fetch    download a finished task (TASK = its id) whose run timed out

Single-clip inputs:
  PHOTO     repo path (broll/in/...) or https URL. Several are comma-separated,
            each optionally tagged as tag=path:
              gen4_image: up to 3 reference photos, named in the prompt as @tag
              veo / kling: first=path and optionally last=path (end frame)
              product_ad: up to 10 product photos, the first is the main one
  PROMPT    the motion / image / ad prompt
  MODEL     see MODELS below
  RATIO     must be on the model's list in MODELS
  DURATION  seconds, must be on the model's list
  AUDIO     1 = the model makes sound (costs more on Veo and Kling; we add our own music)
  NEGATIVE  Veo only: what to avoid
  STYLE     product_ad only: comma-separated style/ambience photos (up to 4)
  INFO      product_ad only: product description (max 2,500 characters)
  SEED      optional integer (not sent to Kling, which has no seed)
  SLUG      output name, e.g. forklift-yard -> broll/forklift-yard-720x1280.mp4
"""
import base64
import io
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
LOG = "broll/log.json"
RECIPE_VERSION = "2026-07"

GEN4_RATIOS = {"720:1280", "1280:720", "1104:832", "832:1104", "960:960", "1584:672"}
VEO_RATIOS = {"1280:720", "720:1280", "1080:1920", "1920:1080"}
# Credits per second (1 credit = $0.01), from dev.runway.com pricing, Nov 6 2026.
MODELS = {
    "gen4_turbo": {"kind": "video", "ratios": GEN4_RATIOS, "durations": {5, 10}, "rate": 5},
    "gen4.5": {"kind": "video", "ratios": GEN4_RATIOS, "durations": {5, 10}, "rate": 12},
    "veo3.1": {"kind": "video", "ratios": VEO_RATIOS, "durations": {4, 6, 8}, "rate": 20, "audio_rate": 40,
               "audio": True, "seed": True, "negative": True},
    "veo3.1_fast": {"kind": "video", "ratios": VEO_RATIOS, "durations": {4, 6, 8}, "rate": 10, "audio_rate": 15,
                    "audio": True, "seed": True, "negative": True},
    "kling3.0_standard": {"kind": "video", "ratios": {"1280:720", "720:1280", "960:960"},
                          "durations": set(range(3, 16)), "rate": 9, "audio_rate": 13, "audio": True},
    "kling3.0_pro": {"kind": "video", "ratios": {"1920:1080", "1080:1920", "1440:1440"},
                     "durations": set(range(3, 16)), "rate": 12, "audio_rate": 17, "audio": True},
    "kling3.0_4k": {"kind": "video", "ratios": {"3840:2160", "2160:3840", "2880:2880"},
                    "durations": set(range(3, 16)), "rate": 43, "audio_rate": 43, "audio": True},
    "gen4_image": {"kind": "image", "ratios": {"1920:1080", "1080:1920", "1024:1024", "1360:768", "1080:1080",
                                               "1168:880", "1440:1080", "1080:1440", "1808:768", "2112:912",
                                               "1280:720", "720:1280", "720:720", "960:720", "720:960", "1680:720"},
                   "seed": True},
    "product_ad": {"kind": "recipe", "ratios": {"1280:720", "720:1280", "960:960", "834:1112", "1920:1080",
                                                "1080:1920", "1440:1440", "1248:1664"},
                   "durations": set(range(4, 16))},
}


def die(msg):
    print(f"runway: {msg}", file=sys.stderr)
    sys.exit(1)


def req(method, path, key, body=None, fatal=True):
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
        if not fatal:
            print(f"  {method} {path} -> HTTP {e.code}: {text}")
            return None
        die(f"{method} {path} -> HTTP {e.code}: {text}")


def balance(key):
    org = req("GET", "/v1/organization", key)
    credits = org.get("creditBalance")
    print(f"credit balance: {credits} (about ${(credits or 0) / 100:.2f})")
    return credits


def is_1080(ratio):
    return max(int(x) for x in ratio.split(":")) >= 1664


def estimate(model, ratio, duration, audio):
    spec = MODELS[model]
    if spec["kind"] == "video":
        return (spec.get("audio_rate", spec["rate"]) if audio else spec["rate"]) * duration
    if spec["kind"] == "image":
        return 8 if max(int(x) for x in ratio.split(":")) >= 1080 else 5
    base, per = (216, 40) if is_1080(ratio) else (200, 36)
    return base + per * (duration - 4)


def photo_input(photo):
    if photo.startswith("https://"):
        return photo
    if not os.path.isfile(photo):
        die(f"photo not found: {photo}")
    size = os.path.getsize(photo)
    mime = mimetypes.guess_type(photo)[0] or "image/jpeg"
    raw = open(photo, "rb").read()
    try:
        from PIL import Image  # on ubuntu-latest; aspect check and re-encode of big stills
        im = Image.open(io.BytesIO(raw))
        w, h = im.size
        if not (0.5 <= w / h <= 2.0):
            die(f"photo {photo} is {w}x{h}, outside the 1:2 to 2:1 range the API accepts")
        if size > 3 * 1024 * 1024 or mime == "image/png":
            buf = io.BytesIO()
            im.convert("RGB").save(buf, "JPEG", quality=92)
            raw, mime = buf.getvalue(), "image/jpeg"
    except ImportError:
        if size > 3 * 1024 * 1024:
            die(f"photo {photo} is over 3 MB; shrink it first")
    return f"data:{mime};base64," + base64.b64encode(raw).decode()


def split_photos(photos):
    """'a.jpg, owner=b.png' -> [(None, 'a.jpg'), ('owner', 'b.png')]"""
    items = photos if isinstance(photos, list) else [x for x in photos.split(",")]
    out = []
    for x in items:
        x = x.strip()
        if not x:
            continue
        if "=" in x and not x.startswith("https://"):
            tag, path = x.split("=", 1)
            out.append((tag.strip(), path.strip()))
        else:
            out.append((None, x))
    return out


def validate(job):
    model, ratio, duration = job["model"], job["ratio"], job["duration"]
    if model not in MODELS:
        die(f"{job['slug']}: model {model} is not on the list {sorted(MODELS)}")
    spec = MODELS[model]
    if ratio not in spec["ratios"]:
        die(f"{job['slug']}: ratio {ratio} is not allowed for {model}: {sorted(spec['ratios'])}")
    if spec["kind"] != "image" and duration not in spec["durations"]:
        die(f"{job['slug']}: duration {duration} is not allowed for {model}: {sorted(spec['durations'])}")
    if model.startswith("veo") and is_1080(ratio) and duration != 8:
        die(f"{job['slug']}: Veo at 1080p only makes 8-second clips")
    if not job["prompt"]:
        die(f"{job['slug']}: prompt is empty")
    if spec["kind"] != "image" and not job["photos"]:
        die(f"{job['slug']}: needs a photo")
    if not all(c.isalnum() or c in "-_" for c in job["slug"]):
        die(f"{job['slug']}: slug may only use letters, digits, - and _")
    for tag, path in job["photos"]:
        if not path.startswith("https://") and not os.path.isfile(path):
            die(f"{job['slug']}: photo not found: {path}")


def body_for(job):
    model, spec = job["model"], MODELS[job["model"]]
    photos = job["photos"]
    if spec["kind"] == "recipe":
        styles = split_photos(job.get("style", ""))[:4]
        body = {"version": RECIPE_VERSION, "productImages": [{"uri": photo_input(p)} for _, p in photos[:10]],
                "userConcept": job["prompt"][:3500], "ratio": job["ratio"], "duration": job["duration"],
                "audio": bool(job.get("audio"))}
        if styles:
            body["styleImages"] = [{"uri": photo_input(p)} for _, p in styles]
        if job.get("info"):
            body["productInfo"] = job["info"][:2500]
        return f"/v1/recipes/{model}", body
    if spec["kind"] == "image":
        body = {"model": model, "promptText": job["prompt"][:1000], "ratio": job["ratio"]}
        if photos:
            body["referenceImages"] = [{"uri": photo_input(p), "tag": tag or "photo"} for tag, p in photos[:3]]
        if job.get("seed") is not None:
            body["seed"] = int(job["seed"])
        return "/v1/text_to_image", body
    # video
    if len(photos) == 1 and photos[0][0] in (None, "first"):
        image = photo_input(photos[0][1])
    else:
        image = [{"uri": photo_input(p), "position": tag or "first"} for tag, p in photos[:2]]
    limit = 2500 if model.startswith("kling") else 1000
    body = {"model": model, "promptImage": image, "promptText": job["prompt"][:limit],
            "ratio": job["ratio"], "duration": job["duration"]}
    if spec.get("audio"):
        body["audio"] = bool(job.get("audio"))
    if spec.get("seed") and job.get("seed") is not None:
        body["seed"] = int(job["seed"])
    if spec.get("negative") and job.get("negative"):
        body["negativePrompt"] = job["negative"][:1000]
    return "/v1/image_to_video", body


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
    if out.endswith(".png"):   # keep the repo small: stills are stored as JPEG
        try:
            from PIL import Image
            jpg = out[:-4] + ".jpg"
            Image.open(out).convert("RGB").save(jpg, "JPEG", quality=92)
            os.remove(out)
            out = jpg
        except ImportError:
            pass
    print(f"saved {out} ({os.path.getsize(out) // 1024} KB)")
    return out


def out_name(job, take, takes):
    tag = job["ratio"].replace(":", "x")
    ext = "png" if MODELS[job["model"]]["kind"] == "image" else "mp4"
    suffix = f"-t{take}" if takes > 1 else ""
    return f"broll/{job['slug']}{suffix}-{tag}.{ext}"


def save_outputs(job, task, take, takes):
    out = download(task["output"][0], out_name(job, take, takes))
    for i, u in enumerate(task["output"][1:], 2):
        download(u, out.rsplit(".", 1)[0] + f"-{i}." + out.rsplit(".", 1)[1])
    return out


def append_log(entries):
    log = []
    if os.path.isfile(LOG):
        with open(LOG) as f:
            log = json.load(f)
    log.extend(entries)
    with open(LOG, "w") as f:
        json.dump(log, f, indent=1)


def log_entry(job, out, seed, credits):
    kind = MODELS[job["model"]]["kind"]
    return {"when": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), "slug": job["slug"],
            "model": job["model"], "ratio": job["ratio"],
            "duration": job["duration"] if kind != "image" else None,
            "photo": ",".join(p if p.startswith("https://") else os.path.basename(p) for _, p in job["photos"]),
            "prompt": job["prompt"], "seed": seed, "file": out, "credits": credits}


def job_from(d, default_slug=None):
    model = (d.get("model") or "gen4_turbo").strip()
    spec = MODELS.get(model, {})
    return {"slug": d.get("id") or d.get("slug") or default_slug or "",
            "model": model, "ratio": (d.get("ratio") or "720:1280").strip(),
            "duration": int(d.get("duration") or (8 if model.startswith("veo") else 5)),
            "photos": split_photos(d.get("photo") or d.get("photos") or ""),
            "prompt": (d.get("prompt") or "").strip(), "seed": d.get("seed"),
            "audio": d.get("audio") in (True, 1, "1", "true", "yes"),
            "negative": d.get("negative") or "", "style": d.get("style") or "", "info": d.get("info") or "",
            "takes": max(1, min(4, int(d.get("takes") or 1))), "kind": spec.get("kind")}


def plan_batch():
    path = os.environ.get("SHOTS", "").strip()
    only = {x.strip() for x in os.environ.get("ONLY", "").split(",") if x.strip()}
    if not path or not os.path.isfile(path):
        die(f"batch needs SHOTS = a shot list in the repo (got {path!r})")
    with open(path) as f:
        plan = json.load(f)
    jobs = [job_from(d) for d in plan["jobs"] if not only or d["id"] in only]
    if only and len(jobs) != len(only):
        die(f"ONLY names jobs that are not in {path}: {sorted(only - {j['slug'] for j in jobs})}")
    if not jobs:
        die("no jobs to run")
    for j in jobs:
        validate(j)
    total = 0
    for j in jobs:
        c = estimate(j["model"], j["ratio"], j["duration"], j["audio"]) * j["takes"]
        total += c
        print(f"  {j['slug']}: {j['model']} {j['ratio']} {j['duration']}s x{j['takes']} = {c} credits")
    print(f"estimate: {total} credits (${total / 100:.2f})")
    return jobs, total


def run_batch(key):
    budget = int(os.environ.get("BUDGET", "0") or 0)
    if budget <= 0:
        die("batch needs BUDGET = the most credits this run may spend")
    jobs, total = plan_batch()
    print(f"budget {budget}")
    before = balance(key)
    if total > budget:
        die(f"estimate {total} is over BUDGET {budget}; nothing was spent")
    if before is not None and total > before:
        die(f"estimate {total} is over the balance {before}; nothing was spent. Add credits at dev.runway.com")

    pending = []
    for j in jobs:
        for t in range(1, j["takes"] + 1):
            seed = j["seed"]
            if seed is not None and j["takes"] > 1:
                seed = int(seed) + t - 1
            elif seed is None and MODELS[j["model"]].get("seed"):
                seed = random.randint(1, 2 ** 31 - 1)
            jj = dict(j, seed=seed)
            ep, body = body_for(jj)
            task = req("POST", ep, key, body, fatal=False)
            if task is None:
                print(f"  {j['slug']} take {t}: not submitted, skipping")
                continue
            print(f"  {j['slug']} take {t}: task {task['id']}")
            pending.append((jj, t, task["id"]))
            time.sleep(1)

    entries, failed = [], []
    t0 = time.time()
    while pending and time.time() - t0 < 2700:
        time.sleep(12 + random.random() * 3)
        still = []
        for jj, t, tid in pending:
            task = req("GET", f"/v1/tasks/{tid}", key, fatal=False)
            st = (task or {}).get("status")
            if st == "SUCCEEDED":
                out = save_outputs(jj, task, t, jj["takes"])
                entries.append(log_entry(jj, out, jj["seed"],
                                         estimate(jj["model"], jj["ratio"], jj["duration"], jj["audio"])))
            elif st in ("FAILED", "CANCELLED"):
                failed.append(f"{jj['slug']} take {t}: {task.get('failure') or task.get('failureCode')}")
            else:
                still.append((jj, t, tid))
        pending = still
        print(f"  {int(time.time() - t0)}s: {len(entries)} done, {len(failed)} failed, {len(pending)} running")
    after = balance(key)
    if entries and before is not None and after is not None:
        print(f"spent {before - after} credits this run")
    append_log(entries)
    for x in failed:
        print(f"FAILED {x}")
    for jj, t, tid in pending:
        print(f"STILL RUNNING {jj['slug']} take {t}: fetch it later with mode=fetch task={tid}")
    if not entries:
        die("nothing finished")


def main():
    if os.environ.get("MODE", "").strip() == "estimate":   # price a shot list, no key, no spend
        plan_batch()
        return
    key = os.environ.get("RUNWAYML_API_SECRET", "").strip()
    if not key:
        die("RUNWAYML_API_SECRET not set yet; nothing was spent")
    mode = os.environ.get("MODE", "clip").strip() or "clip"
    if mode == "balance":
        balance(key)
        return
    if mode == "batch":
        run_batch(key)
        return
    if mode == "fetch":   # download a finished task by id (a run that timed out), no new spend
        tid = os.environ.get("TASK", "").strip()
        slug = os.environ.get("SLUG", "").strip() or "fetched"
        if not tid or not all(c.isalnum() or c in "-_" for c in tid + slug):
            die("fetch needs TASK (a task id) and a plain SLUG")
        task = wait(tid, key, limit=2700)
        os.makedirs("broll", exist_ok=True)
        for i, u in enumerate(task["output"], 1):
            still = u.split("?")[0].lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
            download(u, f"broll/{slug}{'' if i == 1 else f'-{i}'}.{'png' if still else 'mp4'}")
        return

    job = job_from({"slug": os.environ.get("SLUG", "").strip(),
                    "model": os.environ.get("MODEL", ""), "ratio": os.environ.get("RATIO", ""),
                    "duration": os.environ.get("DURATION", ""), "photo": os.environ.get("PHOTO", ""),
                    "prompt": os.environ.get("PROMPT", ""), "seed": os.environ.get("SEED", "").strip() or None,
                    "audio": os.environ.get("AUDIO", "").strip(), "negative": os.environ.get("NEGATIVE", ""),
                    "style": os.environ.get("STYLE", ""), "info": os.environ.get("INFO", "")})
    if not job["slug"]:
        die("SLUG is required")
    validate(job)
    est = estimate(job["model"], job["ratio"], job["duration"], job["audio"])
    print(f"{job['model']} {job['ratio']} {job['duration']}s slug={job['slug']}, about {est} credits")
    before = balance(key)
    if before is not None and est > before:
        die(f"this needs about {est} credits and the balance is {before}; nothing was spent")
    os.makedirs("broll", exist_ok=True)
    ep, body = body_for(job)
    task = req("POST", ep, key, body)
    task = wait(task["id"], key, limit=2700 if job["kind"] == "recipe" else 1500)
    out = save_outputs(job, task, 1, 1)
    if job["model"] in ("gen4_turbo", "gen4.5"):
        rev = out.replace(".mp4", "-rev.mp4")
        try:
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", out, "-vf", "reverse",
                            "-an", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", rev],
                           check=True)
            print(f"saved {rev} (plays backwards, ends on the photo: use this one in the opener)")
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"no reversed copy ({e}); reverse it in the render step")
    after = balance(key)
    entry = log_entry(job, out, job["seed"],
                      (before - after) if (before is not None and after is not None) else None)
    append_log([entry])
    print(json.dumps(entry, indent=1))


if __name__ == "__main__":
    main()
