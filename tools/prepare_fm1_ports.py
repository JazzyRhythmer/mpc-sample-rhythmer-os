from release_profile import require_port
#!/usr/bin/env python3
"""Copy only original synthesis units and their source/license provenance."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import re
ROOT=Path(__file__).resolve().parents[1]
DEPOT=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os/source-depot')
PORTS={
    'obervave':('OberVave','obv_native.c','GOV1',['firmware/src/obv_'+n+'.h' for n in ('dsp','params','fx','engine','patches')]+['firmware/gen/obv_tables.h']),
    's1vave':('S1Vave','obv_native.c','GS11',['firmware/src/obv_'+n+'.h' for n in ('dsp','params','fx','engine','patches')]+['firmware/gen/obv_tables.h']),
    'fm106':('FM-106','fm106_native.c','GF61',[str(p.relative_to(DEPOT/'fm106')) for p in (DEPOT/'fm106/firmware/src').glob('fm106_*.h')]),
    'hortator':('Hortator Kit','hortator_native.c','GHK1',
        [str(p.relative_to(DEPOT/'hortator')) for p in (DEPOT/'hortator/firmware/src').glob('dm*') if p.is_file()]
        +['firmware/src/core.h','firmware/src/dsp.c','firmware/src/phys_dsp.c','firmware/src/eng_sample.c','firmware/src/preset_bank.h','firmware/src/presets.c','tools/gen_tables.py']),
    'cs1':('CS-1','cs1_native.c','GCS1',['firmware/src/'+n for n in ('cs1_dsp.h','cs1_voice.h','cs1_fx.h','cs1.c')]
        +['firmware/gen/cs1_tables.h','firmware/gen/cs1_presets.h','firmware/gen/cs1_sounds_conv.h']),
    'elixir':('Elixir Kit','elixir_native.c','GEK1',
        [str(p.relative_to(DEPOT/'elixir')) for p in (DEPOT/'elixir/firmware/src').glob('*') if p.suffix in ('.c','.h')]
        +['tests/engine_host.h','tools/gen_tables.py','tools/gen_factory_kits.py','assets/kits/README.md']+[str(p.relative_to(DEPOT/'elixir')) for p in (DEPOT/'elixir/assets/kits').rglob('*.SND')]),
    'mono2k':('MONO2K','mono2k_native.c','GM2K',
        [str(p.relative_to(DEPOT/'mono2k')) for path in ('firmware/src','firmware/gen') for p in (DEPOT/'mono2k'/path).glob('*') if p.suffix in ('.c','.h')]),
    'kwasub':('K-WASUB','kwasub_native.c','GKWB',['source/firmware/src/ksub_data.c','source/firmware/src/ksub_dsp.c',
        'source/firmware/gen/ksub_tables.h','source/firmware/gen/ksub_samples.h','source/tools/gen_ksub.py']),
    'fmini':('FMini-1','fmini_native.c','GFM1',
        [str(p.relative_to(DEPOT/'fmini')) for path in ('firmware/src','firmware/engines/src') for p in (DEPOT/'fmini'/path).glob('*') if p.suffix in ('.c','.h')]
        +[str(p.relative_to(DEPOT/'fmini')) for p in (DEPOT/'fmini/firmware/engines/tools').glob('*.py')]
        +['tests/hostsim.c','tools/gen_tables.py','tools/gen_fm6_patches.py','firmware/engines/LICENSE']),
}
PORTS['kwasub-kit']=('K-WASUB Kit','kwasub_native.c','GKWK',PORTS['kwasub'][3])
for ident,source,name,uid in [('prophet','melodee','Prophet','GP51')]:
    PORTS[ident]=(name,'mel_family_native.c',uid,
        [str(p.relative_to(DEPOT/source)) for p in (DEPOT/source/'firmware/src').rglob('*') if p.suffix in ('.c','.h')]
        +['tests/hostsim.c','tools/gen_tables.py','tools/gen_fm6_patches.py']
        +['tools/gen_prophet_factory.py','assets/prophet5-factory/prophet5-v1.03.syx','assets/prophet5-factory/README.md'])
    if (DEPOT/source/'assets/resid').is_dir():
        PORTS[ident][3].extend(str(p.relative_to(DEPOT/source)) for p in (DEPOT/source/'assets/resid').iterdir() if p.is_file())
    if (DEPOT/source/'tools/gen_909_tables.py').is_file():PORTS[ident][3].append('tools/gen_909_tables.py')
    if (DEPOT/source/'firmware/hal/fm1_eq.h').is_file():PORTS[ident][3].append('firmware/hal/fm1_eq.h')
PORTS['guru600']=('Guru-600','guru600_native.c','GG61',
    [str(p.relative_to(DEPOT/'guru600')) for path in ('firmware/firmware/src','firmware/firmware/engines/src')
        for p in (DEPOT/'guru600'/path).glob('*') if p.suffix in ('.c','.h')]
    +[str(p.relative_to(DEPOT/'guru600')) for p in (DEPOT/'guru600/firmware/firmware/engines/tools').glob('*.py')]
    +['firmware/tests/hostsim.c','firmware/tools/gen_tables.py','firmware/tools/gen_fm6_patches.py','firmware/firmware/engines/LICENSE',
      'firmware/firmware/hal/fm1_xip.h','firmware/firmware/hal/fm1_cc.h'])
OMIT={ident:[f for f in PORTS[ident][3] if Path(f).suffix.lower() in ('.syx','.snd')] for ident in ('prophet','elixir')}
for ident in OMIT:
    PORTS[ident]=(PORTS[ident][0],PORTS[ident][1],PORTS[ident][2],[f for f in PORTS[ident][3] if f not in OMIT[ident]])
def prepare(ident):
    require_port('fm1-'+ident)
    name,adapter,uid,files=PORTS[ident];source=DEPOT/({'kwasub-kit':'kwasub','prophet':'melodee'}.get(ident,ident));p=ROOT/'ports'/('fm1-'+ident);o=p/'original';o.mkdir(parents=True,exist_ok=True)
    for f in files:
        dest=o/f.removeprefix('firmware/') if ident=='guru600' else o/f if ident in ('elixir','fmini','prophet') else o/Path(f).name
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/f,dest)
    for f in ('LICENSE','LICENSING.md','NOTICE.md'):
        if (source/f).is_file():shutil.copy2(source/f,p/f)
    if (source/'LICENSES').is_dir():shutil.copytree(source/'LICENSES',p/'LICENSES',dirs_exist_ok=True)
    if (source/'source/LICENSES').is_dir():shutil.copytree(source/'source/LICENSES',p/'LICENSES',dirs_exist_ok=True)
    if (source/'firmware/LICENSES').is_dir():shutil.copytree(source/'firmware/LICENSES',p/'LICENSES',dirs_exist_ok=True)
    sha=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    repo=subprocess.check_output(['git','-C',str(source),'remote','get-url','origin'],text=True).strip()
    modules=subprocess.check_output(['git','-C',str(source),'submodule','status','--recursive'],text=True).splitlines()
    pin=dict(id=ident,name=name,repo=repo,commit=sha,adapter=adapter,submodules=modules,
        files={f:hashlib.sha256((source/f).read_bytes()).hexdigest() for f in files})
    if ident in OMIT:
        pin['omitted_vendor_presets']={f:hashlib.sha256((source/f).read_bytes()).hexdigest() for f in OMIT[ident]}
        for f in OMIT[ident]:
            stale=o/f if ident in ('elixir','prophet') else o/Path(f).name
            if stale.is_file():stale.unlink()
    (p/'SOURCE.json').write_text(json.dumps(pin,indent=2)+'\n')
    cfg=dict(name=name,vendor='FM-1 open-source community',uid=uid,version=1000,so='rhythmer-fm1-'+ident+'.so',
        module='contract.json',custom_skin=True,targets=['aarch64'],defines={'MODULE_SUBDIR':'"module"','FM1_ISOLATED':1})
    (p/'vst.json').write_text(json.dumps(cfg,indent=2)+'\n')
    (p/'VENDORED.md').write_text('# '+name+'\n\nPinned original synthesis sources are compiled natively. '
        'No reduced JAZZY DSP, device firmware image, hardware emulator, updater or platform UI is used. '
        'The common loader isolates the original C globals per instrument instance outside the audio callback. '
        'The adapter supplies MIDI, control metadata, complete control state and bounded block buffering. '
        'Rhythmer supplies project storage and sequencing.\n')
    print('PREPARED',ident,sha)
if __name__=='__main__':
    if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD not mounted')
    for ident in sys.argv[1:]:prepare(ident)
