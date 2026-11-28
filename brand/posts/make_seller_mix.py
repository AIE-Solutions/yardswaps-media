#!/usr/bin/env python3
"""Seller pieces across item types, in the k2 look (Alan, 2026-11-26: "I liek th eone syou made but we gotta
have a mixture of types of items", "theres more thing other than machines").

    python3 brand/posts/seller_photos.py <words from listing Reel slugs>   first: fetch the real photos
    python3 brand/posts/make_seller_mix.py [reels] [pairs] [slug ...]

reels  one 9:16 seller Reel per listing: "FREE TO LIST" + a hook that names the item, then "AI WRITES IT",
       then "NO SELLING FEE", then the seller end card. Lands in brand/posts/seller-mix-out/ as
       yardswaps-seller-<slug>-9x16-k2.mp4; copy to reels/library/, add the entry to reels/library.json
       ("cut": "seller", "real": true, "look": "k2") and run brand/endcard/endcard.py fix to mark the card.
pairs  Stories and 4:5 feed posts with two real photos side by side. The Story has no printed address: its
       link is the sticker added in Meta Business Suite, which sits on the light panel under the band
       (stories/linked/).

Rules: real photos of live listings only, the whole item in frame, no faces, plates or phone numbers, the
listing named on the wordmark row ("Shown: ..."). No single trade leads: vary the item types.
"""
import sys, os, json, random, subprocess, glob
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT+'/listings'); sys.path.insert(0, ROOT+'/brand/posts')
import listing_reels as lr, kit
from PIL import Image, ImageDraw
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=HERE+'/seller-src/'; OUT=HERE+'/seller-mix-out'
W,H,FPS=1080,1920,30
def P(frag,i=0):
    f=glob.glob(f'{SRC}*{frag}-{i}.jpg'); assert len(f)==1,(frag,i,f); return Image.open(f[0]).convert('RGB')

def sband(img, tag_text, head, body, wm_base, right, off=0):
    d=ImageDraw.Draw(img); width=W-2*kit.M
    kit.tag(img, tag_text, top=kit.TAG_TOP+off)
    lines=head if isinstance(head,(list,tuple)) else [head]
    size=86
    while max(kit.tracked_width(d,ln,kit.sg(size),0.0) for ln in lines)>width: size-=2
    y=(1012 if len(lines)>1 else 1011)+off
    for i,ln in enumerate(lines):
        if i: y+=86
        kit.tracked(d,(kit.M,y),ln,kit.sg(size),kit.INK,0.0,anchor="ls")
    if body:
        f=kit.inter(kit.SIZE_SECOND,b"Medium")
        bl=body.split('\n') if '\n' in body else kit.wrap(d,body,f,min(width,900),2)
        for j,ln in enumerate(bl):
            y+=66 if j==0 else 50
            d.text((kit.M,y),ln,font=f,fill=kit.GREY,anchor="ls")
    kit.wordmark_row(img,wm_base,right)
    return y

UP_TOP=1098+kit.UP_OFF+kit.UP_GAP
def ushot(photo, tag, head, body, credit):
    img=Image.new('RGB',(W,H),kit.WHITE)
    sband(img,tag,head,body,kit.MAST_BASE,'Shown: '+credit,off=kit.UP_OFF)
    kit._tall_slot(img,photo,UP_TOP)
    return img

def pair(a,b,gap=12,pa=(0.5,0.5),pb=(0.5,0.5)):
    """Two upright photos side by side in the 1080x720 photo slot, a thin white gutter between."""
    w=(W-gap)//2
    img=Image.new('RGB',(W,kit.PHOTO_H),kit.WHITE)
    img.paste(kit.cover(a,w,kit.PHOTO_H,pa),(0,0)); img.paste(kit.cover(b,w,kit.PHOTO_H,pb),(W-w,0))
    return img

def feed(top, tag, head, body, credit):
    img=Image.new('RGB',(W,kit.FEED_H),kit.WHITE)
    img.paste(top,(0,0)); sband(img,tag,head,body,1283,'Shown: '+credit)
    return img

