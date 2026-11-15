"""Read original FM-1 page membership from the compiled, pinned descriptors.

Only sound controls are described; no source IDs or patch bytes are changed.
"""
import json,subprocess as sp
from prepare_drumx import function
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def export(ident):
 p=ROOT/'ports'/('fm1-'+ident);out=p/'build';adapter=json.loads((p/'SOURCE.json').read_text())['adapter']
 if ident=='prophet':
  mapping='''if(pg->scope==SC_P5){for(unsigned z=0;z<npatch;z++)if(patch_ids[z]==id)ix=1+ntrack+z;}
  else if(pg->scope==SC_GLOBAL){for(unsigned z=0;z<sizeof global_ids;z++)if(global_ids[z]==id)ix=1+ntrack+npatch+z;}
  else if(pg->scope==SC_TRACK||pg->scope==SC_ENGINE){for(unsigned z=0;z<ntrack;z++)if(track_ids[z]==id)ix=1+z;}'''
 elif ident=='fmini':
  mapping='''if(pg->scope==SC_GLOBAL){for(unsigned z=0;z<sizeof global_ids;z++)if(global_ids[z]==id)ix=1+ntrack+FG_NUM+z;for(unsigned z=0;z<6;z++)if(extra_globals[z]==id)ix=extra_base()+z;}
  else if(pg->scope==SC_TRACK||pg->scope==SC_ENGINE){for(unsigned z=0;z<ntrack;z++)if(track_ids[z]==id)ix=1+z;}'''
 else:
  mapping='''if(pg->scope==SC_GLOBAL){for(unsigned z=0;z<sizeof globals;z++)if(globals[z]==id)ix=1+nids+z;}
  else if(pg->scope==SC_TRACK||pg->scope==SC_ENGINE){for(unsigned z=0;z<nids;z++)if(ids[z]==id)ix=1+z;}'''
 # The original page table's first occurrence is the primary presentation of
 # a shared control. The full native parameter set remains independently audited.
 source=out/'source_panels.c';binary=out/'source_panels'
 visible=function((p/'original/firmware/src/ui.c').read_text(),'page_visible') if ident!='prophet' else ''
 source.write_text('#include <stdio.h>\n#include "'+str(ROOT/'ports/common'/adapter)+'"\n'+visible+'\nint main(void){native_init();int families[]={FAM_EDIT,FAM_ENV,FAM_LFO,FAM_FX};puts("[");int comma=0;for(unsigned f=0;f<4;f++)for(unsigned n=0;n<NPAGES;n++){const page_t*pg=&PAGES[n];if(pg->fam!=families[f])continue;'+('if(!page_visible(n))continue;' if ident!='prophet' else 'if(pg->fam==FAM_EDIT&&pg->scope==SC_TRACK&&pg->id[0]>=P_FM1_ATK&&pg->id[0]<=P_FM4_LEVEL)continue;')+'for(unsigned slot=0;slot<4;slot++){unsigned id=pg->id[slot];if(id==255)continue;int ix=-1;'+mapping+'if(ix<0)continue;if(comma++)puts(",");printf("{\\\"key\\\":\\\"p%d\\\",\\\"panel\\\":\\\"%s\\\",\\\"family\\\":%u,\\\"order\\\":%u}",ix,pg->title,f,n*4+slot);}}puts("]");return 0;}')
 flags=json.loads((out/'compile_flags.json').read_text());sp.run(['gcc',*flags,str(source),'-lm','-o',str(binary)],check=True)
 data=json.loads(sp.check_output([str(binary)],text=True));(p/'source-panels.json').write_text(json.dumps(data,indent=2)+'\n');print('Original panels',ident,len(data),flush=True)
if __name__=='__main__':
 import sys
 for ident in sys.argv[1:] or ['fmini','guru600','prophet']:export(ident)
