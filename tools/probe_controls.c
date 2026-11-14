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
    if(argc<4)return 2;
    void *lib=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);if(!lib)return 3;
    move_plugin_init_v2_fn init=(move_plugin_init_v2_fn)dlsym(lib,MOVE_PLUGIN_INIT_V2_SYMBOL);if(!init)return 4;
    plugin_api_v2_t *api=init(&host);if(!api||!api->create_instance||!api->get_param)return 5;
    void *instance=api->create_instance(argv[2],NULL);if(!instance)return 6;
    for(int n=0;n<1500;n++){char text[32]={0};int r=api->get_param(instance,"ready",text,sizeof text);if(r<=0||strcmp(text,"0"))break;usleep(10000);}
    FILE *f=fopen(argv[3],"r");if(!f)return 7;
    char key[256],text[4096];printf("RHYTHMER_CONTROLS_BEGIN\n[");int count=0;
    while(fgets(key,sizeof key,f)){key[strcspn(key,"\r\n")]=0;memset(text,0,sizeof text);int n=api->get_param(instance,key,text,sizeof text);text[sizeof text-1]=0;
        if(count++)putchar(',');printf("{\"key\":");quoted(key);printf(",\"read\":%d,\"text\":",n);quoted(text);putchar('}');
    }puts("]");fclose(f);api->destroy_instance(instance);dlclose(lib);return 0;
}