def story(top, tag, head, body, credit):
    """kit.story() with the listing named on the wordmark row and no printed address: the link is the sticker
    added in Meta Business Suite, which sits on the light panel under the band."""
    o=kit.STORY_OFF
    img=Image.new('RGB',(W,H),kit.LIGHT)
    img.paste(top,(0,o))
    ImageDraw.Draw(img).rectangle((0,o+kit.PHOTO_H,W,o+1240),fill=kit.WHITE)
    sband(img,tag,head,body,1205+o,'Shown: '+credit,off=o)
    return img

def encode(shots, out, seed, secs=3.4, end=2.5):
    total=len(shots)*secs+end
    tracks=sorted(f for f in os.listdir(lr.MUSIC) if f.endswith('.mp3')) if os.path.isdir(lr.MUSIC) else []
    a=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-']
    if tracks:
        a+=['-i',os.path.join(lr.MUSIC,random.Random(seed).choice(tracks)),'-filter_complex',
            f'[1:a]atrim=0:{total},volume=0.35,afade=t=out:st={total-1.2}:d=1.2[a]','-map','0:v','-map','[a]','-c:a','aac','-b:a','128k']
    a+=['-c:v','libx264','-preset','medium','-crf','22','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-t',f'{total}',out]
    enc=subprocess.Popen(a,stdin=subprocess.PIPE)
    for s in shots:
        b=s.tobytes()
        for _ in range(int(secs*FPS)): enc.stdin.write(b)
    eb=lr.end_card().tobytes()
    for _ in range(int(end*FPS)): enc.stdin.write(eb)
    enc.stdin.close(); assert enc.wait()==0
    return round(total,1)

