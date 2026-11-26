#!/bin/bash
cd "$(dirname "$0")"
for c in "$@"; do case $c in
 condenser) MOCK=./mock SCANF=scan-condenser.json UPIMG=condenser.jpg CLIP=condenser PRICE=2000 NOLOC=1 node reclive.js > log-condenser.txt 2>&1; tail -2 log-condenser.txt;;
 cooler) MOCK=./mock SCANF=scan-cooler.json UPIMG=cooler.jpg CLIP=cooler PRICE=19500 PLACE="Cleveland, TX" LAT=30.34 LNG=-95.08 node reclive.js > log-cooler.txt 2>&1; tail -2 log-cooler.txt;;
 toolcabinet) MOCK=./mock SCANF=scan-toolcabinet.json UPIMG=toolcabinet.jpg CLIP=toolcabinet PRICE=600 PLACE="New Waverly, TX" LAT=30.54 LNG=-95.48 node reclive.js > log-toolcabinet.txt 2>&1; tail -2 log-toolcabinet.txt;;
 boxtruck) MOCK=./mock SCANF=scan-boxtruck.json UPIMG=boxtruck.jpg CLIP=boxtruck PRICE=35495 PLACE="San Antonio, TX" LAT=29.42 LNG=-98.49 node reclive.js > log-boxtruck.txt 2>&1; tail -2 log-boxtruck.txt;;
 trailer) MOCK=./mock SCANF=scan-trailer.json UPIMG=trailer.jpg CLIP=trailer PRICE=35000 PLACE="Auburn, AL" LAT=32.61 LNG=-85.48 node reclive.js > log-trailer.txt 2>&1; tail -2 log-trailer.txt;;
 racking) MOCK=./mock SCANF=scan-racking.json UPIMG=racking.jpg CLIP=racking PRICE=39000 PLACE="Sanford, FL" LAT=28.8 LNG=-81.27 node reclive.js > log-racking.txt 2>&1; tail -2 log-racking.txt;;
 engine) MOCK=./mock SCANF=scan-engine.json UPIMG=engine.jpg CLIP=engine PRICE=155000 PLACE="Bellevue, WA" LAT=47.61 LNG=-122.2 node reclive.js > log-engine.txt 2>&1; tail -2 log-engine.txt;;
 generator) MOCK=./mock SCANF=scan-generator.json UPIMG=generator.jpg CLIP=generator PRICE=900 PLACE="Pearland, TX" LAT=29.56 LNG=-95.29 node reclive.js > log-generator.txt 2>&1; tail -2 log-generator.txt;;
 mower) MOCK=./mock SCANF=scan-mower.json UPIMG=mower.jpg CLIP=mower PRICE=2599 PLACE="St. Louis, MO" LAT=38.63 LNG=-90.20 node reclive.js > log-mower.txt 2>&1; tail -2 log-mower.txt;;
esac; done
