const{chromium}=require('/Users/mattsidnell/Sites/pstructures-website/node_modules/playwright');
const path=require('path');
(async()=>{
 const b=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const urls=['concept03-cyan','concept03-yellow','concept03-dark'];
 let checks=[];
 for(const name of urls){
   const p=await b.newPage({viewport:{width:1440,height:900},ignoreHTTPSErrors:true,deviceScaleFactor:1});
   let errors=[];p.on('pageerror',e=>errors.push(e.message));
   let status=(await p.goto('http://127.0.0.1:8797/'+name+'/',{waitUntil:'networkidle',timeout:26000})).status();
   await p.evaluate(async()=>{for(const im of document.images)im.loading='eager';await Promise.all([...document.images].map(im=>im.decode().catch(()=>null)))});
   const d=await p.evaluate(()=>({width:document.documentElement.scrollWidth,innerWidth,projects:document.querySelectorAll('.project-card').length,broken:[...document.images].filter(i=>!i.naturalWidth).map(i=>i.src),color:getComputedStyle(document.body).backgroundColor}));
   await p.screenshot({path:'docs/assets/previews/'+name+'.jpg',type:'jpeg',quality:84,fullPage:false});
   await p.setViewportSize({width:390,height:844});await p.reload({waitUntil:'networkidle'});
   let m=await p.evaluate(()=>({width:document.documentElement.scrollWidth,innerWidth}));
   await p.locator('.menu').click();
   let menu=await p.locator('.nav').evaluate(e=>getComputedStyle(e).display);
   await p.locator('[data-filter="platform"]').click();let filtered=await p.locator('.more-projects article:not([hidden])').count();
   await p.screenshot({path:'screenshots/'+name+'-mobile.jpg',type:'jpeg',quality:68,fullPage:true});
   checks.push({name,status,desktop:d,mobile:m,menu,filtered,errors});
   await p.close();
 }
 const sel=await b.newPage({viewport:{width:390,height:844}});
 await sel.goto('http://127.0.0.1:8797/concept03/',{waitUntil:'networkidle'});
 const gallery=await sel.evaluate(()=>({width:document.documentElement.scrollWidth,innerWidth,conceptLinks:[...document.querySelectorAll('a[href]')].filter(a=>a.href.includes('concept03-')).length,broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).length}));
 await b.close();console.log(JSON.stringify({checks,gallery},null,2));
})().catch(e=>{console.error(e);process.exit(1)});
