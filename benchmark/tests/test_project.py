"""Project profile contracts: isolation, multimodal transport, submission, and spending."""
import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from benchmark.adapters import run_model
from benchmark.adapters.providers import build_request, count_tokens
from benchmark.budget import BudgetLedger
from benchmark.core import ROOT, atomic_json, load_tasks, load_round
from benchmark.project import package
from benchmark.project_tools import ProjectWorkspace, PROJECT_TOOLS
from benchmark.project_reporting import apply_reviews
from test_benchmark import model, response


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.task=load_tasks()['agency-landing-page']
        self.config=load_round(ROOT/'configs/landing-page.json')

    def test_rubric_and_individual_conditions(self):
        from benchmark.core import matrix
        self.assertEqual(sum(c['weight'] for c in self.task['checks']),100)
        self.assertEqual({r['skill'] for r in matrix(self.config)},{None,'wp-block-themes','frontend-design'})
        self.assertEqual(len(matrix(self.config)),3)

    def test_capability_gate_and_mixed_profiles(self):
        config={k:v for k,v in self.config.items() if not k.startswith('resolved_')}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'round.json'
            config['models']=[model('kimi')];atomic_json(path,config)
            with self.assertRaisesRegex(ValueError,'supported multimodal'):load_round(path)
            config['models']=[model('gemini')];config['tasks'].append('theme-single');atomic_json(path,config)
            with self.assertRaisesRegex(ValueError,'separate rounds'):load_round(path)

    def test_read_search_and_freeze(self):
        workspace=ProjectWorkspace(self.task,{'files':{'SKILL.md':'hello skill'}},self.config['limits'])
        self.assertEqual(workspace.call('read_file',{'path':'skill/SKILL.md','offset':'0','limit':'5'})['text'],'hello')
        self.assertEqual(workspace.call('search_files',{'query':'hello'})[0]['path'],'skill/SKILL.md')
        for path in ('../secret','project/../../secret','reference/style.css','skill/SKILL.md'):
            with self.assertRaises(ValueError):workspace.call('write_file',{'path':path,'content':'x'})
        names=workspace.call('list_files',{})
        self.assertFalse(any('evaluate' in n or 'fixtures/' in n or 'reference/' in n for n in names))
        workspace.call('submit',{})
        with self.assertRaisesRegex(ValueError,'frozen'):workspace.call('write_file',{'path':'project/style.css','content':'x'})
        with self.assertRaisesRegex(ValueError,'frozen'):workspace.call('preview',{})

    def test_images_and_native_signatures_counted_on_wire(self):
        messages=[{'role':'system','content':'system'},{'role':'user','content':'brief','_images':[{'mime_type':'image/png','data':'AAAA'}]},
          {'role':'assistant','_native':{'parts':[{'functionCall':{'name':'preview','args':{}},'thoughtSignature':'opaque-signature'}]}},
          {'role':'tool','tool_call_id':'id','name':'preview','content':'{"dom":"hello"}','_images':[{'mime_type':'image/png','data':'BBBB'}]}]
        _,_,_,wire=build_request(model('gemini'),messages,PROJECT_TOOLS,100)
        class Result:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self):return b'{"totalTokens":123}'
        captured=[]
        def opener(req,**kw):captured.append(req);return Result()
        with patch.dict('os.environ',{'GEMINI_API_KEY':'test-secret'}),patch('urllib.request.urlopen',opener):
            self.assertEqual(count_tokens(model('gemini'),messages,PROJECT_TOOLS,100,5),123)
        payload=json.loads(captured[0].data)['generateContentRequest'];self.assertEqual(payload,{'model':'models/test-model',**wire})
        self.assertIn('opaque-signature',json.dumps(payload));self.assertIn('AAAA',json.dumps(payload));self.assertIn('BBBB',json.dumps(payload))
        self.assertNotIn('test-secret',json.dumps(payload));self.assertTrue(captured[0].full_url.endswith(':countTokens'))

    def test_submit_completes_once_and_no_further_writes(self):
        calls=[{'id':'a','function':{'name':'submit','arguments':'{}'}},{'id':'b','function':{'name':'write_file','arguments':'{"path":"project/style.css","content":"bad"}'}}]
        transport_calls=[]
        def transport(*args):transport_calls.append(1);return response(calls)
        with patch('benchmark.project.reference_images',return_value=[]):
            state=run_model(model('gemini'),self.task,None,self.config['limits'],lambda s:None,transport,lambda *a:100)
        self.assertEqual(state['status'],'completed');self.assertTrue(state['submitted']);self.assertEqual(len(transport_calls),1)
        self.assertEqual(state['files']['style.css'],self.task['initial']['style.css'])

    def test_preflight_failure_never_dispatches_generation(self):
        def counter(*args):raise TimeoutError('count service unavailable')
        def transport(*args):self.fail('Generation dispatched without token preflight')
        with patch('benchmark.project.reference_images',return_value=[]):
            state=run_model(model('gemini'),self.task,None,self.config['limits'],lambda s:None,transport,counter)
        self.assertEqual(state['status'],'token_preflight_error');self.assertEqual(state['calls'],[]);self.assertTrue(state['cost_complete'])

    def test_package_reproducibility_and_private_files_excluded(self):
        with tempfile.TemporaryDirectory() as folder:
            a=package(self.task,self.task['reference'],Path(folder)/'a').read_bytes()
            b=package(self.task,self.task['reference'],Path(folder)/'b').read_bytes()
            self.assertEqual(a,b)
            with zipfile.ZipFile(Path(folder)/'a/theme.zip') as z:
                self.assertEqual(set(z.namelist()),{'benchmark-fixture/'+n for n in self.task['reference']})
            with self.assertRaises(ValueError):package(self.task,{'../escape':'bad'},folder)

    def test_global_reservations_survive_round_changes_and_crashes(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'ledger.json';m=model('gemini')
            with BudgetLedger(path) as ledger:
                self.assertTrue(ledger.reserve('round-a/run1',m,6,20))
                ledger.settle('round-a/run1',{'cost_usd':1,'cost_complete':False,'calls':[{'status':'uncertain','reserved_usd':2}]})
                self.assertEqual(ledger.spent(m),3)
                self.assertTrue(ledger.reserve('round-b/run1',m,6,20))
            with BudgetLedger(path) as ledger:
                self.assertEqual(ledger.spent(m),9)
                self.assertTrue(ledger.reserve('round-c/run1',m,6,20))
                self.assertFalse(ledger.reserve('round-d/run1',m,6,20))
                with self.assertRaises(ValueError):ledger.reserve('round-b/run1',m,6,20)

    def test_missing_visual_review_cannot_be_imported_as_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);atomic_json(root/'review-map.json',{'site-a':'run1'})
            atomic_json(root/'scores.json',{'site-a':{'reviewer':'','scores':{}}})
            with self.assertRaises(ValueError):apply_reviews(root,root/'scores.json')
            self.assertFalse((root/'visual-reviews.json').exists())


