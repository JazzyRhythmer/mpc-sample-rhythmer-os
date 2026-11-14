// SPDX-License-Identifier: GPL-3.0-only
#include "rhythmer/shell/context.h"
#include "rhythmer/shell/track_copy.h"
#include "rhythmer/engine/sampler.h"
#include <cmath>
#include "rhythmer/engine/engine_host.h"
#include "rhythmer/shell/sample_library.h"
#include "rhythmer/plugin/plugin_rack.h"
#include "rhythmer/engine/engine_info.h"
namespace rhythmer {
void Context::gen_break_load(const std::string& path,const std::string& name){
    if(host_recording()){notice("Stop recording before BREAK");return;}
    if(frozen_edit(ui.track))return;
    int slot=sample_slot(path,name);if(slot<0){notice("No sample slot");return;}
    ui.break_pending=slot;ui.break_pending_b=ui.break_load_b;ui.break_track=ui.track;ui.break_bank=track().bank;ui.break_bars=ui.break_load_b?project.tracks[ui.break_track].break_bars:project.gen8.bars;
    ui.break_browse=false;open(PageId::Patterns);ui.sheet_open=true;ui.gen8_mode=2;ui.sheet_row=0;notice("Loading BREAK sample");
}
void Context::gen_break_tick(){
    for(unsigned t=0;t<track_count;t++)if(project.tracks[t].break_bars&&!frozen(t))project.tracks[t].break_source=uint8_t(host.break_source_of(t));
    for(unsigned t=0;t<track_count;t++)if(project.tracks[t].break_bars&&!frozen(t)){unsigned variation=0,drift=0;if(host.break_feedback(t,ui.break_feedback_seen[t],variation,drift)){project.tracks[t].break_perf[1]=uint16_t(variation);project.tracks[t].break_perf[2]=uint16_t(drift);}}
    unsigned bar=host.ticks()/384;
    if(!host.playing())acid_auto_bar=~0u;
    else if(bar!=acid_auto_bar){acid_auto_bar=bar;
        if(bar&&!host_recording()&&!host.song_playing()){
            auto selected=ui.track;
            for(unsigned t=0;t<track_count;t++){const auto& tr=project.tracks[t];
                if(!frozen(t)&&tr.engine==EngineKind::Plugin&&tr.plugin<max_plugins&&std::string(project.plugins[tr.plugin].name)=="Acid Engine"&&tr.acid_gen.auto_bars&&bar%tr.acid_gen.auto_bars==0&&!tr.mix.mute&&patterns.at[t][tr.pattern].steps()<=64){ui.track=uint8_t(t);gen8_action(13);}}
            ui.track=selected;
        }
    }
    if(plugins)for(unsigned e=0;e<max_plugins;e++)if(project.plugins[e].gen_program>=0&&plugins->status(e)==PluginStatus::Ready){plugins->select_program(e,project.plugins[e].gen_program);project.plugins[e].gen_program=-1;}
    if(ui.break_pending<0||host_recording())return;
    unsigned slot=unsigned(ui.break_pending),at=ui.break_track;
    if(slot>=sample_slots||at>=track_count){ui.break_pending=-1;return;}
    const auto& sample=project.samples[slot];if(!sample.frames){if(library){auto loaded=library->slot(slot);if(!loaded.error.empty()){ui.break_pending=-1;notice("BREAK: sample load failed");}}return;}
    ui.break_pending=-1;
    if(frozen_edit(at))return; // a track may have frozen while sample decoding ran
    unsigned bars=std::clamp<unsigned>(ui.break_bars,1,4);
    if(sample.instrument()||sample.frames<16){notice("BREAK needs an audio loop");return;}
    double bpm=bars*4.0*60.0*44100.0/sample.frames;
    if(bpm*10<1||bpm*10>65535){notice("BREAK sample duration out of range");return;}
    if(ui.break_pending_b&&project.tracks[at].break_bars){
        Edit edit;edit.what="Load BREAK B";edit.track=uint8_t(at);edit.track_before=std::make_unique<TrackState>(track_state(*this,at));
        auto next=std::make_unique<TrackState>(*edit.track_before);auto& t=next->track;
        auto& layer=t.pads[t.bank*16].layers[0];layer.sample=uint16_t(slot);layer.start=0;layer.end=sample.frames;
        restore_track(*this,at,*next);edit.track_after=std::move(next);edits.push(std::move(edit));dirty=true;ui.break_load_b=false;
        ui.track=uint8_t(at);open(PageId::Edit);ui.edit_page[at]=0;ui.break_perf_page=2;notice("BREAK B ready");return;
    }
    ui.break_load_b=false;
    Edit edit;edit.what="Load BREAK";edit.track=uint8_t(at);
    edit.track_before=std::make_unique<TrackState>(track_state(*this,at));
    auto next=std::make_unique<TrackState>(*edit.track_before);auto& t=next->track;
    rhythmer::load_sound(t,EngineKind::Sampler,0);t.break_bars=uint8_t(bars);t.bank=ui.break_bank%sampler_banks;t.layout=PadLayout::Drums;t.set_name("BREAK");t.last_note=uint8_t(sampler_first_note+t.bank*16);
    t.params[sampler::Follow]=1;t.params[sampler::FollowHow]=0;
    for(unsigned i=0;i<16;i++){
        PadSound sound;sound.sample=uint16_t(slot);sound.start=uint32_t(uint64_t(sample.frames)*i/16);sound.end=uint32_t(uint64_t(sample.frames)*(i+1)/16);
        sound.own_tempo=uint16_t(std::lround(bpm*10));sound.group=16;sound.mono=true;
        t.pads[t.bank*16+i]=sound;
    }
    auto& pat=next->patterns[t.pattern];pat.length=bars*384;
    BreakMap map;map.bars=bars;for(unsigned i=0;i<16;i++)map.slices[i]=uint8_t(sampler_first_note+t.bank*16+i);
    pat=break_generate(pat,BreakAction::Straight,project.gen8,map,project.tempo/10);
    restore_track(*this,at,*next);edit.track_after=std::move(next);edits.push(std::move(edit));dirty=true;
    notice("BREAK ready: "+std::to_string(bars)+" bars / 16 chops");
}
}
