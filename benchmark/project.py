"""Project v2 packaging and a credential-free, bounded Playground tool bridge."""
import base64
import hashlib
import io
import json
import os
import selectors
import signal
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path
from benchmark.core import ROOT, atomic_json, digest

PROFILE = 'wordpress-project-v2'
TASK_ROOT = ROOT / 'tasks/agency-landing-page'


def safe_files(files):
    for name, contents in files.items():
        if not isinstance(name, str) or name.startswith('/') or '\\' in name or any(p in ('', '.', '..', '__proto__', 'constructor') for p in name.split('/')):
            raise ValueError('Invalid package path')
        if not isinstance(contents, str):
            raise ValueError('Only UTF-8 project files are supported')
    return files


def zip_bytes(files):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, value)
    return out.getvalue()


def package(task, files, output):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    safe_files(files)
    theme = zip_bytes({'benchmark-fixture/' + k: v for k, v in files.items()})
    blueprint = json.loads(json.dumps(task['blueprint']))
    blueprint['steps'] = [
        {'step': 'mkdir', 'path': '/wordpress/wp-content/mu-plugins'},
        {'step': 'writeFile', 'path': '/wordpress/wp-content/mu-plugins/benchmark-contact.php',
         'data': (TASK_ROOT / 'fixtures/contact.php').read_text()},
        {'step': 'installTheme', 'themeData': {'resource': 'bundled', 'path': '/theme.zip'},
         'options': {'activate': True}},
        {'step': 'runPHP', 'code': (TASK_ROOT / 'fixtures/setup.php').read_text()},
    ]
    blueprint['landingPage'] = '/'
    (output / 'theme.zip').write_bytes(theme)
    atomic_json(output / 'blueprint.json', blueprint)
    bundle = zip_bytes({'blueprint.json': json.dumps(blueprint), 'theme.zip': theme})
    (output / 'playground-bundle.zip').write_bytes(bundle)
    atomic_json(output / 'package.json', {'profile': PROFILE, 'task_hash': task['hash'],
        'theme_sha256': hashlib.sha256(theme).hexdigest(), 'bundle_sha256': hashlib.sha256(bundle).hexdigest(),
        'source_hash': digest(files)})
    return output / 'playground-bundle.zip'


class Preview:
    """No host mount, model key, hidden evaluator, or reference source in worker input."""
    def __init__(self, task, timeout):
        self.task = task
        self.deadline = time.monotonic() + timeout
        self.temp = tempfile.TemporaryDirectory(prefix='wp-project-preview-')
        env = {k: os.environ[k] for k in ('PATH', 'PLAYWRIGHT_BROWSERS_PATH', 'NODE_EXTRA_CA_CERTS') if k in os.environ}
        env['TMPDIR'] = self.temp.name
        self.log = open(Path(self.temp.name) / 'worker.log', 'w')
        self.proc = subprocess.Popen(['node', str(ROOT / 'environments/project-server.mjs')],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.log, cwd=self.temp.name,
            env=env, start_new_session=True)
        self.buffer = b''
        self.last_hash = None
        try:
            self.request({'op': 'start', 'blueprint': task['blueprint']})
        except BaseException:
            self.close(); raise

    def request(self, value):
        self.proc.stdin.write(json.dumps(value).encode() + b'\n'); self.proc.stdin.flush()
        with selectors.DefaultSelector() as selector:
            selector.register(self.proc.stdout, selectors.EVENT_READ)
            while True:
                while b'\n' in self.buffer:
                    line, self.buffer = self.buffer.split(b'\n', 1)
                    if line.startswith(b'@@BENCH@@'):
                        result = json.loads(line[9:])
                        if 'error' in result: raise ValueError(result['error'])
                        return result
                remaining = min(120, self.deadline - time.monotonic())
                if remaining <= 0 or not selector.select(remaining): raise TimeoutError('Playground tool timed out')
                chunk = os.read(self.proc.stdout.fileno(), 65536)
                if not chunk: raise RuntimeError('Playground preview worker stopped')
                self.buffer += chunk
                if len(self.buffer) > 8_000_000: raise ValueError('Preview response too large')

    def call(self, name, arguments, files):
        fingerprint = digest(files)
        if fingerprint != self.last_hash:
            self.request({'op': 'sync', 'files': safe_files(files), 'fixture': (TASK_ROOT / 'fixtures/contact.php').read_text()})
            self.last_hash = fingerprint
        return self.request({'op': name, 'arguments': arguments})

    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
            try: self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL); self.proc.wait()
        self.proc.stdout.close(); self.log.close(); self.temp.cleanup()


def reference_images(task):
    if task.get('profile') != PROFILE: return []
    return [{'mime_type': 'image/png', 'data': base64.b64encode((TASK_ROOT / 'public' / name).read_bytes()).decode()}
            for name in ('reference-desktop.png', 'reference-mobile.png')]
