#!/usr/bin/env python3
"""Owner-beta sound safety/transport changes on the generated runtime only."""
from pathlib import Path
import sys
from apply_sound_rack import replace

def apply(root):
 p=root/'src/rhythmer/plugin/plugin_files.h'
 replace(p,'    bool folder = false;', '    bool single_drum = false;\n    bool folder = false;')
 p=root/'src/rhythmer/plugin/plugin_files.cpp'
 replace(p,'    // Percussion engines are single sounds outside Rhythmer Kit.', '    f.single_drum = !f.drums.empty() || f.name=="Sophie";\n    // Percussion engines are single sounds outside Rhythmer Kit.')
 replace(p,'        read_drums(f, map.string());\n    return true;', '        read_drums(f, map.string());\n    f.single_drum = f.single_drum || !f.drums.empty();\n    f.drums.clear(); // only Rhythmer Kit advertises multi-sound pads\n    return true;')
 replace(p,'    if ((fs::is_regular_file(folder / "rhythmer-kit.json")', '''    if(fs::is_regular_file(folder / "rhythmer-acid.json")){f.name="Acid Engine";f.instrument=1;f.format=PluginFormat::Vst2;f.fixed_rate=44100;return true;}
    if(fs::is_regular_file(folder / "rhythmer-break.json")){f.name="Break Engine";f.instrument=1;f.format=PluginFormat::Vst2;return true;}
    if ((fs::is_regular_file(folder / "rhythmer-kit.json")''')
 p=root/'src/rhythmer/shell/plugin_jobs.cpp'
 replace(p,'    if (file.folder || file.several())', '''    if(file.name=="Break Engine"){
        if(ui.plugin_target!=UiState::PluginTarget::Instrument){notice("Break Engine is an instrument");return;}
        close_gesture();if(track().engine!=EngineKind::Sampler)load_sound(ui.track,EngineKind::Sampler,0);
        track().break_bars=track().break_bars?track().break_bars:2;track().layout=PadLayout::Drums;track().set_name("BREAK");
        ui.break_browse=true;ui.break_track=ui.track;ui.break_bars=track().break_bars;dirty=true;plugins->sync(project);open(PageId::Samples);notice("BREAK: choose a loop, then source bars 1-4");return;
    }
    if (file.folder || file.several())''')
 replace(p,'        std::string name = file.name;', '        if(file.single_drum){tr.octave=4;tr.last_note=uint8_t(std::clamp(pad_note(project,tr,0).key,0,127));}\n        std::string name = file.name;')
 p=root/'src/rhythmer/plugin/plugin_rack.cpp'
 replace(p,'    if (file.name=="Rhythmer Kit") {found.name="Rhythmer Kit";found.instrument=1;return found;}', '    if (file.name=="Rhythmer Kit"||file.name=="Acid Engine"||file.name=="Break Engine") {found.name=file.name;found.instrument=1;return found;}')
 replace(p,'    out.current = e.live->program;', '    out.current = is_sound_rack(e.live->instance.get())?e.live->instance->getCurrentProgram():e.live->program;')
 p=root/'src/rhythmer/shell/context.cpp'
 replace(p,'    bool engine_changed = tr.engine != kind;', '    tr.break_bars=0; // an explicit ordinary sound load leaves Break Engine\n    bool engine_changed = tr.engine != kind;')
 p=root/'src/rhythmer/shell/project_kits.cpp'
 replace(p,'    into.engine = EngineKind::Sampler;', '    into.engine = EngineKind::Sampler;into.break_bars=src.break_bars;')
 p=root/'src/rhythmer/pages/plugins_page.cpp'  
 replace(p,'r.fact = format_tag(file.format);','r.fact = file.name=="Break Engine"?"NATIVE":format_tag(file.format);')
 p=root/'src/rhythmer/pages/plugin_view.cpp'
 replace(p,'float vw = held ? 0 : p.width(value, value_style) + 10;', 'float vw = held ? 0 : std::min(w*0.55f,p.width(value, value_style) + 10);')
 replace(p,'vw - 10, row_h, value_style, juce::Justification::centredRight);','vw - 10, row_h, p.fit(value,value_style,vw-10,type::floor), juce::Justification::centredRight);')
 p=root/'src/rhythmer/shell/shell.h'
 replace(p,'private:\n    void button', 'private:\n    uint32_t last_stop_ms = 0;\n    bool stop_tap_pending = false;\n    void button')
 p=root/'src/rhythmer/shell/shell.cpp'
 replace(p,'void Shell::button(Button b, bool pressed) {', '''void Shell::button(Button b, bool pressed) {
    if (b == Button::Stop && pressed) {
        const bool twice = stop_tap_pending && uint32_t(context_.now-last_stop_ms) <= 400;
        last_stop_ms = context_.now; stop_tap_pending = !twice;
        if (twice) {
            context_.stop(); context_.midi_panic();
            context_.send({Command::Type::AllNotesOff, 255, 0, 1});
            context_.notice("ALL SOUND OFF"); return;
        }
    }''')
 p=root/'src/rhythmer/engine/engine_host.h'
 replace(p,'    bool running = false;', '    bool panic_latched = false;\n    bool running = false;')
 p=root/'src/rhythmer/engine/engine_host.cpp'
 replace(p,'    case Type::AllNotesOff:\n        midi_all_off', '''    case Type::AllNotesOff:
        if (c.index == 1) {
            panic_latched = true;
            for (auto& s : slots) if (s.engine) s.engine->silence();
            for (auto& chain : fx) for (auto& effect : chain) effect.clear();
            if (pad_fx) for (auto& pads : *pad_fx) for (auto& pad : pads) for (auto& effect : pad) effect.clear();
            knob.clear(); knob_in.clear(); punch.clear(); pad_punch.clear(); flex.clear();
            for (auto& l : live) l.punch.clear();
        }
        midi_all_off''')
 replace(p,'    case Type::NoteOn:\n', '    case Type::NoteOn:\n        panic_latched = false;\n')
 replace(p,'    case Type::PadNote:\n', '    case Type::PadNote:\n        if(c.value>0)panic_latched=false;\n')
 replace(p,'    case Type::Audition:\n', '    case Type::Audition:\n        if(c.value>0)panic_latched=false;\n')
 replace(p,'    case Type::Play:\n', '    case Type::Play:\n        panic_latched = false;\n')
 replace(p,'        float v = park_fading ?', '        float v = panic_latched ? 0.0f : park_fading ?')
 p=root/'src/rhythmer/plugin/plugin_rack.cpp'
 replace(p,'    void silence() override {\n        for', '    void silence() override {\n        cut_output = true;\n        for')
 replace(p,'    void midi(uint8_t status, uint8_t data1, uint8_t data2) override {', '''    void midi(uint8_t status, uint8_t data1, uint8_t data2) override {
        if ((status & 0xf0) == 0x90 && data2) cut_output = false;''')
 replace(p,'        instance->processBlock(buffer, midi_in);','        instance->processBlock(buffer, midi_in);\n        if (cut_output) buffer.clear();')
 replace(p,'    PluginRateBridge bridge;', '    bool cut_output = false;\n    PluginRateBridge bridge;')
 # Upstream parked-load QA must wait for rendered samples, not VM wall time.
 p=root/'tests/rhythmer.cpp';text=p.read_text();start=text.index('void parked_load() {');end=text.find('\nvoid ',start+1);end=len(text) if end<0 else end;part=text[start:end]
 part=part.replace('    std::atomic<bool> stop {false};','    std::atomic<bool> stop {false};std::atomic<size_t> rendered{0};')
 part=part.replace('            std::this_thread::sleep_for(std::chrono::microseconds(300));','            rendered.store(heard.size(),std::memory_order_release);\n            std::this_thread::sleep_for(std::chrono::microseconds(300));')
 part=part.replace('    std::this_thread::sleep_for(std::chrono::milliseconds(60));','''    auto await_frames=[&](size_t target){for(unsigned n=0;n<5000&&rendered.load(std::memory_order_acquire)<target;n++)std::this_thread::sleep_for(std::chrono::milliseconds(1));CHECK(rendered.load(std::memory_order_acquire)>=target);};
    await_frames(size_t(3*Ease::seconds*dsp::sample_rate())+4096);''')
 part=part.replace('    std::this_thread::sleep_for(std::chrono::milliseconds(30));','    await_frames(rendered.load()+2048);')
 part=part.replace('    std::this_thread::sleep_for(std::chrono::milliseconds(150));','    await_frames(rendered.load()+size_t(3*Ease::seconds*dsp::sample_rate())+8192);')
 p.write_text(text[:start]+part+text[end:])
if __name__=='__main__':apply(Path(sys.argv[1]))
