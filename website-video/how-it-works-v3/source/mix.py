#!/usr/bin/env python3
"""Mix VO + music under out/video-silent.mp4 -> out/yardswaps-how-it-works-v3.mp4, and write captions .vtt"""
import json, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
VO = os.environ.get('VO_DIR', '/home/user/yardswaps-media/narration/how-it-works-v3')
MUSIC = os.environ.get('MUSIC', '/home/user/yardswaps-media/music/v2/yardswaps-music-lofi-90bpm.mp3')
tl = json.load(open(os.path.join(OUT, 'timeline.json')))
T = tl['total']
texts = {}
for ln in open(os.path.join(VO, 'lines.tsv')):
    p = ln.rstrip('\n').split('\t')
    if len(p) >= 5 and p[0].endswith('.mp3'): texts[p[0][:-4]] = p[4]

inputs = ['-i', os.path.join(OUT, 'video-silent.mp4'), '-stream_loop', '-1', '-i', MUSIC]
fl = []
for i, s in enumerate(tl['segments']):
    inputs += ['-i', os.path.join(VO, s['vo'] + '.mp3')]
    ms = int(s['vo_start'] * 1000)
    fl.append(f"[{i+2}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}]")
n = len(tl['segments'])
fl.append(''.join(f'[v{i}]' for i in range(n)) + f"amix=inputs={n}:normalize=0,apad,atrim=0:{T}[vo]")
fl.append("[vo]asplit=2[vo1][vo2]")
fl.append(f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{T},volume=0.16,afade=t=in:d=1.2,afade=t=out:st={T-2.5}:d=2.5[mu]")
fl.append("[mu][vo2]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=500[duck]")
fl.append("[vo1][duck]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
cmd = ['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-filter_complex', ';'.join(fl), '-map', '0:v', '-map', '[a]',
       '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', '-t', str(T),
       os.path.join(OUT, 'yardswaps-how-it-works-v3.mp4')]
subprocess.check_call(cmd)

def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"
cues = ['WEBVTT', '']
k = 1
for s in tl['segments']:
    text = texts[s['vo']]
    for a, b in [('thirty days', '30 days'), ('first hundred', 'first 100'), ('twenty-nine dollars a month', '$29 a month'), ('forty-nine dollars a month', '$49 a month'), ('yardswaps dot com', 'yardswaps.com')]: text = text.replace(a, b)
    parts = [p.strip() for p in re.split(r'(?<=[.?!])\s+', text) if p.strip()]
    # merge very short sentences into the next
    merged = []
    for p in parts:
        if merged and len(merged[-1]) < 28: merged[-1] += ' ' + p
        else: merged.append(p)
    split = []
    for p in merged:
        while len(p) > 84 and ', ' in p:
            cuts = [i for i in range(len(p)) if p.startswith(', ', i)]
            i = min(cuts, key=lambda i: abs(i - len(p) / 2))
            split.append(p[:i + 1]); p = p[i + 2:]
        split.append(p)
    merged = split
    total_chars = sum(len(p) for p in merged)
    t0 = s['vo_start']
    for p in merged:
        d = s['vo_len'] * len(p) / total_chars
        cues += [str(k), f"{ts(t0)} --> {ts(t0 + d)}", p, '']; k += 1; t0 += d
open(os.path.join(OUT, 'yardswaps-how-it-works-v3.en.vtt'), 'w').write('\n'.join(cues))
print('ok', T)
