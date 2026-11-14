/* SPDX-License-Identifier: GPL-3.0-only
 * Original FMini-1 engine, allocator, envelopes, modulation and FX. The generated
 * prefix includes only original DSP units, ending before USB/platform/sequence
 * emulation. Rhythmer supplies MIDI, project storage and the sequencer.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "fm1_core.h"
/* This original firmware setting lives in its sequencer unit. Keep its
 * original OFF default while exposing it independently of that sequencer. */
volatile uint8_t fm_vel_sens;
static void events_block(uint32_t frames){(void)frames;}
#include "preset_helpers.h"
#include "patch_names.h"
#define NATIVE_MAX_PARAMS 512
static unsigned selected;static unsigned track_ids[P_COUNT],ntrack;
static const uint8_t global_ids[]={G_DTIME,G_DFDBK,G_DCOLOR,G_DMIX,G_RSIZE,G_RDAMP,G_CRATE,G_CDEPTH};
static int native_count(void){return 2+(int)ntrack+FG_NUM+sizeof global_ids;}
static const char *native_name(int i){
    if(!i)return "Factory Program";--i;
    if((unsigned)i<ntrack)return track_desc(&trk[0],track_ids[i])->label;
    i-=(int)ntrack;if(i<FG_NUM)return patch_names[i];i-=FG_NUM;
    return i<(int)sizeof global_ids?GP[global_ids[i]].label:"Velocity Sensitivity";
}
static int native_min(int i){
    if(!i)return 0;--i;if((unsigned)i<ntrack)return track_desc(&trk[0],track_ids[i])->min;
    i-=(int)ntrack;if(i<FG_NUM)return 0;i-=FG_NUM;return i<(int)sizeof global_ids?GP[global_ids[i]].min:0;
}
static int native_max(int i){
    if(!i)return FMINI_NFACTORY-1;--i;if((unsigned)i<ntrack)return track_desc(&trk[0],track_ids[i])->max;
    i-=(int)ntrack;if(i<FG_NUM)return (int)fmini_max((unsigned)i);i-=FG_NUM;return i<(int)sizeof global_ids?GP[global_ids[i]].max:1;
}
static int native_value(int i){
    if(!i)return (int)selected;--i;if((unsigned)i<ntrack)return trk[0].p[track_ids[i]];
    i-=(int)ntrack;if(i<FG_NUM)return fmini_patch[0][i];i-=FG_NUM;return i<(int)sizeof global_ids?song.g[global_ids[i]]:fm_vel_sens;
}
static void native_control(int i,int v){
    if(!i){selected=(unsigned)v;host_preset(&trk[0],ENGI_FMINI,(unsigned)v);return;}--i;
    if((unsigned)i<ntrack){trk[0].p[track_ids[i]]=(int16_t)v;return;}
    i-=(int)ntrack;if(i<FG_NUM){uint8_t p[FG_SIZE];memcpy(p,fmini_patch[0],sizeof p);p[i]=(uint8_t)v;fmini_set_patch(0,p);fmini_adopt(0);}
    else {i-=FG_NUM;if(i<(int)sizeof global_ids)song.g[global_ids[i]]=(int16_t)v;else fm_vel_sens=(uint8_t)v;}
}
static void native_init(void){
    host_tracks_init();host_preset(&trk[0],ENGI_FMINI,0);
    for(unsigned i=0;i<P_COUNT;++i){const param_desc_t *d=track_desc(&trk[0],i);if(d->label&&d->max>d->min)track_ids[ntrack++]=i;}
}
static void native_note(const uint8_t *m){
    unsigned kind=m[0]&0xf0;
    if(kind==0x90&&m[2])trk_note_on(&trk[0],m[1],m[2]);
    else if(kind==0x80||(kind==0x90&&!m[2]))trk_note_off(&trk[0],m[1]);
    else if(kind==0xb0&&(m[1]==120||m[1]==123))for(unsigned k=0;k<128;++k)trk_note_off(&trk[0],k);
    else if(kind==0xe0)midi_bend_target[0]=((int)(m[1]|m[2]<<7)-8192)/16;
}
static int32_t pcm[2*CTL];static unsigned cursor=CTL;
static void native_audio(int16_t *out,int frames){
    for(int f=0;f<frames;++f){if(cursor==CTL){mix_block(pcm,CTL);cursor=0;}
        for(unsigned c=0;c<2;++c){int32_t v=pcm[2*cursor+c];out[2*f+c]=(int16_t)(v>32767?32767:v<-32768?-32768:v);}++cursor;
    }
}
#define NATIVE_TEMPO 1
static void native_tempo(float bpm){song.g[G_BPM]=(int16_t)(bpm>240?240:bpm<40?40:bpm);}
#include "fm1_facade.h"
