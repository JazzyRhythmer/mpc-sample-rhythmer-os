// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Kerem Kilic (Ellic Studio)
// SAMPLES (Sample Select on a sampler track): the MPC's sample browser.
// MPC drum programs (KIT) first, then instruments (XPM, XTY, SFZ), then folders, as categories, then the WAV files. The wheel and Minus /
// Plus move, Push opens a folder or loads the file onto the last pad hit
// (keeping the pad's settings; the whole file, Trim or Chop shape it), or a
// bank file (BANK, Samples/Banks) into the kit's bank in view, or an MPC drum
// program (KIT) as the track's kit, as Load Kit does, or installs an MPC
// expansion (.xpn, INSTALL) onto the card and opens its folder; Shift +
// Sample Select here saves that bank as a bank file (Save Bank). B1
// goes back out, B2 picks the drive (the card, or the internal one: the
// factory categories and the stock app's samples, read only), B3 hears each
// file as the cursor lands on it. Shift + pad loads the file onto the
// kit's next empty pad (here instead of the printed Shift + pad jobs). K2
// jumps. The pads play the kit.
#include "rhythmer/shell/smf_jobs.h"
#include "rhythmer/pages/common.h"
#include "rhythmer/pages/pages.h"
#include "rhythmer/engine/dsp.h"
#include "rhythmer/shell/sample_library.h"
#include "rhythmer/shell/new_track.h"
#include "rhythmer/ui/widgets.h"
#include <cstdio>
#include <filesystem>
#include <vector>

