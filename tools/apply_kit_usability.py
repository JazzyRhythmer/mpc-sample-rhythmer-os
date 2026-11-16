"""Keep kit-only sources loadable; bind visible editor cards to their layout."""
from pathlib import Path

def apply(root):
 def patch(file,old,new):
  p=root/'src/rhythmer'/file;s=p.read_text();assert s.count(old)==1,(file,old[:80],s.count(old));p.write_text(s.replace(old,new))
 patch('plugin/plugin_files.h','    bool single_drum = false;','    bool single_drum = false;\n    bool kit_only = false;')
 patch('plugin/plugin_files.cpp','    juce::File meta(juce::String((folder / "plugin-meta.xml").string()));','    f.kit_only=fs::is_regular_file(folder / "rhythmer-kit-only.json");\n    juce::File meta(juce::String((folder / "plugin-meta.xml").string()));')
 patch('plugin/plugin_files.cpp','    f.drums.clear(); // only Rhythmer Kit advertises multi-sound pads','    const auto original_name=juce::File(juce::String((folder/"rhythmer-source-name.json").string()));\n    if(original_name.existsAsFile()&&original_name.getSize()<=1024){auto original=juce::JSON::parse(original_name.loadFileAsString()).getProperty("name",{}).toString();if(original.isNotEmpty()&&original.length()<64)f.name=original.toStdString();}\n    f.drums.clear(); // only Rhythmer Kit advertises multi-sound pads')
 patch('plugin/plugin_files.cpp','    std::sort(out.begin(), out.end(), [](const PluginFile& a, const PluginFile& b) {','    out.erase(std::remove_if(out.begin(),out.end(),[](const PluginFile& f){return f.kit_only;}),out.end());\n    std::sort(out.begin(), out.end(), [](const PluginFile& a, const PluginFile& b) {')
 patch('plugin/plugin_panel.h','    bool qlinks = false;','    uint32_t layout_revision=0;\n    int16_t focused_pad=-1;\n    bool qlinks = false;')
 patch('plugin/plugin_rack.h','    void set_param(unsigned entry, unsigned shown, int value);','    void set_param(unsigned entry, unsigned shown, int value, uint32_t revision=0);')
 patch('plugin/plugin_rack.cpp','    out.qlinks = h->qlinks;','    out.layout_revision=sound_rack_revision(h->instance.get());\n    out.focused_pad=int16_t(sound_rack_focus(h->instance.get()));\n    out.qlinks = h->qlinks;')
 patch('plugin/plugin_rack.cpp','void PluginRack::set_param(unsigned entry, unsigned shown_index, int value) {','void PluginRack::set_param(unsigned entry, unsigned shown_index, int value, uint32_t revision) {')
 patch('plugin/plugin_rack.cpp','    p->setValue(v);','    if(revision&&is_sound_rack(h->instance.get()))sound_rack_set_parameter_checked(h->instance.get(),int(h->shown[shown_index]),v,revision);\n    else p->setValue(v);')
 patch('shell/plugin_jobs.cpp', '''    plugins->set_param(entry, shown, value);
    auto& panel = ui.plugin_panel;
    if (panel.entry == entry)
        for (unsigned k = 0; k < 3; ++k)
            if (panel.row * 3u + k == shown) panel.params[k].value = int16_t(std::clamp(value, 0, plugin_param_max));''', '''    plugins->set_param(entry,shown,value,ui.plugin_panel.entry==entry?ui.plugin_panel.layout_revision:0);
    if(ui.plugin_panel.entry==entry){plugins->panel(entry,ui.plugin_row[entry],ui.plugin_panel);ui.plugin_row[entry]=ui.plugin_panel.row;}
    plugin_panel_at=0;''')
 patch('shell/context.cpp','        plugins->set_param(t.plugin,0,int(std::lround(slot*1000.0/63)));','        plugins->set_param(t.plugin,0,int(std::lround(slot*1000.0/63)));\n        plugins->panel(t.plugin,ui.plugin_row[t.plugin],ui.plugin_panel);ui.plugin_row[t.plugin]=ui.plugin_panel.row;plugin_panel_at=0;')
 patch('shell/ui_state.h','    std::array<uint16_t, max_plugins> plugin_row {};','    bool kit_common=false;\n    std::array<uint16_t, max_plugins> plugin_row {};')
 patch('shell/bindings.cpp','        if (track.engine == EngineKind::Plugin) return plugin_cards(ui, track.plugin);', '''        if(track.engine==EngineKind::Plugin&&ui.kit_common&&track.plugin<max_plugins&&std::string(project.plugins[track.plugin].name)=="Rhythmer Kit")
            return {Binding{Kind::Level,0,0,127,track.mix.level},Binding{Kind::Pan,0,-50,50,track.mix.pan},Binding{Kind::Send,0,0,100,track.mix.sends[0]}};
        if (track.engine == EngineKind::Plugin) return plugin_cards(ui, track.plugin);''')
 patch('pages/edit_page.cpp','        frame(p, s, {{"PLUG-INS", presets ? "PRESETS" : "", ""}, -1, c}, h);', '''        bool kit=ours&&juce::String(panel.name)=="Rhythmer Kit";
        frame(p,s,{{"PLUG-INS",presets?"PRESETS":"",kit?(s.ui.kit_common?"PAD EDIT":"KIT MIX"):""},-1,c},h);
        if(kit&&s.ui.kit_common){
            p.text("KIT MIX",zone::pad,zone::picture_y+12,zone::width-2*zone::pad,24,caps_text(colour::text),juce::Justification::centred);
            p.text("ALL PADS / ALL BANKS",zone::pad,zone::picture_y+44,zone::width-2*zone::pad,20,plain(colour::sec,type::body),juce::Justification::centred);
            p.text("LEVEL / PAN / SEND A",zone::pad,zone::picture_y+75,zone::width-2*zone::pad,20,plain(colour::sec,type::small),juce::Justification::centred);
            p.text("Saved with project",zone::pad,zone::picture_y+105,zone::width-2*zone::pad,18,plain(colour::dim,type::small),juce::Justification::centred);
            return;
        }''')
 patch('pages/edit_page.cpp','        if (key == 0) c.open_plugin_picker(UiState::PluginTarget::Instrument);', '''        if(key==2&&c.ui.plugin_panel.entry==c.track().plugin&&std::string(c.ui.plugin_panel.name)=="Rhythmer Kit"){c.ui.kit_common=!c.ui.kit_common;return;}
        if (key == 0) c.open_plugin_picker(UiState::PluginTarget::Instrument);''')
 patch('pages/edit_page.cpp','void plugin_rows(Context& c, int delta) {','void plugin_rows(Context& c, int delta) {\n    if(c.ui.kit_common&&std::string(c.ui.plugin_panel.name)=="Rhythmer Kit")return;')
 patch('shell/plugin_jobs.cpp','    plugins->select_program(ui.presets_entry, programs.list[size_t(index)].index);', '''    plugins->select_program(ui.presets_entry, programs.list[size_t(index)].index);
    if(std::string(project.plugins[ui.presets_entry].name)=="Rhythmer Kit"){
        ui.kit_common=false;ui.plugin_row[ui.presets_entry]=0;
        for(auto& t:project.tracks)if(t.engine==EngineKind::Plugin&&t.plugin==ui.presets_entry){t.bank=0;t.last_pad=0;t.last_note=36;}
    }''')
 patch('tools.cpp','const Preview previews[] {', '''const Preview previews[] {
    {"kit-common-mix",[](Shell&,Snapshot& s){plugin_track(s,PluginStatus::Ready);auto& t=s.project.tracks[s.ui.track];std::snprintf(s.project.plugins[t.plugin].name,sizeof(s.project.plugins[t.plugin].name),"Rhythmer Kit");std::snprintf(s.ui.plugin_panel.name,sizeof(s.ui.plugin_panel.name),"Rhythmer Kit");s.ui.kit_common=true;}},''')
 patch('pages/steps_page.cpp','"BACK", "MODE", s.ui.gen8_mode==3?"DONE"','"BACK", s.ui.gen8_mode==0?"VARY":s.ui.gen8_mode==1?"SETUP":"GEN", s.ui.gen8_mode==3?(s.project.gen8.assign?"SELECT":"DONE")')
 patch('pages/steps_page.cpp','if(s.ui.gen8_mode==3){m.count=1;m.rows[0]={"RETURN TO GEN",{},false,false,false};','''if(s.ui.gen8_mode==3){m.count=s.project.gen8.assign?4:1;
                for(unsigned i=0;i<m.count;i++){m.rows[i]={s.project.gen8.assign?"T"+juce::String(i*4+1)+" - T"+juce::String(i*4+4):juce::String("RETURN TO GEN"),s.project.gen8.assign?"KIT T"+juce::String(i*4+1):juce::String(),false,false,false};}''')
 patch('pages/steps_page.cpp','int count=c.ui.gen8_mode==3?1:c.ui.gen8_mode==4?2:6;', 'int count=c.ui.gen8_mode==3?(c.project.gen8.assign?4:1):c.ui.gen8_mode==4?2:6;')
 patch('pages/steps_page.cpp','if(mode==3){c.ui.gen8_mode=0;c.ui.sheet_row=0;return;}', 'if(mode==3){if(c.project.gen8.assign){c.project.gen8.group=uint8_t(std::min(row,3u));c.dirty=true;}c.ui.gen8_mode=0;c.ui.sheet_row=0;return;}')
 patch('pages/steps_page.cpp','c.ui.gen8_mode=row==5?3:br?2:acid?4:1;c.ui.sheet_row=0;', 'c.ui.gen8_mode=row==5?3:br?2:acid?4:1;c.ui.sheet_row=c.ui.gen8_mode==3&&c.project.gen8.assign?c.project.gen8.group:0;')
 patch('pages/steps_page.cpp','c.ui.gen8_mode=c.ui.gen8_mode==0?1:c.ui.gen8_mode==1?3:0;c.ui.sheet_row=0;', 'c.ui.gen8_mode=c.ui.gen8_mode==0?1:c.ui.gen8_mode==1?3:0;c.ui.sheet_row=c.ui.gen8_mode==3&&c.project.gen8.assign?c.project.gen8.group:0;')
 patch('shell/context.cpp','case Kind::GenGroup:project.gen8.group=uint8_t(std::clamp(value,0,3));break;', 'case Kind::GenGroup:project.gen8.group=uint8_t(std::clamp(value,0,3));if(ui.gen8_mode==3)ui.sheet_row=project.gen8.group;break;')
 print('Applied kit scope, stable edit targets and kit-only browsing')

if __name__=='__main__':
 import sys
 apply(Path(sys.argv[1]))
