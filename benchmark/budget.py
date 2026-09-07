"""Durable, cross-round model budgets. A crash keeps its reservation charged."""
import fcntl
import math
from pathlib import Path
from benchmark.core import ROOT, atomic_json, read_json


def execution_key(manifest, run_id):
    # Copies of a resumed round keep created_at; genuinely separate rounds do not.
    return manifest['identity'] + '/' + manifest['created_at'] + '/' + run_id


def account(model):
    return model.get('budget_group', model['id']).removeprefix('google/').removeprefix('openai/').removeprefix('anthropic/')


def charge(agent):
    known = agent.get('cost_usd', 0) or 0
    reserved = sum(c.get('reserved_usd', 0) for c in agent.get('calls', [])
                   if c.get('status') in ('pending', 'uncertain') or c.get('cost_usd') is None)
    return {'known_usd': known, 'reserved_usd': reserved, 'state': 'settled' if agent.get('cost_complete') and not reserved else 'uncertain'}


class BudgetLedger:
    def __init__(self, path=None):
        self.path = Path(path or ROOT.parent / 'results/model-budget-ledger.json')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = None

    def __enter__(self):
        self.handle = self.path.with_suffix('.lock').open('a')
        try: fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.handle.close(); raise ValueError('Another live benchmark holds the shared model budget') from None
        try:
            self.data = read_json(self.path) if self.path.exists() else {'schema_version': 1, 'entries': {}}
            if self.data.get('schema_version') != 1: raise ValueError('Unsupported budget ledger')
            if self.path == ROOT.parent / 'results/model-budget-ledger.json':
                seed = ROOT / 'budget-history.json'
                if seed.exists():
                    for key, value in read_json(seed)['entries'].items(): self.data['entries'].setdefault(key, value)
                self.import_rounds(ROOT.parent / 'results')
            if not isinstance(self.data.get('entries'), dict): raise ValueError('Invalid budget entries')
            for entry in self.data['entries'].values():
                if not isinstance(entry.get('model'), str) or not entry['model']:
                    raise ValueError('Invalid model in budget ledger')
                for field in ('known_usd', 'reserved_usd'):
                    value = entry.get(field)
                    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                        raise ValueError('Invalid amount in budget ledger')
            self.save()
            return self
        except BaseException:
            self.handle.close()
            raise

    def __exit__(self, *args):
        fcntl.flock(self.handle, fcntl.LOCK_UN); self.handle.close()

    def save(self): atomic_json(self.path, self.data)

    def import_rounds(self, root):
        for manifest_path in sorted(Path(root).glob('**/manifest.json')):
            manifest = read_json(manifest_path)
            if not {'config', 'identity'} <= manifest.keys(): continue
            for directory in sorted((manifest_path.parent / 'runs').glob('*')):
                progress = directory / 'progress.json'
                agent_path = directory / 'agent.json'
                if not progress.exists(): continue
                condition = read_json(progress)['condition']
                model = next(m for m in manifest['config']['models'] if m['id'] == condition['model'])
                if model['adapter'] == 'mock': continue
                key = execution_key(manifest, directory.name)
                if key in self.data['entries']: continue
                value = charge(read_json(agent_path)) if agent_path.exists() else {'known_usd': 0, 'reserved_usd': manifest['config']['limits']['max_run_usd'], 'state': 'interrupted'}
                self.data['entries'][key] = {'model': account(model), 'source': str(directory.relative_to(root)), **value}

    def spent(self, model):
        return sum(v['known_usd'] + v['reserved_usd'] for v in self.data['entries'].values() if v['model'] == account(model))

    def reserve(self, key, model, amount, ceiling):
        if key in self.data['entries']:
            raise ValueError('This live execution already has a budget reservation; inspect its checkpoint')
        if self.spent(model) + amount > min(20, ceiling) + 1e-9:
            return False
        self.data['entries'][key] = {'model': account(model), 'known_usd': 0, 'reserved_usd': amount, 'state': 'generating'}
        self.save(); return True

    def settle(self, key, agent):
        self.data['entries'][key].update(charge(agent)); self.save()
