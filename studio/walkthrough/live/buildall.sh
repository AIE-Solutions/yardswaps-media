#!/bin/bash
cd "$(dirname "$0")"
[ -d WORK/endc/e-espresso ] && [ "$(ls WORK/endc/e-espresso | wc -l)" = 87 ] || node WORK/endc/endrender.js WORK/endc/e-espresso 2.9 "Restaurant gear sells too. One photo each." "Free to list. No cut of the sale." "What gear is sitting in your back room?"
mkdir -p stills/espresso && python3 live.py c-espresso.json out/yardswaps-walkthrough-live-espresso-9x16.mp4 stills/espresso
[ -d WORK/endc/e-generator ] && [ "$(ls WORK/endc/e-generator | wc -l)" = 87 ] || node WORK/endc/endrender.js WORK/endc/e-generator 2.9 "Generators sell too. One photo each." "Free to list. No cut of the sale." "What gear is sitting in your garage?"
mkdir -p stills/generator && python3 live.py c-generator.json out/yardswaps-walkthrough-live-generator-9x16.mp4 stills/generator
[ -d WORK/endc/e-cooler ] && [ "$(ls WORK/endc/e-cooler | wc -l)" = 87 ] || node WORK/endc/endrender.js WORK/endc/e-cooler 2.9 "Coolers sell too. One photo each." "Free to list. No cut of the sale." "What equipment is taking up your floor space?"
mkdir -p stills/cooler && python3 live.py c-cooler.json out/yardswaps-walkthrough-live-cooler-9x16.mp4 stills/cooler
[ -d WORK/endc/e-toolcabinet ] && [ "$(ls WORK/endc/e-toolcabinet | wc -l)" = 87 ] || node WORK/endc/endrender.js WORK/endc/e-toolcabinet 2.9 "Shop gear sells too. One photo each." "Free to list. No cut of the sale." "What tools are sitting in your shop?"
mkdir -p stills/toolcabinet && python3 live.py c-toolcabinet.json out/yardswaps-walkthrough-live-toolcabinet-9x16.mp4 stills/toolcabinet
[ -d WORK/endc/e-boxtruck ] && [ "$(ls WORK/endc/e-boxtruck | wc -l)" = 87 ] || node WORK/endc/endrender.js WORK/endc/e-boxtruck 2.9 "Trucks sell too. One photo each." "Free to list. No cut of the sale." "What trucks are parked in your yard?"
mkdir -p stills/boxtruck && python3 live.py c-boxtruck.json out/yardswaps-walkthrough-live-boxtruck-9x16.mp4 stills/boxtruck
[ -d WORK/endc/e-trailer ] && [ "$(ls WORK/endc/e-trailer | wc -l)" = 87 ] || node WORK/endc/endrender.js WORK/endc/e-trailer 2.9 "Trailers sell too. One photo each." "Free to list. No cut of the sale." "What rigs are parked in your yard?"
mkdir -p stills/trailer && python3 live.py c-trailer.json out/yardswaps-walkthrough-live-trailer-9x16.mp4 stills/trailer
[ -d WORK/endc/e-racking ] && [ "$(ls WORK/endc/e-racking | wc -l)" = 87 ] || node WORK/endc/endrender.js WORK/endc/e-racking 2.9 "Warehouse gear sells too. One photo each." "Free to list. No cut of the sale." "What racking is stacked in your warehouse?"
mkdir -p stills/racking && python3 live.py c-racking.json out/yardswaps-walkthrough-live-racking-9x16.mp4 stills/racking
[ -d WORK/endc/e-mower ] && [ "$(ls WORK/endc/e-mower | wc -l)" = 87 ] || node WORK/endc/endrender.js WORK/endc/e-mower 2.9 "Lawn gear sells too. One photo each." "Free to list. No cut of the sale." "What mowers are parked in your shop?"
mkdir -p stills/mower && python3 live.py c-mower.json out/yardswaps-walkthrough-live-mower-9x16.mp4 stills/mower
