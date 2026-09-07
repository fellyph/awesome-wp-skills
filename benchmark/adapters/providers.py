"""Native API wire formats behind one tool protocol; no provider SDK state."""
import copy
import json
import math
import os
import urllib.error
import urllib.parse
import urllib.request

PROVIDERS = {
    'openai': ('https://api.openai.com/v1/responses', 'OPENAI_API_KEY'),
    'anthropic': ('https://api.anthropic.com/v1/messages', 'ANTHROPIC_API_KEY'),
    'gemini': ('https://generativelanguage.googleapis.com/v1beta/models/', 'GEMINI_API_KEY'),
    'kimi': ('https://api.moonshot.ai/v1/chat/completions', 'MOONSHOT_API_KEY'),
    'glm': ('https://api.z.ai/api/paas/v4/chat/completions', 'ZAI_API_KEY'),
    'openrouter': ('https://openrouter.ai/api/v1/chat/completions', 'OPENROUTER_API_KEY'),
}
PARAMETERS = {
    'openai': {'temperature', 'top_p', 'reasoning_effort'},
    'anthropic': {'temperature', 'top_p', 'thinking', 'output_config'},
    'gemini': {'temperature', 'topP', 'seed', 'thinkingConfig'},
    'kimi': {'temperature', 'top_p', 'thinking'},
    'glm': {'temperature', 'top_p', 'thinking'},
    'openrouter': {'temperature', 'top_p', 'seed', 'reasoning'},
}


def build_request(model, messages, tools, max_tokens):
    adapter = model['adapter']
    url, variable = PROVIDERS[adapter]
    headers = {'Content-Type': 'application/json'}
    parameters = copy.deepcopy(model['parameters'])
    if adapter == 'openai':
        native = []
        for message in messages:
            if message['role'] == 'assistant':
                # Replay reasoning and function items together. Encrypted reasoning stays in memory.
                native.extend(copy.deepcopy(message['_native']))
            elif message['role'] == 'tool':
                native.append({'type': 'function_call_output', 'call_id': message['tool_call_id'],
                               'output': message['content']})
            else:
                native.append({'role': message['role'], 'content': message['content']})
        effort = parameters.pop('reasoning_effort', None)
        payload = {'model': model['id'], 'input': native,
                   'tools': [{'type': 'function', **copy.deepcopy(t['function']), 'strict': True} for t in tools],
                   'max_output_tokens': max_tokens, 'store': False, 'service_tier': 'default',
                   'include': ['reasoning.encrypted_content'], **parameters}
        if effort is not None:
            payload['reasoning'] = {'effort': effort}
        return url, variable, headers, payload
    if adapter in ('kimi', 'glm', 'openrouter'):
        chat_messages = [{k: v for k, v in m.items() if not (m['role'] == 'tool' and k == 'name')} for m in messages]
        payload = {'model': model['id'], 'messages': chat_messages, 'tools': tools, 'stream': False, **parameters}
        payload['max_tokens'] = max_tokens
        if adapter == 'openrouter':
            payload['provider'] = {'only': [model['provider']], 'allow_fallbacks': False, 'require_parameters': True}
        return url, variable, headers, payload
    native = []
    for message in messages[1:]:
        role = message['role']
        if adapter == 'anthropic':
            if role == 'assistant':
                blocks = message['_native']
            elif role == 'tool':
                blocks = [{'type': 'tool_result', 'tool_use_id': message['tool_call_id'], 'content': message['content']}]
            else:
                blocks = [{'type': 'text', 'text': message['content']}]
            native_role = 'assistant' if role == 'assistant' else 'user'
            if native and native[-1]['role'] == native_role:
                native[-1]['content'].extend(blocks)
            else:
                native.append({'role': native_role, 'content': copy.deepcopy(blocks)})
        else:
            if role == 'assistant':
                parts = message['_native']['parts']
            elif role == 'tool':
                parts = [{'functionResponse': {'id': message['tool_call_id'], 'name': message['name'],
                                              'response': {'result': json.loads(message['content'])}}}]
            else:
                parts = [{'text': message['content']}]
            native_role = 'model' if role == 'assistant' else 'user'
            if native and native[-1]['role'] == native_role:
                native[-1]['parts'].extend(copy.deepcopy(parts))
            else:
                native.append({'role': native_role, 'parts': copy.deepcopy(parts)})
    if adapter == 'anthropic':
        headers['anthropic-version'] = '2023-06-01'
        payload = {'model': model['id'], 'max_tokens': max_tokens, 'system': messages[0]['content'],
                   'messages': native, 'tools': [{'name': t['function']['name'], 'description': t['function']['description'],
                   'input_schema': t['function']['parameters']} for t in tools], **parameters}
    else:
        url += urllib.parse.quote(model['id'], safe='') + ':generateContent'
        declarations = []
        for tool in tools:
            declaration = copy.deepcopy(tool['function'])
            declaration['parameters'].pop('additionalProperties', None)
            if not declaration['parameters']['properties']:
                declaration.pop('parameters')
            declarations.append(declaration)
        payload = {'systemInstruction': {'parts': [{'text': messages[0]['content']}]}, 'contents': native,
                   'tools': [{'functionDeclarations': declarations}],
                   'generationConfig': {**parameters, 'maxOutputTokens': max_tokens}}
    return url, variable, headers, payload


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def normalize(model, response):
    adapter = model['adapter']
    if adapter in ('kimi', 'glm', 'openrouter'):
        normalized = copy.deepcopy(response)
        # Z.AI may return already-decoded function arguments.
        for choice in normalized.get('choices', []):
            for call in choice['message'].get('tool_calls') or []:
                if isinstance(call['function']['arguments'], dict):
                    call['function']['arguments'] = json.dumps(call['function']['arguments'])
        return normalized
    if adapter == 'openai':
        native = response.get('output', [])
        completed = response.get('status') == 'completed'
        calls = [{'id': c['call_id'], 'type': 'function',
                  'function': {'name': c['name'], 'arguments': c['arguments']}}
                 for c in native if c['type'] == 'function_call'] if completed else []
        raw = response.get('usage') or {}
        usage = {'raw': raw}
        prompt, completion = raw.get('input_tokens'), raw.get('output_tokens')
        if number(prompt) and number(completion):
            usage.update(prompt_tokens=prompt, completion_tokens=completion, total_tokens=prompt+completion,
                         prompt_tokens_details=raw.get('input_tokens_details') or {},
                         completion_tokens_details=raw.get('output_tokens_details') or {})
        finish = ('tool_calls' if calls else 'stop') if completed else response.get('status', 'incomplete')
        text = ''.join(part.get('text', '') for item in native if item['type'] == 'message'
                       for part in item.get('content', []) if part['type'] == 'output_text')
    elif adapter == 'anthropic':
        content = response['content']
        calls = [{'id': c['id'], 'type': 'function', 'function': {'name': c['name'], 'arguments': json.dumps(c['input'])}}
                 for c in content if c['type'] == 'tool_use']
        raw = response.get('usage', {})
        input_tokens = raw.get('input_tokens')
        output_tokens = raw.get('output_tokens')
        cached = raw.get('cache_read_input_tokens', 0)
        cache_write = raw.get('cache_creation_input_tokens', 0)
        usage = {'raw': raw}
        if all(number(n) for n in (input_tokens, output_tokens, cached, cache_write)):
            total_input = input_tokens + cached + cache_write
            usage.update(prompt_tokens=total_input, completion_tokens=output_tokens, total_tokens=total_input+output_tokens,
                         prompt_tokens_details={'cached_tokens': cached, 'cache_write_tokens': cache_write})
        finish = {'end_turn': 'stop', 'tool_use': 'tool_calls'}.get(response.get('stop_reason'), response.get('stop_reason'))
        native = content
        text = ''.join(c.get('text', '') for c in content if c['type'] == 'text')
    else:
        candidate = response.get('candidates', [{}])[0]
        native = candidate.get('content', {'parts': []})
        calls = []
        for i, part in enumerate(native['parts']):
            if 'functionCall' in part:
                c = part['functionCall']
                calls.append({'id': c.get('id') or f'call_{i}', 'type': 'function',
                              'function': {'name': c['name'], 'arguments': json.dumps(c.get('args', {}))}})
        raw = response.get('usageMetadata', {})
        usage = {'raw': raw}
        prompt = raw.get('promptTokenCount')
        total = raw.get('totalTokenCount')
        if number(prompt) and number(total) and total >= prompt:
            usage.update(prompt_tokens=prompt, completion_tokens=total-prompt, total_tokens=total,
                         prompt_tokens_details={'cached_tokens': raw.get('cachedContentTokenCount', 0)},
                         completion_tokens_details={'reasoning_tokens': raw.get('thoughtsTokenCount', 0)})
        finish = 'tool_calls' if calls else ('stop' if candidate.get('finishReason') == 'STOP' else candidate.get('finishReason', 'blocked'))
        text = ''.join(p.get('text', '') for p in native['parts'] if not p.get('thought'))
    return {'id': response.get('id', response.get('responseId')), 'model': response.get('model', response.get('modelVersion')),
            'usage': usage, 'choices': [{'finish_reason': finish, 'message': {'role': 'assistant', 'content': text,
                'tool_calls': calls, '_native': native}}]}


