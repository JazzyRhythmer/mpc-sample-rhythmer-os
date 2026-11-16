"""Compile the actual wrapper enum parser; verify decorated labels and indices."""
from pathlib import Path
import subprocess as sp
from wrapper_repairs import repair
ROOT=Path(__file__).resolve().parents[1]
text=repair((ROOT/'vendor/mpc-vst-plugins/wrapper/vst2_wrap.c').read_text())
a=text.index('static float str_to_norm(');b=text.index('\n}\n',a)+3
out=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os/plugins')
source=out/'enum-parser-check.c';binary=out/'enum-parser-check'
source.write_text('''#include <assert.h>
#include <ctype.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
typedef struct {int nopts;const char **opts;float min,max;} param_t;
static float clamp01(float v){return fmaxf(0,fminf(1,v));}
'''+text[a:b]+'''
int main(void){const char* labels[]={"32'","16'","8'","4'"};param_t p={4,labels,0,3};
for(int i=0;i<4;i++)assert(fabsf(str_to_norm(&p,labels[i])-i/3.f)<.00001f);
assert(fabsf(str_to_norm(&p,"2")-2/3.f)<.00001f);
const char* beats[]={"OFF","1/4","1/16","16T"};p.opts=beats;
for(int i=0;i<4;i++)assert(fabsf(str_to_norm(&p,beats[i])-i/3.f)<.00001f);
p.nopts=0;p.min=-12;p.max=12;assert(fabsf(str_to_norm(&p,"0")-.5f)<.00001f);
return 0;}
''')
sp.run(['gcc','-O2',str(source),'-lm','-o',str(binary)],check=True);sp.run([str(binary)],check=True)
print('Wrapper enums: footage, beat fractions, triplets, bare indices and continuous values PASS')
