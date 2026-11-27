// node endrender.js <outdir> <seconds> <tag1> <tag2> <ask>   -> transparent PNG frames of the earlier walkthrough ending
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [out,secs,t1,t2,ask]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
 const b=await chromium.launch({args:['--allow-file-access-from-files']});const pg=await b.newPage({viewport:{width:1080,height:1920}});
 await pg.goto('file://'+__dirname+'/end.html?w=1080&h=1920&t1='+encodeURIComponent(t1)+'&t2='+encodeURIComponent(t2)+(ask?'&ask='+encodeURIComponent(ask):''));
 await pg.evaluate(()=>window.init());const N=Math.round(+secs*30);
 for(let i=0;i<N;i++){await pg.evaluate(t=>window.renderAt(t),i/30);await pg.screenshot({path:`${out}/${String(i).padStart(3,'0')}.png`,omitBackground:true});}
 await b.close();console.log(out,N);})();
