#!/usr/bin/env python3
"""Build and accept the independent original DRUM-X native port."""
import json
import os
from pathlib import Path
import shutil
import subprocess as sp
import sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(os.environ.get('RHYTHMER_BUILD_ROOT','/Volumes/SSD/Development/BuildCache/rhythmer-os'))
p=ROOT/'ports/drumx';out=p/'build';mv=ROOT/'vendor/mpc-vst-plugins'
def run(args):sp.run([str(a) for a in args],check=True)
run([sys.executable,ROOT/'tools/prepare_drumx.py','--generate',p])
run([sys.executable,mv/'tools/gen_vst.py',p/'vst.json'])
inc=['-I'+str(out),'-I'+str(mv/'wrapper')]
san=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fwrapv','-g','-O1']
run(['gcc','-std=gnu11',*san,*inc,'-c',ROOT/'tests/drumx_reference.c','-o',out/'ref-test.o'])
run(['g++','-std=gnu++17',*san,*inc,ROOT/'tests/drumx.cpp',p/'drumx.cpp',out/'ref-test.o','-o',out/'drumx-test'])
run([out/'drumx-test'])
run(['g++','-std=gnu++17','-O2','-fwrapv','-fPIC',*inc,'-c',p/'drumx.cpp','-o',out/'drumx.o'])
run(['gcc','-O2','-fPIC',*inc,'-c',mv/'wrapper/vst2_wrap.c','-o',out/'wrap.o'])
run(['g++','-shared',out/'drumx.o',out/'wrap.o','-lm','-lpthread','-ldl','-Wl,--no-undefined','-o',out/'rhythmer-drumx.so'])
run(['strip',out/'rhythmer-drumx.so'])
dest=WORK/'move-stage/Plugins/RHYTHMER - FM1 - drumx - DRUM-X';dest.mkdir(parents=True,exist_ok=True)
for f in ('rhythmer-drumx.so',):shutil.copy2(out/f,dest/f)
for f in ('LICENSE','SOURCE.json','VENDORED.md'):shutil.copy2(p/f,dest/f)
shutil.copy2(mv/'LICENSE',dest/'Open-MPC-MIT-LICENSE.txt')
xml=ET.fromstring((out/'pluginlist-entry.xml').read_text());xml.set('file','%payload-path%/'+dest.name+'/rhythmer-drumx.so')
ET.ElementTree(xml).write(dest/'plugin-meta.xml',encoding='utf-8')
hier=json.loads((p/'contract.json').read_text())['ui_hierarchy'];(dest/'drum-map.json').write_text(json.dumps(hier,indent=2)+'\n')
print('BUILT DRUM-X',flush=True)
