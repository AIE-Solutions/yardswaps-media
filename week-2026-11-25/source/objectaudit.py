#!/usr/bin/env python3
"""objectaudit.py spec.json [...] : the "object matches script" check. Runs on the v2 render specs (video-upgrade/source/v2-port
+ r/spec/<id>.json in the render scratchpad) BEFORE a render, next to cropaudit.py (frames) and audioaudit.py (loudness) after it.

Why: the v2 opener is a match cut, so the opener photo becomes the listing photo on the phone. Alan 11-01: the forklift Short opened
on warehouse racks with no forklift in sight. Eleven of twenty openers showed a different machine than the recording. So:
  1. the opener photo's object must equal the object of the first phone recording (unless that recording is a mixed feed/profile)
  2. if the opener copy names a machine, it must be the same object
  3. every photo and recording a spec uses must be in the tables below; an unknown name fails, so new assets get tagged on purpose
Hand-maintained tables. Add a line when you add a sit/ photo or a recording. Exit 1 on any failure."""
import json, os, sys, re

PHOTO = {  # sit/<name>-9x16.jpg (and -16x9) or a bare snap-*.jpg -> what is in the picture
 'air-compressor':'compressor','generator-trailer':'generator','snap-compressor':'compressor','backhoe-on-trailer':'backhoe','boom-lift':'boom lift',
 'combi-ovens':'oven','combine-harvest':'combine','commercial-kitchen':'kitchen','concrete-mixer':'mixer','drain-crew':'jetter',
 'drill-sparks':'drill','drilling-rig':'drill rig','electrical-panel':'panel','enclosed-trailer':'trailer','excavator-dirt':'excavator',
 'farm-tractor':'tractor','flatbed-truck':'flatbed','forklift-yard':'forklift','grinder-sparks':'grinder','hard-hats':'people',
 'laundromat':'washer','machine-shop':'lathe','mini-excavator':'mini excavator','mobile-crane':'crane','office-furniture':'desk',
 'paving-roller':'roller','pickup-on-trailer':'pickup','pos-kiosk':'pos','real-cranedump':'crane dump truck','real-deere50':'tractor',
 'real-dozer':'dozer','real-hotsy':'pressure washer','real-hyundai':'excavator','real-pete':'day cab','real-takeuchi':'mini excavator',
 'real-tractor':'tractor','riding-mower':'mower','scissor-lifts':'scissor lift','snap-motor':'motor','surplus-cylinders':'hydraulic cylinder','part-tag':'hydraulic cylinder','micrometer-set':'micrometer','boring-bars':'boring bar','chop-saw':'chop saw','condenser-unit':'condenser','hotsy-washer':'pressure washer','air-mover':'air mover','truck-wheel':'wheel','anchor-adhesive':'adhesive cartridge','soil-compactor':'compactor',
 'tank-hoses':'tank','tool-chest':'tool chest','truck-lift':'truck lift','vacuum-truck':'vacuum truck','warehouse-racks':'racks','welding':'welder','donor-thumb':'excavator thumb','parts-wall':'gear lot','corp-stop':'corporation stop','pvc-fittings':'pipe fittings','well-pump':'well pump','copper-bins':'brass fittings','brass-valve':'brass fittings','combi-ovens-clean':'oven',
 'vacuum-truck-clean':'vacuum truck','tank-hoses-clean':'tank','machine-shop-clean':'lathe',
 'gear-motor':'motor','brass-fitting':'corporation stop','fittings-lot':'pipe fittings','dead-well-pump':'well pump','control-panel':'panel',  # Nov 15 re-records
 'trash-pump':'pump','inspection-camera':'camera','jetter-trailer':'jetter','beverage-cooler':'cooler','chain-hoist':'hoist',
 'welder-cart':'welder',
 'engine-welder':'welder','skid-steer':'skid steer','dump-trailer':'trailer','cord-reels':'cord reel','wrench-wall':'wrench lot',  # Nov 18
 'hot-pressure-washer':'pressure washer','towable-mixer':'mixer','scissor-lift':'scissor lift','engine-lathe':'lathe','office-chairs':'chair','real-90kwc7':'conveyor',  # Nov 20
 'real-enr7e2':'packer','real-3no15x':'racks','flat-top-griddle':'griddle','commercial-dryers':'dryer','hvac-condensers':'condenser','lawn-tractor':'mower','backhoe-lowboy':'backhoe',  # Nov 23
 'real-iq3khm':'cooler','real-sfmh3l':'plow','combi-oven':'oven','boom-lift-yellow':'boom lift','electrical-cabinet':'panel','drill-rig':'drill rig','vac-tank-truck':'vacuum truck',  # Nov 25
 'stick-welder':'welder','towable-compressor':'compressor','rooftop-unit':'rooftop unit','sprayer-rig':'sprayer','light-tower':'light tower','fryer-line':'fryer','zero-turn-mower':'mower','combi-oven':'oven','boom-lift-yellow':'boom lift','two-post-lift':'two-post lift','box-truck':'box truck','road-roller':'roller','safety-gear':'safety gear',
}
CLIP = {  # recording name -> the machine on screen in its first seconds ('any' = mixed feed, profile or empty form)
 'browse':'any','ogen':'any','opump':'any','listing':'backhoe','search':'forklift','follow':'mini excavator','starter':'compressor','craigslist':'flatbed',
 'store':'any','cats':'any','demand':'boom lift','inv1':'any','inv2':'any','chat':'forklift','offer':'forklift','offer2':'forklift',
 'sold':'flatbed','price':'compressor','fork':'forklift','sell':'compressor','cold':'compressor','part':'motor','part2':'hydraulic cylinder','tag':'hydraulic cylinder','mics':'micrometer','bars':'boring bar','saw':'chop saw','hvac':'condenser','hotsy':'pressure washer','mover':'air mover','wheel':'wheel','hilti':'adhesive cartridge','trailer':'trailer','thumb':'excavator thumb','gears':'gear lot','corp':'corporation stop','pvc':'pipe fittings','pump':'well pump','panel':'panel','rig':'drill rig','washer':'pressure washer','mixer':'mixer','valve':'brass fittings','compactor':'compactor','ovens':'oven','mower':'mower','kitchen':'kitchen','laundry':'washer','desks':'desk','kiosk':'pos',
 's_sell':'any','s_buy':'forklift','s_deal':'forklift','h2a':'flatbed','h2b':'flatbed','w_signup':'any','w_sell':'any','w_sell2':'any','w_boost':'any',
 'gen':'generator','vac':'vacuum truck','tank':'tank','chest':'tool chest','racks':'racks','scissor':'scissor lift','lathe':'lathe',
 'trashpump':'pump','camera':'camera','jetter':'jetter','cooler':'cooler','hoist':'hoist','import':'any',
 'motor':'motor','compressor':'compressor','cylinders':'hydraulic cylinder','fitting':'corporation stop','fittings':'pipe fittings','wellpump':'well pump','vactruck':'vacuum truck',  # Nov 15 re-records
 'stickwelder':'welder','towable':'compressor','rtu':'rooftop unit','sprayer':'sprayer','lighttower':'light tower','fryers':'fryer','zeroturn':'mower',  # Nov 16
 'migcart':'welder','engwelder':'welder','skid':'skid steer','dumptrailer':'trailer','reels':'cord reel','wrenches':'wrench lot',  # Nov 18
 'washer':'pressure washer','mixer':'mixer','flatbed':'flatbed','chairs':'chair','r90kwc7':'conveyor',  # Nov 20
 'renr7e2':'packer','r3no15x':'racks','griddle':'griddle','dryers':'dryer','condensers':'condenser','lawntractor':'mower','backhoe':'backhoe',  # Nov 23
 'riq3khm':'cooler','rsfmh3l':'plow','combioven':'oven','boomlift':'boom lift','ecabinet':'panel','drillrig':'drill rig','vactank':'vacuum truck',  # Nov 25
 'stats':'any','socials':'any','lift':'two-post lift','boxtruck':'box truck','roller':'roller','safety':'safety gear','w3_card':'any','w3_starter':'any','w3_credit':'any','w3_invite':'any','w6':'oven',
}
WORDS = {  # machine words a line of copy can name -> object (generic lines name none and pass)
 'compressor':'compressor','backhoe':'backhoe','boom lift':'boom lift','trailer':'trailer','excavator':'excavator','tractor':'tractor',
 'flatbed':'flatbed','forklift':'forklift','day cab':'day cab','dozer':'dozer','pressure washer':'pressure washer','motor':'motor',
 'mower':'mower','crane':'crane','skid steer':'skid steer','truck':'truck','welder':'welder','generator':'generator','mini excavator':'mini excavator','cylinder':'hydraulic cylinder','tag':'hydraulic cylinder','label':'hydraulic cylinder','micrometer':'micrometer','boring bar':'boring bar','chop saw':'chop saw','saw':'chop saw','condenser':'condenser','air mover':'air mover','wheel':'wheel','adhesive':'adhesive cartridge','cartridge':'adhesive cartridge','thumb':'excavator thumb','gears':'gear lot','corp stop':'corporation stop','pvc':'pipe fittings','well pump':'well pump','pump':'well pump','panel':'panel','drill rig':'drill rig','rig':'drill rig','mixer':'mixer','valve':'brass fittings',
 'trash pump':'pump','camera':'camera','jetter':'jetter','cooler':'cooler','hoist':'hoist','vacuum truck':'vacuum truck','vac truck':'vacuum truck','fittings':'pipe fittings','fitting':'corporation stop','corporation stop':'corporation stop',
 'rooftop unit':'rooftop unit','sprayer':'sprayer','light tower':'light tower','fryer':'fryer','zero-turn':'mower',
 'cord reel':'cord reel','reel':'cord reel','wrench':'wrench lot','dump trailer':'trailer','soldadora':'welder','genset':'generator','loader':'skid steer',
 'mixer':'mixer','scissor lift':'scissor lift','lathe':'lathe','chair':'chair','conveyor':'conveyor',
 'packer':'packer','racking':'racks','racks':'racks','griddle':'griddle','dryer':'dryer','lawn tractor':'mower',
 'plow':'plow','v-plow':'plow','cabinet':'panel','vac truck':'vacuum truck','combi oven':'oven',
 'oven':'oven','two-post lift':'two-post lift','box truck':'box truck','roller':'roller','hard hat':'safety gear','vest':'safety gear','safety gear':'safety gear',
}
def photo_obj(p):
    b = os.path.basename(p or ''); b = re.sub(r'-(9x16|16x9)\.jpg$', '', b); b = re.sub(r'\.jpg$', '', b)
    b = re.sub(r'^fit-', '', b)  # Nov 9: fitted whole-item originals (sit/fit-<name>.jpg, sit/lib/<name>.jpg) name the same object as the old crop
    b = re.sub(r'-clean$', '', b) if b not in PHOTO and re.sub(r'-clean$', '', b) in PHOTO else b
    return PHOTO.get(b), b
