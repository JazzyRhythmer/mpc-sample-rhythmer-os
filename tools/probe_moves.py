#!/usr/bin/env python3
"""Run each original DSP in a separate, time-bounded Linux process."""
import json
from pathlib import Path
import subprocess
import sys

WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
ROOT=WORK/'plugins'
OUT=WORK/'move-probes'
OUT.mkdir(parents=True,exist_ok=True)
binary=OUT/'probe'
subprocess.run(['gcc','-O2','-std=gnu11',str(ROOT/'tools/probe_move.c'),'-ldl','-o',str(binary)],check=True)
results=[]
for item in json.loads((WORK/'move-release-inventory.json').read_text()):
    if len(sys.argv)>1 and item['id'] not in sys.argv[1:]:continue
    result={'id':item['id']}
    if item['status']!='downloaded' or len(item.get('modules',[]))!=1:
        result['status']='no-module'
    else:
        mod=item['modules'][0];folder=WORK/mod['folder'];meta=json.loads((folder/'module.json').read_text())
        try:
            p=subprocess.run([str(binary),str(folder/mod['dsp']),str(folder),json.dumps(meta.get('defaults',{}))],
                             capture_output=True,text=True,timeout=45)
            (OUT/(item['id']+'.stderr')).write_text(p.stderr)
            if p.returncode:result.update(status='probe-failed',exit=p.returncode,error=p.stderr[-1500:])
            else:
                raw=p.stdout.split('RHYTHMER_PROBE_BEGIN\n',1)[1];info=json.loads(raw)
                for key in ('chain_params','ui_hierarchy','state'):
                    try:info[key]=json.loads(info[key])
                    except (ValueError,TypeError):pass
                (OUT/(item['id']+'.json')).write_text(json.dumps(info,indent=2)+'\n')
                result.update(status='sounding' if info['peak'] else 'silent',peak=info['peak'],metadata=bool(info['chain_params']))
        except Exception as e:result.update(status='probe-error',error=str(e))
    print(result['id'],result['status'],flush=True);results.append(result)
(OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
