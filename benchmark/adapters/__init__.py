"""A shared, file-only agent harness for OpenRouter and deterministic CI mocks."""
import copy
import json
import math
import time
from datetime import datetime, timezone
from pathlib import PurePosixPath

from benchmark.adapters.providers import request as provider_request
SYSTEM = ('You are implementing a WordPress development task. Use the project file tools to make changes. '
          'Only project/ is writable. skill/ contains the one selected skill, if any; read its SKILL.md '
          'and relevant references before working. No other skills, shell, network, or hidden tests are available. '
          'Do not invent test results. Finish with a short description after writing all changes.')


def tool(name, description, properties):
    return {'type': 'function', 'function': {'name': name, 'description': description,
            'parameters': {'type': 'object', 'properties': {k: {'type': 'string'} for k in properties},
                           'required': list(properties), 'additionalProperties': False}}}


TOOLS = [tool('list_files', 'List all project and selected skill files.', []),
         tool('read_file', 'Read one UTF-8 file.', ['path']),
         tool('write_file', 'Create or replace a project file.', ['path', 'content']),
         tool('delete_file', 'Delete a project file.', ['path'])]


class Workspace:
    def __init__(self, project, skill=None):
        self.project = copy.deepcopy(project)
        self.skill = copy.deepcopy(skill or {})
        self.reads = []

    def call(self, name, arguments):
        if name == 'list_files':
            return sorted(['project/' + p for p in self.project] + ['skill/' + p for p in self.skill])
        value = arguments.get('path', '')
        path = PurePosixPath(value)
        if not isinstance(value, str) or path.is_absolute() or '\\' in value or any(p in ('', '.', '..', '__proto__', 'constructor') for p in value.split('/')) or len(path.parts) < 2:
            raise ValueError('Use a relative path in project/ or skill/')
        kind, relative = path.parts[0], '/'.join(path.parts[1:])
        if kind not in ('project', 'skill'):
            raise ValueError('Only project/ and the selected skill/ are accessible')
        target = self.project if kind == 'project' else self.skill
        if name == 'read_file':
            self.reads.append(value)
            return target[relative]
        if kind != 'project':
            raise ValueError('Skill resources are read-only')
        if name == 'write_file':
            content = arguments['content']
            if not isinstance(content, str) or len(content.encode()) > 256_000:
                raise ValueError('File must be UTF-8 text under 256 KB')
            if len(target) >= 100 and relative not in target:
                raise ValueError('Project file limit exceeded')
            if sum(len(v.encode()) for k, v in target.items() if k != relative) + len(content.encode()) > 1_000_000:
                raise ValueError('Project size limit exceeded')
            if any(p.startswith(relative + '/') or relative.startswith(p + '/') for p in target if p != relative):
                raise ValueError('A file conflicts with a directory')
            target[relative] = content
            return 'written'
        if name == 'delete_file':
            del target[relative]
            return 'deleted'
        raise ValueError('Unknown tool')


def valid_number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def usage_cost(usage):
    value = usage.get('cost')
    return float(value) if valid_number(value) else None


def run_model(model, task, skill, limits, checkpoint, transport=provider_request):
    workspace = Workspace(task['initial'], skill['files'] if skill else None)
    state = {'calls': [], 'cost_usd': 0.0, 'cost_complete': True, 'tokens': 0,
             'tokens_complete': True, 'status': 'completed', 'simulated': model['adapter'] == 'mock'}
    if state['simulated']:
        state['files'] = copy.deepcopy(task[model['behavior']])
        state['skill_reads'] = []
        checkpoint(state)
        return state
    skill_instructions = ''
    if skill:
        skill_instructions = '\nSelected skill instructions:\n' + workspace.call('read_file', {'path': 'skill/SKILL.md'})
    messages = [{'role': 'system', 'content': SYSTEM},
                {'role': 'user', 'content': task['prompt'] + skill_instructions + '\nAvailable files:\n' + '\n'.join(workspace.call('list_files', {}))}]
    start = time.monotonic()
    def save():
        state['files'] = workspace.project
        state['skill_reads'] = workspace.reads[:]
        checkpoint(copy.deepcopy(state))
    for call_index in range(limits['max_calls']):
        remaining = limits['timeout_seconds'] - (time.monotonic() - start)
        if remaining <= 0:
            state['status'] = 'timeout'; break
        if state['tokens'] >= limits['max_total_tokens'] or state['cost_usd'] >= limits['max_run_usd']:
            state['status'] = 'budget_exceeded'; break
        # Published, user-supplied rates are conservative planning inputs, not billed cost.
        rates = model['pricing']
        input_bound = len(json.dumps(messages).encode()) * 2 + len(json.dumps(TOOLS).encode()) * 2 + 4096
        output_limit = min(limits['max_output_tokens'], limits['max_total_tokens'] - state['tokens'] - input_bound)
        if output_limit <= 0:
            state['status'] = 'budget_exceeded'; break
        reserve = (input_bound * max(2 * rates['input_per_million_usd'], rates.get('cache_write_per_million_usd', 0)) + output_limit * rates['output_per_million_usd']) / 1_000_000
        if state['cost_usd'] + reserve > limits['max_run_usd']:
            state['status'] = 'budget_exceeded'; break
        record = {'index': call_index, 'status': 'pending', 'reserved_usd': reserve,
                  'started_at': datetime.now(timezone.utc).isoformat()}
        state['calls'].append(record)
        save()  # A killed request remains visible and must not be silently retried.
        try:
            response = transport(model, messages, TOOLS, output_limit, max(1, remaining))
            usage = response.get('usage') or {}
            cost = usage_cost(usage)
            record.update({'status': 'received', 'id': response.get('id'), 'model': response.get('model'),
                           'provider': response.get('provider'), 'usage': usage, 'cost_usd': cost,
                           'cost_basis': usage.get('cost_basis', 'provider_reported'),
                           'system_fingerprint': response.get('system_fingerprint')})
            if cost is None:
                state['cost_complete'] = False
            else:
                state['cost_usd'] += cost
            tokens = usage.get('total_tokens')
            if not valid_number(tokens):
                state['tokens_complete'] = False
            else:
                state['tokens'] += tokens
            if not state['cost_complete'] or not state['tokens_complete']:
                state['status'] = 'usage_unavailable'; save(); break
            choice = response['choices'][0]
            message = choice['message']
            # Preserve provider reasoning metadata for multi-turn tool protocols.
            messages.append(message)
            record['finish_reason'] = choice.get('finish_reason')
            tool_calls = message.get('tool_calls') or []
            for call in tool_calls:
                try:
                    arguments = json.loads(call['function']['arguments'])
                    result = workspace.call(call['function']['name'], arguments)
                except (ValueError, KeyError, TypeError) as error:
                    result = {'error': str(error)}
                messages.append({'role': 'tool', 'tool_call_id': call['id'], 'name': call['function']['name'], 'content': json.dumps(result)})
            # Do not persist private reasoning text. The reproducible inputs, edits and usage suffice.
            record['tools'] = [{'name': c['function']['name'], 'arguments': c['function']['arguments']} for c in tool_calls]
            save()
            if not tool_calls:
                if choice.get('finish_reason') != 'stop':
                    state['status'] = 'incomplete'
                break
        except Exception as error:
            record.update({'status': 'uncertain', 'error': str(error)})
            state['cost_complete'] = False
            state['status'] = 'provider_error'
            save()
            break
    else:
        state['status'] = 'call_limit'
    if state['cost_usd'] > limits['max_run_usd'] or state['tokens'] > limits['max_total_tokens']:
        state['status'] = 'budget_exceeded'
    save()
    return state
