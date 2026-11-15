"""Read each original native control independently of the VST value cache."""
import json,subprocess as sp,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
probe=WORK/'plugins/control_probe'
sp.run(['gcc','-O2','-std=gnu11',str(ROOT/'tools/probe_controls.c'),'-ldl','-o',str(probe)],check=True)
rows=[]
for engine in json.loads((ROOT/'config/sound-catalog.json').read_text())['engines']:
 folder=Path(os.environ.get('RHYTHMER_PLUGIN_ROOT',str(WORK/'sd-stage/Rhythmer/Plugins')))/engine.get('source_folder',engine['folder']);module=folder/'module'
 if not (module/'dsp.so').is_file():continue
 keys=[]
 for p in engine['parameters']:
  key=p['key']
  keys.append(key)
 query=WORK/'plugins/control-keys.txt';query.write_text('\n'.join(keys)+'\n')
 run=sp.run([str(probe),str(module/'dsp.so'),str(module),str(query)],capture_output=True,text=True,timeout=180,check=True)
 controls=json.loads(run.stdout.split('RHYTHMER_CONTROLS_BEGIN\n',1)[1]);rows.append(dict(engine=engine['name'],controls=controls))
 (WORK/'control-api-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
 print('CONTROL API',engine['name'],'missing',sum(not p['read'] for p in controls),flush=True)
 assert all(p['read']>0 for p in controls),(engine['name'],'Native parameter key unavailable')
