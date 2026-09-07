/** Run the submitted WordPress artifact in a fresh, single-worker Playground. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { runCLI } from '@wp-playground/cli';
import { validateBlueprint } from '@wp-playground/blueprints';
import { chromium } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const [requestPath, resultPath] = process.argv.slice(2);
const request = JSON.parse(await fs.readFile(requestPath, 'utf8'));
const { task, files } = request;
const output = { checks: {}, measurements: {} };
let instance;
let browser;
let phase = 'infrastructure';
function tree(entries) {
  const result = {};
  for (const [name, content] of Object.entries(entries)) {
    const parts = name.split('/');
    if (parts.some(p => !p || p === '..' || p === '.' || p === '__proto__' || p === 'constructor')) throw Error('Invalid file path');
    let parent = result;
    for (const part of parts.slice(0, -1)) parent = parent[part] ??= {};
    parent[parts.at(-1)] = content;
  }
  return result;
}
try {
  const blueprint = structuredClone(task.blueprint);
  const validation = validateBlueprint(blueprint);
  if (!validation.valid) throw Error(JSON.stringify(validation.errors));
  if (request.validateOnly) {
    output.valid = true;
  } else {
    instance = await runCLI({command: 'server', blueprint, workers: 1, port: 0,
      wp: blueprint.preferredVersions.wp, php: blueprint.preferredVersions.php, verbosity: 'quiet'});
    phase = 'candidate';
    const base = `/wordpress/wp-content/${task.kind === 'theme' ? 'themes' : 'plugins'}/benchmark-fixture`;
    // File paths and contents arrive only from the in-memory workspace, not host mounts.
    tree(files);
    await instance.playground.mkdirTree(base);
    for (const [name, contents] of Object.entries(files)) {
      const target = `${base}/${name}`;
      await instance.playground.mkdirTree(path.posix.dirname(target));
      await instance.playground.writeFile(target, contents);
    }
    let activation = task.kind === 'theme'
      ? "switch_theme('benchmark-fixture');"
      : "require_once ABSPATH.'wp-admin/includes/plugin.php'; $e=activate_plugin('benchmark-fixture/fixture.php'); if(is_wp_error($e)) throw new Exception($e->get_error_message());";
    const activated = await instance.playground.run({ code: `<?php require '/wordpress/wp-load.php'; ${activation}` });
    if (activated.exitCode !== 0 || activated.errors) throw Error(activated.errors || 'Activation failed');
    const prefix = `<?php
$checks=[]; $measurements=[];
function bench_check($id,$value){global $checks;$checks[$id]=(bool)$value;}
function bench_measure($id,$value){global $measurements;$measurements[$id]=$value;}
try { require '/wordpress/wp-load.php'; `;
    const suffix = ` } catch (Throwable $e) { $error=$e->getMessage(); }
echo "\\nBENCHMARK_RESULT:".json_encode(['checks'=>$checks,'measurements'=>(object)$measurements,'error'=>$error??null]);`;
    const code = prefix + task.evaluator + suffix;
    const evaluated = await instance.playground.run({code});
    const body = new TextDecoder().decode(evaluated.bytes);
    await fs.writeFile(path.join(path.dirname(resultPath), 'php-output.txt'), body + '\n' + (evaluated.errors || ''));
    const marker = body.lastIndexOf('BENCHMARK_RESULT:');
    if (marker < 0 || evaluated.exitCode !== 0) throw Error(evaluated.errors || 'No evaluator result');
    Object.assign(output, JSON.parse(body.slice(marker + 'BENCHMARK_RESULT:'.length)));
    if (output.error) throw Error(output.error);
    if (task.browser) {
      // The test driver is added after generation and is never exposed to the agent.
      await instance.playground.writeFile('/wordpress/bench-preview.php', `<?php require '/wordpress/wp-load.php'; ?><!doctype html><html lang="en"><head><meta charset="utf-8"><title>Benchmark</title><style>body{font:18px sans-serif;color:#111;background:#fff} :focus-visible{outline:3px solid #14532d;outline-offset:3px}</style></head><body><main><?php echo bench_component(); ?></main></body></html>`);
      phase = 'browser-infrastructure';
      browser = await chromium.launch({headless: true});
      const context = await browser.newContext({viewport: {width: 1000, height: 800}});
      const page = await context.newPage();
      page.setDefaultTimeout(2000);
      phase = 'candidate';
      await page.goto(`${instance.serverUrl}/bench-preview.php`, {waitUntil: 'networkidle'});
      await page.screenshot({path: path.join(path.dirname(resultPath), 'screenshot-desktop.png'), fullPage: true});
      phase = 'browser-infrastructure';
      const axe = await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
      phase = 'candidate';
      output.checks.axe = axe.violations.length === 0;
      output.measurements.axe_violations = axe.violations.map(({id, impact, nodes}) => ({id, impact, targets: nodes.map(n=>n.target)}));
      output.checks.keyboard = false;
      output.checks.semantics = false;
      try {
        if (task.browser === 'form') {
          const input = page.getByRole('searchbox', {name: 'Search', exact: true});
          const button = page.getByRole('button', {name: 'Search', exact: true});
          output.checks.semantics = await input.count() === 1 && await button.count() === 1 && await input.getAttribute('name') === 's';
          await page.keyboard.press('Tab');
          const focusedInput = await input.evaluate(el => el === document.activeElement);
          await page.keyboard.press('Tab');
          output.checks.keyboard = focusedInput && await button.evaluate(el=>el===document.activeElement);
        } else if (task.browser === 'disclosure') {
          const button = page.getByRole('button', {name: 'Details', exact: true});
          const target = await button.getAttribute('aria-controls', {timeout: 2000});
          const panel = page.locator(`[id=${JSON.stringify(target)}]`);
          output.checks.semantics = await button.getAttribute('aria-expanded') === 'false' && await panel.isHidden();
          await page.keyboard.press('Tab');
          await page.keyboard.press('Enter');
          const expanded = await button.getAttribute('aria-expanded') === 'true' && await panel.isVisible() && (await panel.textContent()).includes('More information');
          await page.keyboard.press('Space');
          output.checks.keyboard = expanded && await button.getAttribute('aria-expanded') === 'false' && await panel.isHidden();
        } else {
          const link = page.getByRole('link', {name: 'Blue cotton shirt', exact: true});
          output.checks.semantics = await link.count() === 1 && await link.getAttribute('href') === '/product/' && await page.getByAltText('Blue cotton shirt').count() === 1;
          await page.keyboard.press('Tab');
          output.checks.keyboard = await link.evaluate(el => el===document.activeElement && getComputedStyle(el).outlineStyle !== 'none');
        }
      } catch { /* Missing/incorrect semantics are failed criteria, not infrastructure errors. */ }
      await page.screenshot({path: path.join(path.dirname(resultPath), 'screenshot.png'), fullPage: true});
      await page.setViewportSize({width: 390, height: 844});
      await page.screenshot({path: path.join(path.dirname(resultPath), 'screenshot-mobile.png'), fullPage: true});
    }
  }
} catch (error) {
  output.error = String(error.message || error);
  output.failure = phase === 'candidate' ? 'candidate_error' : 'infrastructure_error';
} finally {
  if (browser) await browser.close();
  if (instance) await instance[Symbol.asyncDispose]();
  await fs.writeFile(resultPath, JSON.stringify(output, null, 2) + '\n');
}
