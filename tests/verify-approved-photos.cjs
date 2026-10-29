const {chromium}=require('/Users/mattsidnell/Sites/pstructures-website/node_modules/playwright');const fs=require('fs');
(async()=>{
 const b=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const paths=['/concept03/','/concept03-cyan/','/concept03-yellow/','/concept03-dark/','/digipixel-email-signature/'];let output=[];
 for(const path of paths){
  const p=await b.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});const errs=[];p.on('pageerror',e=>errs.push(e.message));
  const response=await p.goto('http://127.0.0.1:8797'+path,{waitUntil:'networkidle',timeout:28000});
  await p.evaluate(async()=>{for(const img of document.images){img.loading='eager'}await Promise.all([...document.images].map(x=>x.decode().catch(()=>{})))});
  if(path==='/concept03/'){await p.locator('#about').scrollIntoViewIfNeeded();await p.screenshot({path:'screenshots/approved-about-desktop.jpg',type:'jpeg',quality:84});}
  if(path==='/digipixel-email-signature/'){await p.screenshot({path:'screenshots/digipixel-email-sig.jpg',type:'jpeg',quality:83});}
  const desktop=await p.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,window:innerWidth,imgCount:document.images.length,brokenImgs:[...document.images].filter(i=>!i.naturalWidth).map(i=>i.src),seated:!!document.querySelector('img[src*="matt-seated.webp"]'),headshot:!!document.querySelector('img[src*="matt-digipixel-400.jpg"]'),hasCorrectEmail:document.body.textContent.includes('matt@digipixel.uk')||document.body.innerHTML.includes('me@mattsidnell.co.uk')}));
  await p.setViewportSize({width:390,height:844});await p.reload({waitUntil:'networkidle'});const mobile=await p.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,window:innerWidth}));
  output.push({path,http:response.status(),desktop,mobile,errors:errs});await p.close();
 }
 await b.close();console.log(JSON.stringify(output,null,2));})().catch(e=>{console.error(e);process.exit(1)});
