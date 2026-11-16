#!/usr/bin/env python3
"""Run each new instrument through the actual Rhythmer host in isolation."""
import json
from pathlib import Path
import subprocess
from engine_inventory import ROOT,hashes,ports,folder_for

WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
binary=WORK/'plugins/plugin_host_test'
results=[]
for folder in sorted((folder_for(port) for port in ports())):
    if not folder.is_dir():continue
    try:
        p=subprocess.run([str(binary),str(folder)],capture_output=True,text=True,timeout=90)
        result={'folder':folder.name,'passed':p.returncode==0,'exit':p.returncode,'output':p.stdout,'error':p.stderr[-4000:]}
    except subprocess.TimeoutExpired:
        result={'folder':folder.name,'passed':False,'error':'90-second host timeout'}
    results.append(result);print(folder.name,'PASS' if result['passed'] else 'FAIL',result.get('error','')[-500:],flush=True)
    if result['passed']:result['files']=hashes(folder)
(WORK/'move-host-results.json').write_text(json.dumps(results,indent=2)+'\n')
if all(x['passed'] for x in results):
    accepted=[];receipts={x['folder']:x for x in results}
    for port in ports():
        folder=folder_for(port);r=receipts[folder.name];pin=json.loads((port/'SOURCE.json').read_text())
        accepted.append(dict(id=port.name,folder=folder.name,source=pin,files=r['files'],host_validated=True,hardware_validated=False))
    (ROOT/'config').mkdir(exist_ok=True)
    (ROOT/'config/native-engines.lock.json').write_text(json.dumps(accepted,indent=2)+'\n')
raise SystemExit(0 if all(x['passed'] for x in results) else 1)
