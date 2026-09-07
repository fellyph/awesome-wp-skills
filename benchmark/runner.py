"""Sequential execution, durable checkpoints, and explicit cost accounting."""
import os
import platform
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone
from benchmark.core import ROOT, atomic_json, digest, load_round, matrix, read_json
from benchmark.adapters import run_model
from benchmark.budget import execution_key
from benchmark.adapters.providers import PROVIDERS
from benchmark.environments import evaluate


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def environment():
    def command(args):
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    return {'python': platform.python_version(), 'node': command(['node', '--version']),
            'system': platform.platform(), 'machine': platform.machine(), 'cpu_count': os.cpu_count(),
            'runner_os': os.environ.get('RUNNER_OS'), 'runner_arch': os.environ.get('RUNNER_ARCH'),
            'image_version': os.environ.get('ImageVersion'), 'playground': read_json(ROOT.parent / 'package.json')['devDependencies']['@wp-playground/cli'],
            'runtime': 'PHP WASM / SQLite', 'tool_profile': 'files-only-v1'}


def protocol_hash():
    paths = sorted(p for p in ROOT.rglob('*') if p.suffix in ('.py', '.mjs')
                   and not any(part in ('.cache', 'skills', 'tests', '__pycache__') for part in p.relative_to(ROOT).parts))
    values = {str(p.relative_to(ROOT)): p.read_text() for p in paths}
    values['package-lock.json'] = (ROOT.parent / 'package-lock.json').read_text()
    return digest(values)


@contextmanager
def exclusive_lock(output):
    import fcntl
    with (output / '.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Another process is writing this round') from None
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def run(config_path, output, evaluator=evaluate, adapter=run_model):
    config = load_round(config_path)
    if adapter is run_model and any(m['adapter'] != 'mock' for m in config['models']):
        from benchmark.budget import BudgetLedger
        with BudgetLedger() as ledger:
            return _run(config_path, output, evaluator, adapter, ledger)
    return _run(config_path, output, evaluator, adapter)


