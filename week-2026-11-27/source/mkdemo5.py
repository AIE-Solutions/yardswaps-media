"""mkdemo5.py n74s.. : short cut (Nov 16 YouTube report: 17 s Shorts averaged 30 views, 4-10 s clips 942). Same recording,
opener 2.4 s, app ~6 s in four captions, result 0.7 s, brand card 2.3 s; about 11.5 s in all.
Nov 16 23:55Z (Alan: "Slow down the phone action walk through, right now they're super fast in the shorts"): the app part
runs at half the Nov 16 afternoon speed. Photo lands 2x (was 3x), the AI fill 8x (16x), the scroll 6x (12x), the price tap
and publish tap 1.5x (2x), the live listing 4x (7x). PACE below is the only knob; the fast values are kept in mkdemo5-fast-nov16.py. Spec id is <n>s, config comes from cfg-nov16.json[<n>].
mkdemo3.py n15|n17|n19|n22-n31|n36-n39|n53 (Nov 15 re-records, same timeline as mkdemo2) : build a demonstrate-first Short spec (Nov 5 TikTok format) on a sell-flow recording.
Timeline: opener photo with movement (T s, label close-up before the match cut), app part ~6.5 s chunked to 6-word captions,
publish, result beat (before card + one bold line), end card. Scenes are built from raw frame segments [(a,b,speed)]."""
import json,sys,os
n=sys.argv[1]; R='../rec/raw'
CFG=json.load(open('cfg-all.json'))[n[:-1]]; CFG['T']=2.4
PACE=dict(land=2,fill=8,scroll=6,tap=1.5,live=4)  # frames per output frame in the app part (Nov 16 23:55Z, half the afternoon speed)

k=CFG['key']; raw=f'{R}/{k}'; taps=json.load(open(f'{raw}/taps.json')); NF=len([f for f in os.listdir(raw) if f.endswith('.jpg')])
F0=taps[0]['f']; tUP=taps[-2]['f']; tPUB=taps[-1]['f']; T=CFG['T']
# anchor frames: fields filled ~F0+235 (the scan stub answers ~7 s in); the form auto-scrolls to the title just after
# Nov 15: the fill lands 7-13 s in depending on scan speed, so find it in the frames instead of assuming F0+235:
# first frame whose top half differs from the post-upload frame (the title and the 'AI filled' bar appear), then the
# first frame after that which no longer changes (the auto-scroll to the title has settled).
import numpy as _np
from PIL import Image as _Im
def _fr(f): return _np.asarray(_Im.open(f'{raw}/{f:04d}.jpg').convert('L').resize((196,426)),dtype=float)[40:300]
_base=_fr(F0+90); _fch=next(f for f in range(F0+95,tUP,3) if _np.abs(_fr(f)-_base).mean()>12); _fs=_fch
while _fs+15<tUP and _np.abs(_fr(_fs)-_fr(_fs+15)).mean()>1.0: _fs+=3
FFILL=_fs-20; FSCR=FFILL+280; print(n,k,'fill change',_fch,'scroll settled',_fs,'FFILL',FFILL)
def segs(t0,parts):  # parts [(a,b,speed)] -> frames at 30 fps from t0
    fr=[];
    for a,b,sp in parts:
        nfr=max(1,round((b-a)/sp)); fr+= [round(a+(b-a)*i/nfr,1) for i in range(nfr)]
    return dict(t0=round(t0,4),t1=round(t0+len(fr)/30,4),frames=fr)
sc=[]; tp=[]; t=T-0.27
# S1: hold, library tap at T+0.3, the photo lands (2x), the scan fills the fields (6x)
s=[(F0-11,F0-11+10,1)]  # 10 frames hold = 0.33 s -> tap at T+0.2
if n=='n44':
    cat,row=taps[1]['f'],taps[2]['f']
    s+=[(F0,F0+45,2),(F0+45,cat-15,6),(cat-15,row+22,2)]
else:
    s+=[(F0,F0+45,PACE['land']),(F0+45,FFILL+20,PACE['fill'])]
S1=segs(t,s); S1['clip']=k; S1['tr']='none'; sc.append(S1); tp.append(dict(t=round(T+0.2,3),x=round(taps[0]['x']),y=round(taps[0]['y'],1)))
if n=='n44':
    tcat=S1['t0']+(17+45/2+(cat-15-F0-45)/6)/30; tp.append(dict(t=round(tcat+15/60,3),x=round(taps[1]['x']),y=round(taps[1]['y'],1))); tp.append(dict(t=round(tcat+(row-cat+15)/60,3),x=round(taps[2]['x']),y=round(taps[2]['y'],1)))
    sfx_cat=[['tap',tp[1]['t']],['tap',tp[2]['t']]]
