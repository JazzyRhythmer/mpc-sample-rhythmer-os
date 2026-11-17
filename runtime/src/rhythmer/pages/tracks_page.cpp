// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Kerem Kilic (Ellic Studio)
// TRACKS (the MIX hub's B1: Pad Bank held + B1): the
// sixteen tracks as the pads sit, each with its pattern, engine and level,
// and the track in hand as a strip on the right (pages/track_grid.cpp): its
// fader, meter, pan and send. A pad picks its track; K1 the track, K2 its
// level, K3 its pan; the wheel or Minus / Plus the track, Push its Stage.
// Each cell's bottom edge and the header show what a track takes of a block
// (roadmap P2), so the heavy one is found before it crackles.
// The MIX hub's row (shell/mix_hub.h): B1 TRACKS (here), B2 SENDS, B3 FX. Shift + B2 MOVE, Shift + B3 COPY: then a
// track's pad and where it goes (shell/pad_bank.h, as Pad Bank + Shift + B2 or B3 anywhere).
#include "rhythmer/pages/common.h"
#include "rhythmer/pages/pages.h"
#include "rhythmer/shell/erase_copy.h"
#include "rhythmer/shell/ask.h"
#include "rhythmer/shell/project_store.h"
#include "rhythmer/ui/widgets.h"
#include "rhythmer/shell/new_track.h"
#include "rhythmer/shell/features.h"
#include "rhythmer/shell/sample_library.h"
#include "rhythmer/shell/stage_map.h"
#include "rhythmer/shell/pad_bank.h"
#include <cmath>

