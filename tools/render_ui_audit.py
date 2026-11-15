#!/usr/bin/env python3
"""Render host-inspected states with the production UI; keep outputs on SSD."""
import copy,hashlib,json,shutil,subprocess as sp,re,os
from pathlib import Path
import build
ROOT=Path(__file__).resolve().parents[1];WORK=build.WORK
QA=ROOT/'artifacts'/('ui-'+(ROOT/'VERSION').read_text().strip())
HELPER=str(Path.home()/'.local/share/ssd-development/bin/ssd-qa-output')
def run():
 build.check()
 source_root=Path(os.environ.get('RHYTHMER_AUDIT_CARD',str(WORK)))
 sp.run([HELPER,str(QA)],check=True,capture_output=True)
 single=json.loads((source_root/'edit-inspect.json').read_text());factory=json.loads((source_root/'factory-kit-edit-inspect.json').read_text());dynamic=json.loads((source_root/'dynamic-edit-inspect.json').read_text());pad11=json.loads((source_root/'kit-edit-inspect.json').read_text())
 assert len(single)==25 and len(factory)==16*len(json.loads((ROOT/'config/sound-catalog.json').read_text())['kits']) and len(pad11)==25
 assert all(r.get("focused_pad")==10 for r in pad11),"P11 fixture must carry the actual focused pad"
 quick_states=json.loads((source_root/"preset-quick-inspect.json").read_text());assert len(quick_states)==len(single)
 homes=[]
 kit_programs=[k['name'] for k in json.loads((ROOT/'config/sound-catalog.json').read_text())['kits']]
 for item_index,item in enumerate(single+factory):
  row=copy.deepcopy(item);row.update(home=True,meter=.6)
  if 'kit' in row:row.update(programs=kit_programs,selected_program=row['kit'])
  else:row['stage_all_presets']=True;row['preset_quick']=quick_states[item_index]
  homes.append(row)
 for base in (homes[0],homes[len(single)]):
  row=copy.deepcopy(base);row.update(stage_all_presets=False,performance_active=True);homes.append(row)
 browsers=[]
 for source in single:
  row=copy.deepcopy(source);row['preset_browser']=True;browsers.append(row)
 kit=copy.deepcopy(factory[0]);kit['programs']=[x['name'] for x in json.loads((ROOT/'config/sound-catalog.json').read_text())['kits']];kit['preset_browser']=True;browsers.append(kit)
 for row in single+dynamic+pad11:row['capture_rows']=sorted({2,max(2,(len(row['parameters'])+2)//3-1)}|({3} if row.get('focused_pad',-1)>=0 else set()))
 for row in factory:row['capture_rows']=sorted({3}|({2,max(2,(len(row['parameters'])+2)//3-1)} if row['focused_pad']==0 else set()))
 for row in homes:row['capture_rows']=[0]
 for row in browsers:row['capture_rows']=sorted({0,len(row['programs'])-1})
 slow=[]
 aphex=next(r for r in single if r['engine']=='Aphex')
 for name in ('Endless Hold','Slow Evolution','Tape Hiss Drone','Modular Hum'):
  row=copy.deepcopy(aphex);row.update(home=True,meter=.4,programs=[name],capture_rows=[0]);row['parameters'][0].update(text=name,value=aphex['programs'].index(name)/(len(aphex['programs'])-1));slow.append(row)
 sources=[];saves=[]
 for source_row in single+[r for r in factory if r['focused_pad']==0]:
  row=copy.deepcopy(source_row);row.update(save_view=True,capture_rows=[0]);saves.append(row)
 for source_row in [r for r in factory if r['focused_pad']==0]:
  row=copy.deepcopy(source_row);row.update(source_view=True,capture_rows=[0]);sources.append(row)
 perform=[]
 for source in single+[factory[0]]:
  row=copy.deepcopy(source);row.update(home=True,perform_view=True,capture_rows=[0]);perform.append(row)
 groups=[('track-perform',perform),('single-edit',single),('dynamic-edit',dynamic),('factory-kit-edit',factory),('pad11-edit',pad11),('preset-faces',homes),('preset-browsers',browsers),('original-slow-preset-faces',slow),('save',saves),('pad-source',sources),('empty-pads',json.loads((source_root/'empty-pad-inspect.json').read_text()))]
 if os.environ.get('RHYTHMER_AUDIT_GROUPS'):
  wanted=set(os.environ['RHYTHMER_AUDIT_GROUPS'].split(','));groups=[g for g in groups if g[0] in wanted]
  assert {g[0] for g in groups}==wanted,'Unknown UI audit group'
 renderer_sha=hashlib.sha256((WORK/'runtime/build/rhythmer').read_bytes()).hexdigest()
 summary=[]
 for name,data in groups:
  target=QA/name;sp.run([HELPER,str(target)],check=True,capture_output=True)
  inventory=WORK/('ui-audit-'+name+'.json');inventory.write_text(json.dumps(data)+'\n')
  log=QA/(name+'.log')
  saved_inventory=QA/(name+'.json')
  if not os.environ.get('RHYTHMER_AUDIT_FORCE') and log.is_file() and saved_inventory.is_file() and (QA/(name+'.renderer-sha256')).is_file() and (QA/(name+'.renderer-sha256')).read_text().strip()==renderer_sha and json.loads(saved_inventory.read_text())==data:
   completed=[line for line in log.read_text().splitlines() if line.startswith('RHYTHMER_EDIT_PREVIEW ') and 'text_issues=0' in line]
   if completed:
    marker=completed[-1];summary.append(dict(group=name,states=len(data),images=int(re.search(r'saved=(\d+)',marker)[1]),result=marker));print(name,'unchanged verified render retained',flush=True);continue
  log=QA/(name+'.log')
  render=WORK/'runtime/build'
  before={p.name:(p.stat().st_mtime_ns,p.stat().st_size) for p in render.glob('engine-*.png')}
  with log.open('w') as out:
   sp.run([build.DOCKER,'run','--rm','--platform','linux/arm64','-v',str(WORK)+':'+str(WORK),'-v',str(WORK)+':/Volumes/SSD/Development/BuildCache/groove-os','-v',str(WORK/'runtime')+':/work','-w','/work','rhythmer-builder','/work/build/rhythmer','--rhythmer-edit-preview','/work/build',str(inventory)],check=True,stdout=out,stderr=sp.STDOUT)
  files=[p for p in render.glob('engine-*.png') if before.get(p.name)!=(p.stat().st_mtime_ns,p.stat().st_size)];assert files,'Native renderer produced no visible output'
  for image in files:shutil.copy2(image,target/image.name)
  shutil.copy2(inventory,QA/(name+'.json'))
  (QA/(name+'.renderer-sha256')).write_text(renderer_sha+'\n')
  markers=[line for line in log.read_text().splitlines() if line.startswith('RHYTHMER_EDIT_PREVIEW ')];assert len(markers)==1,log
  tail=markers[0];assert 'text_issues=0' in tail,tail
  assert len(files)==int(re.search(r'saved=(\d+)',tail)[1]),'Screenshot count differs from native renderer'
  summary.append(dict(group=name,states=len(data),images=len(files),result=tail));print(name,len(files),'images; zero text issues',flush=True)
 (QA/'render-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
if __name__=='__main__':run()