else: sfx_cat=[]
t=S1['t1']
# S2: scroll through condition + description (fast)
S2=segs(t,[(S1['frames'][-1]+1,FSCR,PACE['scroll'])]); S2['clip']=k; S2['tr']='none'; sc.append(S2); t=S2['t1']
# S3: scrolled back up, Use price tap after 30 recorded frames, price lands
S3=segs(t,[(tUP-30,tUP+34,PACE['tap'])]); S3['clip']=k; S3['tr']='fade'; sc.append(S3); tUPv=round(t+30/PACE['tap']/30,3); tp.append(dict(t=tUPv,x=round(taps[-2]['x']),y=round(taps[-2]['y'],1))); t=S3['t1']
# S4: publish button, tap after 24 recorded frames, live listing, hold
S4=segs(t,[(tPUB-24,tPUB,PACE['tap']),(tPUB,NF-1,PACE['live'])]); S4['clip']=k; S4['tr']='fade'; sc.append(S4); tPUBv=round(t+24/PACE['tap']/30,3); tp.append(dict(t=tPUBv,x=round(taps[-1]['x']),y=round(taps[-1]['y'],1)))
tLive=round(t+24/PACE['tap']/30+(NF-1-tPUB)/(PACE['live']*30),3)
# captions: 5 chunks, ~1.4 s each, first one from T+0.1; c4 around the price tap, c5 from the publish tap
c=[CFG['caps'][0],CFG['caps'][1],CFG['caps'][3],CFG['caps'][4]]; a1=T+0.1
if n=='n44': times=[(a1,a1+1.4),(a1+1.5,a1+3.2),(a1+3.3,S3['t0']+0.9),(tUPv-0.05,tPUBv-0.15),(tPUBv+0.1,tLive+0.9)]
else: times=[(a1,a1+1.3),(a1+1.4,S3['t0']+0.4),(tUPv-0.05,tPUBv+0.05),(tPUBv+0.15,tLive+0.8)]
caps=[dict(l1=l1,l2=l2,a=round(a,3),b=round(b,3)) for (l1,l2),(a,b) in zip(c,times)]
rA=round(caps[-1]['b']+0.1,3); rB=round(rA+0.6,3); TE=round(rB+0.1,3); D=round(TE+2.3,3)
pOut=rA-0.1
pills=[[dict(t=round(caps[1]['a']+0.4,3),label=CFG['pills'][0][0],out=pOut),dict(t=round(caps[1]['a']+0.65,3),label=CFG['pills'][0][1],out=pOut)],
       [dict(t=round(tUPv+0.3,3),label=CFG['pills'][2][0],out=pOut)]]
# callouts (Nov 5 rule): frozen row crops. title+category after the fill (form scrolled to the title), price row after Use price
fT=400 if n=='n44' else FFILL+35; yP=508 if n=='n44' else 250  # Nov 15: price row + Use price sit at y 250-380 in the Nov 11/13 recordings; 456 is the offers/condition rows
cos=[dict(clip=k,x=12,y=92,w=369,h=124,a=round(caps[1]['a']+0.25,3),b=round(caps[1]['b']-0.1,3),f=fT,dx=0.5,dy=0.22),
     dict(clip=k,x=12,y=yP,w=369,h=130,a=round(tUPv+0.15,3),b=round(caps[2]['b']-0.1,3),f=tUP+24,dx=0.33,dy=0.4)]
op=dict(img=f'sit/{CFG["img"]}-9x16.jpg',imgw=f'sit/{CFG["img"]}-16x9.jpg',l1=CFG['l1'],l2=CFG['l2'],slot=None,move=CFG['move'])
if CFG.get('img2'): op.update(img2=f'sit/{CFG["img2"]}-9x16.jpg',imgw2=f'sit/{CFG["img2"]}-16x9.jpg',cut=CFG['cut'])
if CFG['label']: op['label']=dict(CFG['label'],b=round(T-0.15,3))
spec=dict(v=n,D=D,T=T,TE=TE,NF={k:NF},opener=op,scenes=sc,captions=caps,pills=pills,callouts=cos,taps=tp,
  result=dict(text=CFG['result']['text'],a=rA,b=rB,before=dict(img=op['img'],imgw=op['imgw'],label=CFG['result']['before'])),
  end=CFG['end'],sfx=[['hook-riser',round(T-1.1,2)],['camera-shutter',T],['tap',tp[0]['t']]]+sfx_cat+[['tap',tUPv],['tap',tPUBv],['listing-published',round(tPUBv+0.27,3)]])
json.dump(spec,open(f'r/spec/{n}.json','w'))
print(n,k,'NF',NF,'T',T,'TE',TE,'D',D,'live',tLive,'caps',[(x['a'],x['b']) for x in caps])
