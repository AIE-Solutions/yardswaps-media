# Assemble a competitor-style cut from a spec. Vertical (v, 1080x1920) or wide (w, 1920x1080).
# usage: python3 build.py <spec.json> <v|w> <assets dir from assets.py> <clips dir> <frames dir> <music.mp3> <out.mp4> [vo.json]
# vo.json (optional): [{"file": "line1.mp3", "at": 0.6}, ...] voice lines placed on the timeline, music ducked under them.
import json, os, subprocess, sys, tempfile

spec = json.load(open(sys.argv[1])); A = sys.argv[2]; AS = os.path.abspath(sys.argv[3]); CL = os.path.abspath(sys.argv[4])
FR = os.path.abspath(sys.argv[5]); MUSIC = os.path.abspath(sys.argv[6]); OUT = os.path.abspath(sys.argv[7])
VO = json.load(open(sys.argv[8])) if len(sys.argv) > 8 else None
W, H = (1080, 1920) if A == "v" else (1920, 1080)
X = 0.3  # dissolve
N = "fps=30,format=yuv420p,setsar=1"; GRADE = "eq=saturation=0.96:contrast=1.03"
T = tempfile.mkdtemp(); os.chdir(T)


def ff(*a): subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *a], check=True)
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


def source(s, d):
    """filter chain producing a W x H shot from a clip (trimmed) or a still (slow 1.0 -> 1.025 push, under the 1.04 cap)."""
    if s.get("still"):
        n = int(d * 30) + 2
        z = f"zoompan=z='1+0.025*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=30"
        return ["-loop", "1", "-i", f"{CL}/{s['src']}"], f"[0:v]scale=2160:3840,{z},trim=duration={d},setpts=PTS-STARTPTS"
    return ["-i", f"{CL}/{s['src']}"], f"[0:v]trim={s['start']}:{s['start'] + d},setpts=PTS-STARTPTS,scale=1080:1920"


def shot(i, s, out):
    d = s["dur"]; inp, chain = source(s, d)
    cap = f"{AS}/t{i}-{A}.png"
    fade = f"[1:v]format=rgba,fade=in:st=0.35:d=0.4:alpha=1,fade=out:st={d - 0.55}:d=0.3:alpha=1[t]"
    slide = "overlay=x=0:y='max(0\\,22*(1-(t-0.35)/0.5))':eval=frame:shortest=1"
    if A == "v":
        fc = f"{chain},{GRADE},{N}[a];{fade};[a][t]{slide},{N}[v]"
    else:  # vertical panel, whole frame visible, on a blurred dimmed copy of itself
        fc = (f"{chain},{GRADE},split[s1][s2];[s1]scale=1920:-2,crop=1920:1080,gblur=sigma=40,eq=brightness=-0.22:saturation=0.8[bg];"
              f"[s2]scale=608:1080[fg];[bg][fg]overlay=x=200:y=0,{N}[a];{fade};[a][t]{slide},{N}[v]")
    ff(*inp, "-loop", "1", "-i", cap, "-filter_complex", fc, "-map", "[v]", "-t", str(d), "-an", "-c:v", "libx264", "-crf", "16", out)


