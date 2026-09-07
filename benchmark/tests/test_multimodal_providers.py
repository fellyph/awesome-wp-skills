"""Native project-profile parity without paid provider calls."""
import copy
import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from benchmark.adapters.providers import build_request, count_tokens, estimate_cost, normalize, http_failure
from benchmark.core import ROOT, load_round
from benchmark.project_tools import PROJECT_TOOLS


class NativeProjectTests(unittest.TestCase):
    def test_anthropic_workspace_header_is_not_prompt_content(self):
        model = load_round(ROOT / 'configs/landing-page-fable.json')['models'][0]
        with patch.dict('os.environ', {'ANTHROPIC_WORKSPACE_ID': 'wrkspc_test'}):
            _, _, headers, payload = build_request(model, [{'role': 'system', 'content': 's'},
                {'role': 'user', 'content': 'u'}], PROJECT_TOOLS, 100)
        self.assertEqual(headers['anthropic-workspace-id'], 'wrkspc_test')
        self.assertNotIn('wrkspc_test', json.dumps(payload))

    def test_images_and_reasoning_replayed_and_counted(self):
        for name in ('astra', 'fable'):
            with self.subTest(name=name):
                model = load_round(ROOT / f'configs/landing-page-{name}.json')['models'][0]
                native = ([{'type': 'reasoning', 'id': 'r1', 'encrypted_content': 'opaque'}] if name == 'astra'
                          else [{'type': 'thinking', 'thinking': 'private', 'signature': 'opaque'}])
                messages = [{'role': 'system', 'content': 'system'},
                            {'role': 'user', 'content': 'brief', '_images': [{'mime_type': 'image/png', 'data': 'AAAA'}]},
                            {'role': 'assistant', '_native': native},
                            {'role': 'tool', 'tool_call_id': 'call1', 'name': 'preview', 'content': '{}',
                             '_images': [{'mime_type': 'image/png', 'data': 'BBBB'}]}]
                before = copy.deepcopy(messages)
                _, variable, _, wire = build_request(model, messages, PROJECT_TOOLS, 32768)
                captured = []
                def opener(req, **kwargs):
                    captured.append(req)
                    return io.BytesIO(b'{"input_tokens":4321}')
                with patch.dict('os.environ', {variable: 'test-secret'}), patch('urllib.request.urlopen', opener):
                    self.assertEqual(count_tokens(model, messages, PROJECT_TOOLS, 32768, 10), 4321)
                counted = json.loads(captured[0].data)
                for field in ('AAAA', 'BBBB', 'opaque'):
                    self.assertIn(field, json.dumps(counted))
                self.assertNotIn('test-secret', json.dumps(counted))
                self.assertNotIn('max_tokens', counted)
                self.assertNotIn('max_output_tokens', counted)
                self.assertEqual(messages, before)
                if name == 'astra':
                    self.assertEqual(counted['input'], wire['input'])
                    self.assertEqual(wire['input'][-1]['output'][1]['type'], 'input_image')
                    self.assertTrue(captured[0].full_url.endswith('/responses/input_tokens'))
                else:
                    self.assertEqual(counted['messages'], wire['messages'])
                    self.assertEqual(wire['messages'][-1]['content'][0]['content'][1]['type'], 'image')
                    self.assertTrue(captured[0].full_url.endswith('/messages/count_tokens'))

    def test_astra_long_context_tier_and_truncation(self):
        model = load_round(ROOT / 'configs/landing-page-astra.json')['models'][0]
        usage = {'prompt_tokens': 300000, 'completion_tokens': 1000,
                 'prompt_tokens_details': {'cached_tokens': 100000}}
        self.assertAlmostEqual(estimate_cost(model, usage), 4.275)
        value = normalize(model, {'status': 'incomplete', 'output': [],
                                 'incomplete_details': {'reason': 'max_output_tokens'}})
        self.assertEqual(value['choices'][0]['finish_reason'], 'length')

    def test_error_code_without_secret_message(self):
        error = HTTPError('https://api.example', 429, 'failure', {},
                          io.BytesIO(b'{"error":{"code":"insufficient_quota","message":"private-key"}}'))
        text = str(http_failure(error, 'Provider'))
        error.close()
        self.assertIn('insufficient_quota', text)
        self.assertNotIn('private-key', text)
