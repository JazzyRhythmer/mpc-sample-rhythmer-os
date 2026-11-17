#!/usr/bin/env python3
"""Link the real host sound/kit checks, optionally instrumenting the new host."""
import argparse
from pathlib import Path
import shlex
import subprocess as sp
import os

parser=argparse.ArgumentParser()
parser.add_argument('--asan',action='store_true')
parser.add_argument('--runtime',type=Path,help='Reviewed candidate runtime; default is the canonical runtime')
parser.add_argument('--output-dir',type=Path,help='Registered SSD QA output directory')
parser.add_argument('--plugins',type=Path,help='Candidate plugin tree; defaults to the staged SD card')
parser.add_argument('--catalog',type=Path,help='Candidate catalog; defaults to this source snapshot')
parser.add_argument('mode',choices=('websitepreview','acidaliases','singles','kits','audit','inspect','playback','demo','transport','authored','audition','musical','labels','userdefaults','presetcontrols','controlroundtrip','signalquality','kitownership','plaitscontrols','qualityreview','kitmodels','kitfilter','enginefilter'))
parser.add_argument('engine',nargs='?')
args=parser.parse_args()
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
APP=args.runtime or WORK/'runtime'
OUTPUT=args.output_dir or WORK
if not OUTPUT.resolve().is_relative_to(Path('/Volumes/SSD/Development')):raise RuntimeError('QA outputs must stay on the development SSD')
ROOT=Path(__file__).resolve().parents[1]
flags=shlex.split(sp.check_output(['pkg-config','--cflags','--libs','freetype2','fontconfig','alsa','libdrm','libsystemd'],text=True))
common=['-std=c++17','-pthread','-DJUCE_GLOBAL_MODULE_SETTINGS_INCLUDED=1','-DJUCE_STANDALONE_APPLICATION=1',
        '-DJUCE_USE_CURL=0','-DJUCE_WEB_BROWSER=0','-DJUCE_PLUGINHOST_VST3=1','-DNDEBUG',
        '-I'+str(APP/'src'),'-I'+str(APP/'base/src'),'-I'+str(APP/'build/deps/JUCE/modules')]
sources=['plugin/vst2_instance','plugin/plugin_files','plugin/sound_rack','plugin/plugin_support',
         'model/project_file','model/pattern','model/print','engine/engine_info','engine/effects','engine/effects_extra','engine/effect_info']
objects=[]
san=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-O1'] if args.asan else ['-O2']
for source in sources:
    if args.asan and source in ('plugin/vst2_instance','plugin/sound_rack'):
        obj=OUTPUT/(source.replace('/','_')+'_asan.o')
        sp.run(['g++',*common,*san,*flags,'-c',str(APP/'src/rhythmer'/(source+'.cpp')),'-o',str(obj)],check=True)
    else:obj=APP/'build/obj/rhythmer'/(source+'.o')
    objects.append(obj)
objects+=list((APP/'build/obj').glob('juce*.o'))+[APP/'build/obj/plugin_support_pack.o']
# Always inspect the catalogue from this same source snapshot.
import shutil
shutil.copyfile(ROOT/'ports/move-plaits/model-controls.json',WORK/'plaits-model-controls.json')
catalog=args.catalog or WORK/'sound-catalog.json'
if not args.catalog:shutil.copyfile(ROOT/'config/sound-catalog.json',catalog)
binary=OUTPUT/('sound_rack_asan' if args.asan else 'sound_rack_test')
sp.run(['g++',*common,*san,str(ROOT/'tests/sound_rack_test.cpp'),*map(str,objects),*flags,'-ldl','-lrt','-o',str(binary)],check=True)
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
sp.run([str(binary),str(catalog),str(args.plugins or WORK/'sd-stage/Rhythmer/Plugins'),args.mode,*([args.engine] if args.engine else [])],check=True,env=env)