class AdditionalAccountingTests(unittest.TestCase):
    def test_copied_resume_deduplicates_but_new_round_does_not(self):
        from benchmark.budget import execution_key
        first={'identity':'same-protocol','created_at':'2026-09-07T10:00:00Z'}
        second={**first,'created_at':'2026-09-07T11:00:00Z'}
        self.assertEqual(execution_key(first,'run1'),execution_key(copy.deepcopy(first),'run1'))
        self.assertNotEqual(execution_key(first,'run1'),execution_key(second,'run1'))

    def test_distinct_project_failure_statuses(self):
        task=load_tasks()['agency-landing-page'];limits=load_round(ROOT/'configs/landing-page.json')['limits']
        def truncated(*args):
            value=response();value['choices'][0]['finish_reason']='MAX_TOKENS';return value
        with patch('benchmark.project.reference_images',return_value=[]):
            state=run_model(model('gemini'),task,None,limits,lambda s:None,truncated,lambda *a:10)
            self.assertEqual(state['status'],'output_truncation')
            state=run_model(model('gemini'),task,None,limits,lambda s:None,truncated,lambda *a:1000001)
            self.assertEqual(state['status'],'context_limit')
            state=run_model(model('gemini'),task,None,{**limits,'max_run_usd':.000001},lambda s:None,truncated,lambda *a:10)
            self.assertEqual(state['status'],'monetary_limit')

    def test_preview_receives_only_public_data_and_no_credentials(self):
        from benchmark.project import Preview
        task=load_tasks()['agency-landing-page']
        with patch('benchmark.project.subprocess.Popen') as spawn,patch.object(Preview,'request',return_value={'ready':True}) as request:
            spawn.return_value.poll.return_value=0
            with patch.dict('os.environ',{'GEMINI_API_KEY':'private-gemini','OPENAI_API_KEY':'private-openai'}):
                preview=Preview(task,10)
            payload=request.call_args.args[0]
            self.assertEqual(set(payload),{'op','blueprint'})
            self.assertNotIn('KEY',str(spawn.call_args.kwargs['env']))
            self.assertNotIn('mount',str(spawn.call_args))
            preview.close()


    def test_corrupt_budget_is_rejected_and_lock_released(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'ledger.json'
            atomic_json(path,{'schema_version':1,'entries':{'x':{'model':'m','known_usd':-1,'reserved_usd':0}}})
            for _ in range(2):
                with self.assertRaisesRegex(ValueError,'Invalid amount'):
                    with BudgetLedger(path):pass

    def test_artifact_pass_is_not_delivery_success_and_review_stays_pending(self):
        from benchmark.runner import run
        from benchmark.reporting import report
        config=json.loads((ROOT/'configs/landing-page-mock.json').read_text())
        config['skills']=[];config['models'][0]['id']='private-model-identity'
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);atomic_json(folder/'config.json',config)
            def incomplete(m,t,s,limits,checkpoint):
                return {'files':t['reference'],'status':'output_truncation','simulated':True,'calls':[],
                  'cost_usd':0,'cost_complete':True,'tokens':0,'tokens_complete':True,'skill_reads':[]}
            def evaluator(t,files,out):
                return {'status':'passed','success':True,'score':100,'checks':{c['id']:True for c in t['checks']}}
            run(folder/'config.json',folder/'round',evaluator=evaluator,adapter=incomplete)
            def forbidden(*args):self.fail('Completed project evaluation was repeated on resume')
            run(folder/'config.json',folder/'round',evaluator=forbidden,adapter=incomplete)
            summary=report(folder/'round')[0]
            row=json.loads(next((folder/'round/runs').glob('*/result.json')).read_text())
            self.assertTrue(row['artifact_pass']);self.assertFalse(row['execution_completion']);self.assertFalse(row['delivery_success'])
            self.assertEqual(row['visual_review']['status'],'pending');self.assertEqual(summary['success_rate'],0)
            blind=(folder/'round/blind-review/index.html').read_text()
            self.assertNotIn('private-model-identity',blind)
            self.assertIn('Simulated reference fixture',blind)


if __name__=='__main__':unittest.main()