def _run(config_path, output, evaluator, adapter, ledger=None):
    config = load_round(config_path)
    for model in config['models']:
        if model['adapter'] != 'mock' and adapter is run_model and not os.environ.get(PROVIDERS[model['adapter']][1]):
            raise ValueError(f"Set {PROVIDERS[model['adapter']][1]} before starting this round")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    identity = digest({'config': config, 'protocol': protocol_hash()})
    env = environment()
    env['tool_profile'] = next(iter(config['resolved_tasks'].values()))['profile']
    with exclusive_lock(output):
        manifest_path = output / 'manifest.json'
        if manifest_path.exists():
            manifest = read_json(manifest_path)
            if manifest['identity'] != identity:
                raise ValueError('Configuration, task, skill, or executor changed. Use a new output directory.')
            # Cross-job resume is possible on the same declared environment; individual host data is retained.
            for key in ('node', 'python', 'machine', 'playground', 'tool_profile', 'image_version'):
                if manifest['environment'].get(key) != env.get(key):
                    raise ValueError(f'Environment changed ({key}); use a new output directory')
        else:
            manifest = {'schema_version': 1, 'identity': identity, 'created_at': utcnow(),
                        'environment': env, 'config': config, 'runs': matrix(config)}
            atomic_json(manifest_path, manifest)
        spent = 0.0
        model_spent = {}
        skipped = []
        for index, condition in enumerate(manifest['runs']):
            run_id = f'{index:04d}-' + digest({'identity': identity, **condition})[:12]
            directory = output / 'runs' / run_id
            directory.mkdir(parents=True, exist_ok=True)
            result_path = directory / 'result.json'
            agent_path = directory / 'agent.json'
            progress_path = directory / 'progress.json'
            model = next(m for m in config['models'] if m['id'] == condition['model'])
            budget_group = model.get('budget_group', model['id'])
            task = config['resolved_tasks'][condition['task']]
            skill = config['resolved_skills'].get(condition['skill'])
            if result_path.exists():
                previous = read_json(result_path)
                spent += previous['cost_usd'] or 0
                model_spent[budget_group] = model_spent.get(budget_group, 0) + (previous['cost_usd'] or 0)
                if not previous['cost_complete']:
                    raise ValueError('Uncertain provider billing in a previous run; reconcile before starting more paid work')
                continue
            started = utcnow()
            timer = time.monotonic()
            if progress_path.exists():
                previous = read_json(progress_path)
                started = previous['started_at']
                agent = read_json(agent_path) if agent_path.exists() else None
                if previous['phase'] == 'generating' and (not agent or agent['status'] == 'completed'):
                    # The last successful API call may have finished just before a crash. A missing
                    # generation_complete marker cannot authorize another potentially billable call.
                    if model['adapter'] != 'mock':
                        raise ValueError(f'Interrupted generation {run_id}; no automatic paid retry. Inspect checkpoint.')
                    agent = None
            else:
                agent = None
            if agent is None:
                remaining = min(config['limits']['max_round_usd'] - spent, config['limits']['max_model_usd'] - model_spent.get(budget_group, 0))
                if remaining < config['limits']['max_run_usd'] and model['adapter'] != 'mock':
                    skipped.append(run_id)
                    continue
                if ledger and model['adapter'] != 'mock' and not ledger.reserve(execution_key(manifest, run_id), model, config['limits']['max_run_usd'], config['limits']['max_model_usd']):
                    skipped.append(run_id)
                    continue
                atomic_json(progress_path, {'phase': 'generating', 'started_at': started, 'condition': condition})
                agent = adapter(model, task, skill, config['limits'], lambda state: atomic_json(agent_path, state))
                if ledger and model['adapter'] != 'mock':
                    ledger.settle(execution_key(manifest, run_id), agent)
                agent['generation_seconds'] = time.monotonic() - timer
                atomic_json(agent_path, agent)
                atomic_json(progress_path, {'phase': 'evaluating', 'started_at': started, 'condition': condition})
            eval_start = time.monotonic()
            baseline = None
            if task['category'] == 'performance':
                baseline = evaluator(task, task['initial'], directory / 'performance-before')
            evaluation = evaluator(task, agent['files'], directory / 'evaluation')
            if baseline is not None:
                evaluation['performance_before'] = baseline
                if baseline['status'] == 'infrastructure_error':
                    evaluation.update(status='infrastructure_error', success=False, score=None)
            eval_seconds = time.monotonic() - eval_start
            # Preserve criteria evidence, but a budget-limited or incomplete generation is not a success.
            complete = agent['status'] == 'completed'
            result = {**condition, 'run_id': run_id, 'started_at': started, 'finished_at': utcnow(),
                      'environment': env, 'task_hash': task['hash'], 'task_version': task['version'],
                      'profile': task['profile'], 'scoring_version': task['scoring_version'],
                      'artifact_pass': evaluation['success'], 'execution_completion': complete,
                      'delivery_success': complete and evaluation['success'],
                      'visual_review': {'status': 'pending'} if task['profile'] == 'wordpress-project-v2' else None,
                      'development_iterations': agent.get('development_iterations', 0),
                      'skill_hash': skill['sha256'] if skill else None,
                      'cost_basis': sorted({c.get('cost_basis', 'unknown') for c in agent['calls']}) or ['simulated'],
                      'adapter': model['adapter'], 'budget_group': budget_group,
                      'simulated': agent['simulated'], 'generation_status': agent['status'],
                      'evaluation': evaluation, 'status': evaluation['status'] if complete else agent['status'],
                      'success': complete and evaluation['success'], 'score': evaluation['score'],
                      'cost_usd': agent['cost_usd'] if agent['cost_complete'] else None,
                      'known_cost_usd': agent['cost_usd'], 'cost_complete': agent['cost_complete'],
                      'tokens': agent['tokens'] if agent['tokens_complete'] else None,
                      'calls': len(agent['calls']), 'generation_seconds': agent.get('generation_seconds'),
                      'evaluation_seconds': eval_seconds,
                      'skill_reads': agent['skill_reads']}
            atomic_json(result_path, result)
            # Plain text source artifacts can be inspected independently of the JSON checkpoint.
            for name, contents in agent['files'].items():
                target = directory / 'project' / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(contents)
            spent += agent['cost_usd']
            model_spent[budget_group] = model_spent.get(budget_group, 0) + agent['cost_usd']
            print(f'{run_id}: {condition["model"]} / {condition["task"]} / {condition["skill"] or "none"}: {result["status"]}', flush=True)
            if not agent['cost_complete']:
                atomic_json(output / 'round-status.json', {'status': 'billing_uncertain', 'run_id': run_id})
                break
        else:
            atomic_json(output / 'round-status.json', {'status': 'budget_exhausted' if skipped else 'completed', 'spent_usd': spent, 'spent_by_model_usd': model_spent, 'skipped': skipped})
    return output