def walk(out):
    segs = spec["segs"]; parts = []
    sw, sh, sx, sy = (744, 1474, 168, 330) if A == "v" else (456, 904, 360, 88)
    for k, (st, n) in enumerate(segs):
        ff("-framerate", "30", "-start_number", str(st), "-i", f"{FR}/%04d.jpg", "-frames:v", str(n),
           "-vf", f"scale={sw}:{sh}:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-crf", "14", "-r", "30", f"ws{k}.mp4")
        parts.append(dur(f"ws{k}.mp4"))
    offs, o = [], 0
    for p in parts[:-1]: o += p - X; offs.append(round(o, 3))
    chain, prev = [], "0:v"
    for k, off in enumerate(offs, 1):
        lab = f"x{k}"; chain.append(f"[{prev}][{k}:v]xfade=transition=fade:duration={X}:offset={off}[{lab}]"); prev = lab
    ins = sum([["-i", f"ws{k}.mp4"] for k in range(len(segs))], [])
    ff(*ins, "-filter_complex", ";".join(chain) + f";[{prev}]format=yuv420p[v]", "-map", "[v]", "-c:v", "libx264", "-crf", "14", "screen.mp4")
    L = dur("screen.mp4"); c1, c2 = offs[0], offs[1]  # captions change at the first two screen crossfades
    ff("-loop", "1", "-i", f"{AS}/appbg-{A}.png", "-i", "screen.mp4", "-loop", "1", "-i", f"{AS}/bezel-{A}.png",
       "-loop", "1", "-t", str(c1 + 0.3), "-i", f"{AS}/w1-{A}.png", "-loop", "1", "-t", str(c2 - c1 + 0.3), "-i", f"{AS}/w2-{A}.png",
       "-loop", "1", "-t", str(L - c2), "-i", f"{AS}/w3-{A}.png", "-filter_complex",
       f"[0]format=rgba,trim=duration={L}[bg];[bg][1]overlay={sx}:{sy}:shortest=1[p];[p][2]overlay=0:0[ph];"
       f"[3]format=rgba,fade=in:st=0:d=0.3:alpha=1,fade=out:st={c1}:d=0.3:alpha=1[w1];"
       f"[4]format=rgba,fade=in:st=0:d=0.3:alpha=1,fade=out:st={round(c2 - c1, 3)}:d=0.3:alpha=1,setpts=PTS+{c1}/TB[w2];"
       f"[5]format=rgba,fade=in:st=0:d=0.3:alpha=1,setpts=PTS+{c2}/TB[w3];"
       f"[ph][w1]overlay=0:0:eof_action=pass[a];[a][w2]overlay=0:0:eof_action=pass[b];[b][w3]overlay=0:0:eof_action=pass,{N}[v]",
       "-map", "[v]", "-t", str(L), "-r", "30", "-c:v", "libx264", "-crf", "16", out)


segs = []
for i, s in enumerate(spec["shots"]):
    o = f"a{i}.mp4"
    walk(o) if s.get("walk") else shot(i, s, o)
    segs.append(o)
ff("-loop", "1", "-framerate", "30", "-i", f"{AS}/end-{A}.png", "-vf", N, "-t", str(spec["end"]["dur"]), "-c:v", "libx264", "-crf", "16", "end.mp4")
segs.append("end.mp4")
d = [dur(s) for s in segs]; chain, prev, off, starts = [], "0:v", 0, [0]
for i in range(1, len(segs)):
    off += d[i - 1] - X; starts.append(round(off, 3)); lab = f"v{i}"
    chain.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={X}:offset={off:.3f}[{lab}]"); prev = lab
ff(*sum([["-i", s] for s in segs], []), "-filter_complex", ";".join(chain) + f";[{prev}]format=yuv420p[v]", "-map", "[v]",
   "-c:v", "libx264", "-crf", "20", "-preset", "slow", "video.mp4")
D = dur("video.mp4"); FO = round(D - 1.8, 2)
MS = spec.get("music_start", 0)  # skip into the track so a beat lands on a cut
music = f"[1:a]atrim={MS}:{MS + D},asetpts=PTS-STARTPTS,afade=t=in:d=0.2,afade=t=out:st={FO}:d=1.8"
if VO:
    vins = sum([["-i", os.path.abspath(v["file"])] for v in VO], [])
    vlines = ";".join(f"[{k + 2}:a]adelay={int(v['at'] * 1000)}:all=1[l{k}]" for k, v in enumerate(VO))
    mixv = "".join(f"[l{k}]" for k in range(len(VO)))
    fc = (f"{music},volume=0.55[m];{vlines};{mixv}amix=inputs={len(VO)}:normalize=0,apad,atrim=0:{D}[vo];"
          f"[vo]asplit[vo1][vo2];[m][vo1]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[md];"
          f"[md][vo2]amix=inputs=2:normalize=0,acompressor=threshold=-24dB:ratio=2.5:attack=20:release=300:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=9[a]")
    ff("-i", "video.mp4", "-i", MUSIC, *vins, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT)
else:
    fc = f"{music},acompressor=threshold=-28dB:ratio=2.5:attack=20:release=400:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=9[a]"
    ff("-i", "video.mp4", "-i", MUSIC, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT)
print(json.dumps({"out": OUT, "duration": round(D, 2), "shot_starts": starts}))
