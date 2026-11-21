// How-it-works walkthrough (Nov 21): one Hotsy pressure washer, start to finish. node recwt.js sell|buy|store
const {open,startRec,smooth,tap}=require('./lib');const W=(pg,ms)=>pg.waitForTimeout(ms);const fs=require('fs');
async function hold(pg,dir,n){const f=fs.readdirSync(dir).filter(x=>x.endsWith('.jpg')).length;const buf=await pg.screenshot({type:'jpeg',quality:95});for(let i=0;i<n;i++)fs.writeFileSync(`${dir}/${String(f+i).padStart(4,'0')}.jpg`,buf);}
const top=async(pg,re)=>pg.evaluate((src)=>{const r=new RegExp(src);const e=[...document.querySelectorAll('div,span')].find(d=>d.childElementCount===0&&r.test(d.textContent));return e?e.getBoundingClientRect().top:null;},re.source);
(async()=>{const which=process.argv[2];
if(which==='sell'){const {b,pg}=await open({promo:'walk'});await pg.goto('http://localhost:8081/sell',{timeout:240000});await W(pg,8000);
 let stop=await startRec(pg,'raw/wt-tips');await W(pg,1800);await tap(pg,pg.getByText('Photo tips for the best AI listing').first());await W(pg,4500);await stop();
 stop=await startRec(pg,'raw/wt-scan');await W(pg,900);
 const [fc]=await Promise.all([pg.waitForEvent('filechooser',{timeout:10000}),tap(pg,pg.getByText('Choose from Library').first())]);await W(pg,300);await fc.setFiles(['img/hotsy.jpg','img/hotsy-label.jpg']);
 await W(pg,9500);await pg.screenshot({path:'probe/w_scan.png'});await stop();
 // specs: open "Add specs & details" so Manufacturer: Hotsy shows
 stop=await startRec(pg,'raw/wt-specs');await W(pg,600);
 let t;if(await pg.getByText(/Add specs & details/).count()){const tg=pg.getByText(/Add specs & details/).first();t=await top(pg,/Add specs & details/);await smooth(pg,Math.max(0,(t||900)-420),2600,196,500);await W(pg,800);await tap(pg,tg);await W(pg,1200);}
 t=await top(pg,/^Manufacturer$|^MANUFACTURER$/i);console.log('manu top',t);await smooth(pg,Math.max(0,(t||300)-260),1600,196,500);await W(pg,3500);await pg.screenshot({path:'probe/w_specs.png'});await stop();
 // price
 stop=await startRec(pg,'raw/wt-price');await W(pg,500);t=await top(pg,/^Suggested price$/);await smooth(pg,(t||300)-330,2400,196,500);await W(pg,1500);
 await tap(pg,pg.getByText('Use price').first());await W(pg,3000);await pg.screenshot({path:'probe/w_price.png'});await stop();
 // publish
 stop=await startRec(pg,'raw/wt-pub');await W(pg,500);await smooth(pg,-4000,2000,196,400);await W(pg,1300);
 await tap(pg,pg.getByText('Publish',{exact:true}).last());await W(pg,4500);await pg.screenshot({path:'probe/w_pub.png'});
 const vl=pg.getByText('View Listing').first();if(await vl.count()){await tap(pg,vl);await W(pg,4500);}else console.log('NO VIEW LISTING');
 await pg.screenshot({path:'probe/w_live.png'});await stop();await hold(pg,'raw/wt-pub',30);await b.close();}
if(which==='buy'){const {b,pg}=await open({});await pg.goto('http://localhost:8081/',{timeout:240000});await W(pg,8000);
 let stop=await startRec(pg,'raw/wt-search');await W(pg,1500);const sb=pg.getByPlaceholder(/Search equipment/).first();await tap(pg,sb);await W(pg,500);
 await pg.keyboard.type('pressure washer',{delay:110});await W(pg,400);await pg.keyboard.press('Enter');await W(pg,2600);await pg.screenshot({path:'probe/w_res.png'});
 await tap(pg,pg.getByText(/Hotsy Hot Water/).first());await W(pg,3000);await smooth(pg,420,2600,196,450);await W(pg,2600);await pg.screenshot({path:'probe/w_detail.png'});await stop();
 stop=await startRec(pg,'raw/wt-offer');await W(pg,600);await tap(pg,pg.getByText('Make an Offer').first());await W(pg,1600);
 await tap(pg,pg.getByText('$2,200').first());await W(pg,1400);await tap(pg,pg.getByLabel('Send offer').first());await W(pg,3200);await pg.screenshot({path:'probe/w_offer.png'});await stop();
 stop=await startRec(pg,'raw/wt-chat');await W(pg,600);await tap(pg,pg.getByText('Check Availability').first());await W(pg,2200);
 await tap(pg,pg.getByLabel('Send message').first());await W(pg,6500);await pg.screenshot({path:'probe/w_chat.png'});await stop();await hold(pg,'raw/wt-chat',20);await b.close();}
if(which==='store'){const {b,pg}=await open({store:true});
 await pg.addInitScript(()=>{navigator.share=async()=>{const t=document.createElement('div');t.textContent='Link copied';Object.assign(t.style,{position:'fixed',left:'50%',bottom:'96px',transform:'translateX(-50%)',background:'#1A3353',color:'#fff',font:'600 15px Inter,system-ui,sans-serif',padding:'12px 18px',borderRadius:'9999px',zIndex:9999,whiteSpace:'nowrap'});document.body.appendChild(t);setTimeout(()=>t.remove(),2600);};});
 await pg.goto('http://localhost:8081/dealer/demo',{timeout:240000});await W(pg,8000);
 let stop=await startRec(pg,'raw/wt-store');await W(pg,2200);await smooth(pg,560,3000,196,500);await W(pg,1800);await smooth(pg,420,2600,196,500);await W(pg,1800);
 await smooth(pg,-980,2200,196,500);await W(pg,900);await tap(pg,pg.getByLabel('Share storefront').first());await W(pg,2800);await pg.screenshot({path:'probe/w_store.png'});await stop();
 await pg.goto('http://localhost:8081/plans?plan=dealer');await W(pg,6000);
 stop=await startRec(pg,'raw/wt-plans');await W(pg,4000);await smooth(pg,420,3200,196,500);await W(pg,3000);await pg.screenshot({path:'probe/w_plans.png'});await stop();await hold(pg,'raw/wt-plans',20);await b.close();}
})();
