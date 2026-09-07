"""Protocol regressions: budgets, isolation, resumability, grading and API formats."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from benchmark.core import ROOT, atomic_json, digest, load_round, load_tasks, matrix, score
from benchmark.adapters import Workspace, run_model
from benchmark.adapters.providers import build_request, normalize, estimate_cost
from benchmark.runner import run
from benchmark.reporting import report


def model(adapter='openrouter'):
    return {'id': 'test-model', 'adapter': adapter, 'provider': 'test-provider', 'parameters': {},
            'pricing': {'input_per_million_usd': 1, 'output_per_million_usd': 2,
                        'cached_input_per_million_usd': .1, 'cache_write_per_million_usd': 1.25,
                        'source_url': 'https://example.org/pricing', 'checked_on': '2026-09-07'}}


def response(calls=None, cost=.01):
    return {'id': 'request-1', 'model': 'test-model', 'usage': {'total_tokens': 20, 'cost': cost},
            'choices': [{'finish_reason': 'tool_calls' if calls else 'stop',
                         'message': {'role': 'assistant', 'content': '', 'tool_calls': calls or []}}]}


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.config = load_round(ROOT / 'configs/pilot.json')
        self.task = load_tasks()['fix-zero-option']

    def test_individual_skill_matrix_and_one_baseline(self):
        runs = matrix(self.config)
        self.assertEqual(len(runs), 36)
        self.assertEqual(len({digest(r) for r in runs}), len(runs))
        self.assertEqual(sum(r['skill'] is None for r in runs), 12)
        self.assertEqual(runs, matrix(self.config))
        self.assertTrue(all(r['skill'] is None or isinstance(r['skill'], str) for r in runs))

    def test_task_categories_have_multiple_scenarios(self):
        tasks = load_tasks()
        for category in ('themes', 'plugins', 'fixes', 'performance', 'accessibility'):
            self.assertGreaterEqual(sum(t['category'] == category for t in tasks.values()), 3)

    def test_critical_failure_overrides_partial_score(self):
        evidence = {'checks': {'missing': True, 'zero': False, 'configured': True}}
        self.assertFalse(score(self.task, evidence)['success'])
        self.assertAlmostEqual(score(self.task, evidence)['score'], 66.67)
        with self.assertRaises(ValueError):
            score(self.task, {'checks': {'missing': True}})
        with self.assertRaises(ValueError):
            score(self.task, {'checks': dict.fromkeys(['missing','zero','configured'], 'true')})

    def test_isolated_workspace_and_skill_is_read_only(self):
        source = {'fixture.php': 'old'}
        workspace = Workspace(source, {'SKILL.md': 'one skill'})
        workspace.call('write_file', {'path':'project/fixture.php','content':'new'})
        self.assertEqual(source['fixture.php'], 'old')
        self.assertEqual(Workspace(source).project['fixture.php'], 'old')
        for path in ('../secret', '/etc/passwd', 'project/../../secret', 'other/SKILL.md', 'skill/SKILL.md', 'project/a\\b'):
            with self.assertRaises(ValueError):
                workspace.call('write_file', {'path':path,'content':'x'})
        self.assertEqual(workspace.call('read_file', {'path':'skill/SKILL.md'}), 'one skill')
        self.assertNotIn('evaluate.php', workspace.call('list_files', {}))

    def test_tool_loop_and_selected_skill_loaded(self):
        calls=[{'id':'c1','function':{'name':'write_file','arguments':json.dumps({'path':'project/fixture.php','content':'changed'})}}]
        requests=[]; checkpoints=[]
        def transport(m,messages,tools,max_tokens,timeout):
            requests.append(copy.deepcopy(messages))
            return response(calls if len(requests)==1 else None)
        skill={'files':{'SKILL.md':'Unique selected instructions'}}
        state=run_model(model(),self.task,skill,self.config['limits'],checkpoints.append,transport)
        self.assertEqual(state['files']['fixture.php'],'changed')
        self.assertEqual(state['cost_usd'],.02)
        self.assertEqual(state['tokens'],40)
        self.assertEqual(state['status'],'completed')
        self.assertIn('Unique selected instructions',requests[0][1]['content'])
        self.assertNotIn(self.task['evaluator'],str(requests))
        self.assertTrue(any(c['calls'][-1]['status']=='pending' for c in checkpoints if c['calls']))

    def test_missing_usage_stops_without_retry(self):
        count=[]
        def transport(*args):
            count.append(1);return response(cost=None)
        state=run_model(model(),self.task,None,self.config['limits'],lambda s:None,transport)
        self.assertEqual(len(count),1)
        self.assertFalse(state['cost_complete'])
        self.assertEqual(state['status'],'usage_unavailable')

    def test_request_exception_keeps_unknown_billing(self):
        def transport(*args): raise TimeoutError('timeout')
        state=run_model(model(),self.task,None,self.config['limits'],lambda s:None,transport)
        self.assertFalse(state['cost_complete'])
        self.assertEqual(state['calls'][0]['status'],'uncertain')

    def test_budget_blocks_call_before_dispatch(self):
        limits={**self.config['limits'],'max_run_usd':.0000001}
        def transport(*args): self.fail('An over-budget request was sent')
        state=run_model(model(),self.task,None,limits,lambda s:None,transport)
        self.assertEqual(state['status'],'budget_exceeded')
        self.assertEqual(state['calls'],[])

    def test_direct_usage_cache_and_reasoning_not_double_counted(self):
        usage={'prompt_tokens':100,'completion_tokens':50,'prompt_tokens_details':{'cached_tokens':40},'completion_tokens_details':{'reasoning_tokens':30}}
        self.assertAlmostEqual(estimate_cost(model('openai'),usage),.000164)
        self.assertIsNone(estimate_cost(model(),{}))

    def test_native_formats_and_gemini_thought_signature(self):
        from benchmark.adapters import TOOLS
        messages=[{'role':'system','content':'rules'},{'role':'user','content':'task'}]
        for adapter in ('openai','kimi','glm','anthropic','gemini','openrouter'):
            url,var,headers,body=build_request(model(adapter),messages,TOOLS,1234)
            self.assertTrue(url.startswith('https://'))
            self.assertTrue(var.endswith('_API_KEY'))
            self.assertNotIn('Authorization',headers)
            if adapter=='openai': self.assertEqual(body['max_output_tokens'],1234)
            if adapter=='openrouter': self.assertFalse(body['provider']['allow_fallbacks'])
        native={'candidates':[{'content':{'role':'model','parts':[{'functionCall':{'name':'list_files','args':{},'id':'f1'},'thoughtSignature':'opaque'}]},'finishReason':'STOP'}], 'usageMetadata':{'promptTokenCount':10,'candidatesTokenCount':5,'thoughtsTokenCount':7,'totalTokenCount':22}}
        normalized=normalize(model('gemini'),native)
        assistant=normalized['choices'][0]['message']
        self.assertEqual(normalized['usage']['completion_tokens'],12)
        messages.extend([assistant,{'role':'tool','tool_call_id':'f1','name':'list_files','content':'[]'}])
        payload=build_request(model('gemini'),messages,TOOLS,100)[3]
        self.assertEqual(payload['contents'][1]['parts'][0]['thoughtSignature'],'opaque')
        self.assertEqual(payload['contents'][2]['parts'][0]['functionResponse']['name'],'list_files')

    def test_anthropic_cache_and_tool_results(self):
        from benchmark.adapters import TOOLS
        native={'id':'a','model':'claude','content':[{'type':'tool_use','id':'t','name':'list_files','input':{}}], 'stop_reason':'tool_use', 'usage':{'input_tokens':10,'output_tokens':20,'cache_read_input_tokens':5,'cache_creation_input_tokens':7}}
        normalized=normalize(model('anthropic'),native)
        self.assertEqual(normalized['usage']['total_tokens'],42)
        messages=[{'role':'system','content':'rules'},{'role':'user','content':'task'},normalized['choices'][0]['message'],{'role':'tool','tool_call_id':'t','name':'list_files','content':'[]'}]
        payload=build_request(model('anthropic'),messages,TOOLS,100)[3]
        self.assertEqual(payload['messages'][-1]['content'][0]['type'],'tool_result')

    def test_reject_invalid_budget_and_placeholder_models(self):
        config={k:v for k,v in self.config.items() if not k.startswith('resolved_')}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'round.json'
            for value in (float('nan'),0,True,21):
                config['limits']['max_model_usd']=value
                atomic_json(path,config)
                with self.assertRaises(ValueError): load_round(path)

    def test_resume_no_reexecution_and_reject_configuration_drift(self):
        def evaluator(task,files,directory):
            return {'status':'passed','success':True,'score':100}
        config={k:v for k,v in self.config.items() if not k.startswith('resolved_')}
        config.update(tasks=['fix-search'],skills=[],repetitions=1)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'round.json';out=Path(tmp)/'results';atomic_json(path,config)
            run(path,out,evaluator=evaluator)
            with patch('benchmark.runner.run_model',side_effect=AssertionError('rerun')):
                run(path,out,evaluator=lambda *args:self.fail('re-evaluated'))
            summary=report(out)
            self.assertEqual(len(summary),2)
            config['seed']+=1;atomic_json(path,config)
            with self.assertRaises(ValueError):run(path,out,evaluator=evaluator)

    def test_per_model_budget_skips_exhausted_model_only(self):
        config={k:v for k,v in self.config.items() if not k.startswith('resolved_')}
        config.update(tasks=['fix-search'],skills=[],repetitions=3,models=[model(),{**model(),'id':'second-model'}])
        config['limits']={**config['limits'],'max_model_usd':1,'max_run_usd':1,'max_round_usd':20}
        def adapter(m,t,s,l,checkpoint):
            result={'calls':[],'files':t['reference'],'cost_usd':1,'cost_complete':True,'tokens':10,'tokens_complete':True,'status':'completed','simulated':False,'skill_reads':[]}
            checkpoint(result);return result
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'round.json';out=Path(tmp)/'results';atomic_json(path,config)
            run(path,out,evaluator=lambda *a:{'status':'passed','success':True,'score':100},adapter=adapter)
            status=json.loads((out/'round-status.json').read_text())
            self.assertEqual(status['spent_by_model_usd'],{'test-model':1,'second-model':1})
            self.assertEqual(len(status['skipped']),4)
            self.assertEqual(status['status'],'budget_exhausted')

    def test_chat_tool_response_has_only_protocol_fields(self):
        from benchmark.adapters import TOOLS
        messages=[{'role':'system','content':'rules'},{'role':'tool','tool_call_id':'t','name':'list_files','content':'[]'}]
        payload=build_request(model('kimi'),messages,TOOLS,100)[3]
        self.assertNotIn('name',payload['messages'][-1])
        self.assertEqual(messages[-1]['name'],'list_files')

    def test_responses_tool_replay_usage_and_private_reasoning(self):
        from benchmark.adapters import TOOLS
        native = {'id': 'resp_1', 'model': 'gpt-6-astra', 'status': 'completed',
                  'output': [{'type': 'reasoning', 'id': 'rs_1', 'summary': [], 'encrypted_content': 'opaque-private'},
                             {'type': 'function_call', 'id': 'fc_1', 'call_id': 'call_1',
                              'name': 'write_file', 'arguments': json.dumps({'path': 'project/fixture.php', 'content': 'changed'})}],
                  'usage': {'input_tokens': 100, 'output_tokens': 50,
                            'input_tokens_details': {'cached_tokens': 40, 'cache_write_tokens': 20},
                            'output_tokens_details': {'reasoning_tokens': 30}}}
        configured = {**model('openai'), 'id': 'gpt-6-astra', 'parameters': {'reasoning_effort': 'medium'}}
        normalized = normalize(configured, native)
        self.assertEqual(normalized['usage']['total_tokens'], 150)
        self.assertAlmostEqual(estimate_cost(configured, normalized['usage']), .000169)
        messages = [{'role': 'system', 'content': 'rules'}, {'role': 'user', 'content': 'task'},
                    normalized['choices'][0]['message'],
                    {'role': 'tool', 'tool_call_id': 'call_1', 'name': 'write_file', 'content': '"written"'}]
        url, _, _, payload = build_request(configured, messages, TOOLS, 8192)
        self.assertTrue(url.endswith('/responses'))
        self.assertEqual(payload['input'][2:4], native['output'])
        self.assertEqual(payload['input'][-1], {'type': 'function_call_output', 'call_id': 'call_1', 'output': '"written"'})
        self.assertEqual(payload['reasoning'], {'effort': 'medium'})
        self.assertFalse(payload['store'])
        self.assertEqual(payload['tools'][0]['name'], 'list_files')
        checkpoints = []
        def transport(*args):
            if not checkpoints or checkpoints[-1]['files']['fixture.php'] != 'changed':
                normalized['usage']['cost'] = estimate_cost(configured, normalized['usage'])
                return normalized
            return response()
        state = run_model(configured, self.task, None, self.config['limits'], checkpoints.append, transport)
        self.assertEqual(state['status'], 'completed')
        self.assertEqual(state['files']['fixture.php'], 'changed')
        self.assertNotIn('opaque-private', json.dumps(checkpoints))
        self.assertEqual(normalize(configured, {**native, 'status': 'incomplete'})['choices'][0]['message']['tool_calls'], [])
        self.assertIsNone(estimate_cost(configured, normalize(configured, {**native, 'usage': None})['usage']))

    def test_budget_group_shares_native_and_routed_allowance(self):
        config={k:v for k,v in self.config.items() if not k.startswith('resolved_')}
        config.update(tasks=['fix-search'],skills=[],repetitions=2,
                      models=[{**model('openai'),'budget_group':'same-model'},
                              {**model(),'id':'router/model','budget_group':'same-model'}])
        config['limits']={**config['limits'],'max_model_usd':1,'max_run_usd':1}
        def adapter(m,t,s,l,checkpoint):
            result={'calls':[],'files':t['reference'],'cost_usd':1,'cost_complete':True,'tokens':10,'tokens_complete':True,'status':'completed','simulated':False,'skill_reads':[]}
            checkpoint(result);return result
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'round.json';out=Path(tmp)/'results';atomic_json(path,config)
            run(path,out,evaluator=lambda *a:{'status':'passed','success':True,'score':100},adapter=adapter)
            status=json.loads((out/'round-status.json').read_text())
            self.assertEqual(status['spent_usd'],1)
            self.assertEqual(len(status['skipped']),3)

    def test_report_includes_failure_costs_and_excludes_infrastructure(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            condition={'task':'fix-search','category':'fixes','model':'m','skill':None,'simulated':False}
            planned=[{**condition,'repetition':i} for i in range(3)]
            atomic_json(out/'manifest.json',{'identity':'test','runs':planned,'config':{'models':[{'id':'m','adapter':'openai'}],'repetitions':3}})
            for i,status in enumerate(('passed','failed','infrastructure_error')):
                atomic_json(out/'runs'/str(i)/'result.json',{**condition,'repetition':i,'evaluation':{'status':status},'generation_status':'completed','success':i==0,'score':100 if i==0 else (0 if i==1 else None),'cost_usd':1,'generation_seconds':10})
            summary=report(out)[0]
            self.assertEqual(summary['evaluated'],2)
            self.assertEqual(summary['success_rate'],.5)
            self.assertEqual(summary['cost_per_success_usd'],3)
            self.assertEqual(summary['score_mean'],50)


if __name__=='__main__': unittest.main()
