"""Run the pinned original Plaits hysteresis quantizer on all selector transitions."""
from pathlib import Path
import json,hashlib,subprocess as sp
ROOT=Path(__file__).resolve().parents[1];port=ROOT/'ports/move-plaits'
pin=json.loads((port/'SOURCE.json').read_text());refs=pin['reference_sources']
assert refs['commit']==pin['source_commit']
for rel,sha in refs['files'].items():assert hashlib.sha256((port/'reference'/rel).read_bytes()).hexdigest()==sha
out=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os/plugins');src=out/'plaits-quantizer-check.cpp';binary=out/'plaits-quantizer-check'
src.write_text('''#include <cassert>
#include <cstdio>
#include <cstdlib>
#include "stmlib/dsp/hysteresis_quantizer.h"
int main(){stmlib::HysteresisQuantizer2 q;int tests=0;
for(int from=0;from<32;++from)for(int to=0;to<32;++to){q.Init(32,.005f,false);q.Process(((from+.5f)/(32*1.02f))*1.02f);float raw=(to+.5f)/(32*1.02f);assert(q.Process(raw*1.02f)==to);char value[32];snprintf(value,sizeof value,"%.3f",raw);assert(int(atof(value)*32*1.02f)==to);++tests;}
printf("Original Plaits quantizer transitions=%d preset_and_readback=PASS\\n",tests);}
''')
sp.run(['g++','-std=c++17','-O2','-I'+str(port/'reference'),str(src),'-o',str(binary)],check=True);sp.run([str(binary)],check=True)
