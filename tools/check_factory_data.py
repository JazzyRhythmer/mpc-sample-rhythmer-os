#!/usr/bin/env python3
"""Run compiled native factory data/state assertions against original source tables."""
import json,subprocess as sp,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
checks={
 'mono2k':'''for(unsigned k=0;k<LIB_N;k++){native_control(P_COUNT+1,k);m2k_sound_t expected;lib_sound(k,&expected);assert(PAT(cur_pat)->machine[0]==expected.machine);assert(!memcmp(PAT(cur_pat)->kit[0],expected.kit,P_COUNT));char before[2048],after[2048];native_state_get(before,sizeof before);native_control(0,0);native_state_set(before);native_state_get(after,sizeof after);assert(!strcmp(before,after));}''',
 'fm106':'''for(unsigned k=0;k<128;k++){native_control(0,k);assert(g_synth.patch_idx==k);assert(!strcmp(g_synth.patch_name,FM106_PRESETS[k].name));assert(g_synth.dco_noise_level==FM106_PRESETS[k].p[8]);assert(g_synth.dco_pwm_depth==FM106_PRESETS[k].p[6]);}''',
 's1vave':'''for(unsigned k=0;k<NFACT;k++){native_control(0,k);patch_t expected;patch_from_factory(&expected,&FACTORY[k]);assert(!memcmp(&live,&expected,sizeof live));assert(!memcmp(draw,FACT_WAVE[k].draw,sizeof draw));assert(!memcmp(masks,FACT_WAVE[k].chop,sizeof masks));}''',
 'obervave':'''for(unsigned k=0;k<NFACT;k++){native_control(0,k);patch_t expected;patch_from_factory(&expected,&FACTORY[k]);assert(!memcmp(&live,&expected,sizeof live));}''',
 'elixir':'''assert(FACTORY_NKITS==0);for(unsigned k=0;k<=FACTORY_NKITS;k++){uint8_t expected[KIT_LEN];if(k<FACTORY_NKITS)kit_factory_values(k,expected);else kit_init_values(expected);native_control(0,k);for(unsigned j=0;j<KIT_LEN;j++)assert(par[kit_par(j)]==expected[j]);}''',
 'hortator':'''for(unsigned k=0;k<PRE_NFACT;k++){native_control(90,k);unsigned l=factory_lane(PRE_FACTORY[k].model);assert(trk[l].model==PRE_FACTORY[k].model);for(unsigned j=0;j<8;j++){const param_desc_t *d=&DMODELS[trk[l].model].edit[j];int v=PRE_FACTORY[k].k[j];if(v<d->min)v=d->min;if(v>d->max)v=d->max;assert(trk[l].p[P_E0+j]==v);}char before[16384],after[16384];assert(native_state_get(before,sizeof before));native_control(0,0);native_state_set(before);assert(native_state_get(after,sizeof after));assert(!strcmp(before,after));}''',
 'prophet':'''assert(P5_FACTORY_N==0);for(unsigned k=0;k<=P5_FACTORY_N;k++){native_control(0,k);p5_patch_t expected;if(k)p5_factory(k-1,&expected);else p5_patch_init(&expected);assert(!memcmp(p5_patch_of(&trk[0])->raw,expected.raw,sizeof expected.raw));}''',
 'guru600':'''for(unsigned k=0;k<P600_NFIX;k++){native_control(0,k);int16_t expected[P_COUNT];memcpy(expected,trk[0].p,sizeof expected);preset_params(ENGI_P600,k,expected);for(unsigned j=0;j<P_COUNT;j++)assert(trk[0].p[j]==expected[j]);}''',
 'cs1':'''for(unsigned k=0;k<NSOUND;k++){native_control(0,k);assert(set.sound==k);patch_t before=patch;patch=INIT_PATCH;sound_load(k);assert(!memcmp(&before,&patch,sizeof patch));}''',
}
for ident in sys.argv[1:] or checks:
 body=checks[ident].replace('char before[2048],after[2048]', 'char before[16384],after[16384]')
 p=ROOT/'ports'/('fm1-'+ident);out=p/'build';pin=json.loads((p/'SOURCE.json').read_text());source=out/'factory_data_test.c';binary=out/'factory_data_test'
 source.write_text('#include <assert.h>\n#include "'+str(ROOT/'ports/common'/pin['adapter'])+'"\nint main(void){native_init();'+body+'printf("FACTORY_DATA '+ident+' exact=ok\\n");return 0;}\n')
 flags=json.loads((out/'compile_flags.json').read_text())
 sp.run(['gcc',*flags,str(source),'-lm','-o',str(binary)],check=True)
 sp.run([str(binary)],check=True,timeout=120)