namespace rhythmer {
namespace {
using namespace ui;

void draw(Paint& p, const Snapshot& s) {
    Header h = header_of(s);
    // Freeze plan F2c: the share of each block in use, all tracks together (what freezing brings down), first.
    float all = s.machine.render_load;
    h.left.push_back(pill(Icon::Chip, "CPU " + juce::String(int(std::lround(all * 100))) + " %", load_colour(all)));
    if (s.track().speed != speed_normal) // the strip in hand plays its patterns at a speed (Shift + K1, roadmap P1)
        h.left.push_back(pill(juce::String::fromUTF8(speed_name(s.track().speed)), colour_of(s)));
    auto used = pill(juce::String(s.project.used_tracks()) + " USED");
    used.spare = true; // left out before the name when room is short
    h.left.push_back(used);
    float load = s.machine.track_load[s.ui.track % track_count]; // the track in hand's share of a block (roadmap P2)
    if (s.track().used()) {
        const auto& f = s.freeze[s.ui.track % track_count];
        bool frozen = f.frozen();
        h.right.push_back(pill(f.state == FreezeState::Deep ? Icon::DeepSnow : frozen ? Icon::Snow : Icon::Chip, juce::String(int(std::lround(load * 100))) + " %", frozen ? colour::ice : load_colour(load)));
    }
    h.right.push_back(label(s.project.name));
    SoftKeys keys = mix_keys(s);
    keys.labels[0] = "TRACK SETUP";
    if (s.ui.shift) { // Shift: a track moved or copied to another pad
        keys = SoftKeys {{"", "MOVE", "COPY"}, -1, colour_of(s)};
        keys.glyphs[1] = Icon::Swap; keys.glyphs[2] = Icon::Copy;
    }
    frame(p, s, keys, h);
    track_grid(p, s);
}

void pad(Context& c, unsigned pad, uint8_t, bool down) {
    if (!down) return;
    c.select_track(pad % track_count);
    if (c.ui.erase) erase_tap(c); // Erase + pad: that track cleared, once B3 says so (as with Pad Bank held)
    else offer_new_track(c);      // an empty one: its doors, then back here
}

void wheel(Context& c, int delta) { c.select_track(unsigned(int(c.ui.track) + delta + int(track_count)) % track_count); }
void push(Context& c) {
    if (!c.track().used()) { offer_new_track(c); return; } // an empty track: its doors, then back here
    c.open(PageId::Stage);
}

void soft(Context& c, int key) {
    if (c.ui.shift) { // MOVE, COPY: the pads are the tracks until both are picked
        if (key > 0) start_track_pick(c.ui, key == 1);
        return;
    }
    if (key == 0) { open_track_actions(c); return; }
    mix_soft(c, key);
}
unsigned type_count(const UiState& ui) { return full_features(ui) ? 6 : 4; }
unsigned type_index(const UiState& ui, unsigned at) { return !full_features(ui) && at == 3 ? 5 : at; }
void actions_draw(Paint& p, const Snapshot& s) {
    Header h = header_of(s);
    h.left.push_back(chip(s.ui.track_types ? "TRACK TYPE" : "TRACK SETUP",colour_of(s)));
    h.right.push_back(tag_of(s,s.ui.track));
    frame(p,s,{{"BACK","","SELECT"},-1,colour_of(s)},h);
    const char* actions[] = {s.track().sampled()?"LOAD SAMPLE":s.track().engine==EngineKind::Midi?"MIDI DEVICE":s.track().engine==EngineKind::Audio?"AUDIO INPUT":s.track().used()?"CHANGE PLUG-IN":"ADD INSTRUMENT","TRACK TYPE","LOAD MPC KIT","OPEN TRACK","DELETE TRACK"};
    const char* types[] = {"PLUG-IN","SAMPLE KIT","KEYGROUP","MIDI","AUDIO","EMPTY"};
    unsigned count=s.ui.track_types?type_count(s.ui):5;
    for (unsigned i=0;i<count;++i) {
        ListRow row; row.name = s.ui.track_types ? types[type_index(s.ui,i)] : actions[i];
        row.current = std::min<unsigned>(s.ui.track_action,count-1) == i; row.chevron = true; row.accent = colour_of(s);
        list_row(p,zone::pad,zone::picture_y+i*(list_row_h+list_row_gap),zone::width-2*zone::pad,row);
    }
    const char* hint = !s.ui.track_types && s.ui.track_action==4 ? "Removes sound AND all patterns" : "Change sound / type; patterns stay";
    p.text(hint,zone::pad,zone::picture_y+count*(list_row_h+list_row_gap)+4,zone::width-2*zone::pad,16,caps_text(colour::dim),juce::Justification::centred);
}
void actions_wheel(Context& c,int delta) { c.ui.track_action=uint8_t(std::clamp<int>(int(c.ui.track_action)+delta,0,c.ui.track_types?int(type_count(c.ui))-1:4)); }
void actions_push(Context& c) {
    unsigned at=c.ui.track_action;
    if(c.ui.track_types) {
        at=type_index(c.ui,std::min<unsigned>(at,type_count(c.ui)-1));
        static constexpr EngineKind kinds[]={EngineKind::Plugin,EngineKind::Sampler,EngineKind::Keygroup,EngineKind::Midi,EngineKind::Audio,EngineKind::None};
        // A bare kit's direct chooser already has SAMPLE KIT's engine. Start
        // loading its first pad instead of returning to the same empty prompt.
        if (at%6==1 && c.track().engine==EngineKind::Sampler && back_target(c.ui)==PageId::Stage) {
            if(c.ui.recording || c.host_recording()){c.notice("Finish recording first");return;}
            if(c.frozen_edit(c.ui.track))return;
            c.ui.track_types=false;c.ui.layer_load=-1;c.ui.break_browse=false;
            c.open(PageId::Stage);c.open(PageId::Samples);
            if(c.library)c.library->rescan();
            return;
        }
        change_track_type(c,kinds[at%6]); return;
    }
    if(at==1 || (at==0 && !c.track().used())) {c.ui.track_types=true;c.ui.track_action=0;return;}
    if(at==3) {c.open(PageId::Stage);return;}
    if(c.ui.recording || c.host_recording()) {c.notice("Finish recording first");return;}
    if(c.frozen_edit(c.ui.track))return;
    if(at==4) {ask(c,UiState::Ask::ClearTrack,c.ui.track);return;}
    if(at==2) {c.open(PageId::Project);c.ui.project_kit_only=true;c.ui.project_list=true;
        if(c.store)c.store->list(c.project_folder);
        return;
    }
    if(c.track().engine==EngineKind::Plugin)c.open_plugin_picker(UiState::PluginTarget::Instrument);
    else if(c.track().sampled())c.open(PageId::Samples);
    else if(c.track().engine==EngineKind::Audio){c.open(PageId::Stage);stage_go(c.ui,1,0);}
    else {c.open(PageId::Stage);stage_go(c.ui,0,0);c.notice("MIDI: DEVICE sets port/channel");}
}
void actions_soft(Context& c,int key) {
    if(key==0) c.back();
    if(key==2)actions_push(c);
}
} // namespace

const PageSpec track_actions_page {actions_draw,play_pad,actions_wheel,actions_push,actions_soft,actions_wheel};
const PageSpec tracks_page {draw, pad, wheel, push, soft, wheel}; // Minus / Plus: the track, as the wheel

} // namespace rhythmer
