"""Restore the latest CI ledger before live work; missing history fails closed."""
import io
import json
import os
import subprocess
import zipfile
from pathlib import Path
from benchmark.core import atomic_json


def api(endpoint, raw=False):
    data=subprocess.check_output(['gh','api',endpoint])
    return data if raw else json.loads(data)


def main():
    repo=os.environ['GITHUB_REPOSITORY']
    current=os.environ['GITHUB_RUN_ID']
    if int(os.environ.get('GITHUB_RUN_ATTEMPT','1'))>1:
        raise ValueError('Start a new workflow with resume_run_id; rerunning a billable job may reuse stale budget history.')
    runs=api(f'repos/{repo}/actions/workflows/benchmark-live.yml/runs?per_page=100')['workflow_runs']
    older_runs=[r for r in runs if str(r['id'])!=current]
    artifacts=api(f'repos/{repo}/actions/artifacts?name=benchmark-model-budget&per_page=100')['artifacts']
    previous=[a for a in artifacts if str(a['workflow_run']['id'])!=current]
    target=Path('results/model-budget-ledger.json');target.parent.mkdir(parents=True,exist_ok=True)
    if previous:
        latest=max(previous,key=lambda a:a['id'])
        if older_runs and max(r['id'] for r in older_runs) != latest['workflow_run']['id']:
            raise ValueError('The latest live job has no saved budget artifact. Reconcile it before further paid work.')
        if latest['expired']:raise ValueError('Latest model budget expired. Restore the ledger before paid work.')
        raw=api(f'repos/{repo}/actions/artifacts/{latest["id"]}/zip',raw=True)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            ledger=json.loads(archive.read('model-budget-ledger.json'))
        if ledger.get('schema_version')!=1 or not isinstance(ledger.get('entries'),dict):raise ValueError('Invalid saved ledger')
        atomic_json(target,ledger)
    else:
        if older_runs:
            raise ValueError('Prior live jobs exist without a budget ledger. Reconcile their spending before running again.')
        atomic_json(target,{'schema_version':1,'entries':{}})
    print('Shared model budget restored; committed prior costs are merged by the runner.')

if __name__=='__main__':main()
