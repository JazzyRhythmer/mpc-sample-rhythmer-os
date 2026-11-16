#!/usr/bin/env python3
"""Read original prebuilt drum parameter ownership from its pinned release sources."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
result={}
for receipt in json.loads((ROOT/'config/baseline-source.lock.json').read_text()):
 if receipt['repo']!='sd88me/mpc-vst-TR-MPC':continue
 tag=receipt['tag'];short=tag.split('-vst-')[0]
 source=WORK/'baseline-source-depot'/receipt['folder']
 for cfg in source.glob('ports/*/vst.json'):
  if cfg.parent.name.replace('-','')!=('trkit' if short=='trmpc' else short).replace('-',''):continue
  data=json.loads(cfg.read_text());module=cfg.parent/data.get('module','module.mpc.json')
  if not module.exists():
   module=cfg.parent/data.get('params','params.json')
   if not module.exists():continue
  contract=json.loads(module.read_text());bykey={p['key']:p for p in contract.get('chain_params',contract.get('params',[]))};owner={}
  for level in contract.get('ui_hierarchy',{}).get('levels',{}).values():
   if 'note' not in level:continue
   for p in level.get('params',[]):
    key=p if isinstance(p,str) else p.get('key')
    if key:owner.setdefault(key,set()).add(level['note'])
  parameters=[]
  for key in (cfg.parent/'params.lock').read_text().splitlines():
   p=dict(bykey.get(key,dict(key=key)));p['owner_notes']=sorted(owner.get(key,[]));parameters.append(p)
  if short=='trmpc':
   import re
   for p in parameters:
    m=re.match(r's(\d+)_',p['key'])
    if m:p['owner_notes']=[35+int(m[1])]
  result[data['so']]=dict(parameters=parameters,repo=receipt['repo'],commit=receipt['commit'])
(ROOT/'config/baseline-parameters.json').write_text(json.dumps(result,indent=2)+'\n')
print('Pinned drum metadata:',{k:len(v['parameters']) for k,v in result.items()})
