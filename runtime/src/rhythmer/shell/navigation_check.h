// SPDX-License-Identifier: AGPL-3.0-only
#pragma once
#include "rhythmer/shell/menu.h"
#include "rhythmer/shell/new_track.h"
#include "rhythmer/shell/ask.h"
#include "rhythmer/shell/track_copy.h"
#include "rhythmer/shell/name_entry.h"
#include "rhythmer/shell/sample_library.h"
#include <cstdio>
#include <cstring>
namespace rhythmer {
inline int navigation_check(){
    auto ho=std::make_unique<EngineHost>();auto so=std::make_unique<Shell>(*ho);auto& shell=*so;auto& c=shell.context();
    unsigned checks=0,contexts=0,protected_pages=0;uint32_t now=10000;
#define NAV(x,msg) do{++checks;if(!(x)){std::fprintf(stderr,"NAVIGATION FAIL %u: %s page=%u engine=%u\n",checks,msg,unsigned(c.ui.page),unsigned(c.track().engine));return 1;}}while(false)
    auto button=[&](SurfaceButton b,bool down){SurfaceEvent e;e.input.kind=SurfaceInput::Kind::Button;e.input.index=uint8_t(b);e.input.pressed=down;shell.surface(e,++now);};
    auto tap=[&](SurfaceButton b){button(b,true);button(b,false);};
    auto back=[&]{button(SurfaceButton::Shift,true);tap(SurfaceButton::WheelPush);button(SurfaceButton::Shift,false);};
    auto reset=[&](PageId page,EngineKind engine,bool full=true){
        c.ui=UiState{};c.ui.page=page;c.ui.settings.full_features=full;c.edits.clear();c.prints=PrintTable{};
        c.project.tracks[0]=Track{};rhythmer::load_sound(c.project.tracks[0],engine,0);
        c.project.tracks[1]=Track{};rhythmer::load_sound(c.project.tracks[1],EngineKind::Midi,0);
        c.project.tracks[0].plugin=0;std::strcpy(c.project.plugins[0].name,"Sophie");
        c.project.tracks[0].pads[0].sample=0;c.project.samples.edit(0).frames=176400;
        c.patterns.at[0][0]=Pattern{};Event e;e.key=55;e.length=24;e.velocity=100;c.patterns.at[0][0].add(e);
    };
    for(bool full:{false,true})for(auto engine:{EngineKind::None,EngineKind::Sampler,EngineKind::Keygroup,EngineKind::Plugin,EngineKind::Midi,EngineKind::Audio})for(unsigned p=0;p<unsigned(PageId::Count);++p){
        for(bool go:{false,true}){
            reset(PageId(p),engine,full);menu_open(c);
            if(!c.ui.menu){++protected_pages;continue;}
            std::array<MenuItem,menu_here_max> items{};unsigned count=menu_here(c.project,c.ui,items);
            NAV(count<=menu_here_max,"HERE capacity");
            for(unsigned i=0;i<count;++i){NAV(items[i].name&&items[i].name[0],"visible HERE label");for(unsigned j=0;j<i;++j)NAV(std::strcmp(items[i].name,items[j].name)!=0,"HERE labels unique");}
            c.ui.menu=go?menu_go_view:count?menu_here_view:menu_go_view;
            c.ui.menu_row=uint8_t(count?count-1:0); // often the destructive action: Back must not select it
            c.ui.menu_tile=uint8_t(menu_tile_of(PageId(p)==PageId::SettingsPage?PageId::Tempo:PageId::SettingsPage));
            const auto before=c.patterns.at[0][0];const auto pushes=c.edits.pushes;const auto page=c.ui.page;
            back();
            NAV(!c.ui.menu&&c.ui.page==page,"physical Menu Back preserves caller");
            NAV(c.ui.ask==UiState::Ask::None&&!c.ui.sheet_open&&c.ui.copying==UiState::Copying::Off,"Back never dispatches HERE action");
            NAV(c.edits.pushes==pushes&&c.patterns.at[0][0]==before&&c.track().engine==engine,"Menu Back changes no sound or pattern");
            menu_open(c);c.back();NAV(!c.ui.menu&&c.ui.page==page,"direct Back shares Menu hierarchy");++contexts;
        }
    }
    // Menu opened over a custom generator closes first; then engine GEN -> GEN -> PATTERNS.
    for(unsigned mode:{0u,1u,2u,3u,4u})for(bool full:{false,true}){
        reset(PageId::Patterns,mode==2?EngineKind::Sampler:EngineKind::Plugin,full);
        if(mode==2)c.track().break_bars=2;
        if(mode==4)std::strcpy(c.project.plugins[0].name,"Acid Engine");
        c.ui.sheet_open=true;c.ui.gen8_mode=uint8_t(mode);c.ui.back_depth=1;c.ui.back_stack[0]=PageId::Stage;
        menu_open(c);back();NAV(c.ui.sheet_open&&c.ui.gen8_mode==mode&&c.ui.page==PageId::Patterns,"Menu Back keeps GEN context");
        if(mode){back();NAV(c.ui.sheet_open&&c.ui.gen8_mode==0,"sub GEN Back -> main GEN");}
        back();NAV(!c.ui.sheet_open&&c.ui.page==PageId::Patterns,"main GEN Back -> PATTERNS");
        back();NAV(c.ui.page==PageId::Stage,"PATTERNS returns to sound caller");
    }
    reset(PageId::Scenes,EngineKind::Midi);menu_open(c);std::array<MenuItem,menu_here_max> items{};auto n=menu_here(c.project,c.ui,items);unsigned gen=n;
    for(unsigned i=0;i<n;++i)if(items[i].job==MenuJob::Generate)gen=i;
    NAV(gen<n,"SEQUENCES has visible GEN route");c.ui.menu_row=uint8_t(gen);tap(SurfaceButton::WheelPush);
    NAV(c.ui.page==PageId::Patterns&&c.ui.sheet_open&&!c.ui.gen8_mode,"HERE GEN opens main generator");back();NAV(c.ui.page==PageId::Patterns&&!c.ui.sheet_open,"HERE GEN Back closes generator");
    reset(PageId::Stage,EngineKind::Sampler);
    NAV(!stage_skips(stage_groups(c.track().engine),0,0,stage_skip(c.project,c.ui,c.track())),"normal SOUND filter page remains visible");
    c.ui.lesson=4;stage_go(c.ui,c.track().engine,StageKind::Trim);
    NAV(stage_page_now(c.ui,c.track(),stage_skip(c.project,c.ui,c.track())).kind==StageKind::Trim,"lesson begins on TRIM");
    stage_press(c.ui,c.track(),0,stage_skip(c.project,c.ui,c.track()));
    NAV(stage_page_now(c.ui,c.track(),stage_skip(c.project,c.ui,c.track())).kind==StageKind::Tune,"lesson B1 reaches TUNE");
    // Track-scoped questions must never act on a newly selected track.
    for(auto ask_kind:{UiState::Ask::ClearPattern,UiState::Ask::ClearTrack,UiState::Ask::EraseLane,UiState::Ask::EraseKeyEvents,UiState::Ask::Unfreeze,UiState::Ask::BreakLength,UiState::Ask::ReplacePlugin}){
        reset(PageId::Patterns,EngineKind::Midi);c.ui.plugin_target=UiState::PluginTarget::Instrument;ask(c,ask_kind,0);if(ask_kind==UiState::Ask::BreakLength)c.ui.break_pending=0;
        auto old=c.patterns.at[0][0];c.select_track(1);NAV(c.ui.ask==UiState::Ask::None&&c.ui.track==1,"track change cancels old question");NAV(c.patterns.at[0][0]==old,"question cancellation preserves old pattern");
        if(ask_kind==UiState::Ask::BreakLength)NAV(c.ui.break_pending<0,"cancelled length question cannot commit later");
    }
    reset(PageId::PluginPresets,EngineKind::Midi);c.ui.presets_back=PageId::Bus;c.ui.plugin_target=UiState::PluginTarget::Effect;c.ui.plugin_chain=track_count;ask(c,UiState::Ask::ReplacePlugin,0);c.select_track(1);
    NAV(c.ui.page==PageId::PluginPresets&&c.ui.ask==UiState::Ask::ReplacePlugin,"global bus workflow remains global");ask_button(c,SurfaceButton::TopLeft);
    // A tap delayed until release cannot act on a different track/page.
    reset(PageId::Stage,EngineKind::Sampler);button(SurfaceButton::WheelPush,true);c.select_track(1);button(SurfaceButton::WheelPush,false);NAV(c.ui.page==PageId::Stage&&!c.ui.track_types,"old encoder tap cannot enter new track");
    reset(PageId::Stage,EngineKind::Sampler);button(SurfaceButton::WheelPush,true);c.open(PageId::Tracks);button(SurfaceButton::WheelPush,false);NAV(c.ui.page==PageId::Tracks,"old encoder tap cannot activate new page");
    reset(PageId::Stage,EngineKind::Sampler);c.open_name(NameTarget::Scene,"CHANGED",16,false);std::string scene=c.project.scenes[0].name;back();NAV(!c.ui.name.open()&&scene==c.project.scenes[0].name,"name Back cancels rather than saves");
    reset(PageId::Stage,EngineKind::Sampler);c.ui.exit_open=true;c.ui.exit_pick=2;back();NAV(!c.ui.exit_open&&!c.ui.exit_off,"exit Back never leaves for stock app");
    // Empty chooser has a real escape, retaining caller before select_track clears ownership.
    reset(PageId::Stage,EngineKind::None);c.ui.new_for=0;c.ui.new_back=PageId::Tracks;back();NAV(c.ui.page==PageId::Tracks&&c.ui.track==1,"empty cancel restores TRACKS caller");
    reset(PageId::Stage,EngineKind::None);for(auto& t:c.project.tracks)t.engine=EngineKind::None;c.ui.new_for=0;c.ui.new_back=PageId::Stage;back();NAV(c.ui.page==PageId::Tracks,"all-empty chooser can return to TRACKS");
    reset(PageId::Stage,EngineKind::None);c.ui.new_for=0;c.ui.new_sources=true;back();NAV(c.ui.page==PageId::Stage&&!c.ui.new_sources,"source step Back -> type step");
    // Note Repeat retains its approved contextual B1 priority.
    reset(PageId::Tracks,EngineKind::Midi);c.track().repeat=true;c.track().repeat_rate=7;tap(SurfaceButton::TopLeft);NAV(c.ui.page==PageId::Tracks&&c.track().repeat_rate!=7,"NOTE REPEAT retains speed softkeys");c.track().repeat=false;tap(SurfaceButton::TopLeft);NAV(c.ui.page==PageId::TrackActions,"B1 otherwise opens TRACK SETUP");
    reset(PageId::Tracks,EngineKind::Midi);c.ui.recording=true;change_track_type(c,EngineKind::Sampler);NAV(c.track().engine==EngineKind::Midi,"recording protects type change");c.ui.recording=false;c.prints.freeze[0].state=FreezeState::Frozen;change_track_type(c,EngineKind::Sampler);NAV(c.ui.ask==UiState::Ask::Unfreeze&&c.track().engine==EngineKind::Midi,"frozen type change asks first");back();NAV(c.ui.ask==UiState::Ask::None,"frozen question Back cancels");
    // Track replacement/move invalidates late jobs; merely selecting a track does not.
    reset(PageId::Stage,EngineKind::Sampler);auto epoch=c.track_epoch[0];c.select_track(1);NAV(c.track_epoch[0]==epoch,"track focus leaves job owner valid");c.ui.track=0;c.pending_files[0].slot=0;c.pending_files[0].track=0;c.ui.stems_sheet.running=true;c.stems_from.track=0;
    auto replacement=std::make_unique<TrackState>(track_state(c,0));restore_track(c,0,*replacement);NAV(c.track_epoch[0]!=epoch&&c.pending_files[0].slot<0&&!c.ui.stems_sheet.running,"replace invalidates late loads/stems");epoch=c.track_epoch[0];trade_tracks(c,0,1);NAV(c.track_epoch[0]!=epoch,"move/swap invalidates old job destination");
    {SampleLibrary library(*ho);SampleLibrary::StemsRequest request;NAV(library.separate(request),"first stems request accepted");NAV(!library.separate(request),"queued/running result owns stems slot");library.stop_stems();NAV(!library.separate(request),"cancelled request remains owned until result consumed");}
    std::printf("RHYTHMER_NAVIGATION contexts=%u assertions=%u protected_pages=%u pages=%u Basic_Full=ok menu_back=ok GEN_hierarchy=ok dialogs=owned stale_taps=blocked empty_escape=ok repeat_priority=kept async_destinations=guarded\n",contexts,checks,protected_pages,unsigned(PageId::Count));
#undef NAV
    return 0;
}
} // namespace rhythmer
