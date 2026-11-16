// SPDX-License-Identifier: GPL-3.0-only
#include "rhythmer/engine/break_manipulator.h"
#include "rhythmer/model/acid_gen.h"
#include "rhythmer/shell/fm1_gen_bridge.h"
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <vector>
extern "C" {
void jungle_init();int jungle_bind(const uint8_t*,unsigned,unsigned);
void jungle_sequence_mode(unsigned);void jungle_sequence_note(unsigned);void jungle_sequence_off(unsigned);
void jungle_play(unsigned);void jungle_tempo(unsigned);void jungle_tick_mask(uint32_t);void jungle_render(int32_t*,unsigned);
}
using namespace rhythmer;
int main(){
    SampleData loop;loop.frames=48000;loop.left.resize(loop.frames);
    std::vector<uint8_t> packed(72000);
    for(unsigned i=0;i<loop.frames;i+=2){
        int a=int(1500*std::sin(i*.081)),b=int(1500*std::sin((i+1)*.081));
        loop.left[i]=a/2048.f;loop.left[i+1]=b/2048.f;
        unsigned aa=unsigned(a)&4095,bb=unsigned(b)&4095;
        packed[i/2*3]=aa;packed[i/2*3+1]=(aa>>8)|((bb&15)<<4);packed[i/2*3+2]=bb>>4;
    }
    double worst=0;
    for(unsigned roll=0;roll<16;roll++){
        BreakManipulator m;m.configure(2,0);m.tempo(1200);m.sources(&loop,&loop);
        jungle_init();jungle_bind(packed.data(),packed.size(),48000);jungle_sequence_mode(1);jungle_tempo(1200);
        m.note(36,127);jungle_play(1);jungle_sequence_note(0);
        double ticks=0,energy=0;float previous=0;
        for(unsigned block=0;block<3000;block++){
            if(block==100){m.note(roll,127);jungle_sequence_note(roll+16);}
            if(block==2400){m.off(roll);jungle_sequence_off(roll+16);}
            uint32_t mask=0;for(unsigned i=0;i<32;i++){ticks+=1200*4*48;if(ticks>=44100.0*600){ticks-=44100.0*600;mask|=uint32_t(1)<<i;}}
            int32_t expected[64]{};jungle_tick_mask(mask);jungle_render(expected,32);
            float l[32]{},r[32]{};m.render(l,r,32,44100);
            for(unsigned i=0;i<32;i++){assert(std::isfinite(l[i])&&l[i]==r[i]);double difference=std::abs(l[i]-previous);worst=std::max(worst,difference);assert(difference<.00001);previous=expected[2*i]/8388608.f;energy+=l[i]*l[i];}
        }
        assert(energy>1);m.stop();float l[64],r[64];m.render(l,r,64,44100);for(float v:l)assert(v==0);
    }
    // Different-length A/B buffers and device rates, independent per-track DSP.
    SampleData b=loop;b.frames=32000;b.left.resize(b.frames);
    for(unsigned bars=1;bars<=4;bars++)for(unsigned rate:{44100u,48000u,96000u}){
        BreakManipulator a,c;a.configure(bars,7);c.configure(bars,0);a.tempo(1700);c.tempo(1700);a.sources(&loop,&b);c.sources(&loop,&b);
        a.note(148,127);c.note(36,127);a.note(17,127);a.note(6,127);
        for(unsigned k=0;k<200;k++){float l[128],r[128],ll[128],rr[128];a.render(l,r,128,rate);c.render(ll,rr,128,rate);for(unsigned i=0;i<128;i++)assert(std::isfinite(l[i])&&std::isfinite(ll[i]));}
        a.note(18,127);a.note(16,127);a.stop();assert(!a.sounding());
    }
    // These controls do not have an audible purpose in every play mode.
    auto audition=[&](bool chop,bool hold,bool stretch,unsigned grain){
        BreakManipulator m;m.configure(2,0);m.tempo(1200);m.sources(&loop,&loop);
        m.param(9,chop);m.param(1,100);m.param(2,90);m.param(4,hold);m.param(6,grain);
        m.note(36,127);if(stretch)m.note(2,127);
        std::vector<float> out(220500),right(out.size());m.render(out.data(),right.data(),out.size(),44100);
        for(float v:out)assert(std::isfinite(v));return out;
    };
    auto chop=audition(true,false,false,20);
    assert(chop==audition(true,true,false,20)); // pattern hold does not hold chop audio
    assert(chop==audition(true,false,false,60)); // ordinary chops are not stretched
    assert(audition(false,false,false,20)!=audition(false,true,false,20));
    assert(audition(true,false,true,20)!=audition(true,false,true,60));
    std::puts("BREAK_CONDITIONS chop_hold=inaudible loop_hold=audible grain_requires_stretch=ok");
    unsigned checked=0;
    for(auto division:{Division::Eighth,Division::Sixteenth,Division::ThirtySecond})for(unsigned len:{1u,16u,32u,64u})for(unsigned seed=1;seed<=100;seed++)for(bool mutate:{false,true}){
        Pattern source;source.division=division;unsigned grid=source.q();source.length=len*grid;
        uint8_t notes[64]{},flags[64]{};
        for(unsigned n=0;n<len;n+=4){Event e;e.tick=n*grid;e.key=uint8_t(36+n%12);e.length=3*grid;e.velocity=127;e.flags=step_accent|step_slide;source.add(e);
            notes[n]=e.key;flags[n]=1|4|8;for(unsigned k=1;k<std::min(3u,len);k++){notes[(n+k)%len]=e.key;flags[(n+k)%len]=2;}}
        AcidGenSettings settings;settings.seed=seed;settings.slide=seed%101;settings.octaves=seed%3+1;settings.octave=seed%5;
        uint8_t cfg[5]={settings.density,settings.accent,settings.slide,settings.octaves,settings.octave};uint32_t reference=seed;
        for(unsigned i=0;i<len;i++){int n=notes[i];unsigned guard=12;while(guard--&&!(0x5ad&(1u<<unsigned((n-3+120)%12))))--n;if(n<0)n+=12;notes[i]=uint8_t(std::clamp(n,0,127));}
        acid_generate(notes,flags,len,cfg,&reference,mutate,3,0x5ad);
        auto got=acid_generate_pattern(source,settings,mutate,3,0x5ad);assert(settings.seed==reference);
        unsigned count=0;
        for(unsigned n=0;n<len;n++)if((flags[n]&3)==1){count++;auto it=std::find_if(got.events.begin(),got.events.end(),[&](const Event& e){return e.tick==n*grid;});assert(it!=got.events.end());
            assert(it->key==notes[n]);assert(bool(it->flags&step_accent)==bool(flags[n]&4));assert(bool(it->flags&step_slide)==bool(flags[n]&8));assert(it->velocity==(flags[n]&4?127:96));
            unsigned cells=1;while(cells<len&&(flags[(n+cells)%len]&3)==2)cells++;assert(it->length==cells*grid);
        }
        assert(got.events.size()==count);checked++;
    }
    std::printf("BREAK_ACID original_rolls=16 max_sample_error=%.9f rates=3 bars=4 acid_reference_cases=%u\n",worst,checked);
}
