import json,sys
E=[
 dict(n='r3tp04q',slug='listed-billy-goat-leaf-vacuum',cat='landscaping',catname='Landscaping & Turf',style='road',hook='just-listed',angle='real-listing',real=True,listing_id='cmwv95og80026t83akg3tp04q',
  h='Just listed on YardSwaps: a 2024 Billy Goat DL3700VE leaf vacuum, 400 hours, like new.',
  p='A real listing, straight from the app: a 2024 Billy Goat DL3700VE leaf and debris vacuum with 400 hours, like new. One photo. AI wrote the title, filed it under Landscaping & Turf and drafted the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What is parked in your shop until the leaves fall?',tags=['leafvacuum','billygoat','landscapingequipment','usedequipment'],
  d='12 s, music road. Demo format, Nov 27 Friday batch (made Nov 28), real listing: the leaf vacuum listing photo is the opener and the upload; copy names only the item and the category. Voice-free.'),
 dict(n='r5fbt0s',slug='listed-deere-50g-excavator',cat='excavators',catname='Excavators & Loaders',style='clean',hook='just-listed',angle='real-listing',real=True,listing_id='cmvsip9ad002jmp3arr5fbt0s',
  h='Just listed on YardSwaps: a zero-tail-swing Deere 50G excavator with a quick coupler.',
  p='A real listing, straight from the app: a zero-tail-swing John Deere 50G mini excavator with a quick coupler, used, good. One photo. AI wrote the title, filed it under Excavators & Loaders and drafted the description. Tap Use price, publish. No typing.',
  close='Free to list. No cut of the sale. Free boosts.',q='What machine sits in your yard between jobs?',tags=['miniexcavator','deere50g','excavator','usedequipment'],
  d='12 s, music clean. Demo format, Nov 27 Friday batch (made Nov 28), real listing: the excavator listing photo is the opener and the upload; copy names only the item and the category. Voice-free.'),
]
caps=[];lib=[];fmt={};pc=[];pe=[]
for i,e in enumerate(E):
    tags=' '.join('#'+t for t in e['tags']); tagsT=' '.join('#'+t[0].upper()+t[1:] for t in e['tags']); u='motion_'+e['slug'].replace('-','_')
    body=f"{e['h']}\n\n{e['p']}\n\n{e['close']}"
    tell='Tell us in the comments.'
    yd=f"{e['p']}\n\n{e['q']} {tell}"
    lf_t='List it free: yardswaps.com/t (link in bio). Get the app: search YardSwaps on the App Store or Google Play.'
    lf_y='List it free: yardswaps.com/y (link in our channel profile). Get the app: search YardSwaps on the App Store or Google Play.'
    caps.append(f"""## {e['slug']} (Nov 27, Friday batch, demo format{', real listing' if e.get('real') else ''}, {e['catname']})

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
    L=dict(added='2026-11-27',slug=e['slug'],file=f"reels/library/yardswaps-{e['slug']}-9x16.mp4",priority=i,body=body,question=e['q'],ig_tags=tags+' #yardswaps',category=e['cat'],cut='10s')
    if e.get('real'): L.update(listing_id=e['listing_id'],real=True,picture='real')
    lib.append(L)
    fmt[e['slug']]=dict(hook=e['hook'],angle=e['angle'],category=e['cat'],demo=True,structure='problem-action-result',cut='10s',**({'real':True} if e.get('real') else {}))
    pc.append(json.dumps(e['slug'])+':'+json.dumps(dict(b=body+"\n\n"+e['q']+" "+tell,h=tags,yt=e['h']+' | YardSwaps',yd=yd),ensure_ascii=False)+',')
    pe.append(' {id:%s,t:%s,d:%s},'%(json.dumps(e['slug']),json.dumps(f"{e['h']} (New, Nov 27, {e['catname']})",ensure_ascii=False),json.dumps(e['d'],ensure_ascii=False)))
open('gen27-captions.md','w').write('\n'.join(caps)); json.dump(lib,open('gen27-lib.json','w'),indent=1,ensure_ascii=False); json.dump(fmt,open('gen27-fmt.json','w'),indent=1,ensure_ascii=False)
open('gen27-pagecaps.txt','w').write('\n'.join(pc)+'\n'); open('gen27-pageentries.txt','w').write('\n'.join(pe)+'\n'); print('ok',len(E))
