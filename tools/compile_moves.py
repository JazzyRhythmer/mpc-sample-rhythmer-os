#!/usr/bin/env python3
"""Compile the common native API adapter, keeping each original DSP unchanged."""
import json
from pathlib import Path
import shutil
import re
import subprocess as sp
import sys
import xml.etree.ElementTree as ET
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
MV=ROOT/'vendor/mpc-vst-plugins'


def compile_wrapper(port,cfg,ident):
    sp.run([sys.executable,str(MV/'tools/gen_vst.py'),str(port/'vst.json')],check=True)
    out=port/'build'
    wrapper=(MV/'wrapper/vst2_wrap.c').read_text().replace('char chunk[8192];','char chunk[262144];')
    from wrapper_repairs import repair
    wrapper=repair(wrapper)
    # A bounded host extension exposes original native selectors omitted from
    # chain_params. Existing parameter indices/chunk layout stay unchanged.
    wrapper=wrapper.replace('    case effGetChunk: {','''    case 0x47720001: {
        const char *const *pair=p;
        if(!pair||!pair[0]||!pair[1]||strnlen(pair[0],128)>=128||strnlen(pair[1],256)>=256)return 0;
        flush_pend0(e);eng_set(w,pair[0],pair[1]);return 1;
    }
    case effGetChunk: {''',1)
    wrapper=wrapper.replace('static intptr_t dispatcher(', '#include "move_state.h"\n\nstatic intptr_t dispatcher(',1)
    start=wrapper.index('    case effGetChunk: {')
    end=wrapper.index('    default: return 0;',start)
    wrapper=wrapper[:start]+'''    case effGetChunk:
        flush_pend0(e);return move_save(w,p);
    case effSetChunk:
        __atomic_store_n(&w->has_pend0,0,__ATOMIC_RELEASE);
        return v > 0 ? move_restore(w,p,(size_t)v) : 0;
'''+wrapper[end:]
    (out/'vst2_wrap.c').write_text(wrapper)
    defines=[]
    # params.h supplies the wrapper's flags; adapter lifecycle flags apply to its own translation unit.
    if cfg.get('defines',{}).get('FM1_ISOLATED'):defines.append('-DFM1_ISOLATED=1')
    objects=[]
    for number,source in enumerate([ROOT/'ports/common/move_loader.c',out/'vst2_wrap.c']):
        obj=out/(str(number)+'.o')
        sp.run(['gcc','-std=gnu11','-O2','-fPIC','-fvisibility=hidden',*defines,'-I'+str(out),'-I'+str(MV/'wrapper'),
                '-I'+str(ROOT/'ports/common'),'-c',str(source),'-o',str(obj)],check=True)
        objects.append(str(obj))
    sp.run(['gcc','-shared',*objects,'-ldl','-lpthread','-lm','-Wl,--no-undefined','-o',str(out/cfg['so'])],check=True)
    sp.run(['strip',str(out/cfg['so'])],check=True)
    return out


def build(ident):
    from release_profile import require_port
    require_port("move-"+ident)
    if ident=='tenebrae':
        from compile_source_synths import build as original_build
        return original_build(ident)
    port=ROOT/'ports'/('move-'+ident);cfg=json.loads((port/'vst.json').read_text());pin=json.loads((port/'SOURCE.json').read_text())
    out=compile_wrapper(port,cfg,ident)
    folder='RHYTHMER - Move - '+ident+' - '+re.sub(r'[\\/:*?"<>|]','-',cfg['name'])
    dest=WORK/'move-stage/Plugins'/folder
    dest.mkdir(parents=True,exist_ok=True);shutil.copy2(out/cfg['so'],dest/cfg['so'])
    original=WORK/pin['module_folder']
    shutil.copytree(original,dest/'module',dirs_exist_ok=True)
    if ident=='tinyk':
        # The published ELF retains build-machine paths only in DWARF debug
        # sections. Standard debug stripping preserves the DSP/loadable code.
        sp.run(['strip','--strip-debug',str(dest/'module/dsp.so')],check=True)
    # These scripts/images belong to the unused Move UI. The native DSP uses
    # Rhythmer's existing parameter interface; no browser/UI runtime is loaded.
    for asset in (dest/'module').rglob('*'):
        if asset.is_file() and asset.suffix.lower() in ('.js','.html','.png','.svg','.woff','.woff2','.ttf'):asset.unlink()
    if ident=='dexed':
        # Retain the original published banks byte for byte. Never substitute
        # another engine's patches or synthesize a replacement SysEx bank.
        for name in ('Rhythmer.syx','Groove.syx'):
            stale=dest/'module/banks'/name
            if stale.is_file():stale.unlink()
        for name in ('Rhythmer-FM-patches-GPL-3.0.txt','Groove-FM-patches-GPL-3.0.txt'):
            stale=dest/name
            if stale.is_file():stale.unlink()
        if not (original/'patches.syx').is_file():
            stale=dest/'module/patches.syx'
            if stale.is_file():stale.unlink()
    # The upstream generator does not XML-escape author names containing '&'.
    xml=ET.Element('PLUGIN',dict(name=cfg['name'],descriptiveName=cfg['name'],format='VST',category='Synth',
        manufacturer=cfg['vendor'],version='1.0',file='%payload-path%/'+folder+'/'+cfg['so'],
        uid=format(int.from_bytes(cfg['uid'].encode(),'big'),'x'),isInstrument='1',fileTime='0',
        infoUpdateTime='0',numInputs='0',numOutputs='2',isShell='0'))
    ET.ElementTree(xml).write(dest/'plugin-meta.xml',encoding='utf-8')
    hierarchy=json.loads((port/'contract.json').read_text())['ui_hierarchy']
    voices={}
    if isinstance(hierarchy,dict):
        for level in hierarchy.get('levels',{}).values():
            for j,note in enumerate(level.get('child_notes',[])):
                names=level.get('child_names',[])
                voices[str(note)]={'name':names[j] if j<len(names) else 'Voice '+str(j+1),'note':note}
    if voices:(dest/'drum-map.json').write_text(json.dumps({'pad_layout':'drums','levels':voices},indent=2)+'\n')
    for source in port.iterdir():
        if source.is_file() and source.name in ('SOURCE.json','VENDORED.md','LICENSE','COPYING','README.md'):shutil.copy2(source,dest/source.name)
    shutil.copy2(MV/'LICENSE',dest/'Open-MPC-MIT-LICENSE.txt')
    shutil.copy2(ROOT/'ports/common/move-sdk/LICENSE',dest/'Schwung-API-MIT-LICENSE.txt')
    print('BUILT',ident,str(dest),flush=True)


if __name__=='__main__':
    for name in sys.argv[1:]:build(name)
