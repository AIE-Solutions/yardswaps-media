import json,sys
E=[
 dict(n='riq3khm',slug='listed-floral-walk-in-display-cooler',cat='refrigeration',catname='Commercial Refrigeration',style='folk',hook='just-listed',angle='real-listing',real=True,listing_id='cmwsc8u1f001rqk3af9iq3khm',
  h='Just listed on YardSwaps: a floral walk-in display cooler with 8 glass doors.',
  p='A real listing, straight from the app: a floral walk-in display cooler with eight glass doors, new surplus. One photo. AI wrote the title, filed it under Commercial Refrigeration and drafted the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What cooler is standing empty in your store right now?',tags=['walkincooler','commercialrefrigeration','floralcooler','usedequipment'],
  d='12 s, music folk. Demo format, Nov 25 Wednesday batch, real listing: the cooler listing photo is the opener and the upload; copy names only the item and the category. Voice-free.'),
 dict(n='rsfmh3l',slug='listed-caterpillar-140h-v-plow',cat='landscaping',catname='Landscaping & Turf',style='road',hook='just-listed',angle='real-listing',real=True,listing_id='cmwosmtfl003bob3aetsfmh3l',
  h='Just listed on YardSwaps: a Caterpillar 140H V-plow.',
  p='A real listing, straight from the app: a V-plow blade for a Caterpillar 140H, used, sitting in the shop before the snow. One photo. AI wrote the title, filed it under Landscaping & Turf and drafted the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What plow is parked in your yard until the snow?',tags=['snowplow','vplow','snowremoval','usedequipment'],
  d='12 s, music road. Demo format, Nov 25 Wednesday batch, real listing: the plow listing photo is the opener and the upload; copy names only the item and the category. Voice-free.'),
 dict(n='n100',slug='combi-oven-after-the-remodel',cat='cooking',catname='Cooking Equipment',style='clean',hook='pov-idle',angle='idle-gear',
  h='POV: the hotel kitchen was remodeled. The combi oven came out whole.',
  p='A ten pan electric combi oven, three phase, pulled whole from a hotel kitchen remodel. Snap one photo. AI writes the title, files it under Cooking Equipment and drafts the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What came out of the kitchen on your last remodel?',tags=['combioven','restaurantequipment','commercialkitchen','usedequipment'],
  d='12 s, music clean. Demo format, Nov 25 Wednesday batch: the combi oven fills the screen with the question box, then the sell flow with Condition and Fuel pills. Voice-free.'),
 dict(n='n101',slug='boom-lift-after-the-fitout',cat='aerial',catname='Aerial Lifts',style='lofi',hook='pov-idle',angle='idle-gear',
  h='POV: the fitout wrapped. The boom lift is parked by the wall.',
  p='An electric articulating boom lift with a 30 foot platform, used on one fitout and parked by the wall since. Snap one photo. AI writes the title, files it under Aerial Lifts and drafts the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What lift is parked by your wall since the fitout?',tags=['boomlift','aeriallift','constructionequipment','usedequipment'],
  d='12 s, music lofi. Demo format, Nov 25 Wednesday batch: the boom lift fills the screen with the question box, then the sell flow with Condition and Reach pills. Voice-free.'),
 dict(n='n102',slug='control-cabinet-off-the-line',cat='electrical',catname='Electrical',style='tech',hook='pov-idle',angle='idle-gear',
  h='POV: the line shut down. The control cabinet is still on the wall.',
  p='A 480 volt industrial control cabinet with breakers, contactors and relays, still on the wall of a line that shut down. Snap one photo. AI writes the title, files it under Electrical and drafts the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What is still wired on the wall of the line you shut down?',tags=['controlpanel','electrical','industrialelectrical','usedequipment'],
  d='12 s, music tech. Demo format, Nov 25 Wednesday batch: the control cabinet fills the screen with the question box, then the sell flow with Condition and Volts pills. Voice-free.'),
 dict(n='n103',slug='drill-rig-between-contracts',cat='drilling',catname='Drilling & Boring',style='funk',hook='pov-idle',angle='idle-gear',
  h='POV: the drilling contract ended. The rig sits on the lot.',
  p='A truck-mounted water well drill rig rated to 600 feet, parked on the lot since the last contract ended. Snap one photo. AI writes the title, files it under Drilling & Boring and drafts the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What rig is parked on your lot between contracts?',tags=['drillrig','welldrilling','drilling','usedequipment'],
  d='12 s, music funk. Demo format, Nov 25 Wednesday batch: the drill rig fills the screen with the question box, then the sell flow with Condition and Depth pills. Voice-free.'),
 dict(n='n104',slug='vac-truck-after-the-season',cat='vacuum',catname='Vacuum Trucks',style='shop',hook='pov-idle',angle='idle-gear',
  h='POV: the pumping season ended. The vac truck sits in the lot.',
  p='A single axle vacuum tank truck, 2,500 gallons with a PTO pump, parked since the pumping season ended. Snap one photo. AI writes the title, files it under Vacuum Trucks and drafts the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What truck is parked in your lot since the season ended?',tags=['vacuumtruck','vactruck','septic','usedequipment'],
  d='12 s, music shop. Demo format, Nov 25 Wednesday batch: the vac truck fills the screen with the question box, then the sell flow with Condition and Tank pills. Second Vacuum Trucks Short, an empty-scorecard category. Voice-free.'),
]
caps=[];lib=[];fmt={};pc=[];pe=[]
for i,e in enumerate(E):
    tags=' '.join('#'+t for t in e['tags']); tagsT=' '.join('#'+t[0].upper()+t[1:] for t in e['tags']); u='motion_'+e['slug'].replace('-','_')
    body=f"{e['h']}\n\n{e['p']}\n\n{e['close']}"
    tell='Tell us in the comments.'
    yd=f"{e['p']}\n\n{e['q']} {tell}"
    lf_t='List it free: yardswaps.com/t (link in bio). Get the app: search YardSwaps on the App Store or Google Play.'
    lf_y='List it free: yardswaps.com/y (link in our channel profile). Get the app: search YardSwaps on the App Store or Google Play.'
    caps.append(f"""## {e['slug']} (Nov 25, Wednesday batch, demo format{', real listing' if e.get('real') else ''}, {e['catname']})

**Instagram**
```
{body}

{e['q']} {tell}

Link in bio.
{tags}
```

**TikTok**
```
{body}

{e['q']} Comment below.

{lf_t}
{tagsT}
```

**Facebook**
```
{body}

{e['q']} {tell}

Get the app: https://www.yardswaps.com/?utm_source=facebook&utm_medium=social&utm_campaign={u}
{' '.join('#'+t for t in e['tags'][:3])}
```

**YouTube**
```
{e['h']} | YardSwaps

{yd}

{lf_y}

{' '.join('#'+t for t in e['tags'][:3])}
```
""")
    L=dict(added='2026-11-25',slug=e['slug'],file=f"reels/library/yardswaps-{e['slug']}-9x16.mp4",priority=i,body=body,question=e['q'],ig_tags=tags+' #yardswaps',category=e['cat'],cut='10s')
    if e.get('real'): L.update(listing_id=e['listing_id'],real=True)
    lib.append(L)
    fmt[e['slug']]=dict(hook=e['hook'],angle=e['angle'],category=e['cat'],demo=True,structure='problem-action-result',cut='10s',**({'real':True} if e.get('real') else {}))
    pc.append(json.dumps(e['slug'])+':'+json.dumps(dict(b=body+"\n\n"+e['q']+" "+tell,h=tags,yt=e['h']+' | YardSwaps',yd=yd),ensure_ascii=False)+',')
    pe.append(' {id:%s,t:%s,d:%s},'%(json.dumps(e['slug']),json.dumps(f"{e['h']} (New, Nov 25, {e['catname']})",ensure_ascii=False),json.dumps(e['d'],ensure_ascii=False)))
open('gen25-captions.md','w').write('\n'.join(caps)); json.dump(lib,open('gen25-lib.json','w'),indent=1,ensure_ascii=False); json.dump(fmt,open('gen25-fmt.json','w'),indent=1,ensure_ascii=False)
open('gen25-pagecaps.txt','w').write('\n'.join(pc)+'\n'); open('gen25-pageentries.txt','w').write('\n'.join(pe)+'\n'); print('ok',len(E))
