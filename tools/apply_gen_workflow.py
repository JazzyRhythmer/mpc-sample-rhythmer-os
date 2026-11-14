#!/usr/bin/env python3
"""Extend generated GEN UI and existing browser/history with native workflow."""
from pathlib import Path
import sys
r=Path(sys.argv[1])
def patch(file,a,b):
 p=r/file;s=p.read_text();assert s.count(a)==1,(file,a[:60],s.count(a));p.write_text(s.replace(a,b))
base='src/rhythmer/'
patch(base+'model/project.h','struct Track {','struct Track {\n    uint8_t break_bars=0;')
patch(base+'shell/context.h','void gen8_action(unsigned action);','void gen8_action(unsigned action);\n    void gen_break_load(const std::string&,const std::string&);\n    void gen_break_tick();')
patch(base+'shell/ui_state.h','uint8_t gen8_mode = 0;','bool break_browse=false;int break_pending=-1;uint8_t break_track=0,break_bank=0,break_bars=2;\n    uint8_t gen8_mode = 0;')
patch(base+'shell/history.h','struct Edit {','struct Edit {\n    struct GenPluginState {unsigned entry;PluginRef ref;std::vector<uint8_t> state;};\n    std::vector<GenPluginState> gen_plugins_before,gen_plugins_after;\n    std::vector<std::pair<uint8_t,TrackState>> tracks_before,tracks_after;')
patch(base+'shell/history.h','        for (const auto* c : {e.chop_before.get(), e.chop_after.get()})','        for(const auto* group:{&e.tracks_before,&e.tracks_after})for(const auto& t:*group)for(const auto& p:t.second.track.pads)mark(p);\n        for (const auto* c : {e.chop_before.get(), e.chop_after.get()})')
patch(base+'shell/context.cpp','    const auto& whole = after ? e.track_after : e.track_before;','    if(plugins && !(after?e.gen_plugins_after:e.gen_plugins_before).empty()){for(const auto& p:after?e.gen_plugins_after:e.gen_plugins_before){project.plugins[p.entry]=p.ref;plugins->set_gen_state(p.entry,p.state);}}\n    for(const auto& t:after?e.tracks_after:e.tracks_before)restore_track(*this,t.first,t.second);\n    const auto& whole = after ? e.track_after : e.track_before;')
patch(base+'shell/lights.cpp','    // Power was pressed:', '    context_.gen_break_tick();\n    // Power was pressed:')
patch(base+'pages/samples_page.cpp','    else if (file.bank) c.load_bank_file(file.path, file.name);', '    else if(c.ui.break_browse){if(file.bank||file.kit||file.midi||file.expansion){c.notice("Choose an audio loop");return;}c.gen_break_load(file.path,file.name);}\n    else if (file.bank) c.load_bank_file(file.path, file.name);')
patch(base+'shell/bindings.h','Gen8Amount, Gen8Genre, Gen8Seed,','Gen8Amount, Gen8Genre, Gen8Seed, GenFirst,GenLast,GenAssign,GenBars,')
patch(base+'shell/bindings.cpp','            if(ui.gen8_mode==1)', '''            if(ui.gen8_mode==3)return {Binding{Kind::GenFirst,0,0,15,project.gen8.first},Binding{Kind::GenLast,0,0,15,project.gen8.last},Binding{Kind::GenAssign,0,0,1,project.gen8.assign}};
            if(ui.gen8_mode==2)return {Binding{Kind::GenBars,0,1,4,project.gen8.bars},Binding{Kind::Gen8Genre,0,0,58,project.gen8.genre},Binding{Kind::Gen8Seed,0,0,9999,project.gen8.seed}};
            if(ui.gen8_mode==1)''')
patch(base+'shell/context.cpp','    case Kind::Gen8Amount:', '''    case Kind::GenFirst:project.gen8.first=uint8_t(std::clamp(value,0,15));break;
    case Kind::GenLast:project.gen8.last=uint8_t(std::clamp(value,0,15));break;
    case Kind::GenAssign:project.gen8.assign=uint8_t(value!=0);break;
    case Kind::GenBars:project.gen8.bars=uint8_t(std::clamp(value,1,4));break;
    case Kind::Gen8Amount:''')
patch(base+'pages/common.cpp','    case Kind::Gen8Amount:', '''    case Kind::GenFirst:c.label="FROM TRACK";c.value=juce::String(b.value+1);break;
    case Kind::GenLast:c.label="TO TRACK";c.value=juce::String(b.value+1);break;
    case Kind::GenAssign:c.label="GEN MODE";c.value=b.value?"SOUND + MIDI":"MIDI ONLY";break;
    case Kind::GenBars:c.label="SOURCE BARS";c.value=juce::String(b.value);break;
    case Kind::Gen8Amount:''')
