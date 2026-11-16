#!/usr/bin/env python3
"""Read original native preset banks in isolated, bounded worker processes."""
import json
from pathlib import Path
import subprocess as sp
ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
result={}
probe=WORK/'plugins/preset_probe'
sp.run(['gcc','-O2','-std=gnu11',str(ROOT/'tools/probe_presets.c'),'-ldl','-o',str(probe)],check=True)
for port in sorted((ROOT/'ports').glob('move-*')):
    contract=json.loads((port/'contract.json').read_text())
    levels=contract.get('ui_hierarchy',{}).get('levels',{})
    selection=next((v.get('list_param') for v in levels.values() if v.get('count_param')=='preset_count' and v.get('list_param')),None)
    if not selection and any(p.get('key')=='preset' for p in contract.get('chain_params',[])):selection='preset'
    if port.name=='move-signal':selection='patch'
    if not selection:continue
    config=json.loads((port/'vst.json').read_text())
    candidates=list((WORK/'sd-stage/Plugins').glob('RHYTHMER - Move - '+port.name[5:]+' - */module'))
    if len(candidates)!=1:continue
    module=candidates[0]
    try:
        run=sp.run([str(probe),str(module/'dsp.so'),str(module),selection,*(["50"] if port.name=="move-signal" else [])],capture_output=True,text=True,timeout=180,check=True)
        data=json.loads(run.stdout.split('RHYTHMER_PRESETS_BEGIN\n',1)[1])
        if port.name=='move-dexed':
            names=[];setups=[];programs=[]
            for bank_index,bank in enumerate(sorted((module/'banks').glob('*.syx'),key=lambda p:p.name.lower())):
                run=sp.run([str(probe),str(module/'dsp.so'),str(module),selection,'32',str(bank_index)],capture_output=True,text=True,timeout=180,check=True)
                bank_data=json.loads(run.stdout.split('RHYTHMER_PRESETS_BEGIN\n',1)[1]);assert bank_data['count']==32
                names.extend(bank.stem+' / '+n.strip() for n in bank_data['names'])
                setups.extend([[['syx_bank_index',str(bank_index)]]] *32);programs.extend(range(32))
            assert len(names)==1056
            data=dict(count=len(names),names=names,setups=setups,programs=programs)
        data['selector']=selection
        if data['count']>0:result[config['so']]=data
        print(config['name'],data['count'],flush=True)
    except Exception as e:raise RuntimeError('Preset inspection failed: '+port.name) from e
(WORK/'sound-presets.json').write_text(json.dumps(result,indent=2)+'\n')
