// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 jazzy rhythmer
#pragma once
#include "rhythmer/shell/shell.h"
#include "rhythmer/shell/mute_mode.h"
#include "rhythmer/model/project_file.h"
#include "rhythmer/engine/plugin_engine.h"
#include <functional>
#include <iostream>
#include <cstring>
namespace rhythmer {
inline int kit_mute_check(const std::function<void(Shell&,const std::string&)>& capture={}) {
    auto host=std::make_unique<EngineHost>();auto shell=std::make_unique<Shell>(*host);auto& c=shell->context();unsigned checks=0;uint32_t now=10000;
#define KM(ok,msg) do{++checks;if(!(ok)){std::cerr<<"KIT_MUTE_FAIL "<<checks<<": "<<msg<<'\n';return 1;}}while(false)
    auto button=[&](SurfaceButton b,bool down){SurfaceEvent e;e.input.kind=SurfaceInput::Kind::Button;e.input.index=uint8_t(b);e.input.pressed=down;shell->surface(e,++now);};
    auto tap=[&](SurfaceButton b){button(b,true);button(b,false);};
    auto hit=[&](unsigned pad){SurfaceEvent e;e.pad=int(pad);e.midi.status=0x99;e.midi.value=100;shell->surface(e,++now);e.midi.status=0x89;e.midi.value=0;shell->surface(e,++now);};
    auto setup=[&]{c.ui=UiState{};c.project.tracks[0]=Track{};auto& t=c.project.tracks[0];load_sound(t,EngineKind::Plugin,0);t.plugin=0;t.layout=PadLayout::Drums;
        auto& ref=c.project.plugins[0];ref=PluginRef{};std::snprintf(ref.path,sizeof ref.path,"Plugins/RHYTHMER - Rhythmer Kit");std::snprintf(ref.name,sizeof ref.name,"Rhythmer Kit");
        c.open(PageId::Stage);c.ui.drum_voices.entry=0;for(auto& name:c.ui.drum_voices.names)std::snprintf(name.data(),name.size(),"Drum");c.dirty=false;};
    setup();const auto original_note=c.track().last_note;KM(rhythmer_kit_mute(c.project,c.ui,true),"kit identified on play page");
    tap(SurfaceButton::Mute);KM(c.ui.mute_latch,"tap latches mute");
    for(unsigned bank=0;bank<4;++bank){c.track().bank=uint8_t(bank);for(unsigned pad=0;pad<16;++pad){hit(pad);KM(c.track().pad_muted(bank*16+pad),"correct note/bank slot toggled");KM(!c.track().mix.mute,"never changes track mute");KM(c.track().last_note==original_note,"muting never plays/selects a note");hit(pad);KM(!c.track().pad_muted(bank*16+pad),"pad unmuted");}}
    KM(c.dirty,"mute marks project dirty");
    c.track().bank=7;hit(15);KM(c.track().pad_muted(63)&&!c.track().pad_muted(127),"saved out-of-range drum bank uses played bank D");hit(15);c.track().bank=0;
    c.project.tracks[1].engine=EngineKind::Plugin;button(SurfaceButton::PadBank,true);hit(1);button(SurfaceButton::PadBank,false);KM(c.ui.track==1&&!c.project.tracks[0].any_pad_muted(),"track selection keeps priority during mute");c.ui.track=0;

    c.track().bank=0;hit(0);hit(10);KM(c.track().pad_muted(0)&&c.track().pad_muted(10)&&!c.track().pad_muted(11),"independent pads");
    {auto taps=std::make_unique<TrackTaps>();PadFacts facts{};facts.key_pads=true;PadScene scene{c.ui,c.project,shell->patterns(),*host,*taps,facts,now,nullptr,0};std::array<pad_light::Look,16> looks{};pad_looks(scene,looks);
     KM(looks[0].hue==pad_light::Hue::Red&&looks[10].hue==pad_light::Hue::Red,"LEDs match muted pad numbers");KM(looks[11].hue!=pad_light::Hue::Red,"unmuted adjacent pad not marked muted");}
    auto bytes=save_project(c.project,shell->patterns());auto restored=std::make_unique<Project>();auto patterns=std::make_unique<PatternBank>();
    KM(load_project(bytes,*restored,*patterns).empty(),"project reload");KM(restored->tracks[0].pad_mutes==c.track().pad_mutes,"all masks persist");
    const auto params=c.track().params;button(SurfaceButton::Shift,true);hit(10);button(SurfaceButton::Shift,false);
    for(unsigned p=0;p<64;++p)KM(c.track().pad_muted(p)==(p!=10),"Shift solo includes all populated banks");
    button(SurfaceButton::Shift,true);hit(10);button(SurfaceButton::Shift,false);KM(!c.track().any_pad_muted(),"second solo restores kit");KM(c.track().params==params,"mute and solo preserve sound controls");
    c.ui.drum_voices.names[15][0]=0;hit(15);KM(!c.track().pad_muted(15)&&!c.track().mix.mute,"empty pad does not mute track");
    c.ui.drum_voices.entry=no_plugin;hit(0);KM(!c.track().any_pad_muted(),"stale voice snapshot ignored");c.ui.drum_voices.entry=0;
    hit(0);c.project.tracks[1].mix.mute=true;button(SurfaceButton::Shift,true);tap(SurfaceButton::Mute);button(SurfaceButton::Shift,false);
    KM(!c.track().any_pad_muted()&&!c.project.tracks[1].mix.mute,"Shift Mute clears pads and tracks");
    c.ui.mute_latch=false;button(SurfaceButton::Mute,true);now+=500;hit(1);button(SurfaceButton::Mute,false);KM(c.track().pad_muted(1)&&!c.ui.mute_mode(),"held mute ends on release");
    tap(SurfaceButton::Mute);c.open(PageId::Tracks);hit(0);KM(c.track().mix.mute&&c.track().pad_muted(1),"Tracks retains track mute");
    setup();std::snprintf(c.project.plugins[0].name,sizeof c.project.plugins[0].name,"Elixir");tap(SurfaceButton::Mute);hit(0);KM(c.track().mix.mute&&!c.track().any_pad_muted(),"standalone drums keep track mute");
    setup();c.track().layout=PadLayout::Chromatic;KM(!rhythmer_kit_mute(c.project,c.ui,true),"non-drum layout excluded");c.track().layout=PadLayout::Drums;c.track().levels=true;KM(!rhythmer_kit_mute(c.project,c.ui,true),"16 Levels excluded");
    setup();c.prints.freeze[0].state=FreezeState::Frozen;tap(SurfaceButton::Mute);hit(0);KM(c.ui.ask==UiState::Ask::Unfreeze&&!c.track().any_pad_muted(),"frozen kit asks to unfreeze instead of pretending to mute a print");
    c.ui.ask=UiState::Ask::None;c.prints.freeze[0].state=FreezeState::Deep;c.ui.drum_voices={};hit(0);KM(c.ui.ask==UiState::Ask::Unfreeze,"deep frozen kit offers unfreeze before missing voice metadata");
    c.ui.ask=UiState::Ask::None;c.track().set_pad_muted(0,true);button(SurfaceButton::Shift,true);tap(SurfaceButton::Mute);button(SurfaceButton::Shift,false);KM(c.ui.ask==UiState::Ask::Unfreeze&&c.track().pad_muted(0),"global clear preserves frozen baked mute until unfreezing");c.prints.freeze[0]={};
    setup();c.track().engine=EngineKind::Sampler;c.track().pads[0].sample=1;tap(SurfaceButton::Mute);hit(0);KM(c.track().pad_muted(0)&&!c.track().mix.mute,"native Sample Kit preserved");
    struct Runner:PluginRunner{uint64_t mask=0;void set_pad_mutes(uint64_t m)override{mask=m;}void midi(uint8_t,uint8_t,uint8_t)override{}void silence()override{}void render(float*,float*,unsigned)override{}} a,b;
    PluginEngine engine;engine.set_pad_mutes(uint64_t(1)<<63);engine.attach(&a);KM(a.mask==(uint64_t(1)<<63),"late attach restores mask");engine.set_pad_mute(0,true);KM(a.mask==((uint64_t(1)<<63)|1),"live runner updated");engine.attach(&b);KM(b.mask==a.mask,"replacement runner receives mask");engine.set_pad_mutes(0);KM(b.mask==0,"unmute reaches runner");engine.set_pad_mute(64,true);KM(b.mask==0,"invalid index ignored");
    // Commands and project restoration through the actual audio host, including bank D's highest bit.
    {auto project=std::make_unique<Project>();auto patterns=std::make_unique<PatternBank>();project->tracks[0].engine=EngineKind::Plugin;project->tracks[0].plugin=0;project->tracks[0].set_pad_muted(63,true);
     auto h=std::make_unique<EngineHost>(EngineHost::Lean{});h->load(*project,*patterns);a.mask=0;KM(h->offer_plugin(0,&a),"runner offer accepted");int32_t audio[256]{};h->render(audio,128,1);KM(a.mask==(uint64_t(1)<<63),"host project restore before late attachment");
     KM(h->send({Command::Type::PadMute,0,0,11,1}),"mute command queued");h->render(audio,128,1);KM(a.mask==((uint64_t(1)<<63)|(uint64_t(1)<<11)),"host command reaches correct pad");
     h->send({Command::Type::PadMute,0,0,0xffff,0});h->render(audio,128,1);KM(a.mask==0,"host global unmute reaches plugin");h->offer_plugin(0,nullptr);h->render(audio,128,1);}
    setup();tap(SurfaceButton::Mute);hit(0);hit(7);hit(15);if(capture)capture(*shell,"01-kit-pad-mute");
    c.open(PageId::Tracks);if(capture)capture(*shell,"02-track-mute-scope");
    std::cout<<"KIT_MUTE_OK checks="<<checks<<" banks=4 project,pad-solo,unmute,track-scope,late-attach=ok\n";
#undef KM
    return 0;
}
}
