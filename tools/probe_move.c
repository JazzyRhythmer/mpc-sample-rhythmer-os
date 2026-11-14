/* SPDX-License-Identifier: MIT
 * Isolated native probe for original Move modules; no device/MIDI output. */
#define _GNU_SOURCE
#include "../ports/common/move-sdk/plugin_api_v1.h"
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
static double beat;
static float bpm(void){return 120.0f;}
static double position(void){return beat;}
static int clock_status(void){return MOVE_CLOCK_STATUS_RUNNING;}
static int no_midi(const uint8_t *m,int n){(void)m;(void)n;return 0;}
static void no_log(const char *s){(void)s;}
static uint8_t mailbox[4096];
static const host_api_v1_t host={.api_version=1,.sample_rate=44100,.frames_per_block=128,
    .mapped_memory=mailbox,.audio_out_offset=MOVE_AUDIO_OUT_OFFSET,.audio_in_offset=MOVE_AUDIO_IN_OFFSET,
    .log=no_log,.midi_send_internal=no_midi,.midi_send_external=no_midi,.get_clock_status=clock_status,
    .get_bpm=bpm,.get_beat_position=position};
static void quoted(const char *s){
    putchar('"');for(const unsigned char *p=(const unsigned char*)s;*p;p++){
        if(*p=='"'||*p=='\\'){putchar('\\');putchar(*p);}
        else if(*p<32)printf("\\u%04x",*p);else putchar(*p);
    }putchar('"');
}
int main(int argc,char **argv){
    if(argc<3)return 2;
    void *lib=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);if(!lib){fprintf(stderr,"%s\n",dlerror());return 3;}
    move_plugin_init_v2_fn init=(move_plugin_init_v2_fn)dlsym(lib,MOVE_PLUGIN_INIT_V2_SYMBOL);
    if(!init)return 4;
    plugin_api_v2_t *api=init(&host);if(!api||api->api_version!=2||!api->create_instance||!api->render_block)return 5;
    void *instance=api->create_instance(argv[2],argc>3?argv[3]:NULL);if(!instance)return 6;
    /* The published Clementine/organ modules initialise on their own worker. */
    if(strstr(argv[1],"model-72")||strstr(argv[1],"clementine")||strstr(argv[1],"setbfree")||strstr(argv[1],"tablor")) {
        for(unsigned tries=0;tries<1000;tries++) {
            char ready[32]={0};int n=api->get_param?api->get_param(instance,"ready",ready,sizeof ready):0;
            if(n<=0||strcmp(ready,"0"))break;
            usleep(10000);
        }
    }
    usleep(50000);
    char *buf=calloc(1,2*1024*1024);if(!buf)return 7;
    puts("\nRHYTHMER_PROBE_BEGIN");printf("{");
    const char *keys[]={"chain_params","ui_hierarchy","state","preset_count","bank_count"};
    for(unsigned i=0;i<sizeof keys/sizeof *keys;i++){
        memset(buf,0,2*1024*1024);int n=api->get_param?api->get_param(instance,keys[i],buf,2*1024*1024):0;
        buf[2*1024*1024-1]=0;if(n>=2*1024*1024){free(buf);return 8;}
        if(i)putchar(',');quoted(keys[i]);putchar(':');quoted(n>0?buf:"");
    }
    fflush(stdout);
    const uint8_t notes[]={36,38,40,42,46,48,60,64,67,72};
    if(api->on_midi)for(unsigned i=0;i<sizeof notes;i++){
        uint8_t msg[]={0x90,notes[i],100};api->on_midi(instance,msg,3,MOVE_MIDI_SOURCE_EXTERNAL);
    }
    int peak=0;double squares=0;int16_t audio[256];
    for(unsigned block=0;block<160;block++){
        memset(audio,0,sizeof audio);api->render_block(instance,audio,128);beat+=256.0/44100;
        for(unsigned i=0;i<256;i++){int x=audio[i];if(abs(x)>peak)peak=abs(x);squares+=(double)x*x;}
    }
    printf(",\"peak\":%d,\"mean_square\":%.9g}\n",peak,squares/(160*256));
    fflush(stdout);if(api->destroy_instance)api->destroy_instance(instance);dlclose(lib);free(buf);return 0;
}
