#!/usr/bin/env python3
"""Native port locations and content receipts shared by QA and packaging."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
def ports():
    return sorted(p for p in (ROOT/'ports').iterdir() if (p.name.startswith(('move-','fm1-')) or p.name=='drumx') and (p/'SOURCE.json').is_file())
def folder_for(port):
    family='Move' if port.name.startswith('move-') else 'FM1'
    ident=port.name.split('-',1)[1] if port.name!='drumx' else 'drumx'
    matches=list((WORK/'move-stage/Plugins').glob('RHYTHMER - '+family+' - '+ident+' - *'))
    if len(matches)!=1:raise RuntimeError('Missing/ambiguous staged port: '+port.name)
    return matches[0]
def hashes(folder):
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob('*')) if p.is_file()}
def validate():
    accepted=json.loads((ROOT/'config/native-engines.lock.json').read_text())
    for item in accepted:
        folder=WORK/'move-stage/Plugins'/item['folder']
        if hashes(folder)!=item['files']:raise RuntimeError('Port changed after host acceptance: '+item['id'])
    return accepted
