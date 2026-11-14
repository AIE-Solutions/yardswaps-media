const {chromium}=require('/opt/node-tools/node_modules/playwright');const mock=require(process.env.MOCK||'./mock');const fs=require('fs');
const LOC=JSON.stringify({location:{latitude:29.7858,longitude:-95.8245,name:'Katy, TX'},radius:25});
async function open(o={}){o.role=o.role||process.env.ROLE||null;const b=await chromium.launch({args:['--force-device-scale-factor=3']});const ctx=await b.newContext({viewport:{width:393,height:778},deviceScaleFactor:3,isMobile:true,hasTouch:true});
 await ctx.addInitScript(([loc,noAuth])=>{if(!noAuth)localStorage.setItem('yardswaps_token','demo-token');localStorage.setItem('yardswaps_location_pref',loc);localStorage.setItem('yardswaps_push_softask','offer_made:1');
  const fix=()=>{for(const e of document.querySelectorAll('div,span')){if(e.childElementCount===0&&/^(Home|Messages|Saved|Account)$/.test(e.textContent)&&e.getBoundingClientRect().top>innerHeight-120){e.style.height='auto';e.style.overflow='visible';e.style.lineHeight='16px';}}};
  setInterval(fix,200);
  const st=document.createElement('style');st.textContent='::-webkit-scrollbar{display:none}*{scrollbar-width:none;outline:none!important}';document.addEventListener('DOMContentLoaded',()=>document.head.appendChild(st));},[LOC,!!o.noAuth]);
 const pg=await ctx.newPage();pg.on('pageerror',e=>console.log('PE',e.message.slice(0,200)));await mock(pg,o);return {b,pg};}
async function startRec(pg,dir){fs.rmSync(dir,{recursive:true,force:true});fs.mkdirSync(dir,{recursive:true});const cdp=await pg.context().newCDPSession(pg);const frames=[];
 cdp.on('Page.screencastFrame',async f=>{frames.push({t:f.metadata.timestamp,d:f.data});try{await cdp.send('Page.screencastFrameAck',{sessionId:f.sessionId})}catch(e){}});
 await cdp.send('Page.startScreencast',{format:'jpeg',quality:95,maxWidth:1179,maxHeight:2334,everyNthFrame:1});
 return async()=>{await new Promise(r=>setTimeout(r,300));await cdp.send('Page.stopScreencast');
  const t0=frames[0].t,t1=frames[frames.length-1].t;let k=0,j=0;for(let t=t0;t<=t1;t+=1/30){while(j+1<frames.length&&frames[j+1].t<=t)j++;fs.writeFileSync(`${dir}/${String(k++).padStart(4,'0')}.jpg`,Buffer.from(frames[j].d,'base64'));}
  fs.writeFileSync(dir+'/taps.json',JSON.stringify(TAPS.filter(p=>p.t>=t0).map(p=>({f:Math.round((p.t-t0)*30),x:p.x,y:p.y}))));TAPS.length=0;console.log(dir,frames.length,'raw',k,'out',(t1-t0).toFixed(1)+'s');};}
async function smooth(pg,dy,ms=900,x=200,y=450){await pg.mouse.move(x,y);const n=Math.round(ms/16);let done=0;for(let i=1;i<=n;i++){const e=0.5-Math.cos(Math.PI*i/n)/2;const tgt=Math.round(dy*e);await pg.mouse.wheel(0,tgt-done);done=tgt;await pg.waitForTimeout(16);}}
const TAPS=[];async function tap(pg,loc){await loc.scrollIntoViewIfNeeded().catch(()=>{});const bb=await loc.boundingBox();await pg.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2);TAPS.push({t:Date.now()/1000,x:bb.x+bb.width/2,y:bb.y+bb.height/2});await loc.click();}
module.exports={open,startRec,smooth,tap};
