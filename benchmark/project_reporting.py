"""Inspectable delivery reports and a separate, blinded human review pack."""
import difflib
import html
import json
import secrets
import shutil
from pathlib import Path
from benchmark.core import ROOT, atomic_json, read_json

DIMENSIONS = ['fidelity', 'hierarchy', 'typography_spacing', 'responsive_polish']


def apply_reviews(directory, scores_path):
    directory = Path(directory)
    mapping = read_json(directory / 'review-map.json')
    reviews = read_json(scores_path)
    if set(reviews) - set(mapping): raise ValueError('Unknown blind review ID')
    for key, review in reviews.items():
        if not isinstance(review.get('reviewer'), str) or not review['reviewer'].strip(): raise ValueError('A human reviewer name or identifier is required')
        scores = review.get('scores', {})
        if set(scores) != set(DIMENSIONS) or any(type(v) is not int or not 0 <= v <= 4 for v in scores.values()):
            raise ValueError('Each visual dimension requires an integer score from 0 to 4')
    existing = read_json(directory / 'visual-reviews.json') if (directory / 'visual-reviews.json').exists() else {}
    existing.update(reviews); atomic_json(directory / 'visual-reviews.json', existing)


def project_report(directory, manifest, rows):
    directory = Path(directory)
    rows = [r for r in rows if r.get('profile') == 'wordpress-project-v2']
    if not rows: return
    public = ROOT / 'tasks/agency-landing-page/public'
    review = directory / 'blind-review'; review.mkdir(exist_ok=True)
    mapping_path = directory / 'review-map.json'
    mapping = read_json(mapping_path) if mapping_path.exists() else {}
    for row in rows:
        if row['run_id'] not in mapping.values(): mapping['site-' + secrets.token_hex(4)] = row['run_id']
    atomic_json(mapping_path, mapping)
    reviews = read_json(directory / 'visual-reviews.json') if (directory / 'visual-reviews.json').exists() else {}
    for name in ('reference-desktop.png', 'reference-mobile.png', 'brief.md'):
        if (public/name).exists(): shutil.copyfile(public/name, review/name)
    style = '<style>body{font:16px/1.5 system-ui;max-width:1200px;margin:40px auto;padding:0 24px;color:#213a31;background:#f4f2eb}section{margin:48px 0;border-top:1px solid #aaa;padding-top:20px}.screens{display:grid;grid-template-columns:2fr 1fr;gap:24px;align-items:start}.compare{display:grid;grid-template-columns:1fr 1fr;gap:24px}.compare figure{margin:0}.viewport{max-height:650px;overflow:auto;background:white;border:1px solid #b5beb5}figcaption{font-weight:600;margin:12px 0}.mobile img{max-width:390px}summary{cursor:pointer;font-weight:600;padding:12px 0}img{max-width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:20px}table{border-collapse:collapse}td,th{padding:9px;border-bottom:1px solid #aaa;text-align:left}</style>'
    esc=lambda v:html.escape(str(v),quote=True)
    reference='<details><summary>Fixed reference: desktop and mobile</summary><div class="screens"><img alt="Reference desktop" src="blind-review/reference-desktop.png"><img alt="Reference mobile" src="blind-review/reference-mobile.png"></div></details>'
    brief=(public/'brief.md').read_text()
    pages=['<!doctype html><html lang="en"><meta charset="utf-8"><title>WordPress project deliveries</title>'+style+'<h1>Northline / WordPress deliveries</h1><p>Exploratory pilot. Automated score and human visual review are separate. No general model ranking.</p><details><summary>Client brief and acceptance contract</summary><pre>'+esc(brief)+'</pre></details>'+reference]
    blind=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Blind visual review</title>'+style+'<h1>Visual review</h1><p>Score fidelity, hierarchy, typography/spacing and responsive polish from 0–4 each. 0: unusable; 1: major defects; 2: workable with substantial corrections; 3: good with minor corrections; 4: polished and faithful. Review the supplied brief and both viewports. Missing reviews remain pending.</p>'+reference.replace('blind-review/','')]
    template={}
    for blind_id, run_id in sorted(mapping.items()):
        row=next((r for r in rows if r['run_id']==run_id),None)
        if not row: continue
        if not row['simulated'] and row['calls']==0:
            agent=read_json(directory/'runs'/run_id/'agent.json')
            title=f"{row['model']} / {row['skill'] or 'no skill'}"
            pages.append('<section><h2>'+esc(title)+'</h2><p><strong>No model artifact generated.</strong> '+esc(agent.get('error') or row['generation_status'])+'</p><p>Generation calls: 0. Generation cost: US$0. Any saved evaluation files describe the unchanged starter scaffold and are excluded from model-quality comparisons and visual review.</p></section>')
            continue
        evaluation=directory/'runs'/run_id/'evaluation'
        for suffix in ('desktop','mobile'):
            source=evaluation/f'screenshot-{suffix}.png'
            if source.exists(): shutil.copyfile(source,review/f'{blind_id}-{suffix}.png')
        def comparison(viewport):
            return '<div class="compare '+('mobile' if viewport=='mobile' else '')+'">'+''.join(
                f'<figure><figcaption>{caption} · {viewport}</figcaption><div class="viewport"><img alt="{caption} {viewport}" src="{src}"></div><a href="{src}">Open full screenshot</a></figure>'
                for caption,src in [('Reference',f'reference-{viewport}.png'),('Submitted',f'{blind_id}-{viewport}.png')])+'</div>'
        images=comparison('desktop')+'<details><summary>Compare mobile layouts</summary>'+comparison('mobile')+'</details>' 
        notice='<p><strong>Simulated reference fixture — validates the harness, not model or skill quality.</strong></p>' if row['simulated'] else ''
        blind.append('<section><h2>'+esc(blind_id)+'</h2>'+notice+images+'</section>')
        template[blind_id]={'reviewer':'','scores':dict.fromkeys(DIMENSIONS,None),'notes':''}
        visual=reviews.get(blind_id)
        status={'status':'reviewed','blind_id':blind_id,**visual} if visual else {'status':'pending','blind_id':blind_id}
        row['visual_review']=status;atomic_json(directory/'runs'/run_id/'result.json',row)
        title=f"{row['model']} / {row['skill'] or 'no skill'}"
        pages.append('<section><h2>'+esc(title)+'</h2>'+notice+'<p>'+esc(f"Artifact pass: {row['artifact_pass']} · Execution complete: {row['execution_completion']} · Delivery success: {row['delivery_success']} · Score: {row['score']} · Visual review: {status['status']}")+'</p><p>'+esc(f"Known cost USD {row['known_cost_usd']}; cost complete: {row['cost_complete']}; tokens: {row['tokens']}; model calls: {row['calls']}; development iterations: {row.get('development_iterations',0)}; generation seconds: {round(row['generation_seconds'] or 0, 2)}; evaluation seconds: {round(row['evaluation_seconds'], 2)}")+'</p>'+images.replace('src="','src="blind-review/').replace('href="','href="blind-review/'))
        pages.append('<table><tr><th>Criterion</th><th>Weight</th><th>Critical</th><th>Passed</th></tr>')
        for check in manifest['config']['resolved_tasks'][row['task']]['checks']:
            pages.append('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [check['id'],check['weight'],check['critical'],row['evaluation'].get('checks',{}).get(check['id'])])+'</tr>')
        pages.append('</table>')
        audit_path=directory/'runs'/run_id/'navigation-audit-v2.json'
        if audit_path.exists():
            audit=read_json(audit_path)
            verified={'cta':audit.get('cta_works') is True,
                      'keyboard':audit.get('keyboard_cta_works') is True and audit.get('keyboard_faq_works') is True}
            affected=[key for key,value in verified.items() if value and row['evaluation'].get('checks',{}).get(key) is False]
            if affected:
                pages.append('<p><strong>Scoring limitation:</strong> the post-run navigation audit passed '+esc(', '.join(affected))+'. The original tests reject decorative arrow text or check before smooth scrolling finishes. Original scores and outcomes above are retained; these failures are not evidence of broken navigation. Execution completion is unaffected.</p>')
            pages.append(f'<p><a href="runs/{esc(run_id)}/navigation-audit-v2.json">Independent navigation audit evidence</a></p>')
        relative='runs/'+run_id+'/evaluation/'
        for name in ('theme.zip','playground-bundle.zip','evidence.json','editor-saved.png','editor-reloaded.png','handover-published.png','form-submitted.png'):
            if (evaluation/name).exists(): pages.append(f'<p><a href="{esc(relative+name)}">{esc(name)}</a></p>')
        agent=read_json(directory/'runs'/run_id/'agent.json');initial=manifest['config']['resolved_tasks'][row['task']]['initial']
        diff='\n'.join(''.join(difflib.unified_diff(initial.get(name,'').splitlines(True),agent['files'].get(name,'').splitlines(True),fromfile='initial/'+name,tofile='submitted/'+name)) for name in sorted(set(initial)|set(agent['files'])))
        pages.append('<details><summary>Source changes</summary><pre>'+esc(diff)+'</pre></details></section>')
    blind.append('</html>');pages.append('</html>')
    (review/'index.html').write_text('\n'.join(blind));(directory/'deliveries.html').write_text('\n'.join(pages))
    atomic_json(review/'scores-template.json',template)
    (review/'README.txt').write_text('Give only this folder to reviewers; review-map.json and the main report reveal identities. Copy scores-template.json, fill all four scores (0–4) and a human reviewer ID, then import with python -m benchmark review ROUND --scores FILE. Do not assign a score to missing screenshots.\n')