p=r/(base+'pages/steps_page.cpp');s=p.read_text().replace('"GENERATE 8","MUTATE 8"','"GENERATE RANGE","MUTATE RANGE"').replace('"TAIL FILL"','"TAIL FILL","BROWSE SAMPLE"').replace('m.count=s.ui.gen8_mode==2?5:6;','m.count=s.ui.gen8_mode==2?6:6;').replace('s.ui.gen8_mode==2?brk[i]:gen[i]','s.ui.gen8_mode==2?brk[i]:gen[i]').replace('m.title=s.ui.gen8_mode==2?"SELECTED BANK: 16 CHOPS":"T1-4 SYNTH / T5-8 DRUMS";','''m.title=s.ui.gen8_mode==2?"16 SLICES / TEMPO SYNC":"T"+juce::String(s.project.gen8.first+1)+"-"+juce::String(s.project.gen8.last+1)+(s.project.gen8.assign?" SOUND + MIDI":" MIDI ONLY");
            if(s.ui.gen8_mode==3){m.count=1;m.rows[0]={"SET TRACK RANGE",{},false,false,false};m.title="K3: SOUND + MIDI / MIDI ONLY";}''').replace('s.ui.gen8_mode==1?"VARY":s.ui.gen8_mode==2?"BREAK":"GEN 8"','s.ui.gen8_mode==3?"GEN SETUP":s.ui.gen8_mode==1?"VARY":s.ui.gen8_mode==2?"BREAK":"GEN 8"').replace('int count=c.ui.gen8_mode==2?5:6','int count=c.ui.gen8_mode==3?1:6').replace('unsigned mode=c.ui.gen8_mode, row=c.ui.sheet_row;','unsigned mode=c.ui.gen8_mode, row=c.ui.sheet_row;\n        if(mode==3){c.ui.gen8_mode=0;c.ui.sheet_row=0;return;}').replace('(c.ui.gen8_mode+1)%3','(c.ui.gen8_mode+1)%4');p.write_text(s)
# Independent optional sections preserve legacy GN8S and file identity.
patch(base+'model/project_file.cpp','    return w.out;','''    at=w.begin("GN9S");w.u8(project.gen8.first);w.u8(project.gen8.last);w.u8(project.gen8.assign);w.u8(project.gen8.bars);w.end(at);
    at=w.begin("GPPS");for(const auto& p:project.plugins)w.u16(uint16_t(p.gen_program+1));w.end(at);
    at=w.begin("BRKS");for(const auto& t:project.tracks)w.u8(t.break_bars);w.end(at);
    return w.out;''')
patch(base+'model/project_file.cpp','} else if (name == "TRAK") {','''} else if(name=="GN9S") {
            project->gen8.first=uint8_t(std::min<unsigned>(r.u8(),15));project->gen8.last=uint8_t(std::min<unsigned>(r.u8(),15));project->gen8.assign=uint8_t(r.u8()!=0);project->gen8.bars=uint8_t(std::clamp<unsigned>(r.u8(),1,4));
        } else if(name=="GPPS") {for(auto& p:project->plugins)p.gen_program=int16_t(std::min<unsigned>(r.u16(),32768))-1;
        } else if(name=="BRKS") {for(auto& t:project->tracks)t.break_bars=uint8_t(std::min<unsigned>(r.u8(),4));
        } else if (name == "TRAK") {''')

patch(base+'model/project.h','struct PluginRef {','struct PluginRef {\n    int16_t gen_program=-1;')
patch(base+'plugin/plugin_files.h','struct PluginFile {','struct PluginFile {\n    int gen_program=-1;')
patch(base+'shell/context.cpp','void Context::open(PageId page) {','void Context::open(PageId page) {\n    if(page!=PageId::Samples)ui.break_browse=false;')

patch(base+'plugin/plugin_rack.h','    void set_states(PluginStates states);','    void set_states(PluginStates states);\n    void set_gen_state(unsigned entry,std::vector<uint8_t> state);')
patch(base+'plugin/plugin_rack.cpp','void PluginRack::set_states(PluginStates states) {','void PluginRack::set_gen_state(unsigned e,std::vector<uint8_t> state){if(e>=max_plugins)return;std::lock_guard<std::mutex> held(lock);entries[e].state=std::move(state);entries[e].reload=true;}\nvoid PluginRack::set_states(PluginStates states) {')
patch(base+'plugin/plugin_rack.cpp','} else if (!same && !entry.path.empty() && !want.empty()) {','} else if (!again && !same && !entry.path.empty() && !want.empty()) {')

patch(base+'shell/plugin_jobs.cpp','        tr.plugin = uint8_t(entry);','        tr.plugin = uint8_t(entry);tr.break_bars=0;')

patch(base+'shell/context.cpp','void Context::new_project() {','void Context::new_project() {\n    ui.break_pending=-1;ui.break_browse=false;')
patch(base+'shell/context.cpp','    if(page!=PageId::Samples)ui.break_browse=false;','    if(page!=PageId::Samples)ui.break_browse=false;\n    if(page==PageId::Project)ui.break_pending=-1;')

patch(base+'plugin/plugin_rack.h','    View view() const;','    View view() const;\n    std::string source_folder() const;')
patch(base+'plugin/plugin_rack.cpp','PluginRack::View PluginRack::view() const {','std::string PluginRack::source_folder() const {std::lock_guard<std::mutex> held(lock);return root;}\nPluginRack::View PluginRack::view() const {')

patch(base+'shell/context.cpp','    take_track = -1;\n}\n\nvoid Context::undo()', '    if(plugins&&!e.tracks_before.empty())plugins->sync(project);\n    take_track = -1;\n}\n\nvoid Context::undo()')
import subprocess
subprocess.run([sys.executable,str(Path(__file__).with_name('apply_gen_navigation.py')),str(r)],check=True)

patch(base+'shell/history.h','    std::string what;', '    bool gen_key_changed=false;std::array<uint16_t,3> gen_key_before{},gen_key_after{};\n    std::string what;')
patch(base+'shell/context.cpp','void Context::apply_edit(const Edit& e, bool after) {','void Context::apply_edit(const Edit& e, bool after) {\n    if(e.gen_key_changed){auto value=after?e.gen_key_after:e.gen_key_before;project.root=uint8_t(value[0]);project.scale=uint8_t(value[1]);set_tempo(value[2]);}')
