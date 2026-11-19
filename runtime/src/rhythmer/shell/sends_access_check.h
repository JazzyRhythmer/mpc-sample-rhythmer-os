// SPDX-License-Identifier: AGPL-3.0-only
#pragma once
#include "rhythmer/engine/engine_host.h"
#include "rhythmer/shell/shell.h"
#include "rhythmer/pages/common.h"
#include "rhythmer/shell/ask.h"
#include "rhythmer/shell/features.h"
#include "rhythmer/shell/mix_hub.h"
#include "rhythmer/shell/note_repeat.h"
#include "rhythmer/model/project_file.h"
#include <functional>
#include <iostream>
namespace rhythmer {
inline int sends_access_check(const std::function<void(Shell&,const std::string&)>& capture = {}) {
    auto host=std::make_unique<EngineHost>();auto so=std::make_unique<Shell>(*host);auto& shell=*so;auto& c=shell.context();
    unsigned checks=0;uint32_t now=10000;
#define SEND_CHECK(ok,msg) do{++checks;if(!(ok)){std::cerr<<"SENDS ACCESS FAIL "<<checks<<": "<<msg<<'\n';return 1;}}while(false)
    auto button=[&](SurfaceButton b,bool down){SurfaceEvent e;e.input.kind=SurfaceInput::Kind::Button;e.input.index=uint8_t(b);e.input.pressed=down;shell.surface(e,++now);};
    auto tap=[&](SurfaceButton b){button(b,true);button(b,false);};
    auto back=[&]{button(SurfaceButton::Shift,true);tap(SurfaceButton::WheelPush);button(SurfaceButton::Shift,false);};
    auto reset=[&](PageId page,EngineKind engine,bool full=false){c.ui=UiState{};c.ui.settings.full_features=full;c.project.tracks[0]=Track{};load_sound(c.project.tracks[0],engine,0);c.edits.clear();c.dirty=false;c.settings_save_at=0;c.open(page);};
    auto save=[&](const std::string& n){if(capture)capture(shell,n);};
    auto keys=[&]{auto s=std::make_unique<Snapshot>();shell.snapshot(*s,now);return mix_keys(*s);};
    for(auto engine:{EngineKind::None,EngineKind::Sampler,EngineKind::Keygroup,EngineKind::Plugin,EngineKind::Midi,EngineKind::Audio}) {
        for(auto page:{PageId::Tracks,PageId::Rack,PageId::Bus,PageId::Master,PageId::PadFx}) {
            if(page==PageId::PadFx && engine!=EngineKind::Sampler)continue;
            reset(page,engine);SEND_CHECK(keys().labels[1]=="SENDS","BASIC displays SENDS on every MIX page");
            const auto original=save_project(shell.project(),shell.patterns());tap(SurfaceButton::TopMiddle);
            SEND_CHECK(c.ui.ask==UiState::Ask::EnableFullSends && c.ui.ask_pick==0 && c.ui.page==page,"BASIC B2 opens confirmation with CANCEL selected");
            SEND_CHECK(!c.ui.settings.full_features && !c.settings_save_at,"opening prompt does not enable or save settings");
            tap(SurfaceButton::TopLeft);SEND_CHECK(c.ui.ask==UiState::Ask::None && c.ui.page==page && !c.ui.settings.full_features,"CANCEL preserves BASIC and caller");
            tap(SurfaceButton::TopMiddle);tap(SurfaceButton::WheelPush);SEND_CHECK(c.ui.ask==UiState::Ask::None && !c.ui.settings.full_features,"encoder default cancels");
            tap(SurfaceButton::TopMiddle);c.ui.ask_pick=2;back();SEND_CHECK(c.ui.ask==UiState::Ask::None&&!c.ui.settings.full_features&&c.ui.page==page,"SHIFT+push cancels even with ENABLE FULL selected");
            tap(SurfaceButton::TopMiddle);
            for(unsigned k=0;k<3;++k){SurfaceEvent e;e.input.kind=SurfaceInput::Kind::Control;e.input.index=uint8_t(unsigned(SurfaceControl::K1)+k);e.input.value=127;shell.surface(e,++now);}
            SEND_CHECK(original==save_project(shell.project(),shell.patterns())&&!c.ui.settings.full_features,"pots wait while mode confirmation is open");
            tap(SurfaceButton::TopLeft);
            tap(SurfaceButton::TopMiddle);tap(SurfaceButton::TopMiddle);SEND_CHECK(c.ui.ask==UiState::Ask::EnableFullSends&&!c.ui.settings.full_features,"B2 cannot accidentally confirm");
            tap(SurfaceButton::Play);tap(SurfaceButton::Stop);SEND_CHECK(c.ui.ask==UiState::Ask::EnableFullSends,"transport retains confirmation");
            tap(SurfaceButton::TopRight);SEND_CHECK(c.ui.settings.full_features&&c.ui.ask==UiState::Ask::None&&c.ui.page==PageId::Sends&&!c.ui.sends_pads,"ENABLE FULL opens track Sends");
            SEND_CHECK(c.settings_save_at>0&&!c.dirty,"native setting persistence is scheduled without dirtying project");
            Settings restored;restored.read(c.ui.settings.text());SEND_CHECK(restored.full_features,"FULL survives native setting text roundtrip");
            SEND_CHECK(original==save_project(shell.project(),shell.patterns()),"mode change preserves complete project and patterns");
            for(unsigned bus=0;bus<bus_count;++bus){SEND_CHECK(c.ui.sends_bus==bus,"A-D bus selection unchanged");tap(SurfaceButton::Plus);}
            SEND_CHECK(c.ui.sends_bus==0,"D wraps to A");
            if(engine==EngineKind::Sampler){tap(SurfaceButton::TopMiddle);SEND_CHECK(c.ui.sends_pads,"native sampler pad sends cycle preserved");tap(SurfaceButton::TopMiddle);SEND_CHECK(!c.ui.sends_pads,"native sampler returns to track sends");}
            c.open(page);tap(SurfaceButton::TopMiddle);SEND_CHECK(c.ui.page==PageId::Sends&&c.ui.ask==UiState::Ask::None,"FULL B2 opens directly without prompt");
        }
    }
    reset(PageId::Tracks,EngineKind::Sampler);tap(SurfaceButton::TopLeft);SEND_CHECK(c.ui.page==PageId::TrackActions&&c.ui.ask==UiState::Ask::None,"B1 TRACK SETUP preserved");
    reset(PageId::Tracks,EngineKind::Sampler);tap(SurfaceButton::TopRight);SEND_CHECK(c.ui.page==PageId::Rack&&c.ui.ask==UiState::Ask::None,"B3 FX preserved");
    for(int key=1;key<=2;++key){reset(PageId::Tracks,EngineKind::Sampler);button(SurfaceButton::Shift,true);tap(key==1?SurfaceButton::TopMiddle:SurfaceButton::TopRight);button(SurfaceButton::Shift,false);SEND_CHECK(c.ui.copying==UiState::Copying::Tracks&&c.ui.moving==(key==1)&&c.ui.ask==UiState::Ask::None,"SHIFT MOVE/COPY preserve priority");}
    for(int key=1;key<=2;++key){reset(PageId::Tracks,EngineKind::Sampler);button(SurfaceButton::PadBank,true);tap(key==1?SurfaceButton::TopMiddle:SurfaceButton::TopRight);button(SurfaceButton::PadBank,false);SEND_CHECK(c.ui.copying==UiState::Copying::Tracks&&c.ui.moving==(key==1)&&c.ui.ask==UiState::Ask::None,"PAD BANK MOVE/COPY preserve priority");}
    reset(PageId::Sends,EngineKind::Sampler);tap(SurfaceButton::TopMiddle);SEND_CHECK(c.ui.sends_pads&&!c.ui.settings.full_features&&c.ui.ask==UiState::Ask::None,"already-open Sends keeps native Basic pad cycle");
    reset(PageId::Tracks,EngineKind::Sampler);tap(SurfaceButton::NoteRepeat);SEND_CHECK(c.track().repeat,"Note Repeat starts");const auto rate=c.track().repeat_rate;tap(SurfaceButton::TopMiddle);SEND_CHECK(c.track().repeat_rate==repeat_next(rate,1,false)&&c.ui.ask==UiState::Ask::None&&c.ui.page==PageId::Tracks,"repeat rate B2 precedes Sends");tap(SurfaceButton::NoteRepeat);tap(SurfaceButton::TopMiddle);SEND_CHECK(c.ui.ask==UiState::Ask::EnableFullSends,"turning repeat off restores B2 prompt");
    reset(PageId::Tracks,EngineKind::Sampler);c.ui.lesson=4;tap(SurfaceButton::TopMiddle);SEND_CHECK(c.ui.ask==UiState::Ask::None&&!c.ui.settings.full_features&&c.ui.page==PageId::Tracks,"lesson restriction never bypassed");
    reset(PageId::Tracks,EngineKind::Sampler);tap(SurfaceButton::TopMiddle);c.ui.lesson=4;tap(SurfaceButton::TopRight);SEND_CHECK(!c.ui.settings.full_features&&c.ui.page==PageId::Tracks,"lesson starting during prompt blocks enable");
    reset(PageId::Tracks,EngineKind::Sampler);tap(SurfaceButton::TopMiddle);c.ui.page=PageId::Stage;tap(SurfaceButton::TopRight);SEND_CHECK(!c.ui.settings.full_features&&c.ui.page==PageId::Stage,"stale prompt cannot change another page");
    reset(PageId::Tracks,EngineKind::Sampler);save("01-basic-tracks");tap(SurfaceButton::TopMiddle);save("02-enable-full");tap(SurfaceButton::TopRight);save("03-sends-A");tap(SurfaceButton::Plus);save("04-sends-B");c.open(PageId::Tracks);save("05-full-tracks");
    std::cout<<"SENDS_ACCESS_OK checks="<<checks<<" engines=6 cancel,back,repeat,shift,lessons,persistence,project,buses=ok\n";
#undef SEND_CHECK
    return 0;
}
} // namespace rhythmer
