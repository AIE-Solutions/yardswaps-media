"""pickreal.py [N=2] : Nov 16 (Alan: "we usually get new users with new stuff daily so we can add them to promotion mix").
Pick real new listings for the next Shorts run from the Just-listed queue of the media repo (listings/queue.json): only
entries that passed the daily review gate (status approved or posted: no faces, names, plates, addresses), with the
cleaned uncropped photo in listings/photos/<id>.jpg, not used by Motion before (listings/motion-used.json), one per
seller, no forklifts, newest first. Writes cfg-real.json (mkdemo5 configs keyed r<id6>), the scan stubs
(rec/scan/<key>.json), the opener photos (v2p/sit/<img>-9x16.jpg and -16x9.jpg, same file) and the upload copies
(rec/<key>.jpg), then prints the batch.sh ID/ST lines and the objectaudit PHOTO/CLIP lines to add.
Run from the v2p folder (the one with batch.sh), with ../rec beside it. Copy rules: the listing's item and category
only; never the seller's name, phone, description or town; prices only as the app shows them."""
import json,os,re,sys,shutil,random
M=os.environ.get('MEDIA','/home/claude/yardswaps-media'); N=int(sys.argv[1]) if len(sys.argv)>1 else 2
q=json.load(open(f'{M}/listings/queue.json')); used={x if isinstance(x,str) else x.get('id') for x in json.load(open(f'{M}/listings/motion-used.json'))} if os.path.exists(f'{M}/listings/motion-used.json') else set()  # Nov 23: entries are dicts since Nov 20
OBJ={'fleet':'truck','trailers':'trailer','generators':'generator','pressure-washers':'pressure washer','vacuum-trucks':'vacuum truck','pumps':'pump','hydro-jetting':'jetter','pipe-inspection':'camera','compressors':'compressor','welding':'welder','metalworking':'lathe','auto-shop':'two-post lift','tools':'tool chest','excavators':'excavator','paving':'roller','aerial-lifts':'scissor lift','cranes':'hoist','concrete':'mixer','drilling':'drill rig','electrical':'panel','environmental':'tank','safety':'safety gear','agriculture':'sprayer','landscaping':'mower','restaurant':'kitchen','refrigeration':'cooler','cooking':'oven','warehouse':'racks','retail':'kiosk','office':'office furniture','laundry':'washer','hvac':'rooftop unit','parts':'parts'}
ASK={'fleet':'What is parked in your lot that never leaves?','parts':'What parts are stacked in your shop right now?','agriculture':'What is still parked at your field edge?','environmental':'What has not run since your last job?'}
out={}; picked=[]; sellers=set()
cand=[e for e in q if e.get('kind')!='wanted' and e.get('status') in ('approved','posted') and e.get('photo_file') and e['listing_id'] not in used and e.get('category')!='forklifts' and not e.get('opted_out')]
# Nov 16 (Alan): paying Pro/Dealer sellers' listings (feature 'paid', rank 1) first, then trial storefronts (rank 2), then newest.
cand.sort(key=lambda e:(e.get('feature')=='paid', -(e.get('rank') or 9), e.get('created') or e.get('added','')),reverse=True)
for e in cand:
    if len(picked)>=N: break
    if e.get('seller') in sellers: continue
    src=f"{M}/{e['photo_file']}"
    if not os.path.exists(src): print('no photo on disk',e['listing_id']); continue
    lid=e['listing_id']; key='r'+lid[-6:]; img='real-'+lid[-6:]; cat=e.get('category') or 'parts'
    title=e['title']; words=title.split(); short=title if len(title)<=34 else ' '.join(words[:4])
    cfg=dict(key=key,id='listed-'+re.sub(r'[^a-z0-9]+','-',short.lower()).strip('-')[:40],T=2.4,img=img,move=random.choice(['push','pan']),label=None,
        l1='Just listed on YardSwaps.',l2=short+'.',
        caps=[('Just listed?','Snap it.'),('AI fills it.','Title. Category.'),('AI wrote it.','Condition, specs.'),('Tap once.','Price set.'),('Published.','Listed free.')],
        pills=[['Title','Category'],['Condition','Specs'],['Price']],
        result=dict(text='One photo. No typing. Listed free.',before='Just listed'),
        end=dict(tag1='Real listing. One photo.',tag2='Free to list. No cut of the sale.',ask=ASK.get(cat,'What is sitting idle in your yard right now?')),
        listing_id=lid,category=cat,real=True)
    out[key]=cfg
    os.makedirs('sit',exist_ok=True); os.makedirs('../rec/scan',exist_ok=True)
    shutil.copy(src,f'sit/{img}-9x16.jpg'); shutil.copy(src,f'sit/{img}-16x9.jpg'); shutil.copy(src,f'../rec/{key}.jpg')
    p=e.get('price'); 
    scan=dict(title=title,manufacturer=None,category=cat,condition=e.get('condition') or 'Used — Good',
        description=f'{title}. Listed from one photo; details as shown in the listing. Inspect at pickup.',specs={},
        suggestedPriceMin=int(p*0.85) if p else None,suggestedPriceMax=int(p*1.1) if p else None)
    json.dump(scan,open(f'../rec/scan/{key}.json','w'))
    picked.append(e); sellers.add(e.get('seller'))
    print(f"picked {key} {cfg['id']} ({cat}) <- {lid}")
json.dump(out,open('cfg-real.json','w'),indent=1)
if picked:
    print('batch.sh ID:',' '.join(f"[{k}s]={c['id']}" for k,c in out.items())); print('batch.sh ST:',' '.join(f"[{k}s]={random.choice(['funk','lofi','road','clean','folk','shop'])}" for k in out))
    print('objectaudit PHOTO:',','.join(f"'{c['img']}':'{OBJ.get(c['category'],'any')}'" for c in out.values()),' CLIP:',','.join(f"'{k}':'{OBJ.get(c['category'],'any')}'" for k,c in out.items()))
    print('after deploy: add the ids to listings/motion-used.json and put "listing_id" and "real": true on the library entries')
else: print('no eligible real listings (none approved with a cleaned photo yet; the prep step saves photos from Nov 17)')
