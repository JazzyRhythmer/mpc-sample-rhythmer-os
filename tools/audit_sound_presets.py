#!/usr/bin/env python3
"""Survey every preset in isolated hosts, then retry silent patches with a longer gate."""
import json,os,subprocess as sp
from pathlib import Path
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
catalog=WORK/'sound-catalog.json'
os.environ.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
rows=[];errors=[]
for e in json.loads(catalog.read_text())['engines']:
 command=[str(WORK/'sound_rack_asan'),str(catalog),str(WORK/'sd-stage/Rhythmer/Plugins'),'audit',e['folder']]
 run=sp.run(command,capture_output=True,text=True,timeout=900)
 if run.returncode:
  errors.append(dict(engine=e['name'],exit=run.returncode,error=run.stderr[-3000:]));print('ERROR',e['name'],run.returncode,flush=True);continue
 row=json.loads((WORK/'preset-audit.json').read_text())[0]
 silent=[p['index'] for p in row['patches'] if p['silent']]
 if silent:
  env=dict(os.environ,RHYTHMER_AUDIT_LONG='1',RHYTHMER_AUDIT_INDICES=','.join(map(str,silent)))
  run=sp.run(command,capture_output=True,text=True,timeout=900,env=env)
  if run.returncode:errors.append(dict(engine=e['name'],stage='long',exit=run.returncode,error=run.stderr[-3000:]))
  else:
   retry={p['index']:p for p in json.loads((WORK/'preset-audit.json').read_text())[0]['patches']}
   for p in row['patches']:
    if p['index'] in retry:p.update(retry[p['index']]);p['long_gate']=True
 remaining=[p['index'] for p in row['patches'] if p['silent']]
 if remaining:
  # Some original engines keep non-serialized voice/controller history across
  # repeated patch switches. Real rack selection loads a fresh instance.
  env=dict(os.environ,RHYTHMER_AUDIT_LONG='1',RHYTHMER_AUDIT_FRESH='1',RHYTHMER_AUDIT_INDICES=','.join(map(str,remaining)))
  run=sp.run(command,capture_output=True,text=True,timeout=900,env=env)
  if run.returncode:errors.append(dict(engine=e['name'],stage='fresh',exit=run.returncode,error=run.stderr[-3000:]))
  else:
   retry={p['index']:p for p in json.loads((WORK/'preset-audit.json').read_text())[0]['patches']}
   for p in row['patches']:
    if p['index'] in retry:p.update(retry[p['index']]);p['fresh_instance']=True
 remaining=[p['index'] for p in row['patches'] if p['silent']]
 if remaining:
  # Preserve original pre-attack Hold values; measure a fresh 32-second gate.
  slow=[p['index'] for p in row['patches'] if p['silent'] and p['name'] in ('Endless Hold','Slow Evolution','Tape Hiss Drone','Modular Hum')]
  if slow:
   env=dict(os.environ,RHYTHMER_AUDIT_SECONDS='32',RHYTHMER_AUDIT_FRESH='1',RHYTHMER_AUDIT_INDICES=','.join(map(str,slow)))
   run=sp.run(command,capture_output=True,text=True,timeout=900,env=env)
   if run.returncode:errors.append(dict(engine=e['name'],stage='source_hold',exit=run.returncode,error=run.stderr[-3000:]))
   else:
    retry={p['index']:p for p in json.loads((WORK/'preset-audit.json').read_text())[0]['patches']}
    for p in row['patches']:
     if p['index'] in retry:p.update(retry[p['index']]);p['original_hold_gate_seconds']=32
 row['silent']=sum(p['silent'] for p in row['patches']);rows.append(row)
 (WORK/'preset-audit-complete.json').write_text(json.dumps(dict(engines=rows,errors=errors),indent=2)+'\n')
 print('AUDITED',e['name'],len(row['patches']),'silent',row['silent'],flush=True)
raise SystemExit(bool(errors) or any(row['silent'] for row in rows))
