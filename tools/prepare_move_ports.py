from release_profile import require_port
#!/usr/bin/env python3
"""Generate thin native ports from pinned, original Move modules and metadata.

This prepares candidates; packaging requires the independent acceptance list.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')


def descriptors(meta,probe):
    caps=meta.get('capabilities',{})
    params=probe.get('chain_params') or caps.get('chain_params') or meta.get('chain_params')
    hierarchy=probe.get('ui_hierarchy') or caps.get('ui_hierarchy') or {}
    if not isinstance(params,list):
        params=[];seen=set()
        for h in (probe.get('ui_hierarchy'),caps.get('ui_hierarchy')):
            if not isinstance(h,dict):continue
            for level in h.get('levels',{}).values():
                for p in level.get('params',[]):
                    if isinstance(p,dict) and p.get('key') and p.get('type') and p['key'] not in seen:
                        params.append(p);seen.add(p['key'])
    # Host UI cannot edit a path as a float, or write a module's read-only telemetry.
    params=[dict(p) for p in params if p.get('access')!='read' and p.get('type') not in ('filepath','string')]
    for p in params:
        p.setdefault('name',p.get('label',p['key']))
        if p.get('max_param'):
            value=probe.get(p['max_param'])
            if value is None or not str(value).isdigit() or int(value)<1:raise ValueError('Missing dynamic bound: '+p['key'])
            p['max']=int(value)-1
    if not params:raise ValueError('No editable numeric/enum parameter contract')
    return params,hierarchy


def prepare(ident):
    require_port('move-'+ident)
    releases={i['id']:i for i in json.loads((WORK/'move-release-inventory.json').read_text())}
    r=releases[ident];mod=r['modules'][0];folder=WORK/mod['folder']
    meta=json.loads((folder/'module.json').read_text());probe=json.loads((WORK/'move-probes'/(ident+'.json')).read_text())
    source=WORK/'source-depot-releases'/ident
    commit=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    licenses=[p for p in source.iterdir() if p.is_file() and p.name.lower().startswith(('license','copying'))]
    # These tagged projects explicitly grant MIT in README/module metadata.
    # Preserve that original grant rather than inventing an upstream LICENSE file.
    readme_mit=set()
    if not licenses and ident in readme_mit:
        licenses=[source/'README.md']
    if not licenses:raise ValueError('Source license requires separate review: '+ident)
    grant=licenses[0].read_text(errors='ignore')
    if 'PolyForm' in grant:raise ValueError('Redistribution/modification prohibited: '+ident)
    if ident not in readme_mit and not any(s in grant for s in ('Permission is hereby granted','GNU GENERAL PUBLIC LICENSE','BSD 3-Clause','BSD 2-Clause')):
        raise ValueError('Unclassified source license: '+ident)
    params,hierarchy=descriptors(meta,probe)
    port=ROOT/'ports'/('move-'+ident);port.mkdir(parents=True,exist_ok=True)
    contract={'chain_params':params,'ui_hierarchy':hierarchy}
    (port/'contract.json').write_text(json.dumps(contract,indent=2)+'\n')
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';n=int.from_bytes(hashlib.sha256(('rhythmer-move:'+ident).encode()).digest()[:4],'big');uid=''
    for unused in range(4):uid=alphabet[n%62]+uid;n//=62
    cfg={'name':meta.get('name',ident),'vendor':meta.get('author') or 'Schwung community','uid':uid,'version':1000,
         'so':'rhythmer-'+ident+'.so','module':'contract.json','custom_skin':True,'targets':['aarch64'],
         'defines':{'MODULE_SUBDIR':'"module"','HAS_SONG_POS':1},
         'build':{'root':'.','sources':['../common/move_loader.c'],'cflags':[],'libs':['-ldl','-lpthread']}}
    (port/'vst.json').write_text(json.dumps(cfg,indent=2)+'\n')
    for p in licenses:shutil.copy2(p,port/p.name)
    pin={k:r[k] for k in ('id','repo','tag','url','sha256','bytes','digest_checked')}
    pin.update(source_commit=commit,dsp_sha256=hashlib.sha256((folder/mod['dsp']).read_bytes()).hexdigest(),
               name=cfg['name'],parameters=len(params),module_folder=mod['folder'])
    (port/'SOURCE.json').write_text(json.dumps(pin,indent=2)+'\n')
    (port/'VENDORED.md').write_text('# Original '+cfg['name']+' native adapter\n\nOriginal DSP binary is reused byte-for-byte from the pinned release. '
        'Native loader and control metadata adapt the public API; no JAZZY DSP is used. Existing Open MPC wrapper and Rhythmer rack staging are retained. '
        'File-picker controls and read-only telemetry are not mapped to editable floats. Full preset/asset source review and host acceptance are separate gates.\n')
    print(ident,len(params),'parameters',uid)


if __name__=='__main__':
    if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD not mounted')
    for ident in sys.argv[1:]:prepare(ident)
