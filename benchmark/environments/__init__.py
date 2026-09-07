"""Isolated evaluation processes, with no model credentials in their environment."""
import json
import os
import signal
import subprocess
import tempfile
from pathlib import Path
from benchmark.core import ROOT, atomic_json, score


def evaluate(task, candidate, output, timeout=180):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    request = output / 'request.json'
    result = output / 'evidence.json'
    atomic_json(request, {'task': task, 'files': candidate})
    env = {k: os.environ[k] for k in ('PATH', 'SYSTEMROOT', 'PLAYWRIGHT_BROWSERS_PATH', 'NODE_EXTRA_CA_CERTS') if k in os.environ}
    # Keep Playground caches inside its own temporary root; no host workspace is mounted.
    with tempfile.TemporaryDirectory(prefix='wp-bench-') as temp:
        env['TMPDIR'] = temp
        with (output / 'playground.log').open('w') as log:
            proc = subprocess.Popen(['node', str(ROOT / 'environments/playground.mjs'), str(request.resolve()), str(result.resolve())],
                                    cwd=temp, env=env, stdout=log, stderr=log, start_new_session=True)
            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
                return {'status': 'infrastructure_error', 'error': 'Playground evaluation timed out', 'success': False, 'score': None}
    if proc.returncode != 0 or not result.exists():
        return {'status': 'infrastructure_error', 'error': 'Playground process failed; see log', 'success': False, 'score': None}
    evidence = json.loads(result.read_text())
    if evidence.get('failure') == 'infrastructure_error':
        return {'status': 'infrastructure_error', 'error': evidence['error'], 'success': False, 'score': None}
    if evidence.get('failure') == 'candidate_error':
        evidence['checks'] = {c['id']: False for c in task['checks']}
    try:
        graded = score(task, evidence)
    except ValueError as error:
        return {'status': 'infrastructure_error', 'error': str(error), 'success': False, 'score': None}
    return {**graded, 'status': 'passed' if graded['success'] else 'failed', 'error': evidence.get('error')}
