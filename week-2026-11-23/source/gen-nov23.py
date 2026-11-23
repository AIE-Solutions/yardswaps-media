import json,sys
E=[
 dict(n='renr7e2',slug='listed-instapak-speedypacker-floor-model',cat='warehouse',catname='Warehouse',style='shop',hook='just-listed',angle='real-listing',real=True,listing_id='cmwpdczz50009tc3ao0enr7e2',
  h='Just listed on YardSwaps: an Instapak SpeedyPacker foam packaging machine.',
  p='A real listing, straight from the app: an Instapak SpeedyPacker floor model, the foam-in-bag packer from a packing line. One photo. AI wrote the title, filed it under Warehouse and drafted the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What machine is idle on your packing floor right now?',tags=['packaging','warehouse','packingline','usedequipment'],
  d='12 s, music shop. Demo format, Nov 23 Monday batch, real listing: the packer listing photo is the opener and the upload; copy names only the item and the category. Voice-free.'),
 dict(n='r3no15x',slug='listed-used-pallet-racking-complete',cat='warehouse',catname='Warehouse',style='folk',hook='just-listed',angle='real-listing',real=True,listing_id='cmwp8zzf0000jqt3a2d3no15x',
  h='Just listed on YardSwaps: a complete lot of used pallet racking.',
  p='A real listing, straight from the app: used pallet racking, a complete lot of beams, uprights and wire decks taken down from one warehouse. One photo. AI wrote the title, filed it under Warehouse and drafted the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What racking is on the floor since your last move?',tags=['palletracking','warehouse','racking','usedequipment'],
  d='12 s, music folk. Demo format, Nov 23 Monday batch, real listing: the racking listing photo is the opener and the upload; copy names only the item and the category. Voice-free.'),
 dict(n='n95',slug='griddle-from-the-closed-diner',cat='cooking',catname='Cooking Equipment',style='clean',hook='pov-idle',angle='idle-gear',
  h='POV: the diner closed. The griddle is still on the line.',
  p='A 36 inch natural gas flat top griddle, still on the line of a diner that closed. Snap one photo. AI writes the title, files it under Cooking Equipment and drafts the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What is still on the line in the kitchen you closed?',tags=['griddle','restaurantequipment','commercialkitchen','usedequipment'],
  d='12 s, music clean. Demo format, Nov 23 Monday batch: the flat top griddle fills the screen with the question box, then the sell flow with Condition and Fuel pills. Voice-free.'),
 dict(n='n96',slug='dryers-from-the-sold-laundromat',cat='laundry',catname='Commercial Laundry',style='lofi',hook='pov-idle',angle='idle-gear',
  h='POV: the laundromat sold. The dryers still line the wall.',
  p='A wall of gas stack dryers, coin op, from a laundromat that sold. Snap one photo. AI writes the title, files it under Commercial Laundry and drafts the description as a lot. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What is still bolted down in the store you sold?',tags=['laundromat','commerciallaundry','dryers','usedequipment'],
  d='12 s, music lofi. Demo format, Nov 23 Monday batch: the dryer wall fills the screen with the question box, then the sell flow as a lot listing with Condition and Heat pills. Second Commercial Laundry Short. Voice-free.'),
 dict(n='n97',slug='condensers-after-the-changeout',cat='hvac',catname='HVAC',style='tech',hook='pov-idle',angle='idle-gear',
  h='POV: the changeout is done. The old condensers sit by the pipes.',
  p='A lot of 5 ton condensing units pulled on a changeout, working when removed. Snap one photo. AI writes the title, files it under HVAC and drafts the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What came off the roof on your last changeout?',tags=['hvac','condenser','hvactech','usedequipment'],
  d='12 s, music tech. Demo format, Nov 23 Monday batch: the condensing units fill the screen with the question box, then the sell flow with Condition and Tons pills. Voice-free.'),
 dict(n='n98',slug='lawn-tractor-after-the-route',cat='landscaping',catname='Landscaping & Turf',style='road',hook='pov-idle',angle='idle-gear',
  h='POV: the mowing route ended. The lawn tractor sits by the barn.',
  p='A gas lawn tractor with a 42 inch deck, parked by the barn since the mowing route ended. Snap one photo. AI writes the title, files it under Landscaping & Turf and drafts the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What is parked by your barn since the route ended?',tags=['lawntractor','mower','landscaping','usedequipment'],
  d='12 s, music road. Demo format, Nov 23 Monday batch: the lawn tractor fills the screen with the question box, then the sell flow with Condition and Deck pills. Voice-free.'),
 dict(n='n99',slug='backhoe-still-on-the-trailer',cat='excavators',catname='Excavators & Loaders',style='funk',hook='pov-idle',angle='idle-gear',
  h='POV: the site work ended. The backhoe is still on the trailer.',
  p='A diesel 4x4 backhoe loader, still chained to the lowboy since the last site wrapped. Snap one photo. AI writes the title, files it under Excavators & Loaders and drafts the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What is still chained to the trailer from the last site?',tags=['backhoe','constructionequipment','heavyequipment','usedequipment'],
  d='12 s, music funk. Demo format, Nov 23 Monday batch: the backhoe on the lowboy fills the screen with the question box, then the sell flow with Condition and HP pills. The one heavy-iron cut this run, not first. Voice-free.'),
]
caps=[];lib=[];fmt={};pc=[];pe=[]
for i,e in enumerate(E):
    tags=' '.join('#'+t for t in e['tags']); tagsT=' '.join('#'+t[0].upper()+t[1:] for t in e['tags']); u='motion_'+e['slug'].replace('-','_')
    body=f"{e['h']}\n\n{e['p']}\n\n{e['close']}"
    tell='Tell us in the comments.'
    yd=f"{e['p']}\n\n{e['q']} {tell}"
    lf_t='List it free: yardswaps.com/t (link in bio). Get the app: search YardSwaps on the App Store or Google Play.'
    lf_y='List it free: yardswaps.com/y (link in our channel profile). Get the app: search YardSwaps on the App Store or Google Play.'
    caps.append(f"""## {e['slug']} (Nov 23, Monday batch, demo format{', real listing' if e.get('real') else ''}, {e['catname']})

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
    L=dict(added='2026-11-23',slug=e['slug'],file=f"reels/library/yardswaps-{e['slug']}-9x16.mp4",priority=i,body=body,question=e['q'],ig_tags=tags+' #yardswaps',category=e['cat'],cut='10s')
    if e.get('real'): L.update(listing_id=e['listing_id'],real=True)
    lib.append(L)
    fmt[e['slug']]=dict(hook=e['hook'],angle=e['angle'],category=e['cat'],demo=True,structure='problem-action-result',cut='10s',**({'real':True} if e.get('real') else {}))
    pc.append(json.dumps(e['slug'])+':'+json.dumps(dict(b=body+"\n\n"+e['q']+" "+tell,h=tags,yt=e['h']+' | YardSwaps',yd=yd),ensure_ascii=False)+',')
    pe.append(' {id:%s,t:%s,d:%s},'%(json.dumps(e['slug']),json.dumps(f"{e['h']} (New, Nov 23, {e['catname']})",ensure_ascii=False),json.dumps(e['d'],ensure_ascii=False)))
open('gen23-captions.md','w').write('\n'.join(caps)); json.dump(lib,open('gen23-lib.json','w'),indent=1,ensure_ascii=False); json.dump(fmt,open('gen23-fmt.json','w'),indent=1,ensure_ascii=False)
open('gen23-pagecaps.txt','w').write('\n'.join(pc)+'\n'); open('gen23-pageentries.txt','w').write('\n'.join(pe)+'\n'); print('ok',len(E))