S2=('AI WRITES IT','SNAP A FEW PHOTOS','You check the listing before it posts.')
S3=('NO SELLING FEE','BUYERS MESSAGE YOU','They can make an offer. Local pickup only.')
# slug, photo fragment, photo indexes, hook (two lines), credit
REELS=[
 ('espresso-machine','q3nph',[0],['ESPRESSO MACHINE','NOT IN USE?'],'La Spaziale S11 Melodia'),
 ('walk-in-cooler','q3khm',[0,1,2],['WALK-IN COOLER','SITTING EMPTY?'],'Floral walk-in display cooler'),
 ('precision-tools','k5oda',[0],['TOOLS YOU','NO LONGER USE?'],'Mitutoyo micrometer set'),
 ('hvac-unit','uemvl',[0,1],['HVAC UNIT LEFT','FROM A JOB?'],'Goodman condenser and air handler'),
 ('pallet-racking','no15x',[0],['RACKING YOU','TOOK DOWN?'],'Pallet racking, complete lot'),
 ('spare-engine','dsydq',[0,1,2],['SPARE ENGINE','IN THE SHOP?'],'Komatsu HD785-7 engine'),
 ('kitchen-oven','s8tqf',[0],['KITCHEN GEAR','YOU REPLACED?'],'TurboChef Eco rapid-cook oven'),
 ('tool-cabinet','navll',[0],['TOOL CABINET','YOU OUTGREW?'],'Kennedy 8-drawer roller cabinet'),
 ('extra-mower','behok',[0],['EXTRA MOWER','IN THE SHOP?'],'Big Dog Hike T-36 mower'),
 ('generator','gyurk',[1,0],['GENERATOR YOU',"DON'T NEED?"],'Westinghouse WGen11500TFc'),
 # Second set, 2026-11-26 (Alan: "we need people to list more items like sellers"): seller Reels are now the
 # main share of each day, so the set has to be deep enough to rotate.
 ('packaging-machine','nr7e2',[1,0,2],['PACKAGING MACHINE','SITTING IDLE?'],'Instapak SpeedyPacker'),
 ('mini-excavator','2unc7',[1,0],['MINI EXCAVATOR','BETWEEN JOBS?'],'CAT 301.7CR mini excavator'),
 ('coffee-brewer','dwlxs',[0],['COFFEE BREWER','OFF THE COUNTER?'],'Bunn single-funnel brewer'),
 ('spare-controls','oupw3',[0,1],['SPARE PARTS','ON THE SHELF?'],'Genie Smart Link control module'),
 # ('wheels','ng1nl',...) removed: Alan 11-27 'Take those rims out'
 ('ice-maker','3uv4m',[0],['ICE MAKER','UNPLUGGED?'],'Osion OCU-200 ice maker'),
 ('tooling','o6blx',[0],['TOOLING YOU','STOPPED USING?'],'Kennametal indexable boring bars'),
 ('leaf-vacuum','tp04q',[0,1],['LEAF VACUUM DONE','FOR THE SEASON?'],'Billy Goat DL3700VE leaf vacuum'),
 ('convection-oven','1z3jc',[0],['CONVECTION OVEN','NOT IN USE?'],'Cadco Bakerlux convection oven'),
 ('sod-cutter','8m6yd',[0],['SOD CUTTER YOU','RARELY USE?'],'BlueBird SC18 sod cutter'),
 ('display-fridge','xrl5y',[0],['DISPLAY FRIDGE','TAKING UP SPACE?'],'Coldline G53 display refrigerator'),
 ('tool-chest','vp7u1',[0],['TOOL CHEST','GATHERING DUST?'],'Kennedy tool chest and roller cabinet'),
 ('coffee-grinder','vnu8r',[0],['COFFEE GRINDER','OFF THE BAR?'],'Bunn G9 coffee grinder'),
 ('stand-on-mower','bq30f',[0],['STAND-ON MOWER','SITTING OUT?'],'Ferris Z3X stand-on mower'),
]
BODY='Snap a photo and the AI writes the listing.\nNo selling fee. Local pickup.'
# slug, (fragA,iA), (fragB,iB), headline, credit
PAIRS=[
 ('coffee-gear',('q3nph',0),('vnu8r',0),'COFFEE GEAR IDLE?','La Spaziale S11 and Bunn G9'),
 ('walk-in-cooler',('q3khm',0),('q3khm',1),'COOLER SITTING EMPTY?','Floral walk-in display cooler'),
 ('shop-tools',('k5oda',0),('navll',0),"TOOLS YOU DON'T USE?",'Mitutoyo set and Kennedy cabinet'),
 ('hvac-units',('uemvl',0),('90evj',0),'HVAC LEFT FROM A JOB?','Goodman and FresKool units'),
 ('spare-engine',('dsydq',0),('dsydq',2),'SPARE ENGINE IN THE SHOP?','Komatsu HD785-7 engine'),
 ('kitchen-ovens',('s8tqf',0),('1z3jc',0),'REPLACED YOUR OVEN?','TurboChef and Cadco ovens'),
 ('yard-gear',('tp04q',0),('behok',0),'UPGRADED YOUR MOWER?','Billy Goat vacuum and Big Dog mower'),
]
if __name__=='__main__':
    # Slugs after reels/pairs build only those pieces (their photos must be in seller-src/).
    names=[a for a in sys.argv[1:] if a not in ('reels','pairs')]
    what=[a for a in sys.argv[1:] if a in ('reels','pairs')] or ['reels','pairs']
    os.makedirs(OUT,exist_ok=True)
    sheet=[]
    if 'reels' in what:
        for slug,frag,idx,hook,credit in REELS:
            if names and slug not in names: continue
            ph=[P(frag,i) for i in idx]
            shots=[ushot(ph[0],'FREE TO LIST',hook,'',credit),ushot(ph[1%len(ph)],*S2,credit),ushot(ph[2%len(ph)],*S3,credit)]
            secs=encode(shots,f'{OUT}/yardswaps-seller-{slug}-9x16-k2.mp4',slug)
            shots[0].save(f'{OUT}/seller-{slug}-cover.jpg',quality=90)
            for k,s in enumerate(shots): s.save(f'{OUT}/_f-{slug}-{k}.jpg',quality=85)
            print('reel',slug,secs,flush=True)
    if 'pairs' in what:
        for slug,(fa,ia),(fb,ib),head,credit in PAIRS:
            if names and slug not in names: continue
            top=pair(P(fa,ia),P(fb,ib))
            story(top,'LIST IT FREE',head,BODY,credit).save(f'{OUT}/story-{slug}.jpg',quality=92)
            feed(top,'LIST IT FREE',head,BODY,credit).save(f'{OUT}/seller-post-{slug}.jpg',quality=92)
            print('pair',slug,flush=True)
