const USER={id:"u_demo",email:"demo@yardswaps.com",name:"Demo Seller",accountType:"INDIVIDUAL",verified:true,emailVerified:true,phoneVerified:true,sellerVerified:false,location:"Katy, TX",latitude:29.7858,longitude:-95.8245,createdAt:"2026-09-01T00:00:00Z",acceptedTermsAt:"2026-09-01T00:00:00Z",termsAccepted:true};
const fs0=require("fs");const UPIMG=process.env.UPIMG||"comp.jpg";
const SCAN={detected:true,confidence:"high",title:"Swan Belt-Drive Air Compressor, Horizontal Tank",manufacturer:"Swan",model:null,partNumber:null,year:null,category:"compressors",condition:"Used — Fair",
 description:"Swan belt-drive air compressor on a horizontal receiver tank with a twin-cylinder pump, electric motor, pressure gauge and wheels. Shows its age with surface wear and dirt from shop use. Inspect and run it at pickup.",
 specs:{"Drive":"Belt drive","Tank":"Horizontal"},suggestedPriceMin:350,suggestedPriceMax:650,priceBasis:"ai",priceExplanation:"AI estimate from the photos. Check similar listings before you set a price."};
if(process.env.SCANF)Object.assign(SCAN,JSON.parse(fs0.readFileSync(process.env.SCANF,"utf8")));
const LISTINGS=require('./listings');const fs=require('fs');
module.exports=async function mock(page,{scanDelay=2600,store=false,counter=false,promo=null}={}){
 const D=864e5,fut=ms=>new Date(Date.now()+ms).toISOString(),day=iso=>new Date(iso).toLocaleDateString('en-US',{month:'short',day:'numeric'});
 const ME=promo==='dealer'?{...USER,accountType:'DEALER',slug:'yourco',businessName:'Your Equipment Co.',name:'Your Equipment Co.'}:USER;
 const PUB={done:false,dealer:false};const STAT={};const WIN2=fut(14*D),WIN=fut(9*D),STX=fut(14*D),CRX=fut(7*D);
 const own=(id,extra={})=>{const L=LISTINGS.find(l=>l.id===id);return {...L,sellerId:ME.id,seller:{id:ME.id,name:ME.name,avatar:'YE',verified:true,slug:ME.slug||null,accountType:ME.accountType},location:'Katy, TX',activeBoost:null,pausedBoost:null,...extra};};
 const NEWROW=()=>({...own('demo-17'),id:'new1',title:promo==='starter'||promo==='walk'?SCAN.title:'Flatbed Work Truck, Dually',price:promo==='starter'||promo==='walk'?(SCAN.suggestedPriceMin&&SCAN.suggestedPriceMax?Math.round((SCAN.suggestedPriceMin+SCAN.suggestedPriceMax)/2/100)*100:500):24500,photoUrls:[promo==='starter'||promo==='walk'?'https://www.yardswaps.com/demo-img/'+UPIMG:'https://www.yardswaps.com/demo-img/50.jpg'],createdAt:new Date().toISOString()});
 const ownerRows=()=>{if(promo==='dealer') return ['demo-77','demo-88','demo-80','demo-85'].map(id=>own(id,id==='demo-77'&&PUB.dealer?{activeBoost:{tier:'dealer',expiresAt:CRX,free:false,label:'Dealer boost'}}:{}));
  const ids=promo==='sold'?['demo-50','demo-18','demo-48']:promo==='starter'?['demo-18','demo-47','demo-17']:promo==='walk'?[]:['demo-88','demo-64'];let rows=ids.map(id=>own(id,STAT[id]?{status:STAT[id]}:{}));if(PUB.done) rows=[NEWROW(),...rows];
  if(promo==='starter'&&PUB.done) rows=rows.map(r=>({...r,activeBoost:{tier:'starter',expiresAt:STX,free:true,label:'Starter boost'}}));
  if(promo==='craigslist'&&PUB.done) rows[0]={...rows[0],activeBoost:{tier:'credit',expiresAt:CRX,free:true,label:'Free boost'}};return rows;};
 const RULES=[{id:'starter',title:'Starter boost',line:'Post 4 listings within 14 days of your first and every listing you have is boosted free for 14 days. Anything you post while it runs is boosted too. Once per account.'},{id:'credits',title:'Boost credits',line:'Every 4 listings you post earns a free 7-day boost, up to 5. Credits never expire: spend one from the Boost button on any live listing, or when you publish.'},{id:'referral',title:'Invite a seller',line:'Share your invite link: you and the seller you invite both get a free 7-day boost after their first listing has been live for 3 days. It lands in the same credit balance.'}];
 const summary=()=>{const cp={enabled:true,every:4,max:5,days:7,count:3,progress:3,toNext:1,earned:0,pending:0,complete:false};
  const st={state:'locked',enabled:true,need:4,days:14,windowDays:14,count:3,toGo:1,windowEndsAt:WIN,expiresAt:null,boostedCount:0};let credits=0,next;
  if(promo==='walk'){const c=PUB.done?1:0;Object.assign(st,{count:c,toGo:4-c,windowEndsAt:PUB.done?WIN2:null});Object.assign(cp,{count:c,progress:c,toNext:4-c});next={id:'starter_locked',title:`Post ${4-c} more listings${PUB.done?' by '+day(WIN2):''}`,body:'Reach 4 and every listing you have is boosted free for 14 days.',cta:'List an item',href:'/sell'};}
  else if(promo==='starter'&&!PUB.done) next={id:'starter_locked',title:`Post 1 more listing by ${day(WIN)}`,body:'Reach 4 and every listing you have is boosted free for 14 days.',cta:'List an item',href:'/sell'};
  else if(promo==='starter'){Object.assign(st,{state:'active',count:4,toGo:0,windowEndsAt:null,expiresAt:STX,boostedCount:4});Object.assign(cp,{count:4,progress:0,toNext:4,earned:1});credits=1;next={id:'starter_active',title:'Starter boost: 4 listings boosted',body:'14 days left. Anything you post before it ends is boosted free too.',cta:'List an item',href:'/sell'};}
  else {Object.assign(st,{state:'used',count:4,toGo:0,windowEndsAt:null,expiresAt:fut(-2*D),boostedCount:4});credits=PUB.done?0:1;Object.assign(cp,{count:PUB.done?5:4,progress:PUB.done?1:0,toNext:PUB.done?3:4,earned:1});
   next=credits?{id:'credits_ready',title:'You have 1 free boost',body:'7 days each, and they never expire. Use one from the Boost button on any live listing or when you publish.',cta:'Use a free boost',href:'/account/listings'}:{id:'credits_progress',title:'Post 3 more listings for a free boost',body:'Every 4 listings you post earns a free 7-day boost.',cta:'List an item',href:'/sell'};}
  return {credits,creditDays:7,balanceLine:credits?`You have ${credits} free boost`:'No free boosts yet',starter:st,creditProgress:cp,referral:{enabled:true,code:'KATY42',link:'https://www.yardswaps.com/invite/KATY42',shareText:null,invited:0,rewarded:0,pending:0,rewardLine:'You both get a free 7-day boost after their first listing has been live for 3 days.'},rules:RULES,next};};
 const OFFERS=[];const FOLLOW={on:false,n:0};
 const t0=Date.now();const iso=ms=>new Date(t0-ms).toISOString();
 const SEARCHES=[{id:'ss0',name:'Boom lift',filters:JSON.stringify({search:'boom lift',location:'Katy, TX',radius:25}),notifyEmail:true,notifyPush:true,lastNotified:null,lastPushedAt:null,lastOpenedAt:iso(3*864e5),createdAt:iso(9*864e5),newMatchCount:3}];
 const MSGS=[{id:'m1',senderId:USER.id,text:'Hi, is the forklift still available?',createdAt:iso(26*60e3),reactions:[]},{id:'m2',senderId:'u_sample',text:'Yes, still here. It runs great and the forks are in good shape.',createdAt:iso(24*60e3),reactions:[]}];
 const REPLY='Saturday at 10 works. Bring cash and I can load it for you.';
 const F=LISTINGS.find(l=>l.id==='demo-80');
 const convo=()=>({id:'c1',listing:{id:F.id,title:F.title,price:F.price,photoUrls:F.photoUrls,sellerId:'u_sample',category:F.category,status:'active'},participants:[{userId:USER.id,lastReadAt:new Date().toISOString(),user:USER},{userId:'u_sample',lastReadAt:new Date().toISOString(),user:{id:'u_sample',name:'YardSwaps Demo',avatar:null,verified:true,emailVerified:true,phoneVerified:true,createdAt:'2026-08-01T00:00:00Z'}}],messages:MSGS.slice()});
 await page.route('**/demo-img/**',r=>r.fulfill({status:200,contentType:'image/jpeg',body:fs.readFileSync(__dirname+'/img/'+r.request().url().split('/').pop())}));
 await page.route('**/api/**',async route=>{
  const u=new URL(route.request().url()), p=u.pathname, m=route.request().method();
  const j=(b,s=200)=>route.fulfill({status:s,contentType:'application/json',body:JSON.stringify(b)});
  if(p==='/api/auth/signup'&&m==='POST'){await new Promise(r=>setTimeout(r,900));PUB.signed=true;return j({user:ME,token:'demo-token'});}
  if(p==='/api/auth/me'&&promo==='walk'&&!PUB.signed&&!(route.request().headers()['authorization']||'').includes('demo-token')) return j({error:'Unauthorized'},401);
  if(p==='/api/auth/me') return j({user:ME});
  if(promo&&p==='/api/free-boosts') return j(summary());
  if(promo==='craigslist'&&p.startsWith('/api/listings/price-guide')) return j({min:22000,max:27000,basis:'ai',confidence:'medium',explanation:'AI estimate from the photos. Check similar listings before you set a price.'});
  if(promo&&p==='/api/upload'&&m==='POST') return j({urls:['https://www.yardswaps.com/demo-img/'+UPIMG],url:'https://www.yardswaps.com/demo-img/'+UPIMG});
  if(promo&&p==='/api/import/craigslist'&&m==='POST'){await new Promise(r=>setTimeout(r,1500));const L=LISTINGS.find(l=>l.id==='demo-50');return j({listing:{title:L.title,price:L.price,description:'Dually flatbed work truck with steel deck and headache rack. Used daily on a crew until this year. Runs and drives, cold A/C, clean title.',condition:L.condition,manufacturer:null,model:null,year:L.year,category:L.category,photoUrls:L.photoUrls}});}
  if(promo&&p==='/api/listings'&&m==='POST'){PUB.done=true;const fb=promo==='walk'?{message:null,starter:null,creditsEarned:0,creditBoost:null,credits:0}:promo==='starter'?{message:`Starter boost on: 4 listings boosted free until ${day(STX)}. You earned 1 free boost.`,starter:{kind:'unlock',expiresAt:STX,days:14,boosted:4},creditsEarned:1,creditBoost:null,credits:1}
    :{message:`Your free boost runs until ${day(CRX)}.`,starter:null,creditsEarned:0,creditBoost:{expiresAt:CRX,creditsLeft:0},credits:0};
    return j({listing:{...NEWROW(),status:'active'},freeBoosts:fb});}
  if(promo==='sold'&&/^\/api\/listings\/demo-\d+$/.test(p)&&m==='PATCH'){const id=p.split('/')[3];const b=JSON.parse(route.request().postData()||'{}');if(b.status)STAT[id]=b.status;return j({listing:{...own(id),status:STAT[id]}});}
  if(promo&&p==='/api/listings'&&m==='GET'&&u.searchParams.get('sellerId')) {const r=ownerRows();return j({listings:r,total:r.length});}
  if(promo==='dealer'&&/^\/api\/listings\/demo-\d+$/.test(p)&&m==='GET'){const r=ownerRows().find(x=>x.id===p.split('/')[3]);if(r) return j({listing:r});}
  if(promo==='dealer'&&p.startsWith('/api/stripe/boost-status')){const run=PUB.dealer;return j({credits:0,creditDays:7,boost:run?{id:'b1',tier:'dealer',priorityValue:3,status:'active',paidAt:null,expiresAt:CRX,createdAt:new Date().toISOString(),free:false,dealer:true,label:'Dealer boost'}:null,tiers:[],located:true,listingStatus:'active',paidUntil:run?CRX:null,freeRunning:false,paused:null,lastBoost:null,
    dealerBoosts:{credits:run?4:5,perMonth:5,days:7,resetsAt:fut(20*D),trial:false,canUse:!run,reason:run?'already_boosted':null}});}
  if(promo==='dealer'&&/boost\/dealer$/.test(p)&&m==='POST'){await new Promise(r=>setTimeout(r,700));PUB.dealer=true;return j({boost:{tier:'dealer',expiresAt:CRX,free:false,dealer:true,label:'Dealer boost'},dealerCreditsLeft:4,resetsAt:fut(20*D)});}
  if(promo==='dealer'&&p==='/api/stripe/billing-summary') return j({hasBilling:true,accountType:'DEALER',plans:[],entitlements:{},prices:{},dealerTools:true,dealerBoosts:{credits:PUB.dealer?4:5,perMonth:5,days:7,resetsAt:fut(20*D),trial:false}});
  if(promo==='dealer'&&/^\/api\/dealers\/[^/]+\/demand$/.test(p)){const n=+(u.searchParams.get('days')||30);const k=n===90?2.6:1;const r5=x=>Math.max(5,Math.round(x/5)*5);const c=(id,name,s,z,sv,mk,y,ns)=>({id,name,searches:r5(s*k),zeroResultSearches:z?r5(z*k):0,savedSearches:sv?r5(sv*k):0,marketListings:mk,yourListings:y,needsSupply:ns});
    return j({window:{days:n,from:fut(-n*D),to:new Date().toISOString()},region:{kind:'radius',miles:50,label:'Katy, TX'},minSearchers:3,dataSince:'2026-10-04T00:00:00Z',
     categories:[c('aerial','Aerial Lifts',50,20,5,3,1,true),c('excavators','Excavators & Loaders',40,5,5,14,1,false),c('forklifts','Forklifts',35,10,5,6,1,true),c('paving','Paving & Compaction',15,5,0,2,1,true)],
     topSearches:[{term:'boom lift',count:r5(20*k),category:'aerial'},{term:'mini excavator',count:r5(15*k),category:'excavators'},{term:'scissor lift',count:r5(15*k),category:'aerial'},{term:'forklift',count:r5(10*k),category:'forklifts'},{term:'skid steer',count:r5(10*k),category:'excavators'}],
     zeroResultSearches:[{term:'60 ft boom lift',count:r5(10*k),category:'aerial'},{term:'telehandler',count:r5(5*k),category:'forklifts'},{term:'plate compactor',count:r5(5*k),category:'paving'}],
     savedSearchTerms:[{term:'boom lift',count:r5(5*k),category:'aerial'},{term:'forklift',count:r5(5*k),category:'forklifts'}]});}
  if(p==='/api/scan-label/status') return j({isPro:false,freeScansUsed:2,freeScansLimit:5,scansRemaining:3,priceLabel:"$9.99/mo",chargePolicy:"per_listing",allowanceLabel:"AI fills in the details from your photos · 3 free left"});
  if(p==='/api/scan-label'&&m==='POST'){await new Promise(r=>setTimeout(r,scanDelay));return j({scan:SCAN,photosAnalyzed:1,scansRemaining:2,isPro:false,scanSessionId:"ss_demo",charged:true});}
  if(p==='/api/listings'&&m==='GET'){let ls=LISTINGS;const q=(u.searchParams.get('search')||'').toLowerCase().trim(),c=u.searchParams.get('category');
    if(q) ls=ls.filter(l=>l.title.toLowerCase().includes(q.replace(/s$/,'')));if(c&&c!=='all') ls=ls.filter(l=>l.category===c);
    if(u.searchParams.get('ids')) ls=LISTINGS.filter(l=>u.searchParams.get('ids').split(',').includes(l.id));
    return j({listings:ls,total:ls.length});}
  if(p==='/api/saved'&&m==='GET') return j({saved:LISTINGS.filter(l=>['demo-77','demo-88'].includes(l.id))});
  if(p==='/api/saved-searches'&&m==='GET') return j({searches:SEARCHES});
  if(p==='/api/saved-searches'&&m==='POST'){const b=JSON.parse(route.request().postData()||'{}');const s={id:'ss'+(SEARCHES.length+1),name:b.name,filters:typeof b.filters==='string'?b.filters:JSON.stringify(b.filters),notifyEmail:true,notifyPush:true,lastNotified:null,lastPushedAt:null,lastOpenedAt:null,createdAt:new Date().toISOString(),newMatchCount:0};SEARCHES.unshift(s);return j({search:s,savedSearch:s});}
  if(p.startsWith('/api/saved-searches/')) return j({search:SEARCHES[0]});
  if(p==='/api/messages/conversations/c1'&&m==='GET') return j({conversation:convo()});
  if(p==='/api/messages/conversations/c1/messages'&&m==='POST'){const b=JSON.parse(route.request().postData()||'{}');const mm={id:'m'+(MSGS.length+1),senderId:USER.id,text:b.text,createdAt:new Date().toISOString(),reactions:[]};MSGS.push(mm);
    setTimeout(()=>MSGS.push({id:'m'+(MSGS.length+1),senderId:'u_sample',text:REPLY,createdAt:new Date().toISOString(),reactions:[]}),1500);return j({message:mm});}
  if(p.startsWith('/api/listings/demo-')&&m==='GET'&&p.split('/').length===4) return j({listing:LISTINGS.find(l=>l.id===p.split('/')[3])});
  if(p==='/api/offers'&&m==='POST'&&counter){const b=JSON.parse(route.request().postData()||'{}');const L=LISTINGS.find(l=>l.id===b.listingId);const base={listingId:b.listingId,buyerId:USER.id,sellerId:'u_sample',initiatedBy:'buyer',listing:{id:L.id,title:L.title,price:L.price,photoUrls:L.photoUrls},buyer:{id:USER.id,name:USER.name},seller:{id:'u_sample',name:'YardSwaps Demo'}};
   const o1={...base,id:'of1',amount:Math.round(b.amount*100),message:b.message||null,status:'countered',parentId:null,createdAt:new Date(Date.now()-1000).toISOString()};
   const o2={...base,id:'of2',amount:1400000,message:null,status:'pending',parentId:'of1',createdAt:new Date().toISOString()};OFFERS.push(o1,o2);return j({offer:o1,autoCountered:true,counterOffer:o2});}
  if(p.startsWith('/api/offers/of')&&m==='PATCH'){const o=OFFERS.find(x=>x.id===p.split('/').pop());const b=JSON.parse(route.request().postData()||'{}');if(o&&b.action==='accept'){o.status='accepted';o.acceptedAt=new Date().toISOString();}return j({offer:o});}
  if(p==='/api/offers'&&m==='POST'){const b=JSON.parse(route.request().postData()||'{}');const L=LISTINGS.find(l=>l.id===b.listingId);const o={id:'of1',listingId:b.listingId,buyerId:USER.id,sellerId:'u_sample',amount:Math.round(b.amount*100),message:b.message||null,status:'pending',initiatedBy:'buyer',createdBy:'buyer',createdAt:new Date().toISOString(),listing:{id:L.id,title:L.title,price:L.price,photoUrls:L.photoUrls},buyer:{id:USER.id,name:USER.name},seller:{id:'u_sample',name:'YardSwaps Demo'}};OFFERS.push(o);return j({offer:o});}
  if(p==='/api/offers'&&m==='GET') return j({offers:OFFERS});
  const DEALER={id:'u_sample',name:'YardSwaps Demo',businessName:store?'Your Equipment Co.':null,slug:'demo',avatar:store?'YE':'YD',logoUrl:null,accountType:store?'DEALER':'BUSINESS',verified:true,emailVerified:true,phoneVerified:true,sellerVerified:true,sellerVerifiedVia:'phone',
   bio:store?'Your storefront on YardSwaps. Every unit you list, in one place, with your hours and service area.':null,location:'Houston, TX',createdAt:'2026-03-01T00:00:00Z',businessHours:store?'Mon to Sat, 7 am to 5 pm':null,serviceArea:store?'Delivers across the Houston area':null,
   website:null,phone:null,ratingCount:0,avgRating:null,soldCount:0,activeListingCount:LISTINGS.length,isFollowing:FOLLOW.on,followerCount:FOLLOW.n,presence:null,complimentCounts:null};
  if(p==='/api/dealers/demo'||p==='/api/dealers/u_sample') return j({dealer:{...DEALER,isFollowing:FOLLOW.on,followerCount:FOLLOW.n}});
  if(/^\/api\/dealers\/[^/]+\/listings$/.test(p)){let ls=LISTINGS;const q=(u.searchParams.get('search')||'').toLowerCase().trim();if(q) ls=ls.filter(l=>(l.title+' '+l.category).toLowerCase().includes(q.replace(/s$/,'')));return j({listings:ls,total:ls.length});}
  if(p.startsWith('/api/ratings/')) return j({ratings:[],stats:{total:0,average:null,automatic:0}});
  if(p==='/api/sellers/u_sample/follow'){FOLLOW.on=m==='POST';FOLLOW.n+=FOLLOW.on?1:-1;return j({following:FOLLOW.on,followerCount:FOLLOW.n});}
  if(p==='/api/following') return j({sellers:FOLLOW.on?[{id:'u_sample',name:'YardSwaps Demo',businessName:null,avatar:'YD',slug:'demo',location:'Houston, TX',activeListingCount:LISTINGS.length,newListingCount:3}]:[]});
  if(p.startsWith('/api/listings/price-guide')) return j({min:SCAN.suggestedPriceMin||350,max:SCAN.suggestedPriceMax||650,basis:"ai",confidence:"high",explanation:SCAN.priceExplanation});
  if(p.startsWith('/api/stripe/boost-tiers')) return j({tiers:[]});
  if(p.startsWith('/api/free-boosts')) return j({});
  if(p.startsWith('/api/notifications')) return j({notifications:[],unread:0,unreadCount:0});
  if(p.startsWith('/api/conversations')||p.startsWith('/api/messages')) return j({conversations:[],unreadCount:0});
  return j({});
 });
};
