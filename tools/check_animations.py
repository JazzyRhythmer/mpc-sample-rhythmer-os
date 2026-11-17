#!/usr/bin/env python3
"""Exercise the shipped geometric renderer without names influencing image hashes."""
import copy,hashlib,json,shutil,subprocess as sp
from pathlib import Path
import build
ROOT=Path(__file__).resolve().parents[1];WORK=build.WORK;QA=ROOT/'artifacts/geometric-motion-v040'
def run():
 sp.run([str(Path.home()/'.local/share/ssd-development/bin/ssd-qa-output'),str(QA)],check=True,capture_output=True)
 profiles=json.loads((ROOT/'config/animation-profiles.json').read_text())['profiles'];names=[p['engine'] for p in profiles]
 assert set(names)==set(json.loads((ROOT/'config/first-release-candidates.json').read_text())['track_picker'])
 items=[];index={}
 states=[('idle0',0,100000,False),('idle1',0,101400,False),('active0',.65,100000,False),('active1',.65,100700,False),('active2',.65,101400,False),('held',0,100000,True),('quiet',.05,100000,False),('loud',.95,100000,False),('low',.65,100000,True),('high',.65,100000,True)]
 for name in names:
  for label,meter,at,held in states:
   index[(name,label)]=len(items);items.append(dict(engine=name,parameters=[],programs=['Default'],art_only=True,meter=meter,at=at,held=held,note=36 if label=='low' else 84 if label=='high' else 60,focused_pad=10))
 # Thirty-two sustained-note frames per engine form the comparison sheet.
 frames={}
 for name in names:
  frames[name]=[]
  for i in range(32):
   frames[name].append(len(items));items.append(dict(engine=name,parameters=[],programs=['Default'],art_only=True,meter=.65,held=True,at=100000+i*150,note=60,focused_pad=10))
 inventory=WORK/'animation-audit.json';inventory.write_text(json.dumps(items)+'\n')
 render=WORK/'runtime/build'
 before={p.name:(p.stat().st_mtime_ns,p.stat().st_size) for p in render.glob('engine-*.png')}
 log=QA/'renderer.log'
 with log.open('w') as out:
  sp.run([build.DOCKER,'run','--rm','--platform','linux/arm64','-v',str(WORK)+':'+str(WORK),'-v',str(WORK)+':/Volumes/SSD/Development/BuildCache/groove-os','-v',str(WORK/'runtime')+':/work','-w','/work','rhythmer-builder','/work/build/rhythmer','--rhythmer-edit-preview','/work/build',str(inventory)],check=True,stdout=out,stderr=sp.STDOUT)
 for p in render.glob('engine-*.png'):
  if before.get(p.name)!=(p.stat().st_mtime_ns,p.stat().st_size):shutil.copy2(p,QA/p.name)
 marker=next(line for line in log.read_text().splitlines() if line.startswith('RHYTHMER_EDIT_PREVIEW '));assert 'text_issues=0' in marker
 def digest(i):return hashlib.sha256((QA/f'engine-{i:02d}-row-000.png').read_bytes()).hexdigest()
 results=[]
 for name in names:
  hashes={k:digest(index[name,k]) for k,_,_,_ in states}
  assert hashes['idle0']==hashes['idle1'],(name,'idle drift')
  assert len({hashes['active0'],hashes['active1'],hashes['active2']})>1,(name,'no active movement')
  assert hashes['held']!=hashes['idle0'],(name,'no held-note response')
  assert hashes['quiet']!=hashes['loud'],(name,'no level response')
  assert hashes['low']!=hashes['high'],(name,'no pitch response')
  assert len({digest(i) for i in frames[name]})>=24,(name,'sustain animation stalled')
  results.append(dict(engine=name,hashes=hashes,frames=frames[name]))
 assert len({r['hashes']['active0'] for r in results})==len(names),'Shared active graphic between engines'
 assert len({r['hashes']['idle0'] for r in results})==len(names),'Shared idle graphic between engines'
 report=dict(engine_profiles=len(names),idle_stable=True,unique_active_graphics=len(names),unique_idle_graphics=len(names),note_response=True,pitch_response=True,sustain_frames=32,level_response=True,source='production performance_art; image hashes exclude names and control text',renderer=marker,engines=results)
 (QA/'animation-check.json').write_text(json.dumps(report,indent=2)+'\n');print(str(len(names))+' unique geometric sculptures: stable idle, input and level response, animated active frames passed',flush=True)
if __name__=='__main__':run()
