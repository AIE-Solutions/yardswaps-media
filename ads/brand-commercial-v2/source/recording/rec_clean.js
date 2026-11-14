// Clean Hotsy walkthrough for the brand commercial: pick photo -> AI fills -> type price -> publish free
const {open,startRec,smooth,tap}=require('./lib');const W=(pg,ms)=>pg.waitForTimeout(ms);const fs=require('fs');
async function hold(pg,dir,n){const f=fs.readdirSync(dir).filter(x=>x.endsWith('.jpg')).length;const buf=await pg.screenshot({type:'jpeg',quality:95});for(let i=0;i<n;i++)fs.writeFileSync(`${dir}/${String(f+i).padStart(4,'0')}.jpg`,buf);}
async function scrollTo(pg,loc,y,ms){const bb=await loc.boundingBox();await smooth(pg,Math.round(bb.y-y),ms,200,500);}
(async()=>{const {b,pg}=await open({promo:'walk'});await pg.goto('http://localhost:8081/sell',{timeout:240000});await W(pg,6000);
 const stop=await startRec(pg,'raw/clean');const T0=Date.now();const mark=n=>console.log('MARK',n,((Date.now()-T0)/1000).toFixed(2));
 await W(pg,1200);mark('tap-library');
 const [fc]=await Promise.all([pg.waitForEvent('filechooser',{timeout:10000}),tap(pg,pg.getByText('Choose from Library'))]);await W(pg,200);await fc.setFiles('hotsy.jpg');mark('photo');
 await W(pg,7600);mark('filled');await W(pg,900);
 const price=pg.getByPlaceholder('Price').first();await scrollTo(pg,price,330,1000);await W(pg,400);mark('price');
 await tap(pg,price);await W(pg,250);await pg.keyboard.type('1200',{delay:170});mark('typed');await W(pg,1200);
 await pg.mouse.click(200,120);await W(pg,200);
 const pub=pg.getByLabel('Publish listing').last();await scrollTo(pg,pub,330,1300);await W(pg,700);mark('pub');
 await tap(pg,pub);await W(pg,2600);mark('live');await stop();await hold(pg,'raw/clean',45);await pg.screenshot({path:'clean_end.png'});
 await b.close();})();
