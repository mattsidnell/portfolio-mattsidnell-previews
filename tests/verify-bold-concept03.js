const {chromium}=require('/Users/mattsidnell/Sites/pstructures-website/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const root='http://127.0.0.1:8797';
 let results=[];
 for(const path of ['/studio/','/concept03-yellow/','/concept03-cyan/','/concept03-dark/']){
  const p=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});const errors=[];p.on('pageerror',e=>errors.push(e.message));
  const res=await p.goto(root+path,{waitUntil:'networkidle',timeout:30000});
  await p.evaluate(async()=>{for(const image of document.images){image.loading='eager'}await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))});
  const name=path.split('/')[1];
  await p.screenshot({path:'docs/assets/previews/'+(name==='studio'?'studio-corrected':name)+'.jpg',type:'jpeg',quality:87,fullPage:false});
  const desk=await p.evaluate(()=>({w:document.documentElement.scrollWidth,window:innerWidth,h1:document.querySelector('h1')?.innerText,images:document.images.length,broken:[...document.images].filter(i=>!i.naturalWidth).map(i=>i.src),workCards:document.querySelectorAll('.work-card').length,realPortraitImages:[...document.images].filter(i=>/matt-(portrait|headshot)/.test(i.src)).length}));
  await p.setViewportSize({width:390,height:844});await p.reload({waitUntil:'networkidle'});
  const mobile=await p.evaluate(()=>({w:document.documentElement.scrollWidth,window:innerWidth}));
  await p.screenshot({path:'screenshots/'+name+'-mobile.jpg',type:'jpeg',quality:77,fullPage:false});
  await p.locator('.toggle').click();
  const menu=await p.locator('.top-right').evaluate(e=>getComputedStyle(e).display);
  results.push({path,status:res.status(),desktop:desk,mobile,menu,errors});
  await p.close();
 }
 await browser.close();console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
