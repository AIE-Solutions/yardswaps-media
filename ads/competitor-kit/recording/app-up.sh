#!/bin/bash
# Needs once per container: cd /home/claude/Marketplace && npm ci --ignore-scripts && npm i --no-save --ignore-scripts --workspace @yardswaps/mobile react-dom@19.2.0 react-native-web@~0.21.0
# LOCAL RECORDING ONLY: stub native modules for Expo web, start Expo. Undo with app-down.sh.
SP=$(cd "$(dirname "$0")" && pwd)
M=/home/claude/Marketplace/apps/mobile
mkdir -p $M/.rec-stubs && cp $SP/stubs/{maps,heycatch,securestore,alert}.js $M/.rec-stubs/
cat > $M/.rec-stubs/filesystem.js <<'E'
export const EncodingType = { Base64: "base64", UTF8: "utf8" };
export const cacheDirectory = "/cache/", documentDirectory = "/docs/";
export async function readAsStringAsync(uri) {
  const blob = await (await fetch(uri)).blob();
  return await new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(String(r.result).split(",")[1] || ""); r.onerror = rej; r.readAsDataURL(blob); });
}
export async function getInfoAsync(uri) { return { exists: true, uri, size: 1 }; }
export async function deleteAsync() {}
export async function writeAsStringAsync() {}
export async function copyAsync() {}
export async function makeDirectoryAsync() {}
E
R=$(cd /home/claude/Marketplace/node_modules/react-native-web/dist/exports/AccessibilityInfo && pwd)/index.js
cat > $M/.rec-stubs/a11y.js <<E
import A from '$R';
if (!A.announceForAccessibilityWithOptions) A.announceForAccessibilityWithOptions = (m) => A.announceForAccessibility && A.announceForAccessibility(m);
export default A;
E
cd $M && git checkout -- metro.config.js && python3 - <<'PY'
p='metro.config.js';s=open(p).read()
add='''// LOCAL RECORDING ONLY (not committed): web stubs for native-only modules.
const __STUBS = path.join(__dirname, '.rec-stubs') + '/';
const __base = config.resolver.resolveRequest;
config.resolver.resolveRequest = (context, moduleName, platform) => {
  if (platform === 'web') {
    const m = { 'react-native-maps': 'maps.js', '@heycatch/sdk': 'heycatch.js', 'expo-secure-store': 'securestore.js', 'expo-file-system/legacy': 'filesystem.js' }[moduleName];
    if (m) return { type: 'sourceFile', filePath: __STUBS + m };
    if (/^react-native-web\\/dist\\/(cjs\\/)?exports\\/Alert(\\/index(\\.js)?)?$/.test(moduleName) || (moduleName === './exports/Alert' && String(context.originModulePath).includes('react-native-web'))) return { type: 'sourceFile', filePath: __STUBS + 'alert.js' };
    if (moduleName === './exports/AccessibilityInfo' && !String(context.originModulePath).includes('.rec-stubs')) return { type: 'sourceFile', filePath: __STUBS + 'a11y.js' };
  }
  return (__base || context.resolveRequest)(context, moduleName, platform);
};
module.exports = config;'''
i=s.rindex('module.exports = config;');s=s[:i]+add+s[i+len('module.exports = config;'):]
open(p,'w').write(s)
PY
bash $SP/expo-up.sh
