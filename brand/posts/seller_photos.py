#!/usr/bin/env python3
"""Pull the approved, privacy-cleaned photos of a few real listings for the seller pieces.

    python3 brand/posts/seller_photos.py espresso cooler micrometer ...   (words from the listing Reel slugs)

Saves brand/posts/seller-src/<listing reel slug>-<n>.jpg (not committed: the photos belong to the listings
and are re-fetched when needed). Only listings that already have a listing Reel in reels/library.json are
used, and only the same photos that Reel shows, so every photo has passed the face check and the plate and
phone blur. make_seller_mix.py reads this folder.
"""
import sys, os, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT+'/listings'); sys.path.insert(0, ROOT+'/brand/posts')
import listing_reels as lr, just_listed as jl, kit
import cv2, numpy as np
from PIL import Image
want=sys.argv[1:]
data=lr.fetch_all()
got=data.get('listings',data) if isinstance(data,dict) else data
active={l['id']:l for l in got if l.get('status','active')=='active'}
lib=lr.load_library(); vids=lib['videos']
rq=jl.load(lr.REEL_QUEUE,[]); queue=jl.load(jl.QUEUE,[])
latest={r["listing_id"]: r for r in rq if r.get("listing_id")}
cards={q["listing_id"]: q.get("photo_file") for q in queue if q.get("status") in ("approved","posted") and q.get("photo_file")}
out=os.path.dirname(os.path.abspath(__file__))+'/seller-src'; os.makedirs(out,exist_ok=True)
meta={}
for v in vids:
    if v.get('cut')!='listing' or v.get('listing_id') not in active: continue
    if not any(w in v['slug'] for w in want): continue
    l=active[v['listing_id']]
    photos,_=lr.same_photos(cv2,np,l,latest.get(l['id']),cards.get(l['id']))
    if not photos: continue
    names=[]
    for i,p in enumerate(photos):
        fn=f"{out}/{v['slug']}-{i}.jpg"; Image.fromarray(p).save(fn,quality=93); names.append(fn)
    meta[v['slug']]={'title':jl.spec_title(l),'raw_title':l.get('title'),'photos':names,'sizes':[Image.fromarray(p).size for p in photos],'category':l.get('category')}
    print(v['slug'], meta[v['slug']]['title'], meta[v['slug']]['sizes'], flush=True)
json.dump(meta,open(out+'/meta.json','w'),indent=1)
