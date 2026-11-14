/* SPDX-License-Identifier: GPL-3.0-only
 * Original Hortator synthesis models, organized into eight playable kit lanes.
 * The sample player uses Rhythmer's sampler separately; restricted Felucca assets
 * are not compiled here. Model kernels and their original ranges are unchanged.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "felucca_tables.h"
#include "core.h"
#include "dsp.c"
#include "pitch_helper.h"
#include "registry.h"
#include "original_presets.h"
#define NATIVE_MAX_PARAMS 128
static unsigned kit,acid_mode,acid_key,factory_sound;
static uint32_t age;
static const int notes[8]={36,38,39,42,46,45,37,49};
static const char *lane_names[8]={"Kick","Snare","Clap","Closed Hat","Open Hat","Tom","Rim","Cymbal"};
static const uint8_t kits[6][8]={
    {DM_KTRX,DM_SDTRX,DM_CPTRX,DM_CHTRX,DM_OHTRX,DM_XTTRX,DM_RSTRX,DM_CYTRX},
    {DM_K808,DM_S808,DM_C808,DM_HATC,DM_HATO,DM_TOM,DM_RIM,DM_CYMB},
    {DM_K909,DM_S909,DM_C909,DM_HATC,DM_HATO,DM_TOM,DM_RIM,DM_CYMB},
    {DM_KBOOM,DM_SSNAP,DM_C909,DM_HMETL,DM_HNOIS,DM_MEMB,DM_CLAVE,DM_CYMB},
    {DM_BDEFM,DM_SDEFM,DM_CPEFM,DM_HHEFM,DM_HHEFM,DM_XTEFM,DM_RSEFM,DM_CYEFM},
    {DM_KPUNC,DM_SCRAK,DM_CPTRX,DM_HMETL,DM_HNOIS,DM_FM,DM_CBEFM,DM_CYEFM}};
static void model(unsigned l,unsigned m){
    track_t *t=&trk[l];memset(t->v,0,sizeof t->v);t->p[P_MODEL]=(int16_t)m;t->model=(uint8_t)m;
    for(unsigned j=0;j<8;++j)t->p[P_E0+j]=DMODELS[m].edit[j].def;
    if(!l)acid_mode=(m==DM_ACID);
}
static void load_kit(unsigned k){
    kit=k;for(unsigned l=0;l<8;++l){model(l,kits[k][l]);trk[l].p[P_LEVEL]=100;trk[l].p[P_PAN]=64;}
}
static unsigned factory_lane(unsigned m){switch(m){
    case DM_S808:case DM_S909:case DM_SSNAP:case DM_SCRAK:case DM_SDTRX:case DM_SDEFM:return 1;
    case DM_C808:case DM_C909:case DM_CPTRX:case DM_CPEFM:return 2;
    case DM_HATC:case DM_HMETL:case DM_HNOIS:case DM_CHTRX:case DM_MATRX:case DM_HHEFM:return 3;
    case DM_HATO:case DM_OHTRX:return 4;
    case DM_TOM:case DM_CONGA:case DM_MEMB:case DM_XTTRX:case DM_XCTRX:case DM_XTEFM:return 5;
    case DM_RIM:case DM_CLAVE:case DM_RSTRX:case DM_CLTRX:case DM_RSEFM:case DM_COWB:case DM_CBTRX:case DM_CBEFM:case DM_FM:return 6;
    case DM_CYMB:case DM_CYTRX:case DM_CYEFM:return 7;default:return 0;}}
static void factory_load(unsigned i){i%=PRE_NFACT;factory_sound=i;unsigned l=factory_lane(PRE_FACTORY[i].model);model(l,PRE_FACTORY[i].model);for(unsigned j=0;j<8;j++){const param_desc_t *d=&DMODELS[PRE_FACTORY[i].model].edit[j];int v=PRE_FACTORY[i].k[j];trk[l].p[P_E0+j]=(int16_t)(v<d->min?d->min:v>d->max?d->max:v);}}
static int native_count(void){return 3+8*11;}
static const char *native_name(int i){
    if(i==90)return "Factory Sound";if(i==89)return "Acid MIDI mode";if(!i)return "Kit";unsigned l=(unsigned)(i-1)/11,p=(unsigned)(i-1)%11;
    static char label[128];if(p>0&&p<9){const param_desc_t *d=&DMODELS[trk[l].model].edit[p-1];if(!d->label||!strcmp(d->label,"-")||d->min==d->max)return "Unused";}const char *name=p==0?"Model":p==9?"Level":p==10?"Pan":DMODELS[trk[l].model].edit[p-1].label;
    snprintf(label,sizeof label,"%s %s",lane_names[l],name?name:"Unused");return label;
}
static int native_min(int i){(void)i;return 0;}
static int native_max(int i){return i==90?PRE_NFACT-1:i==89?1:!i?5:(i-1)%11==0?NMODELS-1:127;}
static int native_value(int i){
    if(i==90)return factory_sound;if(i==89)return acid_mode; if(!i)return (int)kit;unsigned l=(unsigned)(i-1)/11,p=(unsigned)(i-1)%11;track_t *t=&trk[l];
    if(!p)return t->model;if(p>=9)return t->p[p==9?P_LEVEL:P_PAN];
    const param_desc_t *d=&DMODELS[t->model].edit[p-1];int range=d->max-d->min;
    return range?(t->p[P_E0+p-1]-d->min)*127/range:0;
}
static void native_control(int i,int v){
    if(i==90){factory_load((unsigned)v);return;}if(i==89){acid_mode=(unsigned)v;return;}if(!i){load_kit((unsigned)v);return;}unsigned l=(unsigned)(i-1)/11,p=(unsigned)(i-1)%11;track_t *t=&trk[l];
    if(!p){model(l,(unsigned)v);return;}if(p>=9){t->p[p==9?P_LEVEL:P_PAN]=(int16_t)v;return;}
    const param_desc_t *d=&DMODELS[t->model].edit[p-1];t->p[P_E0+p-1]=(int16_t)(d->min+(d->max-d->min)*v/127);
}
static void native_init(void){acid_mode=0;load_kit(0);}
#define NATIVE_CUSTOM_STATE 1
static int native_state_get(char *out,int capacity){
    if(capacity<5+91*4+1)return 0;memcpy(out,"HKT2:",5);
    int values[91];values[0]=(int)kit;
    for(unsigned l=0;l<8;++l){unsigned at=1+l*11;values[at]=trk[l].model;
        for(unsigned j=0;j<8;++j)values[at+1+j]=trk[l].p[P_E0+j];
        values[at+9]=trk[l].p[P_LEVEL];values[at+10]=trk[l].p[P_PAN];
    }
    values[89]=acid_mode;values[90]=factory_sound;
    for(unsigned i=0;i<91;++i)snprintf(out+5+4*i,5,"%04x",(uint16_t)values[i]);return 5+91*4;
}
static void native_state_set(const char *state){
    if(strlen(state)!=5+91*4||strncmp(state,"HKT2:",5))return;
    int values[91];for(unsigned i=0;i<91;++i){char text[5],*end;memcpy(text,state+5+4*i,4);text[4]=0;
        unsigned long v=strtoul(text,&end,16);if(*end||v>65535)return;values[i]=(int16_t)v;}
    if(values[0]<0||values[0]>5||values[89]<0||values[89]>1||values[90]<0||values[90]>=(int)PRE_NFACT)return;
    for(unsigned l=0;l<8;++l){unsigned at=1+l*11;int m=values[at];if(m<0||m>=NMODELS)return;
        for(unsigned j=0;j<8;++j){const param_desc_t *d=&DMODELS[m].edit[j];if(values[at+1+j]<d->min||values[at+1+j]>d->max)return;}
        if(values[at+9]<0||values[at+9]>127||values[at+10]<0||values[at+10]>127)return;
    }
    load_kit((unsigned)values[0]);factory_sound=(unsigned)values[90];
    for(unsigned l=0;l<8;++l){unsigned at=1+l*11;model(l,(unsigned)values[at]);
        for(unsigned j=0;j<8;++j)trk[l].p[P_E0+j]=(int16_t)values[at+1+j];
        trk[l].p[P_LEVEL]=(int16_t)values[at+9];trk[l].p[P_PAN]=(int16_t)values[at+10];}
    acid_mode=(unsigned)values[89];
}
static void native_note(const uint8_t *m){
    unsigned status=m[0]&0xf0;
    if(status==0xb0&&(m[1]==120||m[1]==123)){for(unsigned l=0;l<8;++l)memset(trk[l].v,0,sizeof trk[l].v);return;}
    int lane=acid_mode?0:-1;if(!acid_mode)for(unsigned l=0;l<8;++l)if(notes[l]==m[1])lane=(int)l;if(lane<0)return;
    track_t *t=&trk[lane];const dmodel_t *d=&DMODELS[t->model];
    if(status==0x80||(status==0x90&&!m[2])){if(acid_mode&&m[1]!=acid_key)return;if(d->gate)for(unsigned j=0;j<NDV;++j)d->gate(t,&t->v[j],0);return;}
    if(status!=0x90)return;
    if(acid_mode){acid_key=m[1];if(d->glide&&t->v[0].active){t->nt=(int)m[1]-60;t->v[0].vel=m[2];d->glide(t,&t->v[0]);if(d->gate)d->gate(t,&t->v[0],1);return;}}
    if(lane==3)for(unsigned j=0;j<NDV;++j)trk[4].v[j].active=0;
    /* Preserve the original eight-voice weighted DSP budget, local to this kit. */
    unsigned weight=d->weight?d->weight:1,used=0;
    for(unsigned l=0;l<8;++l)for(unsigned j=0;j<NDV;++j)if(trk[l].v[j].active)used+=DMODELS[trk[l].model].weight?DMODELS[trk[l].model].weight:1;
    while(used+weight>8){dvoice_t *old=NULL;unsigned w=1;
        for(unsigned l=0;l<8;++l)for(unsigned j=0;j<NDV;++j)if(trk[l].v[j].active&&(!old||trk[l].v[j].age<old->age)){old=&trk[l].v[j];w=DMODELS[trk[l].model].weight?DMODELS[trk[l].model].weight:1;}
        if(!old)break;old->active=0;used-=w;
    }
    dvoice_t *v=&t->v[0];if(d->voices>1&&(!t->v[1].active||t->v[1].age<v->age))v=&t->v[1];
    memset(v,0,sizeof *v);v->active=1;v->vel=m[2];v->age=++age;v->rng=(int32_t)(0x9e3779b9u*age+lane+1);t->nt=acid_mode?(int)m[1]-60:0;d->trigger(t,v);
}
static int32_t pcm[64];static unsigned cursor=32;
static void native_audio(int16_t *out,int frames){
    for(int f=0;f<frames;++f){
        if(cursor==32){memset(pcm,0,sizeof pcm);
            for(unsigned l=0;l<8;++l){track_t *t=&trk[l];int32_t mono[32]={0};
                for(unsigned j=0;j<NDV;++j)if(t->v[j].active)DMODELS[t->model].render(t,&t->v[j],mono,32);
                for(unsigned s=0;s<32;++s){int64_t v=(int64_t)mono[s]*t->p[P_LEVEL]/127;
                    pcm[2*s]+=(int32_t)(v*(127-t->p[P_PAN])/127);pcm[2*s+1]+=(int32_t)(v*t->p[P_PAN]/127);}
            }cursor=0;
        }
        for(unsigned c=0;c<2;++c){int32_t v=pcm[2*cursor+c];out[2*f+c]=(int16_t)(v>32767?32767:v<-32768?-32768:v);}++cursor;
    }
}
#define NATIVE_DISPLAY 1
static int native_display(int i,char *out,int capacity){
    if(i==89)return snprintf(out,capacity,"%s",acid_mode?"Acid":"Kit");
    if(i==90)return snprintf(out,capacity,"%s",PRE_FACTORY[factory_sound].name);if(!i){static const char* names[]={"TRX Classic","808","909","Plaits","FM","Industrial"};return snprintf(out,capacity,"%s",names[kit]);}
    unsigned l=(unsigned)(i-1)/11,p=(unsigned)(i-1)%11;track_t* t=&trk[l];
    if(!p)return snprintf(out,capacity,"%s",N_MODEL[t->model]);
    if(p>=9)return snprintf(out,capacity,"%d",t->p[p==9?P_LEVEL:P_PAN]);
    const param_desc_t* d=&DMODELS[t->model].edit[p-1];int value=t->p[P_E0+p-1];
    if(d->fmt==F_ENUM&&d->names&&value>=d->min&&value<=d->max)return snprintf(out,capacity,"%s",d->names[value-d->min]);
    return snprintf(out,capacity,"%d%s",value,d->fmt==F_SEMI?" st":d->unit?d->unit:"");
}
#include "fm1_facade.h"
