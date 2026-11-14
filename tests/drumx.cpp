// SPDX-License-Identifier: GPL-3.0-only
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>
extern "C" {
#include "engine.h"
void drumx_reference_reset(unsigned,unsigned);
void drumx_reference_block(unsigned,unsigned,int32_t*);
}
#include "felucca_tables.h"
#include "helpers.h"
#define CTL 32
#include "core.h"
int main() {
    for(unsigned kit=0;kit<9;++kit)for(unsigned lane=0;lane<8;++lane) {
        DrumXCore core{};DrumXCore::dx_voice_t voice{};
        std::memcpy(core.dx_kit,core.DX_KITS[kit].lane,sizeof core.dx_kit);
        std::memcpy(core.dx_lay,core.DX_KITS[kit].lay,sizeof core.dx_lay);
        core.dx_trigger(&voice);drumx_reference_reset(kit,lane);
        for(unsigned block=0;block<256;++block) {
            core.dx_tone=uint8_t((block/17)%256);core.dx_hands=(block/29)%16;
            if(block==127)core.dx_choke(&voice);
            int32_t actual[32],expected[32];drumx_reference_block(lane,block,expected);
            core.dx_run(&core.dx_kit[lane],&voice,block%128,int(block%65)-32,int(block%33)-16,
                int(block%25)-12,int(block%17)-8,block%128,block%128,actual,32);
            assert(!std::memcmp(actual,expected,sizeof actual));
        }
    }
    auto api=mpc_engine();void *a=api->create(nullptr),*b=api->create(nullptr);assert(a&&b&&a!=b);
    for(unsigned k=0;k<9;++k) {
        char kit[16];std::snprintf(kit,sizeof kit,"%u",k);api->set_param(a,"kit",kit);
        for(unsigned lane=0;lane<8;++lane) {
            uint8_t msg[]={0x90,uint8_t(36+lane),110};api->midi(a,msg,3);
            int64_t energy=0;
            for(int frames:{1,31,32,127,129,256,1024}) {
                std::vector<int16_t> out(size_t(frames)*2+2,12345);api->render(a,out.data()+1,frames);
                assert(out.front()==12345&&out.back()==12345);
                for(int i=1;i<=2*frames;++i)energy+=int64_t(out[i])*out[i];
            }
            assert(energy>0);
        }
    }
    char state[4096],restored[4096];assert(api->get_param(a,"state",state,sizeof state)>0);
    api->set_param(b,"state",state);assert(api->get_param(b,"state",restored,sizeof restored)>0);
    assert(!std::strcmp(state,restored));
    api->set_param(a,"l0_a_pitch","77");assert(api->get_param(b,"state",restored,sizeof restored)>0);
    assert(!std::strcmp(state,restored));
    api->set_param(b,"state","DXS1:bad");api->get_param(b,"state",restored,sizeof restored);assert(!std::strcmp(state,restored));
    api->destroy(a);api->destroy(b);
    std::puts("PASS DRUM-X: 9 kits, 8 lanes, 589824 bit-identical samples, odd blocks, independent instances, state bounds");
}
