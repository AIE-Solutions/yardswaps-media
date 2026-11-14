#!/bin/bash
# start Expo web for recording on :8081 (background, production bundle so no dev overlay); pid in expo.pid
D=$(cd "$(dirname "$0")" && pwd)
cd /home/claude/Marketplace/apps/mobile
EXPO_OFFLINE=1 CI=1 EXPO_NO_TELEMETRY=1 BROWSER=none setsid npx expo start --web --port 8081 --no-dev --minify --clear > $D/expo.log 2>&1 &
echo $! > $D/expo.pid
