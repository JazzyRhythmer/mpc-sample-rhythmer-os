// SPDX-License-Identifier: AGPL-3.0-only
#pragma once
#include "rhythmer/shell/new_track.h"
#include "rhythmer/shell/ask.h"
#include "rhythmer/plugin/plugin_files.h"
#include "rhythmer/shell/track_copy.h"

namespace rhythmer {
inline int track_workflow_check() {
    unsigned checks=0;
    auto require=[&](bool ok,const char* what){++checks;if(!ok)std::fprintf(stderr,"TRACK_WORKFLOW FAIL %u: %s\n",checks,what);return ok;};
#define TRACK_CHECK(x,what) do {if(!require((x),what))return 1;}while(false)
    EngineHost host;Shell shell(host);auto& c=shell.context();
    auto press=[&](SurfaceButton b,bool down){SurfaceEvent e;e.input.kind=SurfaceInput::Kind::Button;e.input.index=uint8_t(b);e.input.pressed=down;shell.surface(e,2000+checks);};
    c.ui.track=0;c.ui.page=PageId::Stage;
    c.load_sound(0,EngineKind::Midi,0);c.track().mix.level=77;c.track().mix.pan=-12;c.track().pattern=73;
    for(unsigned n=0;n<pattern_count;++n){Event e;e.tick=n;e.key=uint8_t(36+n%60);c.patterns.at[0][n].events={e};}
    auto before=c.patterns.at[0];
    auto patterns_kept=[&]{return c.patterns.at[0]==before;};
    c.open(PageId::Tracks);tracks_page.push(c);
    TRACK_CHECK(c.ui.page==PageId::Stage && patterns_kept(),"used track encoder still opens its sound");
    c.open(PageId::Tracks);
    tracks_page.soft(c,0);
    TRACK_CHECK(c.ui.page==PageId::TrackActions,"TRACKS exposes actions");
    c.ui.track_action=1;track_actions_page.push(c);
    TRACK_CHECK(c.ui.track_types,"type submenu");
    c.back();TRACK_CHECK(!c.ui.track_types && c.ui.page==PageId::TrackActions,"Back leaves submenu first");
    c.ui.track_types=true;c.ui.track_action=1;track_actions_page.push(c);
    TRACK_CHECK(c.track().engine==EngineKind::Sampler && patterns_kept(),"MIDI to kit retains all 128 patterns");
    TRACK_CHECK(c.track().pattern==73 && c.track().mix.level==77 && c.track().mix.pan==-12,"selected pattern and mix survive");
    TRACK_CHECK(c.ui.page==PageId::Stage && c.ui.back_depth==0,"successful conversion lands on track, no stale menu");
    c.undo();TRACK_CHECK(c.track().engine==EngineKind::Midi && patterns_kept(),"type undo");
    c.redo();TRACK_CHECK(c.track().engine==EngineKind::Sampler && patterns_kept(),"type redo");
    change_track_type(c,EngineKind::None);TRACK_CHECK(!c.track().used() && patterns_kept(),"empty retains patterns");
    TRACK_CHECK(c.ui.page==PageId::Stage && c.ui.new_for==0 && c.ui.new_pick==uint8_t(NewChoice::Plugin),"intentional EMPTY opens native type carousel");
    c.open(PageId::Tracks);tracks_page.push(c);
    TRACK_CHECK(c.ui.page==PageId::Stage && c.ui.new_for==0 && patterns_kept(),"intentional EMPTY encoder opens type selection, not actions");
    c.ui.page=PageId::Edit;edit_page.push(c);
    TRACK_CHECK(c.ui.page==PageId::Stage && c.ui.new_for==0 && patterns_kept(),"EMPTY stranded on Edit opens type selection");
    c.open(PageId::Tracks);tracks_page.soft(c,0);
    TRACK_CHECK(c.ui.page==PageId::TrackActions,"EMPTY actions still require B1");
    c.open(PageId::Stage);
    TRACK_CHECK(!new_track_lock(c,SurfaceButton::Minus,true),"empty track permits Undo");
    TRACK_CHECK(!new_track_lock(c,SurfaceButton::TopMiddle,true) && !new_track_lock(c,SurfaceButton::TopRight,true),"visible KIT/MIDI empty-track buttons are enabled");
    TRACK_CHECK(!new_track_lock(c,SurfaceButton::WheelPush,true),"empty browser permits Back");
    press(SurfaceButton::Shift,true);press(SurfaceButton::Minus,true);press(SurfaceButton::Minus,false);press(SurfaceButton::Shift,false);
    TRACK_CHECK(c.track().engine==EngineKind::Sampler,"physical Shift-Minus restores empty track");
    open_track_actions(c);c.ui.track_action=4;track_actions_page.push(c);
    TRACK_CHECK(c.ui.ask==UiState::Ask::ClearTrack && patterns_kept(),"delete requires confirmation");
    ask_button(c,SurfaceButton::TopLeft);TRACK_CHECK(c.track().used() && patterns_kept(),"cancel delete is non-destructive");
    c.ui.track_action=4;track_actions_page.push(c);ask_button(c,SurfaceButton::TopRight);
    bool clear=true;for(const auto& p:c.patterns.at[0])clear &= p.events.empty();
    TRACK_CHECK(!c.track().used() && clear && c.ui.page==PageId::Stage,"confirmed delete clears all patterns and lands empty");
    c.undo();TRACK_CHECK(c.track().engine==EngineKind::Sampler && patterns_kept(),"delete undo restores sound and patterns");
    c.ui.recording=true;change_track_type(c,EngineKind::Midi);TRACK_CHECK(c.track().engine==EngineKind::Sampler,"recording guard");c.ui.recording=false;
    c.prints.freeze[0].state=FreezeState::Frozen;change_track_type(c,EngineKind::Midi);
    TRACK_CHECK(c.track().engine==EngineKind::Sampler && c.ui.ask==UiState::Ask::Unfreeze,"freeze guard");c.ui.ask=UiState::Ask::None;c.prints.freeze[0]={};
    const PageId owned[]={PageId::PluginPresets,PageId::Plugins,PageId::Samples,PageId::Sounds,PageId::Edit,PageId::Chop,PageId::PadPage,PageId::LayersPage,PageId::Print,PageId::TrackActions};
    for(auto page:owned){c.ui.track=0;c.ui.page=page;c.ui.presets_back=PageId::Stage;c.ui.plugin_target=UiState::PluginTarget::Instrument;c.ui.sheet_open=true;
        c.select_track(1);TRACK_CHECK(c.ui.track==1 && c.ui.page==PageId::Stage && !c.ui.sheet_open,"track-owned screen follows selected track");
        c.back();TRACK_CHECK(c.ui.page==PageId::Stage,"Back cannot resurrect previous track's browser");}
    c.ui.track=0;c.ui.page=PageId::PluginPresets;c.ui.presets_back=PageId::Bus;c.select_track(1);
    TRACK_CHECK(c.ui.page==PageId::PluginPresets,"bus preset list remains global");
    c.ui.back_depth=1;c.ui.back_stack[0]=PageId::Bus;c.select_track(2);c.back();
    TRACK_CHECK(c.ui.page==PageId::Bus,"global Back retains bus owner");
    c.ui.page=PageId::Plugins;c.ui.plugin_target=UiState::PluginTarget::Effect;c.ui.plugin_chain=track_count;c.select_track(2);
    TRACK_CHECK(c.ui.page==PageId::Plugins,"bus effect picker remains global");
    c.ui.track=0;c.ui.page=PageId::PluginPresets;c.ui.presets_back=PageId::Edit;c.select_track(1);offer_new_track(c);make_new_track(c,NewChoice::Kit);
    TRACK_CHECK(c.ui.track==1 && c.ui.page==PageId::Stage && c.track().engine==EngineKind::Sampler,"preset A to empty B to kit B");
    c.ui.track=0;c.ui.page=PageId::PluginPresets;c.ui.presets_back=PageId::Stage;
    SurfaceEvent button;button.input.kind=SurfaceInput::Kind::Button;button.input.index=uint8_t(SurfaceButton::PadBank);button.input.pressed=true;shell.surface(button,1000);
    SurfaceEvent hit;hit.pad=8;hit.midi.status=0x90;hit.midi.key=8;hit.midi.value=100;shell.surface(hit,1001);
    hit.midi.status=0x80;hit.midi.value=0;shell.surface(hit,1002);button.input.pressed=false;shell.surface(button,1003);
    TRACK_CHECK(c.ui.track==8 && c.ui.page==PageId::Stage,"physical PAD BANK plus pad follows new track");
    c.ui.track=3;c.ui.page=PageId::Plugins;c.ui.plugin_target=UiState::PluginTarget::Instrument;c.track().engine=EngineKind::None;
    TRACK_CHECK(!new_track_lock(c,SurfaceButton::PadBank,true),"empty plug-in picker permits track switching");
    // Async whole-kit load belongs to the original target, never whichever track is selected later.
    auto source=std::make_unique<Project>();source->tracks[0].engine=EngineKind::Sampler;source->tracks[0].set_name("TEST KIT");
    source->tracks[0].pads[0].sample=0;std::strcpy(source->samples[0].path,"Samples/workflow.wav");
    c.project.samples[0]=source->samples[0];
    c.ui.track=4;c.project.tracks[4].engine=EngineKind::Midi;c.kit_target=5;c.load_kit(*source,"TEST KIT");
    TRACK_CHECK(c.ui.track==4 && c.project.tracks[4].engine==EngineKind::Midi && c.project.tracks[5].engine==EngineKind::Sampler,"async kit target captured");
    BankFile bank;bank.pads[0].sample=0;std::strcpy(bank.samples[0].path,"Samples/workflow.wav");
    c.project.tracks[7]=Track{};c.project.tracks[7].engine=EngineKind::Sampler;c.project.tracks[7].bank=1;
    c.bank_target=7;c.bank_target_bank=3;c.load_bank(bank,"ASYNC BANK");
    TRACK_CHECK(c.ui.track==4 && c.project.tracks[7].pads[48].used() && !c.project.tracks[7].pads[16].used(),"async bank retains original track AND bank");
    c.kit_target=4;c.bank_target=4;auto restored=std::make_unique<TrackState>(track_state(c,4));restore_track(c,4,*restored);
    TRACK_CHECK(c.kit_target==-2 && c.bank_target==-2,"whole-track undo/replacement invalidates late loads");
    c.kit_target=-2;c.load_kit(*source,"TEST KIT");TRACK_CHECK(c.project.tracks[4].engine==EngineKind::Midi,"invalidated request discarded");
    c.ui.track=4;c.ui.break_pending=0;c.ui.break_pending_b=true;c.ui.break_track=5;c.ui.break_bars=2;c.project.tracks[5].break_bars=2;c.project.samples[0].frames=176400;
    c.gen_break_tick();TRACK_CHECK(c.ui.track==4,"Break B completion does not steal selected track");
    if(const char* card=std::getenv("RHYTHMER_GEN_CARD")){
        PluginRack rack(host);rack.set_card(card);c.plugins=&rack;
        auto files=list_plugins(plugin_folder(card));
        auto file=[&](const char* name){return std::find_if(files.begin(),files.end(),[&](const PluginFile& f){return f.name==name;});};
        auto first=file("FM-106"),second=file("Sophie"),br=file("Break Engine");
        TRACK_CHECK(first!=files.end() && second!=files.end() && br!=files.end(),"real plugin fixture available");
        auto wait=[&]{for(unsigned n=0;n<2000;++n){if(rack.status(c.track().plugin)==PluginStatus::Ready)return true;std::this_thread::sleep_for(std::chrono::milliseconds(10));}return false;};
        c.ui.track=0;c.ui.page=PageId::Stage;c.ui.plugin_target=UiState::PluginTarget::Instrument;c.choose_plugin(*first);
        TRACK_CHECK(c.track().engine==EngineKind::Plugin && wait() && patterns_kept(),"load real plugin over kit, keep patterns");
        auto entry=c.track().plugin;auto old_ref=c.project.plugins[entry];auto old_state=rack.states()[entry];
        c.open_plugin_presets(entry);TRACK_CHECK(c.ui.page==PageId::PluginPresets,"native preset list opens from Stage");
        plugin_presets_page.soft(c,1);TRACK_CHECK(c.ui.page==PageId::Plugins,"preset list exposes replacement");
        c.choose_plugin(*second);TRACK_CHECK(wait() && c.ui.page==PageId::Stage && c.ui.back_depth==0 && patterns_kept(),"replacement lands at selected track");
        c.undo();bool undo_ready=wait();auto restored_state=rack.states()[entry];
        if(!undo_ready || std::strcmp(c.project.plugins[entry].path,old_ref.path) || restored_state!=old_state){
            std::fprintf(stderr,"BEFORE %.180s\nAFTER %.180s\n",std::string(old_state.begin(),old_state.end()).c_str(),std::string(restored_state.begin(),restored_state.end()).c_str());
            size_t diff=0;while(diff<restored_state.size()&&diff<old_state.size()&&restored_state[diff]==old_state[diff])++diff;
            std::fprintf(stderr,"UNDO detail ready=%d old=%s actual=%s old_bytes=%zu new_bytes=%zu first_diff=%zu notice=%s\n",undo_ready,old_ref.path,c.project.plugins[entry].path,old_state.size(),restored_state.size(),diff,c.ui.notice);
        }
        TRACK_CHECK(undo_ready && std::strcmp(c.project.plugins[entry].path,old_ref.path)==0 && restored_state==old_state,"replacement undo restores original plugin and sound state");
        c.redo();TRACK_CHECK(wait() && std::strcmp(c.project.plugins[entry].name,"Sophie")==0,"replacement redo");
        auto plugin_state=rack.states()[c.track().plugin];
        change_track_type(c,EngineKind::Midi);TRACK_CHECK(c.track().engine==EngineKind::Midi && patterns_kept(),"plugin to MIDI keeps sequence");
        c.undo();TRACK_CHECK(c.track().engine==EngineKind::Plugin && wait() && rack.states()[c.track().plugin]==plugin_state,"type undo restores real plugin state");
        auto engine=c.track().engine;auto history=c.edits.size();c.choose_plugin(*br);
        TRACK_CHECK(c.track().engine==engine && c.edits.size()==history && c.ui.break_browse,"choosing Break defers destructive conversion");
        samples_page.soft(c,0);TRACK_CHECK(c.track().engine==engine && c.ui.page==PageId::Plugins,"Break browser cancel preserves instrument");
        c.ui.track=0;c.ui.page=PageId::PluginPresets;c.ui.presets_back=PageId::Stage;c.select_track(6);offer_new_track(c);make_new_track(c,NewChoice::Plugin);c.choose_plugin(*first);
        TRACK_CHECK(c.ui.track==6 && c.ui.page==PageId::Stage && wait(),"preset A to empty B to plugin B");
        c.back();TRACK_CHECK(c.ui.page==PageId::Stage,"loaded B Back cannot return to A");
        c.plugins=nullptr;
    }else {std::fprintf(stderr,"TRACK_WORKFLOW: missing real plugin card fixture\n");return 2;}
    std::printf("TRACK_WORKFLOW passed %u assertions; 128-pattern retention, real plugins, undo/redo, scoped navigation, async ownership\n",checks);
#undef TRACK_CHECK
    return 0;
}
} // namespace rhythmer
