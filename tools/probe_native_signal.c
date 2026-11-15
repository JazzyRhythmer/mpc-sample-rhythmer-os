/* SPDX-License-Identifier: MIT: deterministic off-device native signal probe. */
#define _GNU_SOURCE
#include "../ports/common/move-sdk/plugin_api_v1.h"
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static float bpm(void){return 132;}
static const host_api_v1_t host={.api_version=1,.sample_rate=44100,.frames_per_block=128,.get_bpm=bpm};
int main(int argc,char **argv){
 if(argc<2)return 2;void*lib=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);if(!lib){fprintf(stderr,"%s",dlerror());return 3;}
 move_plugin_init_v2_fn init=(move_plugin_init_v2_fn)dlsym(lib,MOVE_PLUGIN_INIT_V2_SYMBOL);if(!init)return 4;plugin_api_v2_t*a=init(&host);void*p=a->create_instance(".",0);if(!p)return 5;
 for(int i=2;i<argc;i++){char pair[128];snprintf(pair,sizeof pair,"%s",argv[i]);char*v=strchr(pair,'=');if(!v)return 6;*v++=0;a->set_param(p,pair,v);}
 int note=getenv("RHYTHMER_NOTE")?atoi(getenv("RHYTHMER_NOTE")):60;uint8_t on[]={0x90,note,100},off[]={0x80,note,0};
 a->on_midi(p,on,3,0);uint64_t hash=1469598103934665603ull;double energy=0;int peak=0;
 for(int block=0;block<1400;block++){int16_t pcm[256];if(block==350)a->on_midi(p,off,3,0);a->render_block(p,pcm,128);for(int i=0;i<256;i++){int v=pcm[i];if(abs(v)>peak)peak=abs(v);energy+=(double)v*v;hash=(hash^(uint16_t)v)*1099511628211ull;}}
 printf("SIGNAL {\"hash\":\"%016llx\",\"energy\":%.0f,\"peak\":%d}\n",(unsigned long long)hash,energy,peak);a->destroy_instance(p);dlclose(lib);return 0;
}
