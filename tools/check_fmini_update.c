/* SPDX-License-Identifier: MIT
 * Exercise the actual native port, not a substitute synth. Output is a signal
 * regression report; nonzero PCM is not a listening or hardware acceptance test.
 */
#include "../ports/common/move-sdk/plugin_api_v1.h"
#include <assert.h>
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static float bpm(void) { return 132; }
static const host_api_v1_t host = {.api_version=1,.sample_rate=44100,
    .frames_per_block=128,.get_bpm=bpm};
int main(int argc,char **argv) {
    assert(argc==2);
    void *lib=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);
    if(!lib){fprintf(stderr,"%s\n",dlerror());return 2;}
    move_plugin_init_v2_fn init=(move_plugin_init_v2_fn)dlsym(lib,MOVE_PLUGIN_INIT_V2_SYMBOL);
    assert(init);plugin_api_v2_t *api=init(&host);
    void *instance=api->create_instance(".",NULL);assert(instance);
    unsigned silent=0;
    for(int program=0;program<200;program++) {
        char value[32],before[16384],after[16384];
        snprintf(value,sizeof value,"%d",program);api->set_param(instance,"p0",value);
        assert(api->get_param(instance,"state",before,sizeof before)>0);
        api->set_param(instance,"p107","127");
        api->set_param(instance,"state",before);
        api->get_param(instance,"state",after,sizeof after);assert(!strcmp(before,after));
        for(int note=36;note<=84;note+=24) {
            uint8_t on[]={0x90,note,100},off[]={0x80,note,0};
            api->on_midi(instance,on,3,0);
            uint64_t energy=0,hash=1469598103934665603ull;
            unsigned peak=0,clipped=0;
            for(int block=0;block<1034;block++) {
                int16_t pcm[256];
                if(block==862)api->on_midi(instance,off,3,0);
                api->render_block(instance,pcm,128);
                for(int k=0;k<256;k++) {
                    int x=pcm[k];unsigned a=(unsigned)abs(x);
                    energy+=(uint64_t)((int64_t)x*x);if(a>peak)peak=a;
                    clipped+=a>=32767;hash=(hash^(uint16_t)x)*1099511628211ull;
                }
            }
            silent+=peak==0;
            printf("{\"program\":%d,\"note\":%d,\"peak\":%u,\"energy\":%llu,\"clipped\":%u,\"hash\":\"%016llx\"}\n",
                program,note,peak,(unsigned long long)energy,clipped,(unsigned long long)hash);
        }
    }
    fprintf(stderr,"FMINI_SIGNAL cases=600 state_roundtrips=200 silent=%u\n",silent);
    api->destroy_instance(instance);dlclose(lib);return silent?3:0;
}
