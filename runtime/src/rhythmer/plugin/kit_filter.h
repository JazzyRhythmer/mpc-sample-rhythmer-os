// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 jazzy rhythmer
#pragma once
#include "rhythmer/engine/effects.h"
#include <array>
#include <cstdint>
namespace rhythmer {
using KitFilterValues=std::array<int16_t,3>;
// The existing OS SVF, owned by an instrument or Kit engine. No insert slot, delay block,
// external routing, allocation or lock is needed while audio runs.
class KitFilterStage {
public:
    KitFilterStage(){filter.set_bypass(true);filter.set_kind(EffectKind::Filter,pool);}
    void silence(){filter.clear();}
    void process(const KitFilterValues& values,uint64_t generation,float* left,float* right,unsigned frames){
        const bool open=values[0]==100&&values[1]==0&&values[2]==0;
        const float rate=dsp::sample_rate();
        if(generation!=epoch||rate!=last_rate){filter.set_bypass(open);filter.set_kind(EffectKind::Filter,pool);epoch=generation;last_rate=rate;last={{-1,-1,-1}};}
        if(values!=last){filter.set_params({{values[0],values[1],values[2],0,0,0}});last=values;}
        filter.set_bypass(open);filter.process(left,right,frames);
    }
private:
    DelayPool pool{0};Effect filter;
    KitFilterValues last{{-1,-1,-1}};uint64_t epoch=0;float last_rate=0;
};
}
