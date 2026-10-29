const{chromium}=require('/Users/mattsidnell/Sites/pstructures-website/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const p=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 for(const width of [1440,390]){
  await p.setViewportSize({width,height:900});
  let res=await p.goto('http://127.0.0.1:8797/concept03/',{waitUntil:'networkidle',timeout:30000});
  const photo=p.locator('.about-portrait img');
  await photo.scrollIntoViewIfNeeded();await photo.evaluate(i=>i.decode());
  const check=await p.evaluate(()=>({pageWidth:document.documentElement.scrollWidth,windowWidth:innerWidth,portraitImages:document.querySelectorAll('.about-portrait img').length,portraitLoaded:[...document.querySelectorAll('.about-portrait img')].every(i=>i.complete&&i.naturalWidth===850),contactEmail:[...document.querySelectorAll('a[href^="mailto:"]')].every(a=>a.getAttribute('href').includes('me@mattsidnell.co.uk'))}));
  await p.screenshot({path:'screenshots/portfolio-portrait-'+width+'.jpg',quality:80,type:'jpeg'});
  console.log(JSON.stringify({width,status:res.status(),...check}));
  if(check.pageWidth>width||!check.portraitLoaded||!check.contactEmail)process.exitCode=1;
 }
 const sig=await browser.newPage({viewport:{width:650,height:340}});
 await sig.goto('http://127.0.0.1:8797/assets/digipixel-email-signature.html',{waitUntil:'domcontentloaded'});
 const content=await sig.locator('body').innerText();
 console.log(JSON.stringify({signature:content.slice(0,280),hostedImage:await sig.locator('img').getAttribute('src'),errors}));
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