namespace rhythmer {
namespace {
using namespace ui;
constexpr unsigned visible = list_rows;

juce::String folder_title(const Snapshot& s) {
    if (s.ui.files_drive == unsigned(Drive::Internal) && s.files_top) return "CATEGORIES";
    if (s.files_folder.empty()) return "NO CARD";
    return juce::String(std::filesystem::path(s.files_folder).filename().string());
}

void draw(Paint& p, const Snapshot& s) {
    const auto& track = s.track();
    auto c = colour_of(s);
    Header h = header_of(s);
    Drive drive = Drive(s.ui.files_drive);
    auto drive_chip = chip(drive_name(drive), c);
    drive_chip.spare = true; // a long folder name keeps its room: B2 names the other drive
    h.left.push_back(drive_chip);
    h.left.push_back(pill(s.ui.break_browse
        ? juce::String(s.ui.break_load_b ? "LOAD B / " : "LOAD A / ") + juce::String(s.ui.break_load_b ? track.break_bars : s.ui.break_bars) + " BARS"
        : folder_title(s) + juce::String::fromUTF8(" \xc2\xb7 ") + juce::String(s.files.size()), c));
    if (track.engine == EngineKind::Sampler) { // a kit: the pad Push loads onto, the last one hit
        char label[8];
        pad_label(track.last_pad % sampler_pads, label);
        h.right.push_back(pill(Icon::ArrowRight, juce::String(label), c)); // an arrow: the rows' pad glyph marks files already on a pad
    }
    h.right.push_back(tag_of(s, s.ui.track));
    juce::String other = drive == Drive::Card ? "INTERNAL" : "CARD";
    // The file under the cursor as it previews (mock 7): its row fills as it plays; B3 lit while there is sound.
    PreviewPlace heard = s.ui.preview ? preview_place(s.heads, int(sampler_pads), uint16_t(preview_slot), dsp::model_rate) : PreviewPlace {};
    SoftKeys keys {{s.files_top ? (s.ui.break_browse?(s.ui.break_from_picker?"CANCEL":s.ui.break_load_b?"PERF":"GEN"):"") : "BACK", other, "PREVIEW"}, -1, c, {s.files_top&&!s.ui.break_browse ? KeyIcon::None : KeyIcon::Back, KeyIcon::None, KeyIcon::None}};
    keys.toggles = 4; // PREVIEW names a thing that is on or off: its LED, never ON / OFF (the row fills while it sounds)
    keys.lit = s.ui.preview ? 4 : 0;
    frame(p, s, keys, h);
    if (s.files.empty()) { // a glyph and two words: no card, or nothing here
        bool no_card = drive == Drive::Card && s.sample_root.empty();
        icon(p, no_card ? Icon::Card : Icon::Folder, zone::width / 2.0f - 14, zone::picture_y + 40, 28, colour::dim, 1.4f);
        p.text(no_card ? "NO CARD" : "EMPTY", 0, zone::picture_y + 76, zone::width, 14, caps_text(colour::dim), juce::Justification::centred);
        return;
    }
    const unsigned shown=s.ui.break_browse?5:visible;
    unsigned count = unsigned(s.files.size()), cursor = std::min<unsigned>(s.ui.files_cursor, count - 1);
    unsigned first = cursor < 2 ? 0 : std::min(cursor - 2, count > shown ? count - shown : 0);
    for (unsigned row = 0; row < shown && first + row < count; ++row) {
        const auto& file = s.files[first + row];
        ListRow r;
        r.name = name_case(juce::String(file.name)); r.accent = c; r.current = first + row == cursor;
        const juce::String path(file.path);
        juce::String format = path.endsWithIgnoreCase(".xpm") ? "XPM" : path.endsWithIgnoreCase(".xty") ? "XTY" : path.endsWithIgnoreCase(".exs") ? "EXS"
                            : path.endsWithIgnoreCase(".xpn") ? "XPN" : path.endsWithIgnoreCase(".sf2") || path.contains(".sf2#") || path.contains(".SF2#") ? "SF2"
                            : path.endsWithIgnoreCase(".dspreset") ? "DS" : "SFZ";
        if (file.folder) { r.icon = Icon::Folder; r.chevron = true; }
        else if (file.bank) r.icon = Icon::Layers;
        else if (file.kit) { r.icon = Icon::Pads; r.fact = format; }
        else if (file.expansion) { r.icon = Icon::ArrowDown; r.fact = format; } // Push installs it
        else if (file.instrument) { r.icon = Icon::Keyboard; r.fact = format; }
        else if (file.midi) { r.icon = Icon::Note; r.fact = "MIDI"; } // roadmap P4: Push lays it on the pattern
        else {
            r.icon = Icon::Wav;
            if (path.endsWithIgnoreCase(".mp3")) r.fact = "MP3";
            else if (path.endsWithIgnoreCase(".flac")) r.fact = "FLAC";
            else if (path.endsWithIgnoreCase(".ogg") || path.endsWithIgnoreCase(".oga")) r.fact = "OGG";
            else if (path.endsWithIgnoreCase(".aif") || path.endsWithIgnoreCase(".aiff")) r.fact = "AIFF";
            for (unsigned k = 0; k < sampler_pads && r.pad.isEmpty(); ++k) // which pad of this kit plays it, on any layer
                for (unsigned l = 0; l < pad_layers; ++l) {
                    const PadLayer layer = track.pads[k].layer(l);
                    if (!layer.used() || file.path != s.project.samples[layer.sample].path) continue;
                    char label[4]; pad_label(k, label); r.pad = juce::String(label);
                    break;
                }
        }
        if (r.current && heard.shown && !file.folder && !file.bank) { // the time heard of its length
            char now[16], of[24];
            std::snprintf(now, sizeof(now), "%.1f", heard.heard);
            std::snprintf(of, sizeof(of), " / %.1f s", heard.length);
            r.tag_lead = now; r.tag = of; r.fact = {};
            r.played = heard.through; r.played_wake = heard.wake; r.played_head = heard.strength;
        }
        p.g.saveState();
        list_row(p, zone::pad, zone::picture_y + 0.5f + row * (list_row_h + list_row_gap), zone::width - 2 * zone::pad, r);
        p.g.restoreState();
    }
    if(s.ui.break_browse){
        juce::String status="PREVIEW reads source / K2 audition";
        const auto& file=s.files[cursor];
        if(file.path==s.preview_path && s.preview_complete && s.preview_seconds<=0)status="PREVIEW UNAVAILABLE / choose audio";
        if(file.path==s.preview_path && s.preview_seconds>0){
            unsigned bars=s.ui.break_load_b?track.break_bars:s.ui.break_bars;
            double bpm=bars*240.0/s.preview_seconds;
            auto source_bpm=juce::String(bpm,1);if(source_bpm.endsWith(".0"))source_bpm=source_bpm.dropLastCharacters(2);
            status="CALC "+source_bpm+" BPM / "+juce::String(bars)+" bars";
            if(s.ui.break_preview_sync && s.preview_complete)status="CALC "+source_bpm+" BPM / SYNC "+tempo_text(s);
            if(s.ui.preview && s.ui.break_preview_sync && !s.preview_complete)status="READING SYNC / "+source_bpm+" BPM calc";
            if(s.preview_seconds>=30)status="30s PREVIEW LIMIT / ORIGINAL ONLY";
        }
        p.text(status,zone::pad,zone::picture_y+122,zone::width-2*zone::pad,18,plain(colour::sec,type::small));
    }
}

void wheel(Context& c, int delta) {
    int was = c.ui.files_cursor;
    c.ui.files_cursor = uint16_t(std::clamp<int>(c.ui.files_cursor + delta, 0, std::max(int(c.ui.files_count) - 1, 0)));
    if (c.ui.files_cursor != was) c.preview_cursor();
}

void push(Context& c) {
    if (!c.library) return;
    auto files = sample_browser_files(c.library->files(), c.ui.break_browse);
    if (c.ui.files_cursor >= files.size()) return;
    const auto& file = files[c.ui.files_cursor];
    if (file.folder) c.library->browse(Drive(c.ui.files_drive), file.path);
    else if(c.ui.break_browse){if(file.bank||file.kit||file.midi||file.expansion){c.notice("Choose an audio loop");return;}c.gen_break_load(file.path,file.name);}
    else if (file.bank) c.load_bank_file(file.path, file.name);
    else if (file.kit) c.load_kit_file(file.path, file.name);
    else if (file.expansion) c.library->install(file.path);
    else if (file.midi) import_midi(c, file.path); // roadmap P4: its notes onto the track's pattern
    else c.load_file(file.path, file.name, false);
}

void soft(Context& c, int key) {
    if(key==0&&c.ui.break_browse&&(!c.library||c.library->top())){if(c.ui.break_from_picker){c.ui.break_from_picker=false;c.open(PageId::Plugins);return;}if(c.ui.break_load_b){c.ui.break_load_b=false;c.open(PageId::Edit);c.ui.break_perf_page=2;return;}c.open(PageId::Patterns);c.ui.sheet_open=true;c.ui.gen8_mode=2;c.ui.sheet_row=5;return;}
    if (!c.library) return;
    auto& ui = c.ui;
    if (key == 0) { if (c.library->top()) samples_cancel(c); else c.library->browse_up(); } // at the top: CANCEL
    if (key == 1) { // the other drive, where it was left
        unsigned from = ui.files_drive % unsigned(Drive::Count), to = (from + 1) % unsigned(Drive::Count);
        c.files_places[from] = {c.library->folder(), ui.files_cursor, true};
        const auto& back = c.files_places[to];
        c.files_row_wanted = back.set ? back.row : -1;
        ui.files_drive = uint8_t(to);
        c.library->browse(Drive(to), back.set ? back.folder : std::string());
    }
    if (key == 2) { ui.preview = !ui.preview; c.preview_cursor(); } // its LED says which
}
} // namespace

// Shift + pad on the browser: the file under the cursor onto the next empty pad.
bool samples_shift_pad(Context& c) {
    if (c.ui.page != PageId::Samples || !c.library || c.track().engine != EngineKind::Sampler) return false;
    if (c.ui.break_browse) { c.notice("Push loads the selected BREAK source"); return true; }
    auto files = sample_browser_files(c.library->files(), c.ui.break_browse);
    if (c.ui.files_cursor >= files.size() || files[c.ui.files_cursor].folder) { c.notice("Shift + pad: a file first"); return true; }
    const auto& file = files[c.ui.files_cursor];
    if (file.bank) { c.notice("Push loads a bank"); return true; }
    if (file.kit) { c.notice("Push loads a kit"); return true; }
    if (file.expansion) { c.notice("Push installs it"); return true; }
    if (file.midi) { c.notice("Push lays it on the pattern"); return true; }
    c.load_file(file.path, file.name, true);
    return true;
}

const PageSpec samples_page {draw, play_pad, wheel, push, soft, wheel}; // Minus / Plus move the list

} // namespace rhythmer
