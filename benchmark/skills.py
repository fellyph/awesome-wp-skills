"""Download only pinned, hash-checked skill resources; never load global skills."""
import hashlib
import urllib.request
from benchmark.core import ROOT, read_json


def sync():
    for skill_id, lock in read_json(ROOT / 'skills.lock.json').items():
        folder = ROOT / lock['path']
        for name, metadata in lock['resources'].items():
            target = folder / name
            if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == metadata['sha256']:
                continue
            with urllib.request.urlopen(metadata['url'], timeout=30) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != metadata['sha256']:
                raise ValueError(f'Upstream hash mismatch: {skill_id}/{name}')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        print(f'Prepared {skill_id} at {lock["revision"][:12]}')
