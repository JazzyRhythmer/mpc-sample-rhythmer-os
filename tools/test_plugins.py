#!/usr/bin/env python3
"""Link a small integration test against the objects of the real Rhythmer host."""
from pathlib import Path
import shlex
import subprocess as sp
import sys

WORK = Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
ROOT = WORK / 'plugins'
APP = WORK / 'runtime'
modules = APP / 'build/deps/JUCE/modules'
binary = ROOT / 'plugin_host_test'
flags = shlex.split(sp.check_output(
    ['pkg-config', '--cflags', '--libs', 'freetype2', 'fontconfig', 'alsa', 'libdrm', 'libsystemd'], text=True))
sp.run(['g++', '-std=c++17', '-O2', '-pthread', '-DJUCE_GLOBAL_MODULE_SETTINGS_INCLUDED=1',
        '-DJUCE_STANDALONE_APPLICATION=1', '-DJUCE_USE_CURL=0', '-DJUCE_WEB_BROWSER=0',
        '-DJUCE_PLUGINHOST_VST3=1', '-DNDEBUG', '-I' + str(APP / 'src'), '-I' + str(modules),
        str(ROOT / 'tests/plugin_host.cpp'),
        str(APP / 'build/obj/rhythmer/plugin/vst2_instance.o'),
        str(APP / 'build/obj/rhythmer/plugin/plugin_files.o'),
        str(APP / 'build/obj/rhythmer/model/project_file.o'),
        str(APP / 'build/obj/rhythmer/model/pattern.o'),
        str(APP / 'build/obj/rhythmer/model/print.o'),
        str(APP / 'build/obj/rhythmer/engine/engine_info.o'),
        *[str(p) for p in sorted((APP / 'build/obj').glob('juce*.o'))],
        *flags, '-ldl', '-lrt', '-o', str(binary)], check=True)
folders = [Path(p) for p in sys.argv[1:]] if len(sys.argv)>1 else sorted(p for p in (WORK / 'sd-stage/Plugins').iterdir() if p.is_dir())
sp.run([str(binary), *[str(p) for p in folders]], check=True)
