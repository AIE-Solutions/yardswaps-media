// One continuous take of the real app's listing flow (local app, mocked API: nothing reaches the live site).
const {open,startRec,smooth,tap,mark}=require('./lib');const W=(pg,ms)=>pg.waitForTimeout(ms);const fs=require('fs');
(async()=>{const {b,pg}=await open({promo:'walk'});await pg.goto('http://localhost:8081/sell',{timeout:240000});await W(pg,7000);
 const dir='raw/'+process.env.CLIP;
 const stop=await startRec(pg,dir);await W(pg,1300);mark('tap_photo');
 const [fc]=await Promise.all([pg.waitForEvent('filechooser',{timeout:10000}),tap(pg,pg.getByText('Take Photo'))]);await W(pg,350);await fc.setFiles(process.env.UPIMG);mark('photo_in');
 await pg.getByText(/AI filled in/).first().waitFor({timeout:20000}).catch(()=>console.log('no filled toast'));mark('filled');await W(pg,1100);
 await smooth(pg,330,1100,196,430);await W(pg,700);mark('price');
 const price=pg.getByPlaceholder('Price').first();await tap(pg,price);await W(pg,350);await pg.keyboard.type(process.env.PRICE,{delay:170});mark('priced');await W(pg,800);
 await smooth(pg,360,1100,196,430);await W(pg,800);mark('condition');
 await smooth(pg,420,1200,196,430);await W(pg,800);mark('specs');
 await smooth(pg,2600,1900,196,430);await W(pg,700);mark('bottom');
 await pg.screenshot({path:process.env.CLIP+'_pre.png'});
 await tap(pg,pg.getByLabel('Publish listing').last());mark('publish');await pg.getByText('Your listing is live!').waitFor({timeout:12000}).catch(async e=>{await pg.screenshot({path:process.env.CLIP+'_fail.png'});throw e;});mark('live');await W(pg,2400);mark('end');await stop();
 await pg.screenshot({path:process.env.CLIP+'_pub.png'});console.log(fs.readFileSync(dir+'/marks.json','utf8'));
 await b.close();})();
