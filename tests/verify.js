const { chromium }=require('/Users/mattsidnell/Sites/pstructures-website/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const root='http://127.0.0.1:8797';
 const names=['independent','studio','systems'];
 const results=[];
 for (const name of names) {
  const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/'+name+'/',{waitUntil:'networkidle',timeout:30000});
  await page.screenshot({path:'docs/assets/previews/'+name+'-desktop.jpg',type:'jpeg',quality:83,fullPage:false});
  const desktop=await page.evaluate(()=>({width:document.documentElement.scrollWidth,innerWidth:window.innerWidth,heading:document.querySelector('h1')?.innerText,links:[...document.querySelectorAll('a[href^="mailto:"]')].length}));
  await page.setViewportSize({width:390,height:844});await page.reload({waitUntil:'networkidle'});
  await page.screenshot({path:'screenshots/'+name+'-mobile.jpg',type:'jpeg',quality:77,fullPage:true});
  const mobile=await page.evaluate(()=>({width:document.documentElement.scrollWidth,innerWidth:window.innerWidth}));
  await page.locator('.menu, .toggle').first().click();
  const menuVisible=await page.locator('#mainnav').evaluate(el=>getComputedStyle(el).display!=='none');
  let filterWorks=null;
  if(name==='systems'){await page.locator('[data-filter="integrations"]').click();filterWorks=await page.locator('.project:not([hidden])').count();}
  results.push({name,desktop,mobile,menuVisible,filterWorks,errors});await page.close();
 }
 const sel=await browser.newPage({viewport:{width:1440,height:900}});
 await sel.goto(root,{waitUntil:'networkidle'});await sel.screenshot({path:'screenshots/selector-desktop.jpg',type:'jpeg',quality:80});
 results.push({selector:{title:await sel.title(),cards:await sel.locator('a[href$="/"]').count()}});
 await sel.setViewportSize({width:390,height:844});await sel.reload({waitUntil:'networkidle'});
 results.push({selectorMobileWidth:await sel.evaluate(()=>document.documentElement.scrollWidth),innerWidth:390});
 await browser.close();console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
