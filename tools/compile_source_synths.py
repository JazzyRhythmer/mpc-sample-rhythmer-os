#!/usr/bin/env python3
"""Build pinned Frodhes/Tenebrae sources in the registered SSD build root.

Run inside the existing Linux ARM64 builder. No upstream installer is executed.
On macOS first register BuildCache/rhythmer-os/source-built with ssd-qa-output.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess as sp
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode=True
from compile_moves import compile_wrapper,ROOT,WORK,MV
from frodhes_host_guard import apply as guard

OUT=WORK/'source-built'

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def atomic_copy(source,destination):
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    temporary=destination.with_name(destination.name+'.candidate')
    shutil.copy2(source,temporary);os.replace(temporary,destination)

def build(ident):
    port=ROOT/'ports'/('fm1-frodhes' if ident=='frodhes' else 'move-tenebrae')
    pin=json.loads((port/'SOURCE.json').read_text());cfg=json.loads((port/'vst.json').read_text())
    for relative,expected in pin['files'].items():
        if digest(port/'original'/relative)!=expected:raise RuntimeError('Original source changed: '+relative)
    if not OUT.is_dir():raise RuntimeError('Register SSD output with ssd-qa-output first: '+str(OUT))
    out=OUT/ident;out.mkdir(exist_ok=True)
    fingerprint=hashlib.sha256(json.dumps(pin['files'],sort_keys=True).encode()+Path(__file__).read_bytes()+(ROOT/'tools/frodhes_host_guard.py').read_bytes()).hexdigest()
    receipt=out/'build-receipt.json';library=out/'native/frodhes.so' if ident=='frodhes' else out/'module/dsp.so'
    cached=json.loads(receipt.read_text()) if receipt.is_file() else {}
    if cached.get('inputs')!=fingerprint or not library.is_file() or cached.get('binary')!=digest(library):
        source=out/'source'
        shutil.copytree(port/'original',source,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','.local','build','dist'))
        if ident=='frodhes':
            wrapper=source/'mpc/src/frodhes_mpc.cpp';wrapper.write_text(guard(wrapper.read_text()))
            compiler=out/'native-compiler'
            compiler.write_text('''#!/bin/sh
lang=$1
shift
case "$lang" in cc) compiler=gcc ;; c++) compiler=g++ ;; *) exit 2 ;; esac
for arg do
 shift
 case "$arg" in -flto=full) set -- "$@" -flto ;; *) set -- "$@" "$arg" ;; esac
done
exec "$compiler" "$@"
''');compiler.chmod(0o755)
            sdk=out/'sdk-export/tools';sdk.mkdir(parents=True,exist_ok=True)
            (sdk/'exports.map').write_text('{ global: VSTPluginMain; local: *; };\n')
            spec=importlib.util.spec_from_file_location('frodhes_original_build',source/'mpc/build.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            args=argparse.Namespace(no_lto=False,voices=16,version='0.9.12',jobs=1)
            module.build_arch('native',[str(compiler)],str(sdk.parent),args,str(out))
        else:
            library.parent.mkdir(exist_ok=True)
            sp.run(['gcc','-O3','-shared','-fPIC','-std=gnu11','-march=armv8-a',
                '-fno-math-errno','-fno-trapping-math','-fvisibility=hidden',
                '-I'+str(source/'src'),'-I'+str(source/'src/dsp'),str(source/'src/dsp/tenebrae.c'),
                '-o',str(library),'-lm','-lpthread'],check=True)
            shutil.copy2(source/'src/module.json',library.parent/'module.json')
        sp.run(['strip','--strip-unneeded',str(library)],check=True)
        receipt.write_text(json.dumps(dict(inputs=fingerprint,binary=digest(library),
            source_commit=pin['source_commit'],compiler='GNU native Linux ARM64',
            adaptation='Reject exhausted upstream instance pool' if ident=='frodhes' else 'Existing Rhythmer native API wrapper'),indent=2)+'\n')
    family='FM1' if ident=='frodhes' else 'Move'
    destination=WORK/'move-stage/Plugins'/('RHYTHMER - '+family+' - '+ident+' - '+cfg['name'])
    destination.mkdir(exist_ok=True)
    if ident=='frodhes':atomic_copy(library,destination/cfg['so'])
    else:
        # This wrapper uses the original numeric keys; the canvas/random-page
        # helpers are not sound parameters and are intentionally not exported.
        wrapper=compile_wrapper(port,cfg,ident)
        atomic_copy(wrapper/cfg['so'],destination/cfg['so'])
        atomic_copy(library,destination/'module/dsp.so')
        atomic_copy(library.parent/'module.json',destination/'module/module.json')
    xml=ET.Element('PLUGIN',dict(name=cfg['name'],descriptiveName=cfg['name'],format='VST',category='Synth',
        manufacturer=cfg['vendor'],version=str(cfg['version']),file='%payload-path%/'+destination.name+'/'+cfg['so'],
        uid=format(int.from_bytes(cfg['uid'].encode(),'big'),'x'),isInstrument='1',numInputs='0',numOutputs='2',isShell='0',fileTime='0',infoUpdateTime='0'))
    ET.ElementTree(xml).write(destination/'plugin-meta.xml',encoding='utf-8')
    for name in ['LICENSE','LICENSING.md','SOURCE.json','VENDORED.md']:
        if (port/name).is_file():atomic_copy(port/name,destination/name)
    if ident=='tenebrae':
        atomic_copy(MV/'LICENSE',destination/'Open-MPC-MIT-LICENSE.txt')
        atomic_copy(ROOT/'ports/common/move-sdk/LICENSE',destination/'Schwung-API-MIT-LICENSE.txt')
    print('SOURCE_BUILT',ident,digest(library),flush=True)
    return destination

if __name__=='__main__':
    for ident in sys.argv[1:] or ['frodhes','tenebrae']:build(ident)
