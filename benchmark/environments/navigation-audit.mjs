/** Post-run behavioral audit; preserves original scoring and submitted packages. */
import fs from 'node:fs/promises';
import {ProjectRuntime} from './project-runtime.mjs';
import {ZipFilesystem} from '@wp-playground/storage';
const [bundle,output]=process.argv.slice(2);
const runtime=new ProjectRuntime();const evidence={audit:'navigation-observation-v2',changes_to_artifact:false};
try{
 const zip=new Uint8Array(await fs.readFile(bundle));await runtime.installBundle(ZipFilesystem.fromArrayBuffer(zip.buffer));
 const page=runtime.page;const cta=page.getByRole('link',{name:/^Start a project(?:\s*[→➜➔])?$/});
 evidence.cta_count=await cta.count();evidence.cta_text=await cta.textContent();
 await cta.click();await page.waitForFunction(()=>Math.abs(document.querySelector('#contact').getBoundingClientRect().top)<innerHeight,{},{timeout:5000});
 evidence.cta_works=new URL(page.url()).hash==='#contact';
 await page.goto(runtime.url);const journey=[];let reached=false;
 for(let i=0;i<40;i++){
  await page.keyboard.press('Tab');
  const focused=await cta.evaluate(e=>e===document.activeElement);
  journey.push(await page.evaluate(()=>document.activeElement.textContent.trim()));
  if(focused){evidence.focus_visible=await cta.evaluate(e=>{let s=getComputedStyle(e);return s.outlineStyle!=='none'&&parseFloat(s.outlineWidth)>0});await page.keyboard.press('Enter');reached=true;break;}
 }
 await page.waitForFunction(()=>location.hash==='#contact'&&Math.abs(document.querySelector('#contact').getBoundingClientRect().top)<innerHeight,{},{timeout:5000});
 evidence.keyboard_cta_works=reached&&evidence.focus_visible;
 const faq=page.locator('#faq summary').first();await faq.focus();await page.keyboard.press('Enter');const opened=await faq.evaluate(e=>e.parentElement.open);await page.keyboard.press('Space');
 evidence.keyboard_faq_works=opened&&!await faq.evaluate(e=>e.parentElement.open);evidence.journey=journey;
 await page.screenshot({path:output.replace('.json','.png'),fullPage:true});
}catch(e){evidence.error=String(e.message)}finally{await runtime.close();await fs.writeFile(output,JSON.stringify(evidence,null,2));console.log(JSON.stringify(evidence));}
