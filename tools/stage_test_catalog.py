#!/usr/bin/env python3
"""Keep existing native QA cards on the exact catalog the SD package ships.

The accepted libraries stay in place; this synchronises companion metadata,
including source names, kit-only visibility and the complete factory bank map.
"""
from pathlib import Path
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')

def atomic_write(path,data):
    temporary=path.with_name(path.name+'.qa-'+str(os.getpid()))
    temporary.write_bytes(data);os.replace(temporary,path)

def stage():
    if not os.path.ismount('/Volumes/SSD'):raise RuntimeError('SSD is not mounted')
    data=(ROOT/'config/sound-catalog.json').read_bytes();catalog=json.loads(data)
    accepted={x['folder']:x['files'] for x in json.loads((ROOT/'config/native-engines.lock.json').read_text())}
    for relative in ('Plugins','Rhythmer/Plugins'):
        plugins=WORK/'sd-stage'/relative
        kit=plugins/'RHYTHMER - Rhythmer Kit'
        if not kit.is_dir():continue
        # Reject a mixed-generation card before making its catalogue visible.
        for engine in catalog['engines']:
            source=engine.get('source_folder',engine['folder']);expected=accepted.get(source)
            if expected is None:continue
            for rel in (engine['library'],'module/dsp.so'):
                if rel not in expected:continue
                file=plugins/source/rel
                if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=expected[rel]:
                    raise RuntimeError('QA card native library differs from accepted build: '+source+'/'+rel)
        atomic_write(kit/'rhythmer-kit.json',data)
        for engine in catalog['engines']:
            folder=plugins/engine['folder']
            if not folder.is_dir():continue
            atomic_write(folder/'rhythmer-source-name.json',(json.dumps({'name':engine['name']})+'\n').encode())
            marker=folder/'rhythmer-kit-only.json'
            if engine.get('kit_only'):atomic_write(marker,b'{"kit_only":true}\n')
            elif marker.exists():marker.unlink()
    print('QA card catalog matches the release:',sum(len(e.get('selection',e['sounds'])) for e in catalog['engines']),'source selections,',len(catalog['kits']),'kits',flush=True)
if __name__=='__main__':stage()
