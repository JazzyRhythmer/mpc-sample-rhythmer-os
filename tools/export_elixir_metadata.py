#!/usr/bin/env python3
"""Extract original Elixir voice/category/enum labels without changing its DSP."""
from pathlib import Path
import subprocess as sp
from engine_inventory import WORK,ROOT
p=WORK/'plugins/ports/fm1-elixir';out=p/'build';source=out/'parameter_metadata.c'
source.write_text(r'''#include "elixir_native.c"
static void q(const char*s){putchar('"');for(;*s;s++){if(*s=='"'||*s=='\\')putchar('\\');if((unsigned char)*s>=32)putchar(*s);}putchar('"');}
int main(void){native_init();printf("[{}");for(int i=0;i<count;i++){unsigned p=ids[i],m=par_menu(p),v=par_voice(p);printf(",{\"owner\":%d,\"parameter\":%u,\"name\":",v<6?(int)v:-1,p);q(par_name(p));printf(",\"category\":");q(par_cat(p));printf(",\"options\":[");if(par_dtype(p)==DTYPE_MENU&&m<sizeof MENUS/sizeof MENUS[0])for(unsigned n=0;n<MENUS[m].n;n++){if(n)putchar(',');q(MENUS[m].s[n]);}printf("]}");}puts("]");return 0;}
''')
sp.run(['gcc','-O1','-std=gnu11','-fwrapv','-I'+str(ROOT/'ports/common'),'-I'+str(out),'-I'+str(p/'original'),'-I'+str(p/'original/firmware/src'),str(source),'-lm','-o',str(out/'parameter_metadata')],check=True)
with (WORK/'elixir-parameter-metadata.json').open('w') as output:sp.run([str(out/'parameter_metadata')],check=True,stdout=output)
