#!/usr/bin/env python3
"""Preserve pre-port authorship/lineage documents from each exact FM-1 source pin."""
from pathlib import Path
import hashlib,json,re,subprocess as sp
from engine_inventory import ROOT,WORK
MAP={'prophet':'melodee','kwasub-kit':'kwasub'}
LEGAL=('license','licence','licensing','copying','notice','copyright','authors','credits','acknowledg')
reports=[]
for port in sorted(p for p in (ROOT/'ports').iterdir() if p.name.startswith('fm1-') or p.name=='drumx'):
 pin=json.loads((port/'SOURCE.json').read_text());ident=pin.get('id','drumx')
 src=WORK/'source-depot'/MAP.get(ident,ident)
 if ident=='drumx':src=Path('/Volumes/SSD/Development/BuildCache/jazzy/upstream-review/jiant')
 commit=pin['commit'];rows=[]
 paths=sp.check_output(['git','-C',str(src),'ls-tree','-r','--name-only',commit],text=True).splitlines()
 for path in paths:
  base=Path(path).name.lower()
  if not (any(x in base for x in LEGAL) or any(x.lower() in ('licenses','licences') for x in Path(path).parts[:-1]) or (base.startswith('readme') and '/' not in path)):continue
  if base in ('agents.md','claude.md'):continue
  data=sp.check_output(['git','-C',str(src),'show',commit+':'+path])
  if len(data)>2*1024*1024:continue
  try:data.decode('utf-8')
  except UnicodeDecodeError:continue
  out=port/'UPSTREAM_NOTICES'/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
  rows.append(dict(path=path,sha256=hashlib.sha256(data).hexdigest(),source_url=pin['repo'].removesuffix('.git')+'/blob/'+commit+'/'+path))
 record=dict(repo=pin['repo'],commit=commit,scope='Upstream full-firmware credit context; actual DSP inclusion must be distinguished from UI/hardware/measurement references',documents=rows)
 (port/'UPSTREAM_NOTICES/PROVENANCE.json').write_text(json.dumps(record,indent=2)+'\n');reports.append(dict(port=port.name,documents=len(rows)))
print(json.dumps(reports));print(sum(x['documents'] for x in reports),'pinned upstream legal/credit documents preserved')
