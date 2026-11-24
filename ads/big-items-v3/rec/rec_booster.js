const {open,startRec,smooth,tap}=require('./lib');const W=(pg,ms)=>pg.waitForTimeout(ms);const fs=require('fs');
async function hold(pg,dir,n){const f=fs.readdirSync(dir).filter(x=>x.endsWith('.jpg')).length;const buf=await pg.screenshot({type:'jpeg',quality:95});for(let i=0;i<n;i++)fs.writeFileSync(`${dir}/${String(f+i).padStart(4,'0')}.jpg`,buf);}
(async()=>{const {b,pg}=await open({promo:'walk',scanDelay:1800});await pg.goto('http://localhost:8081/sell',{timeout:240000});await W(pg,6000);
 await pg.screenshot({path:'booster_start.png'});
 let stop=await startRec(pg,'raw/booster');await W(pg,1200);
 const [fc]=await Promise.all([pg.waitForEvent('filechooser',{timeout:10000}),tap(pg,pg.getByText('Choose from Library'))]);await W(pg,250);await fc.setFiles('booster.jpg');
 await W(pg,1400);const sn=pg.getByText('Scan now');if(await sn.isVisible().catch(()=>false)){await tap(pg,sn);}else console.log('NO SCAN NOW');
 await W(pg,3800);await pg.screenshot({path:'booster_filled.png'});
 for(const dy of [260,260,260]){await smooth(pg,dy,1100,388,500);await W(pg,500);}
 await pg.screenshot({path:'booster_mid.png'});await W(pg,800);await stop();
 await b.close();})();
