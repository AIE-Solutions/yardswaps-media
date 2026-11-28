#!/usr/bin/env python3
"""wordsheet10.py <slug> ... : words-vs-screen sheet for the 10 s cuts (assets/motion/yardswaps-<slug>-10s-9x16.mp4, spec r/spec/<n>s.json), written to the project motion/audit/."""
import json,os,sys,subprocess
from PIL import Image,ImageDraw,ImageFont
A='/mnt/project-files/yardswaps-campaign/assets/motion'
SPEC='/tmp/claude-0/-home-claude/765b8cd9-b345-549d-b9fa-6b192160c528/scratchpad/mo/v2p/r/spec'
OUT='/mnt/project-files/yardswaps-campaign/motion/audit'
exec(open('/tmp/claude-0/-home-claude/765b8cd9-b345-549d-b9fa-6b192160c528/scratchpad/mo/v2p/compile.py').read().split('\n')[6])  # NUM
NUM.update({'welder-from-one-job':'n74','compressor-by-the-fence':'n75','rooftop-unit-on-the-pallet':'n76','sprayer-after-the-season':'n77','light-tower-after-night-work':'n78','fryers-from-the-closed-kitchen':'n79','zero-turn-after-the-account':'n80','generator-for-the-storm-season':'n81','soldadora-en-el-carrito':'n82','read-the-plate-welder':'n83','skid-steer-after-the-grading':'n84','dump-trailer-after-the-cleanouts':'n85','cord-reels-after-the-events':'n86','wrench-wall-from-the-sold-shop':'n87','listed-omni-metalcraft-powered-24-w':'r90kwc7','pressure-washer-the-crew-skips':'n88','mixer-after-the-pour':'n89','scissor-lift-after-the-fitout':'n90','lathe-from-the-closed-shop':'n91','flatbed-after-the-last-contract':'n92','chairs-from-the-closed-office':'n93','listed-instapak-speedypacker-floor-model':'renr7e2','listed-used-pallet-racking-complete':'r3no15x','griddle-from-the-closed-diner':'n95','dryers-from-the-sold-laundromat':'n96','condensers-after-the-changeout':'n97','lawn-tractor-after-the-route':'n98','backhoe-still-on-the-trailer':'n99','listed-floral-walk-in-display-cooler':'riq3khm','listed-caterpillar-140h-v-plow':'rsfmh3l','combi-oven-after-the-remodel':'n100','boom-lift-after-the-fitout':'n101','control-cabinet-off-the-line':'n102','drill-rig-between-contracts':'n103','vac-truck-after-the-season':'n104','listed-deere-50g-excavator':'r5fbt0s','listed-billy-goat-leaf-vacuum':'r3tp04q'})
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
FONTB=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16)
def dur(p): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p]).decode().strip())
def frame(p,t,h=576):
    o=f'/tmp/ws_{os.getpid()}.jpg'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{t:.3f}','-i',p,'-frames:v','1','-vf',f'scale=-2:{h}',o],check=True)
    im=Image.open(o).convert('RGB'); os.remove(o); return im
for slug in sys.argv[1:]:
    p=os.environ.get('WS_SRC','/home/claude/yardswaps-media/reels/library/yardswaps-{slug}-9x16.mp4').format(slug=slug); n=NUM[slug]+'s'; s=json.load(open(f'{SPEC}/{n}.json'))  # WS_SRC: pre-publish check on the scratch final (Nov 18)
    D=dur(p); pts=[]
    for c in s['captions']:
        lab=f"{c['a']:.1f}-{c['b']:.1f} {c.get('l1','')} / {c.get('l2','')}"
        pts.append((c['a']+0.25,lab)); pts.append(((c['a']+c['b'])/2,'(mid) '+lab)); pts.append((c['b']-0.15,'(end) '+lab))
    for grp in s.get('pills',[]):
        for q in grp: pts.append((q['t']+0.4,f"pill {q['label']}"))
    for k in ('callouts',):
        for q in s.get(k,[]): pts.append(((q['a']+q['b'])/2,f"callout {q.get('kind',q.get('label',''))}"))
    if s.get('result'): r=s['result']; pts.append(((r['a']+r['b'])/2,f"result: {r['text']}"))
    pts.sort()
    W,H=324,576; cols=6; rows=(len(pts)+cols-1)//cols; LH=56
    sheet=Image.new('RGB',(cols*W,30+rows*(H+LH)),'white'); d=ImageDraw.Draw(sheet)
    d.text((6,6),f"{slug}-10s  {D:.1f}s  spec {n}.json  file reels/library/yardswaps-{slug}-9x16.mp4",font=FONTB,fill='black')
    for i,(t,lab) in enumerate(pts):
        im=frame(p,t).resize((W,H)); x=(i%cols)*W; y=30+(i//cols)*(H+LH)
        sheet.paste(im,(x,y)); d.text((x+4,y+H+2),f"t={t:.2f}s",font=FONTB,fill='black')
        d.text((x+4,y+H+20),lab[:44],font=FONT,fill='black'); d.text((x+4,y+H+36),lab[44:88],font=FONT,fill='black')
    os.makedirs(OUT,exist_ok=True); sheet.save(f'{OUT}/{slug}-10s.jpg',quality=80); print('ok',slug,len(pts))
