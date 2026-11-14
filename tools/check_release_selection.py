#!/usr/bin/env python3
"""Reject drift between the selected engines, dependency closure and packages."""
import json
from pathlib import Path
from release_profile import profile,require_port
ROOT=Path(__file__).resolve().parents[1]
def check():
 p=profile();c=json.loads((ROOT/'config/sound-catalog.json').read_text())
 assert p['status']=='APPLIED' and len(p['track_picker'])==20
 assert len(c['engines'])==25 and len(c['kits'])==len(p['kit_presets'])
 assert {d.name for d in (ROOT/'ports').iterdir() if d.is_dir()}==set(p['active_ports'])|{'common'}
 assert set(p['engine_folders'])=={e['folder'] for e in c['engines']}
 assert {e['folder'] for e in c['engines'] if e['kit_only']}==set(p['kit_only']) and len(p['kit_only'])==7
 actual={'Rhythmer Kit','Break Engine'}|{e['name'] for e in c['engines'] if not e['kit_only']}
 assert actual==set(p['track_picker'])
 assert {k['name'] for k in c['kits']}==set(p['kit_presets'])
 for k in c['kits']:
  assert len(k['routes'])>=16
  for r in k['routes']:
   assert 0<=r['engine']<25
   assert 0<=r['sound']<len(c['engines'][r['engine']]['sounds'])
 for e in c['engines']:assert len(e['sounds'])>=1 and all(s['name'] for s in e['sounds'])
 for n in ('move-dr32','fm1-hydra','303','move-monksynth'):
  try:require_port(n)
  except ValueError:pass
  else:raise AssertionError('Excluded import accepted: '+n)
 names=json.loads((ROOT/'config/public-port-names.json').read_text())
 assert {x['port'] for x in names['ports']}==set(p['active_ports'])
 assert {x['repository_slug'] for x in names['ports']}=={'mpc-sample-engine-ports'}
 assert len({x['source_directory'] for x in names['ports']})==19
 print('Selection OK: 20 picker entries, 25 source views,',len(c['kits']),'complete kits, 19 port variants / 18 names')
if __name__=='__main__':check()
