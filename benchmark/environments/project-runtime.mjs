/** Public development runtime. Never import final acceptance code here. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { runCLI } from '@wp-playground/cli';
import { chromium } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
export const base = '/wordpress/wp-content/themes/benchmark-fixture';
export const seedPHP = await fs.readFile(new URL('../tasks/agency-landing-page/fixtures/setup.php', import.meta.url),'utf8');
export class ProjectRuntime {
  constructor() { this.files = {}; this.errors = []; this.requests = new Set(); this.blocked = []; }
  async start(blueprint) {
    this.instance = await runCLI({command:'server', blueprint, workers:1, port:0, wp:blueprint.preferredVersions?.wp || '6.9', php:blueprint.preferredVersions?.php || '8.3', verbosity:'quiet'});
    this.url = this.instance.serverUrl;
    this.origin = new URL(this.url).origin;
    this.browser = await chromium.launch({headless:true});
    this.context = await this.browser.newContext({viewport:{width:1280,height:900}, serviceWorkers:'block', acceptDownloads:false});
    await this.context.route('**/*', route => {
      const url = new URL(route.request().url());
      if (url.origin === this.origin || ['data:','blob:'].includes(url.protocol)) return route.continue();
      this.blocked.push(url.origin); return route.abort();
    });
    await this.context.routeWebSocket('**/*', ws=>ws.close());
    this.page = await this.context.newPage();
    this.page.on('popup', p=>void p.close());
    this.page.on('pageerror', e=>this.errors.push(e.message));
    this.page.on('request', r=>this.requests.add(r.url()));
    this.page.setDefaultTimeout(10000);
    this.page.setDefaultNavigationTimeout(60000);
  }
  async php(code) {
    const r = await this.instance.playground.run({code});
    if(r.exitCode!==0) throw Error('Candidate PHP failed: '+(r.errors||''));
    return new TextDecoder().decode(r.bytes);
  }
  async sync(files, fixture) {
    for (const [name, content] of Object.entries(files)) {
      if(name.startsWith('/') || name.includes('\\') || name.split('/').some(p=>!p||['.','..','__proto__','constructor'].includes(p)) || typeof content !== 'string') throw Error('Invalid project file');
    }
    for(const name of Object.keys(this.files)) if(!(name in files)) await this.instance.playground.unlink(`${base}/${name}`);
    for(const [name,content] of Object.entries(files)) {
      await this.instance.playground.mkdirTree(path.posix.dirname(`${base}/${name}`));
      await this.instance.playground.writeFile(`${base}/${name}`, content);
    }
    this.files = structuredClone(files); // Track even a failed activation so later deletions apply.
    await this.instance.playground.mkdirTree('/wordpress/wp-content/mu-plugins');
    await this.instance.playground.writeFile('/wordpress/wp-content/mu-plugins/benchmark-contact.php', fixture);
    await this.php("<?php require '/wordpress/wp-load.php'; switch_theme('benchmark-fixture');");
    this.pageId = Number(await this.php(seedPHP));
    this.files = structuredClone(files);
    await this.page.goto(this.url, {waitUntil:'networkidle'});
  }
  async installBundle(bundle) {
    // CLI resolves bundled theme.zip itself; evaluation uses this fresh installation.
    await this.start(bundle);
    this.pageId = Number(await this.php("<?php require '/wordpress/wp-load.php'; echo get_option('page_on_front');"));
    await this.page.goto(this.url,{waitUntil:'networkidle'});
  }
  async login() {
    await this.page.goto(this.url+'/wp-login.php');
    await this.page.getByLabel('Username or Email Address').fill('admin');
    await this.page.getByLabel('Password', {exact:true}).fill('password');
    await this.page.getByRole('button',{name:'Log In',exact:true}).click();
    await this.page.waitForURL('**/wp-admin/**');
  }
  async editor() {
    await this.login();
    await this.page.goto(`${this.url}/wp-admin/post.php?post=${this.pageId}&action=edit`);
    await this.page.waitForFunction(()=>window.wp?.data?.select('core/editor')?.getCurrentPostId());
    await this.page.locator('iframe[name="editor-canvas"]').waitFor({timeout:60000});
    await this.page.getByRole('dialog',{name:'Welcome to the editor'}).getByRole('button',{name:'Close',exact:true}).click({timeout:3000}).catch(()=>{});
  }
  async publicChecks() {
    const activated=await this.php("<?php require '/wordpress/wp-load.php'; echo json_encode(['active'=>get_stylesheet()==='benchmark-fixture','block_theme'=>wp_is_block_theme()]);");
    const axe = await new AxeBuilder({page:this.page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
    let log=''; try { log=await this.instance.playground.readFileAsText('/wordpress/wp-content/debug.log'); } catch {}
    // Check serialization with WordPress's actual editor parser, not PHP parse_blocks alone.
    const previous=this.page.url(); await this.editor();
    const blocks=await this.page.evaluate(()=>{
      const walk=items=>items.flatMap(b=>[b,...walk(b.innerBlocks||[])]);
      const items=walk(wp.data.select('core/block-editor').getBlocks());
      return {count:items.length,invalid:items.filter(b=>!b.isValid||!wp.blocks.getBlockType(b.name)).map(b=>b.name),names:items.map(b=>b.name)};
    });
    await this.page.goto(previous,{waitUntil:'networkidle'});
    return {activation:JSON.parse(activated),blocks,php_errors:log.slice(-8000),axe:axe.violations.map(v=>({id:v.id,impact:v.impact,targets:v.nodes.map(n=>n.target)}))};
  }
  async snapshot() {
    const editor=this.page.frameLocator('iframe[name="editor-canvas"]');
    const editor_dom=await this.page.locator('iframe[name="editor-canvas"]').count() ? (await editor.locator('body').ariaSnapshot()).slice(0,18000) : null;
    return {url:this.page.url().replace(this.origin,''),editor_dom,dom:(await this.page.locator('body').ariaSnapshot()).slice(0,18000),
      image:{mime_type:'image/png',data:(await this.page.screenshot()).toString('base64')}};
  }
  async action(args) {
    const {action,target='',value=''}=args;
    const locator=()=>target.startsWith('editor::') ? this.page.frameLocator('iframe[name="editor-canvas"]').locator(target.slice(8)).first() : this.page.locator(target).first();
    if(action==='navigate') {
      const url=new URL(target,this.url);
      if(url.origin!==this.origin||url.username||url.password)throw Error('Only this test site is allowed');
      await this.page.goto(url.href,{waitUntil:'networkidle'});
    } else if(action==='click') await locator().click();
    else if(action==='type') await locator().fill(value);
    else if(action==='key') {
      if(!/^(Tab|Shift\+Tab|Enter|Space|Escape|ArrowDown|ArrowUp|ArrowLeft|ArrowRight|Home|End)$/.test(value))throw Error('Unsupported key');
      await this.page.keyboard.press(value);
    } else if(action==='scroll') { const amount=Number(value);if(!Number.isFinite(amount)||Math.abs(amount)>2000)throw Error('Scroll must be between -2000 and 2000');await this.page.mouse.wheel(0,amount); }
    else if(action==='viewport') {
      if(!['desktop','mobile'].includes(value))throw Error('Use desktop or mobile');
      await this.page.setViewportSize(value==='mobile'?{width:390,height:844}:{width:1280,height:900});
    } else throw Error('Unsupported browser action');
    return this.snapshot();
  }
  async close() { if(this.browser)await this.browser.close();if(this.instance)await this.instance[Symbol.asyncDispose](); }
}
