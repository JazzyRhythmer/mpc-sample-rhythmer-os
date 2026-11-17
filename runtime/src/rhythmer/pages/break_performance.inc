// SPDX-License-Identifier: GPL-3.0-only
#include "rhythmer/pages/break_status.h"
bool break_home(const Snapshot& s){return s.track().engine==EngineKind::Sampler&&s.track().break_bars;}
bool break_home(Context& c){return c.track().engine==EngineKind::Sampler&&c.track().break_bars;}
void break_performance(Paint& p,const Snapshot& s){
    unsigned page=s.ui.break_perf_page%6;
    auto h=header_of(s);h.left.push_back(pill(Icon::Chip,"BRK PERF",colour::text));
    frame(p,s,{{"GEN",page==2?"LOAD B":"LOAD A","RETURN"},-1,colour::text},h);
    const float x=zone::pad,y=zone::picture_y,w=zone::width-2*zone::pad;
    const char* titles[]={"ROLLS / HOLD PADS","CHOPS","SOURCE A / B","LOOP VARIATIONS","GRAIN / STRETCH","TRACK MIX"};
    p.text(juce::String(page+1)+" / 6   "+titles[page],x,y,w,16,plain(colour::text,type::small,Weight::Bold));
    const char* hints[]={"Hold a pad / Release ends command","CHOP: play slices / HOLD affects LOOP","Load A: ROLLS B2 / Load B: B2 here","LOOP + Play / Hold OFF to vary","Hold P3 on ROLLS; wheel here","Track level / Pan / Send A"};
    p.text(hints[page],x,y+17,w,14,plain(colour::sec,type::small));
    if(page<2){
        const float cw=(w-9)/4,rh=24;
        for(unsigned pad=0;pad<16;pad++){
            float xx=x+(pad%4)*(cw+3),yy=y+36+(3-pad/4)*(rh+3);bool held=(s.ui.held_pads>>pad)&1;
            p.fill(xx,yy,cw,rh,held?colour::text:colour::raised,2);
            auto text=page==0?juce::String(break_roll_labels[pad]):"CHOP "+juce::String(pad+1);
            p.text(text,xx+2,yy+4,cw-4,rh-8,p.fit(text,plain(held?colour::bg:colour::text,type::small,Weight::Medium),cw-4,type::floor),juce::Justification::centred);
        }
    }else if(page==2){
        const auto& t=s.track();
        const auto a=t.pads[t.bank*16].sample,b=t.pads[t.bank*16].layers[0].sample;
        p.text(s.track().break_source==0?"PAD 1: SOURCE A [ACTIVE]":"PAD 1: SOURCE A",x,y+40,w,18,plain(colour::text,type::small,Weight::Bold));
        p.text(a<sample_slots?juce::String(s.project.samples[a].name):"Load loop A",x,y+60,w,17,plain(colour::sec,type::small));
        p.text(s.track().break_source==1?"PAD 2: SOURCE B [ACTIVE]":"PAD 2: SOURCE B",x,y+82,w,18,plain(colour::text,type::small,Weight::Bold));
        p.text(b<sample_slots?juce::String(s.project.samples[b].name):"Load loop B",x,y+102,w,17,plain(colour::sec,type::small));
        p.text("PAD 3 / RETURN: straight playback",x,y+126,w,15,plain(colour::sec,type::small));
    }else{
        performance_art(p,s,"Break Engine","User loop",x,y+43,w,56,int(s.track().last_pad));
        p.text(page==3?break_variation_status(s.track().break_perf[9],s.track().break_perf[4],s.playing,s.break_activity,s.track().break_perf[1],s.track().break_perf[2]):page==4?break_stretch_status(s.playing,s.break_activity):"Wheel: page / Record + Play: capture",x,y+111,w,17,plain(colour::sec,type::small));
        if(page==3 || page==4)p.text(page==3?"Values can be prepared while inactive":"Grain needs STRETCH / not Pattern Hold",x,y+129,w,13,plain(colour::dim,type::small));
    }
}
void break_pad(Context& c,unsigned pad,uint8_t velocity,bool down){
    if(!break_home(c)||c.ui.break_perf_page%6==1||c.ui.break_perf_page%6>=3){c.play_pad(pad,velocity,down);return;}
    c.release_pad(pad);if(!down)return;
    unsigned page=c.ui.break_perf_page%6;int key=page==0?int(pad):pad<3?16+int(pad):-1;
    if(key<0)return;
    if(page==2&&pad==1&&!c.track().pads[c.track().bank*16].layers[0].used()){c.notice("Load loop B first");return;}
    c.pad_track[pad]=c.ui.track;c.pad_keys[pad][0]=key;c.key(key,velocity,true);
}
