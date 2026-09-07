/** Private behavioral acceptance checks. Never loaded by the preview worker. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {ZipFilesystem} from '@wp-playground/storage';
import AxeBuilder from '@axe-core/playwright';
import {ProjectRuntime} from './project-runtime.mjs';
const [requestPath,resultPath]=process.argv.slice(2);
const {task,files,bundle}=JSON.parse(await fs.readFile(requestPath,'utf8'));
const folder=path.dirname(resultPath);
const runtime=new ProjectRuntime();
const out={checks:Object.fromEntries(task.checks.map(c=>[c.id,false])),measurements:{},evidence:{}};
async function check(id,fn) {try {out.checks[id]=Boolean(await fn());}catch(e){out.evidence[id]=String(e.message).slice(0,1800); if(runtime.page){await runtime.page.screenshot({path:path.join(folder,'failed-'+id+'.png')}).catch(()=>{});await fs.writeFile(path.join(folder,'failed-'+id+'.txt'),await runtime.page.locator('body').ariaSnapshot().catch(()=>''));}}}
const screenshot=(name)=>runtime.page.screenshot({path:path.join(folder,name),fullPage:true});
try {
  const zip=new Uint8Array(await fs.readFile(bundle));
  await runtime.installBundle(ZipFilesystem.fromArrayBuffer(zip.buffer));
  const page=runtime.page;
  await check('activation',async()=>JSON.parse(await runtime.php("<?php require '/wordpress/wp-load.php'; echo json_encode(wp_is_block_theme() && get_stylesheet()==='benchmark-fixture');")));
  await screenshot('screenshot-desktop.png');
  await page.setViewportSize({width:390,height:844});await screenshot('screenshot-mobile.png');
  await page.setViewportSize({width:1280,height:900});
  const initialBlocked=[...runtime.blocked];
  const audit=await runtime.publicChecks();runtime.blocked=[];out.measurements.development=audit;
  await check('blocks',async()=>audit.blocks.invalid.length===0 && audit.blocks.count>=20 &&
    ['core/heading','core/image','core/button'].every(n=>audit.blocks.names.includes(n)) && audit.blocks.names.every(n=>n.startsWith('core/')) && !audit.blocks.names.includes('core/html') &&
    Boolean(files['theme.json'] && files['parts/header.html'] && files['parts/footer.html'] &&
      Object.entries(files).some(([name,content])=>name.startsWith('templates/')&&content.includes('wp:template-part')&&content.includes('wp:post-content'))));
  await page.goto(runtime.url,{waitUntil:'networkidle'});
  await check('sections',async()=>{
    for(const id of ['home','services','portfolio','testimonials','faq','contact'])if(!await page.locator('#'+id).isVisible())return false;
    for(const text of ['Brand strategy','WordPress development','Care and growth','Fieldwork','Form','Alex Morgan','What does a project cost?','How long does a website take?','Can our team edit the website?'])
      if(!await page.getByText(text,{exact:false}).first().isVisible())return false;
    return await page.locator('header').count()>0 && await page.locator('footer').count()>0;
  });
  await check('cta',async()=>{
    const cta=page.getByRole('link',{name:'Start a project',exact:true});await cta.click();
    return new URL(page.url()).hash==='#contact' && await page.locator('#contact').isVisible() && await page.locator('#contact').evaluate(e=>Math.abs(e.getBoundingClientRect().top)<window.innerHeight);
  });
  await check('form',async()=>{
    const suffix=crypto.randomBytes(4).toString('hex');out.measurements.submission_fixture=suffix;
    await page.getByRole('button',{name:'Send enquiry',exact:true}).click();
    const invalid=await page.locator('form.bench-contact').evaluate(e=>!e.checkValidity());
    await page.getByLabel('Name',{exact:true}).fill('Client '+suffix);
    await page.getByLabel('Email',{exact:true}).fill(`client-${suffix}@example.test`);
    await page.getByLabel('Message',{exact:true}).fill('A new WordPress project '+suffix);
    const nonce=await page.locator('[name="benchmark_nonce"]').inputValue();
    const rejected=await page.request.post(runtime.url+'/wp-admin/admin-post.php',{form:{action:'benchmark_contact',benchmark_nonce:nonce,client_name:'Test',email:'invalid',message:'test'}});
    await page.getByRole('button',{name:'Send enquiry',exact:true}).click();await page.waitForURL('**/*contact=sent*');
    const saved=JSON.parse(await runtime.php("<?php require '/wordpress/wp-load.php'; echo json_encode(get_option('benchmark_submissions',[]));"));
    await screenshot('form-submitted.png');
    return invalid && rejected.status()===400 && saved.length===1 && saved[0].name==='Client '+suffix && saved[0].email===`client-${suffix}@example.test` && saved[0].message==='A new WordPress project '+suffix && await page.getByRole('status').isVisible();
  });
  await check('security',async()=>{
    const before=await runtime.php("<?php require '/wordpress/wp-load.php'; echo json_encode(get_option('benchmark_submissions',[]));");
    const response=await page.request.post(runtime.url+'/wp-admin/admin-post.php',{form:{action:'benchmark_contact',benchmark_nonce:'invalid',client_name:'<script>alert(1)</script>',email:'x@example.test',message:'test'}});
    const after=await runtime.php("<?php require '/wordpress/wp-load.php'; echo json_encode(get_option('benchmark_submissions',[]));");
    const fixture=await fs.readFile(new URL('../tasks/agency-landing-page/fixtures/contact.php',import.meta.url),'utf8');
    const installed=await runtime.instance.playground.readFileAsText('/wordpress/wp-content/mu-plugins/benchmark-contact.php');
    return installed===fixture && response.status()===403 && before===after && initialBlocked.length===0 && runtime.blocked.length===0 && await page.locator('form.bench-contact').getAttribute('action')===runtime.url+'/wp-admin/admin-post.php';
  });
  await page.goto(runtime.url,{waitUntil:'networkidle'});
  await check('axe',async()=>{
    const results=[];
    for(const width of [1280,390]){await page.setViewportSize({width,height:900});results.push(...(await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations);}
    out.measurements.axe_violations=results.map(v=>({id:v.id,impact:v.impact,targets:v.nodes.map(n=>n.target)}));return results.length===0;
  });
  await check('responsive',async()=>{
    for(const width of [360,390,768,1280]){
      await page.setViewportSize({width,height:900});
      if(!await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1))return false;
      for(const id of ['services','portfolio','testimonials','faq','contact'])if(!await page.locator('#'+id).isVisible())return false;
    }return true;
  });
  await check('mobile_navigation',async()=>{
    await page.setViewportSize({width:390,height:844});await page.goto(runtime.url);
    const open=page.getByRole('button',{name:'Open menu',exact:true});
    await open.focus();await page.keyboard.press('Enter');
    const contact=page.getByRole('navigation').getByRole('link',{name:'Contact',exact:true});
    if(!await contact.isVisible())return false;
    await page.keyboard.press('Escape');
    const restored=await open.evaluate(e=>e===document.activeElement);
    await open.press('Enter');await contact.click();
    return restored && new URL(page.url()).hash==='#contact' && await open.isVisible();
  });
  await check('keyboard',async()=>{
    await page.setViewportSize({width:1280,height:900});await page.goto(runtime.url);
    const journey=[];
    for(let i=0;i<40;i++){
      await page.keyboard.press('Tab');
      const el=await page.evaluate(()=>{const e=document.activeElement;const s=getComputedStyle(e);return {name:(e.textContent||e.getAttribute('name')||'').trim(),tag:e.tagName,focus:s.outlineStyle!=='none'&&parseFloat(s.outlineWidth)>0};});journey.push(el);
      if(el.name==='Start a project'){if(!el.focus)return false;await page.keyboard.press('Enter');break;}
    }
    if(new URL(page.url()).hash!=='#contact')return false;
    const faq=page.locator('#faq summary').first();await faq.focus();await page.keyboard.press('Enter');
    const open=await faq.evaluate(e=>e.parentElement.open);await page.keyboard.press('Space');
    out.measurements.keyboard_journey=journey;
    return open && !await faq.evaluate(e=>e.parentElement.open) && await page.getByLabel('Name',{exact:true}).count()===1;
  });
  await check('assets',async()=>{
    await page.goto(runtime.url,{waitUntil:'networkidle'});
    return await page.locator('img').count()>=3 && await page.locator('img').evaluateAll(images=>images.every(i=>i.complete&&i.naturalWidth>0&&i.alt.trim()));
  });
  // Freeze frontend resource/error observations before loading the heavier editor.
  out.measurements.frontend_requests=runtime.requests.size;
  out.measurements.theme_bytes=Object.values(files).reduce((n,s)=>n+Buffer.byteLength(s),0);
  out.checks.resources=out.measurements.theme_bytes<=1_000_000;
  await check('editable',async()=>{
    await runtime.editor();
    const original=await page.evaluate(()=>wp.data.select('core/editor').getEditedPostContent());
    const id=crypto.randomBytes(4).toString('hex');
    const title='A better home for ideas '+id;const label='Discuss your next project '+id;
    out.measurements.editor_fixture={title,label,image:'replacement.svg'};
    if(!original.includes('Good ideas deserve a great home.')||!original.includes('studio.svg')||!original.includes('Start a project'))return false;
    const canvas=page.frameLocator('iframe[name="editor-canvas"]');
    await canvas.locator('h1[data-type="core/heading"]').fill(title);
    await canvas.locator('[data-type="core/image"]').filter({has:canvas.locator('img[src*="studio.svg"]')}).click();
    await page.getByRole('button',{name:'Replace',exact:true}).click();
    await page.getByRole('button',{name:'Edit link',exact:true}).click();
    await page.getByRole('combobox',{name:'Paste or type URL',exact:true}).fill(runtime.url+'/wp-content/themes/benchmark-fixture/assets/replacement.svg');
    await page.getByRole('button',{name:'Apply',exact:true}).click();
    await page.keyboard.press('Escape');
    await canvas.getByRole('textbox',{name:'Button text',exact:true}).filter({hasText:'Start a project'}).fill(label);
    await page.getByRole('button',{name:'Edit link',exact:true}).click();
    await page.getByRole('combobox',{name:'Search or type URL',exact:true}).fill('#services');
    await page.getByRole('button',{name:'Apply',exact:true}).click();
    await page.keyboard.press('Escape');
    await page.getByRole('button',{name:'Save',exact:true}).click();
    await page.waitForFunction(()=>!wp.data.select('core/editor').isSavingPost()&&!wp.data.select('core/editor').isEditedPostDirty());
    await screenshot('editor-saved.png');await page.reload();
    await page.waitForFunction(()=>window.wp?.data?.select('core/editor')?.getCurrentPostId());
    const persisted=await page.evaluate(()=>wp.data.select('core/editor').getEditedPostContent());
    await screenshot('editor-reloaded.png');
    await page.goto(runtime.url,{waitUntil:'networkidle'});await screenshot('handover-published.png');
    const link=page.getByRole('link',{name:label,exact:true});
    return persisted.includes(title)&&persisted.includes('replacement.svg')&&persisted.includes(label)&&
      await page.getByRole('heading',{name:title,exact:true}).isVisible()&&await link.getAttribute('href')==='#services'&&
      await page.locator('img[src*="replacement.svg"]').count()===1;
  });
  out.measurements.browser_errors=runtime.errors;
  out.checks.errors=runtime.errors.length===0&&!audit.php_errors;
  // Fresh frontend context for the request budget, preserving the exact installed artifact.
  const ctx=await runtime.browser.newContext({serviceWorkers:'block'});let requests=0;
  await ctx.route('**/*',r=>new URL(r.request().url()).origin===runtime.origin?r.continue():r.abort());
  const p=await ctx.newPage();p.on('request',()=>requests++);await p.goto(runtime.url,{waitUntil:'networkidle'});await ctx.close();
  out.measurements.frontend_requests=requests;out.checks.resources&&=requests<=45;
} catch(e) {
  out.error=String(e.message);out.failure=e.step || (runtime.browser?.isConnected()) ? 'candidate_error' : 'infrastructure_error';
} finally {
  await runtime.close();await fs.writeFile(resultPath,JSON.stringify(out,null,2)+'\n');
}
