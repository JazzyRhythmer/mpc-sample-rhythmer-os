#!/usr/bin/env python3
"""Fetch only locked upstream assets into SSD cache and verify every SHA-256."""
import hashlib
import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path('/Volumes/SSD/Development/Caches/rhythmer-os/downloads')


if __name__ == '__main__':
    if not os.path.ismount('/Volumes/SSD'):
        raise SystemExit('SSD is not mounted')
    CACHE.mkdir(parents=True, exist_ok=True)
    for item in json.loads((ROOT / 'config/releases.lock.json').read_text()):
        target = CACHE / item['asset']
        if not target.is_file():
            temporary = target.with_suffix(target.suffix + '.part')
            with urllib.request.urlopen(item['url'], timeout=120) as src, temporary.open('wb') as out:
                while True:
                    data = src.read(1024 * 1024)
                    if not data:
                        break
                    out.write(data)
            temporary.replace(target)
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != item['sha256'] or target.stat().st_size != item['bytes']:
            raise SystemExit('Asset checksum/size mismatch: ' + item['asset'])
        print('Verified', item['asset'])
