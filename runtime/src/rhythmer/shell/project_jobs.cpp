// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Kerem Kilic (Ellic Studio)
// The Project page's jobs from the MPC's project page (parity phase 10):
// New project asks first (B3 DO IT, B1 CANCEL), and Load Kit takes another
// project's kit (pads, samples, their effects; no patterns) onto the
// selected track as one undo; a bank file loads into one bank of it.
#include "rhythmer/shell/ask.h"
#include "rhythmer/shell/card_access.h"
#include "rhythmer/shell/context.h"
#include "rhythmer/shell/lesson.h"
#include "rhythmer/shell/project_kits.h"
#include "rhythmer/shell/project_store.h"
#include "rhythmer/shell/sample_library.h"
#include "rhythmer/shell/track_copy.h"
#include "rhythmer/shell/stage_map.h"
#include "rhythmer/plugin/plugin_rack.h"
#include <filesystem>
#include <memory>

namespace rhythmer {

void Context::ask_new_project() {
    ask(*this, UiState::Ask::NewProject, !dirty ? 0 : project_path.empty() ? 2 : 1);
}

void Context::start_new_project(bool kit) {
    if (dirty && !project_path.empty()) save_project();
    new_project();
    open(PageId::Stage);
    notice("New project");
    // The pads play at once: the MPC's factory kit on track 1 (shell/lesson.h). Not there (another firmware): the
    // track stays an empty kit, as EMPTY leaves it.
    if (kit && store && std::filesystem::exists(factory_kit_path)) load_kit_file(factory_kit_path, factory_kit_name);
}

void Context::load_kit_file(const std::string& path, const std::string& name) {
    if (!store) return;
    if(!kit_from.empty()){notice("Wait for the current kit load");return;}
    if(ui.recording || host_recording()) {notice("Finish recording first");return;}
    if(frozen_edit(ui.track))return;
    kit_target=ui.track;
    kit_from = path;
    store->load(path); // lands in load_kit() instead of switching (shell/lights.cpp)
    notice("Loading kit from " + name);
}

void Context::load_kit(const Project& from, const std::string& name) {
    if(kit_target==-2){kit_target=-1;return;}
    unsigned target=unsigned(kit_target>=0?kit_target:ui.track)%track_count;
    kit_target=-1;
    if(frozen_edit(target))return;
    int k = kit_track(from);
    if (k < 0) { notice("No kit in " + name); return; }
    if (ui.recording) { notice("Load Kit: not in a take"); return; }
    std::string what = "Load kit " + name;
    Edit edit = begin_edit(what.c_str(), target, -1, false);
    edit.motion_before.reset(); // the kit brings no motion
    edit.track_before = std::make_unique<TrackState>(track_state(*this, target));
    if(plugins && project.tracks[target].engine==EngineKind::Plugin && project.tracks[target].plugin<max_plugins){
        unsigned entry=project.tracks[target].plugin;auto states=plugins->states();
        edit.gen_plugins_before.push_back({entry,project.plugins[entry],states[entry]});
        edit.gen_plugins_after=edit.gen_plugins_before;
    }
    auto next = std::make_unique<TrackState>(*edit.track_before);
    auto result = import_kit(from, unsigned(k), next->track, [&](const SampleRef& ref) { return sample_slot(ref.path, ref.name); });
    restore_track(*this, target, *next);
    edit.track_after = std::move(next);
    edits.push(std::move(edit));
    notice(result.missing ? what + ": " + std::to_string(result.missing) + " pads without a slot" : what);
    if (ui.track == target && (ui.page == PageId::Project || ui.page == PageId::Samples)) {open(PageId::Stage);ui.back_depth=0;stage_go(ui,0,0);} // the kit's sound (Sample held shows its pads)
}

// A kit bank file (Push on one in the Samples browser): read on the service
// thread, then into the bank in view of the selected kit (files_landed()).
void Context::load_bank_file(const std::string& path, const std::string& name) {
    if (!library) return;
    if(!bank_from.empty()){notice("Wait for the current bank load");return;}
    if (track().engine != EngineKind::Sampler) { notice("Load Bank: kit tracks"); return; }
    if(ui.recording || host_recording()) {notice("Finish recording first");return;}
    if(frozen_edit(ui.track))return;
    bank_target=ui.track;bank_target_bank=track().bank;
    bank_from = path;
    library->read_bank(path);
    notice("Loading " + name);
}

void Context::load_bank(const BankFile& bank, const std::string& name) {
    if(bank_target==-2){bank_target=-1;return;}
    unsigned target=unsigned(bank_target>=0?bank_target:ui.track)%track_count;
    unsigned into=bank_target>=0?bank_target_bank%sampler_banks:track().bank%sampler_banks;
    bank_target=-1;
    if(frozen_edit(target))return;
    auto& t = project.tracks[target];
    if (t.engine != EngineKind::Sampler) { notice("Load Bank: kit tracks"); return; }
    if (ui.recording) { notice("Load Bank: not in a take"); return; }
    std::string bank_name = std::string("Bank ") + char('A' + into), what = "Load " + bank_name; // the notice holds 31 characters
    Edit edit = begin_edit(what.c_str(), target, -1, false);
    edit.motion_before.reset(); // a bank brings no motion
    edit.track_before = std::make_unique<TrackState>(track_state(*this, target));
    auto next = std::make_unique<TrackState>(*edit.track_before);
    auto result = import_bank(bank, into, next->track, [&](const SampleRef& ref) { return sample_slot(ref.path, ref.name); });
    restore_track(*this, target, *next);
    edit.track_after = std::move(next);
    edits.push(std::move(edit));
    dirty = true;
    notice(result.missing ? bank_name + ": " + std::to_string(result.missing) + " pads had no slot" : bank_name + ": " + name);
}

// SD card access (parity phase 10b): the service thread lends the card; the
// page shows how it goes and owns the controls until it is back.
void Context::card_access() {
    if (!card || card_away(ui.card)) return;
    ui.sheet_open = false; ui.move_open = false;
    card->request.store(uint8_t(CardRequest::Lend));
    open(PageId::CardAccess);
}

} // namespace rhythmer
