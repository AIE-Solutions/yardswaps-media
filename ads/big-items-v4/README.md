# Too big to ship? List it free. (v4)

v4 (Nov 24): the owner asked "Does anyone really say the semi?". New voiceover (ElevenLabs v4, Justin Case, take A):
"Got something too big to ship? That old Peterbilt. A booster pump. A rock bucket. A whole cooling system. A V-plow.
List it free on YardSwaps. Snap a few photos, and the AI writes the listing. No selling fee. Local pickup."
The on-screen label reads "Peterbilt 379"; cuts retimed to the new read (16.6 s). Phone shot and everything else as v3 below.
Cuts: project files `yardswaps-campaign/assets/ads/big-items-v4/`; raw phone frames stay in `big-items-v3/rec/raw/booster`.

## v3

Same cut as v2 (semi truck, booster pump, rock bucket, cooling system, V-plow; 16.1 s, Justin Case VO), with one change
asked for by the owner on Nov 24: the phone shot now shows an item the ad just featured. The sell flow is recorded in the
real app with jim whitefield's booster pump photo (`src/booster-1.jpg`, the same photo the ad shows at 3.25 s), and the
fields fill in with that listing's details (Tigerflow ES-3000, Pumps & Motors, Tecumseh, OK, Used — Excellent).

- "List it free." (7.75 s): close on the booster photo going in as the cover, easing back to the whole phone.
- "Snap photos. The AI writes the listing." (9.70 s): title, category, place, price range and condition filled in.

Rebuild:
1. Recording (motion kit, `assets/motion/source/recording/`): `app-up.sh`, then from a folder holding these `rec/` files,
   the kit's `listings.js` and `stubs/`, and `img/booster.jpg` + `booster.jpg` (copies of `src/booster-1.jpg`):
   `UPIMG=booster.jpg SCANF=booster-scan.json LOCNAME="Tecumseh, OK" LOCLAT=35.2573 LOCLON=-96.9356 node rec_booster.js`.
   The scan answer is stubbed from the real listing (`booster-scan.json`); the screens are the real app.
2. `APPDIR=<raw/booster> python3 build.py 9x16 4x5 1x1` (clips/ from big-items-v2).

Cuts and raw frames: project files `yardswaps-campaign/assets/ads/big-items-v3/`. v1 and v2 are kept as they were.
