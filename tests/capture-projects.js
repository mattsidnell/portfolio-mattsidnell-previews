const {chromium}=require('/Users/mattsidnell/Sites/pstructures-website/node_modules/playwright');
const fs=require('fs');const path=require('path');const base='/Users/mattsidnell/Sites/mattsidnell-portfolio/docs/cyan/assets/projects';fs.mkdirSync(base,{recursive:true});
const sites=[
 {slug:'grinders',url:'https://grinders.golf/'},
 {slug:'sidnell',url:'https://sidnell.uk/'},
 {slug:'digipixel',url:'https://digipixel.uk/'},
 {slug:'pstructures',url:'https://pstructures.com/'},
 {slug:'wdd',url:'https://webdesignerdirect.com/'},
 {slug:'sunnyside',url:'https://sunnysideaccountancy.co.uk/'},
 {slug:'lps',url:'https://lpsgardenbuildings.co.uk/'}
];
(async()=>{const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});let results=[];
for(const site of sites){let page=await browser.newPage({viewport:{width:1440,height:920},deviceScaleFactor:1,ignoreHTTPSErrors:true});try{let resp=await page.goto(site.url,{waitUntil:'domcontentloaded',timeout:22000});await page.waitForTimeout(2200);await page.evaluate(async()=>{await document.fonts.ready;window.scrollTo(0,0)});await page.screenshot({path:path.join(base,site.slug+'.jpg'),type:'jpeg',quality:86,fullPage:false,animations:'disabled'});const info=await page.evaluate(()=>({title:document.title,h1:document.querySelector('h1')?.innerText?.slice(0,135),images:[...document.images].filter(i=>i.complete&&i.naturalWidth>0).length}));results.push({name:site.slug,status:resp?.status(),url:page.url(),...info})}catch(e){results.push({name:site.slug,error:String(e).slice(0,200)})}await page.close()}
await browser.close();console.log(JSON.stringify(results,null,2));})().catch(e=>{console.error(e);process.exit(1)});
