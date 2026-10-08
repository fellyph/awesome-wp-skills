"""Assertion audits inspired by WP-Bench: reference plus targeted broken artifacts."""
import copy
import re
from benchmark.core import atomic_json, load_tasks
from benchmark.environments import evaluate


def variants(task):
    reference=task['reference']
    yield 'initial',task['initial'],'blocks'
    yield 'reference',reference,None
    for name,criterion in [('static-html','blocks'),('broken-cta','cta'),('invalid-blocks','blocks'),
                           ('inaccessible-navigation','mobile_navigation'),('horizontal-overflow','responsive'),
                           ('missing-assets','assets'),('failed-form','form')]:
        files=copy.deepcopy(reference)
        content=files['patterns/landing.php']
        if name=='static-html': files['patterns/landing.php']=re.sub(r'<!--.*?-->','',content,flags=re.S)
        elif name=='broken-cta':files['patterns/landing.php']=content.replace('href="#contact"','href="#missing-contact"')
        elif name=='invalid-blocks':files['patterns/landing.php']=content.replace('<!-- wp:heading {"level":1} -->','<!-- wp:heading {"level":6} -->')
        elif name=='inaccessible-navigation':files['style.css']+='\n.wp-block-navigation__responsive-container-open{display:none!important}\n'
        elif name=='horizontal-overflow':files['style.css']+='\nbody{min-width:1600px}\n'
        elif name=='missing-assets':files.pop('assets/fieldwork.svg')
        elif name=='failed-form':files['style.css']+='\n.bench-contact button{pointer-events:none!important}\n'
        yield name,files,criterion


def verify(output, selected=None):
    task=load_tasks()['agency-landing-page'];results=[]
    available = list(variants(task))
    if selected and set(selected) - {v[0] for v in available}:
        raise ValueError('Unknown assertion-audit variant')
    for name,files,criterion in available:
        if selected and name not in selected:continue
        result=evaluate(task,files,output/name)
        valid=result['status']!='infrastructure_error' and (result['success'] if name=='reference' else not result['success'] and result.get('checks',{}).get(criterion) is False)
        results.append({'variant':name,'target_criterion':criterion,'valid_evaluator':valid,'result':result})
        atomic_json(output/'assertion-audit.json',results)
        print(f'{name}: {"OK" if valid else "ERROR"} score={result["score"]} checks={result.get("checks")} error={result.get("error")}',flush=True)
    return all(r['valid_evaluator'] for r in results)


def verify_tools(output):
    import base64
    from benchmark.project import Preview
    task=load_tasks()['agency-landing-page']
    preview=Preview(task,180)
    try:
        snapshot=preview.call('preview',{},task['reference'])
        assert 'Good ideas deserve' in snapshot['dom']
        assert base64.b64decode(snapshot['image']['data']).startswith(b'\x89PNG')
        for action,args in [('viewport',{'value':'mobile'}),('scroll',{'value':'400'}),('key',{'value':'Tab'}),('navigate',{'target':'/'})]:
            value=preview.call('browser',{'action':action,**args},task['reference'])
            assert value['image']['mime_type']=='image/png'
        try:preview.call('browser',{'action':'navigate','target':'https://example.org'},task['reference'])
        except ValueError:pass
        else:raise AssertionError('External navigation was not rejected')
        checks=preview.call('public_checks',{},task['reference'])
        assert checks['activation']['active'] and not checks['blocks']['invalid']
        assert 'editable' not in checks and 'checks' not in checks
        changed=copy.deepcopy(task['reference']);changed['patterns/landing.php']=changed['patterns/landing.php'].replace('Good ideas deserve a great home.','An updated public preview.')
        assert 'An updated public preview.' in preview.call('preview',{},changed)['dom']
        atomic_json(output/'tool-audit.json',{'passed':True,'checks':['native-image','dom','viewport','scroll','keyboard','same-origin','public-checks','source-resync']})
        print('Public Playground tool audit: OK',flush=True)
    finally:preview.close()
