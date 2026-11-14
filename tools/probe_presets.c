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
    void *instance=api->create_instance(argv[2],NULL);if(!instance)return 6;
    /* The published Clementine/organ modules initialise on their own worker. */
    if(strstr(argv[1],"clementine")||strstr(argv[1],"setbfree")||strstr(argv[1],"tablor")) {
        for(unsigned tries=0;tries<1000;tries++) {
            char ready[32]={0};int n=api->get_param?api->get_param(instance,"ready",ready,sizeof ready):0;
            if(n<=0||strcmp(ready,"0"))break;
            usleep(10000);
        }
    }
    usleep(50000);
    const char *selector=argc>3?argv[3]:"preset";
    if(argc>5)api->set_param(instance,"syx_bank_index",argv[5]);
    char text[4096]={0};
    api->get_param(instance,"preset_count",text,sizeof text);
    int count=argc>4?atoi(argv[4]):atoi(text);if(count<0||count>8192)return 9;
    printf("\nRHYTHMER_PRESETS_BEGIN\n{\"count\":%d,\"names\":[",count);fflush(stdout);
    for(int i=0;i<count;i++) {
        char value[32];snprintf(value,sizeof value,"%d",i);api->set_param(instance,selector,value);
        text[0]=0;api->get_param(instance,"preset_name",text,sizeof text);
        if(!text[0])api->get_param(instance,selector,text,sizeof text);
        if(i)putchar(',');quoted(text);fflush(stdout);
    }
    printf("]");
    if(!strcmp(selector,"patch")) {
        printf(",\"audible\":[");
        for(int i=0;i<count;++i){if(i)putchar(',');putchar('[');
            for(int voice=0;voice<4;++voice){
                void *test=api->create_instance(argv[2],NULL);if(!test)return 10;
                char value[32];snprintf(value,sizeof value,"%d",i);api->set_param(test,"patch",value);
                for(int k=1;k<=4;++k){char key[16];snprintf(key,sizeof key,"seq%d",k);api->set_param(test,key,"1");}
                api->set_param(test,"tempo_sync","Sync");
                uint8_t msg[]={0x90,(uint8_t)(36+voice),110};api->on_midi(test,msg,3,MOVE_MIDI_SOURCE_EXTERNAL);
                int peak=0;int16_t audio[256];
                for(int block=0;block<128;++block){memset(audio,0,sizeof audio);api->render_block(test,audio,128);for(int j=0;j<256;++j)if(abs(audio[j])>peak)peak=abs(audio[j]);}
                api->destroy_instance(test);if(voice)putchar(',');printf("%s",peak>16?"true":"false");
            }putchar(']');fflush(stdout);
        }printf("]");
    }
    puts("}");api->destroy_instance(instance);dlclose(lib);return 0;
}
