// Walkthrough feed (Nov 21). Real YardSwaps listing photos; titles, prices and places are demo values.
const L=[
 ['hotsy','Hotsy Hot Water Pressure Washer, Electric','pressure',2300,'Used — Good',null,null,null,'Katy, TX',2,['hotsy','hotsy-label']],
 ['excavator','Excavator, 14 Ton, Enclosed Cab','excavators',68500,'Used — Good',2018,3900,null,'Houston, TX',8],
 ['telehandler','Telehandler, 10,000 lb','forklifts',47500,'Used — Good',2016,4100,null,'Pasadena, TX',13],
 ['condenser','Goodman Condenser, 3 Ton','hvac',900,'Used — Good',2021,null,null,'Sugar Land, TX',11],
 ['tractor','Utility Tractor with Cab, 4WD','agriculture',41000,'Used — Good',2017,2300,null,'Waller, TX',19],
 ['rolloff','Roll-Off Truck with Container','fleet',52000,'Used — Good',2015,null,141000,'Baytown, TX',22],
 ['toolbox','Rolling Tool Chest Set','tools',650,'Used — Good',null,null,null,'Cypress, TX',9],
 ['skidsteer','Compact Track Loader','excavators',39000,'Used — Good',2019,2100,null,'Conroe, TX',27],
 ['jettrailer','Trailer-Mounted Water Jetter','hydro',14500,'Used — Good',2017,null,null,'Houston, TX',15],
 ['wheel','Aftermarket Truck Wheel, 8-Lug','parts',350,'Used — Excellent',null,null,null,'Fulshear, TX',7],
 ['airmover','Air Mover, Axial Fan','environmental',180,'Used — Good',null,null,null,'Brookshire, TX',11],
 ['chopsaw','Chop Saw, 12 in','tools',140,'Used — Good',null,null,null,'Richmond, TX',14],
 ['minix','Mini Excavator, Rubber Tracks','excavators',27500,'Used — Good',2019,1650,null,'Katy, TX',5],
 ['mics','Outside Micrometer Set in Case','machining',420,'Used — Excellent',null,null,null,'Stafford, TX',16],
];
const DESC={hotsy:'Hotsy hot water pressure washer on a four-wheel cart, with an electric motor, a heated tank and a coiled hose. Brand read from the label on the tank. Shows wear on the paint from shop use. Inspect and run it at pickup.'};
module.exports=L.map(([img,title,category,price,condition,year,hours,mileage,location,dist,photos],i)=>({
 id:'demo-'+img,title,category,price,condition,year,hours,mileage,location,distance:dist,
 description:DESC[img]||`${title}. Inspect and run it at pickup. Message with questions.`,
 specs:{},manufacturer:img==='hotsy'?'Hotsy':null,featured:false,priority:0,photoUrls:(photos||[img]).map(p=>`https://www.yardswaps.com/demo-img/${p}.jpg`),
 status:'active',createdAt:new Date(Date.now()-(i*5+2)*3600e3).toISOString(),updatedAt:new Date().toISOString(),
 sellerId:'u_sample',seller:{id:'u_sample',name:'YardSwaps Demo',avatar:'YD',verified:true,slug:'demo',accountType:'BUSINESS',rating:null,ratingCount:0},
 viewsLabel:null,savesLabel:null,quantity:1}));
