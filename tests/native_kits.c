/* SPDX-License-Identifier: GPL-3.0-only
 * Exercise every factory kit/pad through the native module boundary, using
 * deliberately irregular host sizes and guard samples. Not a sound-quality test. */
#include "move-sdk/plugin_api_v1.h"
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
int main(int argc,char **argv){
    assert(argc>=5);void *lib=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);if(!lib){fprintf(stderr,"%s\n",dlerror());return 1;}
    plugin_api_v2_t *(*init)(const host_api_v1_t*)=dlsym(lib,"move_plugin_init_v2");assert(init);
    plugin_api_v2_t *api=init(NULL);void *instance=api->create_instance(".","{}");assert(instance);
    const int sizes[]={1,31,32,100,127,128,129,256,1024};
    int tested=0;char kit[32],saved[65536],after[65536];
    for(int k=0;k<atoi(argv[2]);++k){
        snprintf(kit,sizeof kit,"%d",k);api->set_param(instance,"p0",kit);
        for(int p=3;p<argc;++p){
            uint8_t panic[]={0xb0,120,0},note[]={0x90,(uint8_t)atoi(argv[p]),110};
            api->on_midi(instance,panic,3,0);api->on_midi(instance,note,3,0);
            uint64_t energy=0;int16_t pcm[2*1024+2];
            for(int b=0;b<160;++b){int n=sizes[b%9];pcm[0]=1234;pcm[2*n+1]=5678;
                api->render_block(instance,pcm+1,n);assert(pcm[0]==1234&&pcm[2*n+1]==5678);
                for(int i=0;i<2*n;++i)energy+=(uint64_t)abs((int)pcm[1+i]);
            }
            if(!energy){fprintf(stderr,"Silent kit=%d note=%s\n",k,argv[p]);return 2;}++tested;
        }
        assert(api->get_param(instance,"state",saved,sizeof saved)>0);
        api->set_param(instance,"state","FM1S1:9999999999999999999999999999999");
        assert(api->get_param(instance,"state",after,sizeof after)>0);assert(!strcmp(saved,after));
        api->set_param(instance,"state",saved);api->get_param(instance,"state",after,sizeof after);assert(!strcmp(saved,after));
    }
    printf("PASS %d kit/pad combinations; state round trips; irregular block guards\n",tested);
    api->destroy_instance(instance);dlclose(lib);return 0;
}
