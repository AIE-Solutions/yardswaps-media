cd "$(dirname "$0")"
for k in riq3khm rsfmh3l combioven boomlift ecabinet drillrig vactank; do rm -rf raw/$k; echo "== rec $k $(date +%H:%M:%S)"; SCANF=scan/$k.json UPIMG=$k.jpg CLIP=$k timeout 400 node recsell.js 2>&1 | tail -3; echo "frames $(ls raw/$k 2>/dev/null | grep -c jpg)"; done; echo RECDONE25
