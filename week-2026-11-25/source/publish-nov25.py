# after batch18.sh + deploy.sh on renr7e2s r3no15xs n95s..n99s: media library entries (10 s cut is the posting file), formats rows, week folder, captions
import json,shutil,os,subprocess
M='/home/claude/yardswaps-media'; P='/mnt/project-files/yardswaps-campaign'; W=f'{M}/week-2026-11-25'; os.makedirs(W,exist_ok=True)
lib=json.load(open(f'{M}/reels/library.json')); new=json.load(open('gen25-lib.json')); have={v['slug'] for v in lib['videos']}
for e in new:
    s=e['slug']; src=f"final/yardswaps-{s}-10s-9x16.mp4"  # Nov 25: read scratch finals, project folder is flaky
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',src]))
    e['seconds']=round(d,1)
    shutil.copy(src,f"{M}/reels/library/yardswaps-{s}-9x16.mp4"); shutil.copy(src,f"{W}/yardswaps-{s}-10s-9x16.mp4")
    shutil.copy(f"final/yardswaps-{s}-10s-16x9-music.mp4",f"{W}/yardswaps-{s}-10s-16x9-music.mp4")
    if s not in have: lib['videos'].append(e)
    print(s,round(d,2))
json.dump(lib,open(f'{M}/reels/library.json','w'),indent=1,ensure_ascii=False); open(f'{M}/reels/library.json','a').write('\n')
fm=json.load(open(f'{M}/metrics/formats.json')); fm['videos'].update(json.load(open('gen25-fmt.json')))
json.dump(fm,open(f'{M}/metrics/formats.json','w'),indent=1,ensure_ascii=False); open(f'{M}/metrics/formats.json','a').write('\n')
cap=open(f'{P}/MOTION-CAPTIONS.md').read(); add=open('gen25-captions.md').read()
if 'combi-oven-after-the-remodel (Nov 25' not in cap:
    i=cap.index('## sponsor-38s'); open(f'{P}/MOTION-CAPTIONS.md','w').write(cap[:i]+add+'\n'+cap[i:])
print('library',len(lib['videos']),'formats',len(fm['videos']))
# real listing used this run goes into listings/motion-used.json in the same media commit
u=json.load(open(f'{M}/listings/motion-used.json'))
for e in new:
    if e.get('real') and e['listing_id'] not in [x if isinstance(x,str) else x.get('id') for x in u]:
        u.append(dict(id=e['listing_id'],slug=e['slug'],used='2026-11-25'))
json.dump(u,open(f'{M}/listings/motion-used.json','w'),indent=1); open(f'{M}/listings/motion-used.json','a').write('\n'); print('motion-used',len(u))