def clip_of(sc):
    return sc.get('src') or sc.get('clip') or sc.get('rec')
bad = 0
for f in sys.argv[1:]:
    s = json.load(open(f)); name = os.path.basename(f); op = s.get('opener') or {}
    probs = []
    if op:
        o, b = photo_obj(op.get('img'))
        if o is None: probs.append(f'opener photo {b!r} not in PHOTO table')
        copy = ((op.get('l1') or '') + ' ' + (op.get('l2') or '')).lower()
        named = {WORDS[w] for w in WORDS if re.search(r'\b' + re.escape(w) + r's?\b', copy)}
        named -= {'truck'} if o in ('flatbed', 'day cab', 'crane dump truck', 'vacuum truck', 'pickup') and 'truck' in named else set()
        if o and named and o not in named and not (o == 'mini excavator' and 'excavator' in named):
            probs.append(f'copy names {sorted(named)} but opener photo shows {o!r}')
        first = next((clip_of(c) for c in s.get('scenes', []) if clip_of(c)), None)
        co = CLIP.get(first)
        if first and co is None: probs.append(f'recording {first!r} not in CLIP table')
        elif co and co != 'any' and o and o != co: probs.append(f'opener photo shows {o!r} but the recording {first!r} shows {co!r}')
        elif co and co != 'any' and named and co not in named and not (co == 'mini excavator' and 'excavator' in named):
            probs.append(f'copy names {sorted(named)} but the recording {first!r} shows {co!r}')
    for c in s.get('scenes', []):
        cl = clip_of(c)
        if cl and cl not in CLIP: probs.append(f'recording {cl!r} not in CLIP table'); break
    print(('FAIL ' if probs else 'ok   ') + name + ('' if not probs else ': ' + '; '.join(probs)))
    bad += bool(probs)
sys.exit(1 if bad else 0)
