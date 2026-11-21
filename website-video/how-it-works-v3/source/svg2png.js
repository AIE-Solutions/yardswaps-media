const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({deviceScaleFactor:3});
for(const [src,out,h] of JSON.parse(process.argv[2])){
 const svg=fs.readFileSync(src,'utf8');
 await p.setContent(`<html><body style="margin:0;background:transparent"><img id=i src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}" style="height:${h}px;display:block"></body></html>`);
 await p.waitForTimeout(200);
 const el=await p.$('#i'); await el.screenshot({path:out,omitBackground:true});}
await b.close();})();
