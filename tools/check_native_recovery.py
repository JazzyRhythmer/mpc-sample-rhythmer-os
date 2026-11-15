"""Exercise restored original controls, MIDI expression and complete state."""
from pathlib import Path
import json,subprocess as sp,sys
ROOT=Path(__file__).resolve().parents[1]
checks={
 's1vave':r'''
 char value[128];native_control(1+P_ATTACK,0);native_display(1+P_ATTACK,value,sizeof value);assert(strstr(value,"ms"));native_control(1+P_LFO_SYNC,0);native_display(1+P_LFO_RATE,value,sizeof value);assert(strstr(value,"Hz"));native_control(1+P_LFO_SYNC,1);native_display(1+P_LFO_RATE,value,sizeof value);assert(!strstr(value,"Hz"));
 for(int i=1;i<native_count();i++)for(int v=native_min(i);v<=native_max(i);v++){native_control(i,v);native_display(i,value,sizeof value);assert(value[0]);}
''',
 'obervave':r'''
 char value[128];native_control(1+P_FA,0);native_display(1+P_FA,value,sizeof value);assert(strstr(value,"ms"));native_display(1+P_LFO_RATE,value,sizeof value);assert(strstr(value,"Hz"));
 for(int i=1;i<native_count();i++)for(int v=native_min(i);v<=native_max(i);v++){native_control(i,v);native_display(i,value,sizeof value);assert(value[0]);}
''',
'fmini':r'''
 for(unsigned p=0;p<FMINI_NFACTORY;p++){
  native_control(0,p);char before[16384],after[16384];native_get(0,"state",before,sizeof before);
  native_control(extra_base()+X_DETUNE2,-123);native_control(extra_base()+X_SWITCHES,0);
  native_set(0,"state",before);native_get(0,"state",after,sizeof after);
  if(strcmp(before,after)){fprintf(stderr,"state differs program=%u\n",p);return 3;}
 }
 native_control(extra_base()+X_RELEASE_LINK,1);int linked_release=FMINI_FREL(&trk[0]);native_control(extra_base()+X_FILTER_RELEASE,linked_release);assert(!(trk[0].frel&128));
 native_control(extra_base()+X_RELEASE_LINK,1);native_control(extra_base()+X_FILTER_RELEASE,31);assert(trk[0].frel==(128|31));
 native_control(extra_base()+X_RELEASE_LINK,1);assert(!(trk[0].frel&128));
 native_control(extra_base()+X_DETUNE2,-700);assert(fmini_det(fmini_patch[0],FG_DC2L)==-700);
 native_control(extra_base()+X_DETUNE3,700);assert(fmini_det(fmini_patch[0],FG_DC3L)==700);
 for(unsigned j=0;j<10;j++){native_control(extra_base()+X_SWITCHES+j,1);assert(native_value(extra_base()+X_SWITCHES+j)==1);native_control(extra_base()+X_SWITCHES+j,0);assert(!native_value(extra_base()+X_SWITCHES+j));}
 for(unsigned j=0;j<6;j++){native_control(extra_base()+j,GP[extra_globals[j]].max);assert(song.g[extra_globals[j]]==GP[extra_globals[j]].max);}
 uint8_t cc[]={0xb0,11,91},at[]={0xd0,73};native_midi(0,cc,3,0);native_midi(0,at,2,0);assert(trk[0].ex_off==36&&trk[0].at==73);
''',
'prophet':r'''
 for(unsigned j=0;j<3;j++){unsigned id=G_MFXTYPE+j*FX_PARAMS;unsigned i;for(i=0;i<sizeof global_ids;i++)if(global_ids[i]==id)break;assert(i<sizeof global_ids);native_control(1+ntrack+npatch+i,FX_ROOM);assert(song.g[id]==FX_ROOM);}
 char before[16384],after[16384];native_get(0,"state",before,sizeof before);native_control(0,0);native_set(0,"state",before);native_get(0,"state",after,sizeof after);assert(!strcmp(before,after));
 uint8_t cc[]={0xb0,11,91},at[]={0xd0,73};native_midi(0,cc,3,0);native_midi(0,at,2,0);assert(trk[0].ex_off==36&&trk[0].at==73);
''',
'guru600':r'''
 native_control(native_count()-1,GP[G_RTYPE].max);assert(song.g[G_RTYPE]==GP[G_RTYPE].max);
 char before[16384],after[16384];native_get(0,"state",before,sizeof before);native_control(0,1);native_set(0,"state",before);native_get(0,"state",after,sizeof after);assert(!strcmp(before,after));
 uint8_t cc[]={0xb0,11,91},at[]={0xd0,73};native_midi(0,cc,3,0);native_midi(0,at,2,0);assert(trk[0].ex_off==36&&trk[0].at==73);
''',
'hortator':r'''
 for(unsigned m=0;m<NMODELS;m++){model(0,m);trk[0].p[P_E0]=DMODELS[m].edit[0].max;int untouched=trk[0].p[P_E0];native_control(1,m);assert(trk[0].p[P_E0]==untouched);
  for(unsigned j=0;j<8;j++){const param_desc_t*d=&DMODELS[m].edit[j];assert(d->max-d->min<=127);for(int value=d->min;value<=d->max;value++){trk[0].p[P_E0+j]=value;native_control(2+j,native_value(2+j));assert(trk[0].p[P_E0+j]==value);}}
 }load_kit(0);
 for(unsigned l=0;l<8;l++)for(unsigned j=0;j<EXTRA_N;j++){int i=91+l*EXTRA_N+j;const param_desc_t*d=extra_desc(i);native_control(i,d->max);assert(trk[l].p[extra_ids[j]]==d->max);native_control(i,d->min);assert(trk[l].p[extra_ids[j]]==d->min);native_control(i,d->def);}
 char before[16384],after[16384];native_get(0,"state",before,sizeof before);native_control(0,5);native_set(0,"state",before);native_get(0,"state",after,sizeof after);assert(!strcmp(before,after));
 char legacy[370];memcpy(legacy,"HKT2:",5);memcpy(legacy+5,before+5,364);legacy[369]=0;native_state_set(legacy);assert(trk[0].model==kits[0][0]);
 native_tempo(96);assert(song.g[G_BPM]==96);native_tempo(165);assert(song.g[G_BPM]==165);
''',
'fm106':r'''
 native_control(native_count()-1,1);assert(g_synth.arp_on);native_control(native_count()-1,0);assert(!g_synth.arp_on);
 uint8_t bend[]={0xe0,0,0},sustain[]={0xb0,64,127};native_midi(0,bend,3,0);native_midi(0,sustain,3,0);assert(g_synth.pitch_bend_val==-8192&&g_synth.hold_pedal);
 char before[16384],after[16384];native_get(0,"state",before,sizeof before);native_control(0,1);native_set(0,"state",before);native_get(0,"state",after,sizeof after);assert(!strcmp(before,after));
''',
'mono2k':r'''
 native_tempo(140);assert(bpm10==1400);native_tempo(165);assert(bpm10==1650);
 for(unsigned l=0;l<3;l++){unsigned p=P_LFO+8*l+L_TRCK;native_control(1+p,127);assert(native_value(1+p)==trck_enc(0));}
 char display[256];native_control(1+P_LFO+L_DEST,1);native_display(1+P_LFO+L_DEST,display,sizeof display);assert(!strcmp(display,pinfo(0,0)->name));assert(native_max(1+P_LFO+L_DEST)==P_COUNT);
'''
}
for ident in sys.argv[1:] or checks:
 p=ROOT/'ports'/('fm1-'+ident);out=p/'build';adapter=json.loads((p/'SOURCE.json').read_text())['adapter'];file=out/'native_recovery.c';binary=out/'native_recovery'
 file.write_text('#include <assert.h>\n#include "'+str(ROOT/'ports/common'/adapter)+'"\nint main(void){native_init();'+checks[ident]+'printf("RECOVERY '+ident+' state_controls_midi=PASS\\n");return 0;}')
 flags=json.loads((out/'compile_flags.json').read_text());sp.run(['gcc',*flags,str(file),'-lm','-o',str(binary)],check=True);sp.run([str(binary)],check=True)
