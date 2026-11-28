#!/usr/bin/env python3
"""compile.py <name> <style> id1,id2,...  : weekly reel / sponsor spot from the v2 silent 16x9 cuts.
Opener stays only on the first clip, end card only on the last, 0.3 s fades between clips; SFX events carried over at
their new offsets; music + loudness via finish.py. Writes final/yardswaps-<name>-16x9.mp4 (silent) and -16x9-music.mp4."""
import sys,subprocess as sp,json,os
name,style,ids=sys.argv[1],sys.argv[2],sys.argv[3].split(',')
NUM={'ai-lists-it':'n1','find-it-nearby':'n2','free-to-list':'n3','message-the-seller':'n4','save-a-search':'n5','every-category':'n6','make-an-offer':'n7','dealer-storefront':'n8','follow-a-seller':'n9','list-4-boosted-free':'n10','already-on-craigslist':'n11','see-what-buyers-want':'n12','snap-it-list-it':'n14','spare-part':'n15','invite-a-seller':'n16','show-the-cold-start':'n17','sold-it-list-the-next':'n18','that-trailer-next-season':'n19','forklift-sitting-there':'n20','surplus-parts-cash-flow':'n22','surplus-parts-labels':'n23','micrometer-set-small-tools':'n24','boring-bars-tooling':'n25','chop-saw-small-tools':'n26','condenser-changeout':'n27','pressure-washer-replaced':'n28','air-mover-fleet':'n29','spare-truck-wheel':'n30','leftover-anchor-adhesive':'n31','part-tag-scan':'n32','commercial-idle-forklift':'n14s','parts-donor-thumb':'n34','parts-bin-lot':'n35','plumbing-part-label':'n36','leftover-fittings-lot':'n37','stripped-well-pump':'n38','control-panel-pulled':'n39','drilling-rig-parked':'n40','pressure-washer-1000-psi':'n41','building-things-concrete-mixer':'n43','bluecollar-shelf-parts':'n44','job-wrapped-generator':'n52','downsized-to-one-truck':'n53','sold-the-septic-route':'n54','second-bay-closed-tools':'n55','warehouse-lease-ended':'n56','interior-job-done-lifts':'n57','shop-went-cnc-lathe':'n58','trash-pump-after-the-job':'n59','inspection-camera-in-the-van':'n60','second-jetter-by-the-fence':'n61','cooler-still-humming':'n62','chain-hoist-on-the-beam':'n63','whole-lot-one-link':'n64','import-from-your-website':'n65','storefront-stats':'n66','socials-on-storefront':'n67','see-what-buyers-want-v2':'n68','lift-still-bolted-down':'n69','box-truck-after-the-route':'n70','roller-after-the-overlay':'n71','safety-gear-on-the-wall':'n72','light-tower-after-night-work':'n78s','fryers-from-the-closed-kitchen':'n79s','generator-for-the-storm-season':'n81s','read-the-plate-welder':'n83s','dump-trailer-after-the-cleanouts':'n85s','pressure-washer-the-crew-skips':'n88s','scissor-lift-after-the-fitout':'n90s','listed-used-pallet-racking-complete':'r3no15xs','listed-instapak-speedypacker-floor-model':'renr7e2s','listed-floral-walk-in-display-cooler':'riq3khms','listed-caterpillar-140h-v-plow':'rsfmh3ls','listed-billy-goat-leaf-vacuum':'r3tp04qs','listed-deere-50g-excavator':'r5fbt0ss','listed-used-pallet-racking-complete-10s':'r3no15xs','listed-instapak-speedypacker-floor-model-10s':'renr7e2s','listed-floral-walk-in-display-cooler-10s':'riq3khms','listed-caterpillar-140h-v-plow-10s':'rsfmh3ls','listed-billy-goat-leaf-vacuum-10s':'r3tp04qs','listed-deere-50g-excavator-10s':'r5fbt0ss','listed-omni-metalcraft-powered-24-w':'r90kwc7s'}
X=0.3; SKIP=2.0
HOLDS=[float(x) for x in os.environ.get('HOLDS','').split(',') if x]  # Nov 20: freeze each clip's last frame this long so a narration line fits a 12 s cut's chapter   # later clips start right after their match cut (the opener card is the first clip's only)
def dur(f): return float(sp.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
segs=[];events=[];T=0.0;chap=[]
for i,id in enumerate(ids):
    f=f'final/yardswaps-{id}-16x9.mp4'
    try: spec=json.load(open(f'r/spec/{NUM[id]}.json'))
    except FileNotFoundError: spec={'T':4.3,'TE':dur(f)-3.2}   # spec lost with the Nov 9 scratchpad: demo format, 3.2 s end card
    try: sj=json.load(open(f'out/{NUM[id]}/16x9.sfx.json'))
    except FileNotFoundError: sj={'sfx':[]}
    a=0 if i==0 else max(SKIP,spec['T']-2.0); b=dur(f) if i==len(ids)-1 else spec['TE']   # cut before the end card except on the last clip
    h=HOLDS[i] if i<len(HOLDS) else 0.0
    chap.append((id,round(T,2))); segs.append((f,a,b,h)); off=T-a
    for n,t in sj['sfx']:
        if a<=t<b: events.append([n,round(t+off,3)])
    T+=b-a+h-(X if i<len(ids)-1 else 0)
inp=[];fl=[]
for i,(f,a,b,h) in enumerate(segs):
    pad=f',tpad=stop_mode=clone:stop_duration={h:.3f}' if h>0 else ''
    inp+=['-i',f];fl.append(f'[{i}:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS,fps=30{pad},format=yuv420p,setsar=1,settb=1/30[s{i}]')
cur='s0';t=segs[0][2]-segs[0][1]+segs[0][3]
for i in range(1,len(segs)):
    t-=X;fl.append(f'[{cur}][s{i}]xfade=transition=fade:duration={X}:offset={t:.3f}[x{i}]');cur=f'x{i}';t+=segs[i][2]-segs[i][1]+segs[i][3]
os.makedirs(f'out/{name}',exist_ok=True); raw=f'out/{name}/16x9.mp4'
sp.run(['ffmpeg','-y','-v','error',*inp,'-filter_complex',';'.join(fl),'-map',f'[{cur}]','-an','-c:v','libx264','-preset','slow','-crf','15','-pix_fmt','yuv420p','-r','30','-movflags','+faststart',raw],check=True)
D=dur(raw); json.dump({'D':D,'sfx':[e for e in events if e[1]<D-0.1]},open(f'out/{name}/16x9.sfx.json','w'))
sp.run(['python3','-I','finish.py',raw,f'out/{name}/fin.mp4',style],check=True)
os.replace(f'out/{name}/fin.mp4',f'final/yardswaps-{name}-16x9-music.mp4'); os.replace(f'out/{name}/fin-silent.mp4',f'final/yardswaps-{name}-16x9.mp4'); os.replace(f'out/{name}/fin-cover.jpg',f'final/covers/yardswaps-{name}-16x9.jpg')
os.remove(raw); print(name,'%.1f s'%D,'sfx',len(events)); json.dump(chap,open(f'out/{name}/chapters.json','w')); print('chapters',' '.join(f'{int(t)//60}:{int(t)%60:02d}={i}' for i,t in chap))
