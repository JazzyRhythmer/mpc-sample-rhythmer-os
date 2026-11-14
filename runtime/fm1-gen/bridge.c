// SPDX-License-Identifier: GPL-3.0-only
// Native event bridge by jazzy rhythmer. Included firmware files are unmodified.
#define UI_TEST_NO_MAIN 1
#define FM1_HOST_TEST 1
#define UI_INVERT_INDEX 0
static const unsigned UI_STORAGE_IDS[4]={0,1,2,3};
#include "tests/ui_test.c"
#include "bridge.h"
unsigned rhythmer_fm1_bridge_size(void){return sizeof(struct Fm1GenResult);}
static unsigned host_ticks_of(uint64_t samples){return (unsigned)((samples*(unsigned)song.g[G_BPM]*96u+FS*30u)/(FS*60u));}
void rhythmer_fm1_generate(unsigned genre,unsigned seed,unsigned energy,unsigned complex,int press,struct Fm1GenResult* out){
 ui_power_on();go_home();ui_rec_prefs |= PREF_SIX >> 8;rp_apply();six_native_init();trk_live=6;set_engine_of(&trk[0],ENGI_DRUM);for(unsigned k=1;k<4;k++)set_engine_of(&trk[k],ENGI_ANALOG);
 gp.genre=genre==0?GEN_EXPLORE:genre==1?0:GEN_ORDER[(genre-2)%NGENRE]+1;gp.seed=seed;gp.energy=energy;gp.form=0;gp.target=0;
 for(unsigned k=0;k<GP_N;k++)gp.amt[k]=GA_AUTO;
 gp.complex=complex;gp.swing=GA_AUTO;gp.human=30;
 host_ticks=(uint32_t)clock();if(press)gen_press();else gen_go();memset(out,0,sizeof(*out));out->seed=gp.seed;out->steps=gs.len;out->tempo=song.g[G_BPM];out->root=gs.root;out->scale=0;for(unsigned i=0;i<7;i++)out->scale|=1u<<gs.sc[i];
 for(unsigned t=0;t<4;t++){
  out->role[t]=gs.role[t];out->recipe[t]=gsnd(gs.role[t]);out->engine[t]=trk[t].eng_req;
  unsigned len=dlen(&trk[t]);if(len>out->steps)out->steps=len;
  uint32_t period=div_samples(trk[t].p[P_SDIV]);uint64_t at=0;out->grid[t]=host_ticks_of(period);
  for(unsigned i=0;i<len;i++){step_t* s=&trk[t].step[i];if(s->time!=ST_NOTE){at+=step_samples(&trk[t],period,i);continue;}
   unsigned length=1;while(i+length<len&&trk[t].step[i+length].time==ST_TIE)length++;
   for(unsigned n=0;n<(t==0?8u:s->n);n++){
    if(t==0&&!(s->hit&(1u<<n)))continue;if(out->count>=8192)continue;
    struct Fm1GenEvent* e=&out->events[out->count++];e->step=i;e->length=length;e->track=t;e->key=t==0?n:s->note[n];e->velocity=t==0&&(s->acc&(1u<<n))?127:s->vel;e->flags=s->flags;e->micro=ST_MICRO(s);
    int64_t when=(int64_t)at+(int64_t)e->micro*step_samples(&trk[t],period,i)/64;
    e->tick=host_ticks_of(when<0?0:(uint64_t)when);uint64_t held=0;
    for(unsigned j=0;j<length;j++){unsigned frames=step_samples(&trk[t],period,i+j);held+=j+1<length?frames:(uint64_t)frames*(unsigned)trk[t].p[P_SGATE]/100;}
    e->ticks=host_ticks_of(held);if(!e->ticks)e->ticks=1;e->ratchet=(uint8_t)step_ratchet(s);e->chance=(uint8_t)step_chance(s);
    if(t==0){unsigned mode=step_lmode(s,n);if(mode==LM_X2)e->ratchet=2;else if(mode==LM_X4)e->ratchet=4;else if(mode==LM_X8)e->ratchet=8;}

   }
   at+=step_samples(&trk[t],period,i);
  }
  out->track_ticks[t]=host_ticks_of(at);
 }
}

/* Host-only audio endpoints: GEN never renders the FM-1 audio interrupt. */
void jungle_init(void){}
int jungle_bind(const uint8_t *sea, unsigned bytes, unsigned frames){return 0;}
void jungle_tick_mask(uint32_t mask){}
int jungle_fallback(const uint8_t **data, unsigned *bytes, unsigned *frames){return 0;}
const uint8_t * jungle_bound(void){return 0;}
void jungle_play(unsigned on){}
void jungle_start_phase(unsigned tick){}
void jungle_seed(uint32_t seed){}
void jungle_tempo(unsigned bpm_x10){}
void jungle_pitch(int semitones){}
void jungle_warp(unsigned amount){}
void jungle_stretch_hold(unsigned on){}
void jungle_stretch_grain(unsigned piece_ms, unsigned fade_tenths){}
void jungle_stretch_slow(unsigned times){}
void jungle_feedback(unsigned amount){}
void jungle_feedback_note(unsigned pitch_class){}
void jungle_feedback_delay(unsigned tenths){}
void jungle_filter(unsigned value){}
void jungle_filter_resonance(unsigned q_tenths){}
void jungle_variation(unsigned rhythm){}
void jungle_auto_roll(unsigned on){}
void jungle_freeze(unsigned on){}
void jungle_straight(void){}
void jungle_roll(unsigned key){}
void jungle_roll_off(void){}
void jungle_one_shot(unsigned slice){}
void jungle_swap(const uint8_t *data){}
void jungle_sequence_mode(unsigned chop){}
void jungle_sequence_note(unsigned command){}
void jungle_sequence_off(unsigned command){}
void jungle_midi_realtime(unsigned status){}
int jungle_clock(unsigned *bpm_x10){return 0;}
int jungle_playing(void){return 0;}
int jungle_current_step(void){return 0;}
int jungle_roll_active(void){return 0;}
void jungle_pattern(struct jungle_step out[JUNGLE_STEPS]){}
void jungle_render(int32_t *out, unsigned frames){}

#include "firmware/six/tb3po.c"
#include "firmware/six/acid_generate.c"