def estimate_cost(model, usage):
    """Count cached input as a subset; output already includes reasoning tokens."""
    prompt, completion = usage.get('prompt_tokens'), usage.get('completion_tokens')
    if not number(prompt) or not number(completion):
        return None
    details = usage.get('prompt_tokens_details') or {}
    cached = details.get('cached_tokens', usage.get('cached_tokens', 0))
    created = details.get('cache_write_tokens', 0)
    if not number(cached) or not number(created) or cached + created > prompt:
        return None
    rates = model['pricing']
    # Missing cache-specific rates use conservative normal-input pricing, with cache writes
    # charged at at least 2x input. Reports label all direct-provider costs as estimates.
    read_rate = rates.get('cached_input_per_million_usd', rates['input_per_million_usd'])
    write_rate = rates.get('cache_write_per_million_usd', 2 * rates['input_per_million_usd'])
    return ((prompt-cached-created)*rates['input_per_million_usd'] + cached*read_rate + created*write_rate
            + completion*rates['output_per_million_usd']) / 1_000_000


def request(model, messages, tools, max_tokens, timeout):
    url, variable, headers, payload = build_request(model, messages, tools, max_tokens)
    key = os.environ.get(variable)
    if not key:
        raise ValueError(f'Set {variable} for this adapter')
    if model['adapter'] == 'anthropic':
        headers['x-api-key'] = key
    elif model['adapter'] == 'gemini':
        headers['x-goog-api-key'] = key
    else:
        headers['Authorization'] = 'Bearer ' + key
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as result:
            raw = json.load(result)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f'Provider HTTP {error.code}; no automatic retry') from None
    response = normalize(model, raw)
    usage = response.setdefault('usage', {})
    if model['adapter'] != 'openrouter':
        usage['cost'] = estimate_cost(model, usage)
        usage['cost_basis'] = 'estimated_from_configured_rates'
    else:
        usage['cost_basis'] = 'provider_reported' if number(usage.get('cost')) else 'unavailable'
    return response
