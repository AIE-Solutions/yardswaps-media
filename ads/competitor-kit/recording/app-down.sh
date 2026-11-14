SP=$(cd "$(dirname "$0")" && pwd)
kill -- -$(cat $SP/expo.pid) 2>/dev/null; cd /home/claude/Marketplace && git checkout -- apps/mobile/metro.config.js && rm -rf apps/mobile/.rec-stubs && git status --short
