"""Categorized control pages on the original Edit page; native indices stay fixed."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
def apply(root):
 def patch(file,old,new):
  p=root/'src/rhythmer'/file;s=p.read_text();assert s.count(old)==1,(file,old[:100],s.count(old));p.write_text(s.replace(old,new))
 for name in ('design_pages.h','design_panel.inc'):shutil.copy2(ROOT/'extensions/plugin'/name,root/'src/rhythmer/plugin'/name)
 shutil.copy2(ROOT/'extensions/pages/plugin_design.inc',root/'src/rhythmer/pages/plugin_design.inc')
 patch('plugin/plugin_panel.h','struct PluginPanelParam {','''constexpr unsigned plugin_design_max_pages=192;
struct PluginDesignPage {
    char title[28] {};
    uint16_t part=1,parts=1;
    std::array<int16_t,6> shown {{-1,-1,-1,-1,-1,-1}};
};
struct PluginPanelParam {
    int16_t shown=-1;''')
 patch('plugin/plugin_panel.h','    bool qlinks = false;', '''    bool design=false;
    char design_source[32] {};
    uint16_t design_count=0,design_page=0;
    uint8_t design_half=0;
    std::array<PluginDesignPage,plugin_design_max_pages> design_pages {};
    bool qlinks = false;''')
 patch('plugin/plugin_rack.h','    void panel(unsigned entry, unsigned row, PluginPanel& out) const;','    void panel(unsigned entry, unsigned row, PluginPanel& out) const;\n    void edit_panel(unsigned entry,unsigned page,unsigned half,PluginPanel& out) const;')
 patch('plugin/plugin_rack.cpp','void PluginRack::set_param(unsigned entry, unsigned shown_index, int value, uint32_t revision) {','#include "rhythmer/plugin/design_panel.inc"\n\nvoid PluginRack::set_param(unsigned entry, unsigned shown_index, int value, uint32_t revision) {')
 patch('shell/ui_state.h','    bool kit_common=false;','    std::array<uint16_t,max_plugins> plugin_design_page {};\n    std::array<uint8_t,max_plugins> plugin_design_half {};\n    bool kit_common=false;')
 patch('shell/context.h','    void set_plugin_param(int32_t id, int value);','    void set_plugin_param(int32_t id, int value);\n    void refresh_plugin_panel(unsigned entry);')
 patch('shell/plugin_jobs.cpp','void Context::set_plugin_param(int32_t id, int value) {', '''void Context::refresh_plugin_panel(unsigned entry){
    if(!plugins||entry>=max_plugins)return;
    const bool editing=(ui.page==PageId::Edit||(ui.page==PageId::PluginPresets&&ui.presets_back==PageId::Edit))&&track().engine==EngineKind::Plugin&&track().plugin==entry&&ui.edit_page[ui.track];
    if(editing){
        ui.kit_common=false;plugins->edit_panel(entry,ui.plugin_design_page[entry],ui.plugin_design_half[entry],ui.plugin_panel);
        if(ui.plugin_panel.design){ui.plugin_design_page[entry]=ui.plugin_panel.design_page;ui.plugin_design_half[entry]=ui.plugin_panel.design_half;if(ui.map_open)ui.map_cursor=uint8_t(std::min<unsigned>(ui.map_cursor,ui.plugin_panel.design_count?ui.plugin_panel.design_count-1:0));}
    }else {plugins->panel(entry,ui.plugin_row[entry],ui.plugin_panel);ui.plugin_row[entry]=ui.plugin_panel.row;}
    plugin_panel_at=0;
}
void Context::set_plugin_param(int32_t id, int value) {''')
 patch('shell/plugin_jobs.cpp','if(ui.plugin_panel.entry==entry){plugins->panel(entry,ui.plugin_row[entry],ui.plugin_panel);ui.plugin_row[entry]=ui.plugin_panel.row;}','if(ui.plugin_panel.entry==entry)refresh_plugin_panel(entry);')
 patch('shell/plugin_jobs.cpp','    plugins->panel(unsigned(entry), ui.plugin_row[size_t(entry)], ui.plugin_panel);\n    ui.plugin_row[size_t(entry)] = ui.plugin_panel.row;','    refresh_plugin_panel(unsigned(entry));')
 patch('shell/plugin_jobs.cpp','    plugins->select_program(ui.presets_entry, programs.list[size_t(index)].index);','    plugins->select_program(ui.presets_entry, programs.list[size_t(index)].index);\n    ui.plugin_design_page[ui.presets_entry]=0;ui.plugin_design_half[ui.presets_entry]=0;ui.plugin_panel.design=false;')
 patch('shell/context.cpp','        plugins->panel(t.plugin,ui.plugin_row[t.plugin],ui.plugin_panel);ui.plugin_row[t.plugin]=ui.plugin_panel.row;plugin_panel_at=0;','        refresh_plugin_panel(t.plugin);')
 patch('shell/context.cpp','    if(ui.page==PageId::Edit&&track().engine==EngineKind::Plugin&&ui.edit_page[ui.track]){','    if(ui.page==PageId::Edit&&track().engine==EngineKind::Plugin&&ui.edit_page[ui.track]&&ui.map_open){ui.map_open=false;return;}\n    if(ui.page==PageId::Edit&&track().engine==EngineKind::Plugin&&ui.edit_page[ui.track]){')
 patch('shell/bindings.cpp','plugin_binding(entry, panel.row * 3u + k)','plugin_binding(entry, panel.design?unsigned(panel.params[k].shown):panel.row * 3u + k)')
 patch('shell/bindings.cpp','        if(track.engine==EngineKind::Plugin&&!ui.edit_page[ui.track]){','        if(track.engine==EngineKind::Plugin&&ui.edit_page[ui.track]&&ui.map_open)return {};\n        if(track.engine==EngineKind::Plugin&&!ui.edit_page[ui.track]){')
 patch('shell/bindings.cpp','case PageId::PluginPresets: return plugin_cards(ui, ui.presets_entry);','case PageId::PluginPresets: return {Binding{Kind::PluginJump,0,0,std::max(1,int(ui.plugin_panel.programs))-1,int(ui.presets_cursor)},Binding{},Binding{}};')
 patch('shell/context.cpp','case Kind::PluginJump: ui.plugins_cursor = uint16_t(value); break;','case Kind::PluginJump: if(ui.page==PageId::PluginPresets)ui.presets_cursor=uint16_t(value);else ui.plugins_cursor=uint16_t(value);break;')
 patch('pages/common.cpp','c.label = "JUMP"; c.value = juce::String(b.value + 1).paddedLeft(\'0\', 2); c.unit = "/ " + juce::String(int(s.plugins.files.size()));','c.label = s.ui.page==PageId::PluginPresets?"PRESET":"JUMP"; c.value = juce::String(b.value + 1); c.unit = "/ " + juce::String(s.ui.page==PageId::PluginPresets?b.max+1:int(s.plugins.files.size()));')
 patch('pages/common.cpp','if(s.ui.plugin_panel.preset[0]&&','if(!panel.design&&s.ui.plugin_panel.preset[0]&&')
 patch('pages/common.cpp','        const auto& card = s.ui.plugin_panel.params[plugin_binding_shown(b.id) % 3];', '''        const auto& panel=s.ui.plugin_panel;unsigned slot=plugin_binding_shown(b.id)%3;
        if(panel.design)for(unsigned k=0;k<3;++k)if(panel.params[k].used&&panel.params[k].shown==int(plugin_binding_shown(b.id))){slot=k;break;}
        const auto& card=panel.params[slot];''')
 patch('pages/common.cpp','c.label = juce::String(plugin_binding_shown(b.id) + 1);','c.label = juce::String(panel.design?slot+1:plugin_binding_shown(b.id)+1);')
 patch('pages/edit_page.cpp','#include "rhythmer/pages/plugin_home.inc"','#include "rhythmer/pages/plugin_home.inc"\n#include "rhythmer/pages/plugin_design.inc"')
 patch('pages/edit_page.cpp','home?(kit?"EDIT PAD":"EDIT SOUND"):kit?(s.ui.kit_common?"PAD EDIT":"KIT MIX"):""','home?(kit?"EDIT PAD":"EDIT SOUND"):(panel.design?(s.ui.map_open?"SELECT":panel.design_count?"PAGES":""):kit?(s.ui.kit_common?"PAD EDIT":"KIT MIX"):"")')
 patch('pages/edit_page.cpp','home?"PLUG-INS":"MAIN",presets?"PRESETS":""','home?"PLUG-INS":s.ui.map_open?"BACK":"MAIN",s.ui.map_open?"":presets?(kit?"KIT PRESETS":"PRESETS"):""')
 patch('pages/edit_page.cpp','        if(kit&&s.ui.kit_common){','        if(!home&&ours&&panel.design){plugin_design(p,s);return;}\n        if(kit&&s.ui.kit_common){')
 patch('pages/edit_page.cpp','        if(key==0&&c.ui.edit_page[c.ui.track]){c.back();return;}','''        if(key==0&&c.ui.edit_page[c.ui.track]){c.back();return;}
        if(c.ui.edit_page[c.ui.track]&&c.ui.plugin_panel.design&&key==2){
            if(!c.ui.plugin_panel.design_count)return;
            if(c.ui.map_open){c.ui.plugin_design_page[c.track().plugin]=c.ui.map_cursor;c.ui.plugin_design_half[c.track().plugin]=0;c.ui.map_open=false;c.refresh_plugin_panel(c.track().plugin);}
            else {c.ui.map_open=true;c.ui.map_cursor=uint8_t(c.ui.plugin_panel.design_page);}return;
        }
        if(c.ui.map_open)return;''')
 patch('pages/edit_page.cpp','            c.ui.edit_page[c.ui.track]=1;c.ui.kit_common=false;','''            c.ui.edit_page[c.ui.track]=1;c.ui.kit_common=false;c.ui.map_open=false;
            if(c.track().plugin<max_plugins){c.ui.plugin_design_page[c.track().plugin]=0;c.ui.plugin_design_half[c.track().plugin]=0;c.ui.plugin_panel.design=false;}''')
 patch('pages/edit_page.cpp','if(c.plugins)c.plugins->panel(c.track().plugin,c.ui.plugin_row[c.track().plugin],c.ui.plugin_panel);','if(c.plugins)c.refresh_plugin_panel(c.track().plugin);')
 patch('pages/edit_page.cpp','        if(key==2&&c.ui.plugin_panel.entry==c.track().plugin&&std::string(c.ui.plugin_panel.name)=="Rhythmer Kit"){c.ui.kit_common=!c.ui.kit_common;return;}','        if(key==2)return;')
 patch('pages/edit_page.cpp','    if(c.ui.kit_common&&std::string(c.ui.plugin_panel.name)=="Rhythmer Kit")return;', '''    if(c.ui.plugin_panel.design){
        auto& panel=c.ui.plugin_panel;unsigned entry=c.track().plugin;if(entry>=max_plugins||!panel.design_count)return;
        if(c.ui.map_open)c.ui.map_cursor=uint8_t(std::clamp<int>(int(c.ui.map_cursor)+delta,0,panel.design_count-1));
        else {c.ui.plugin_design_page[entry]=uint16_t(std::clamp<int>(int(panel.design_page)+delta,0,panel.design_count-1));c.ui.plugin_design_half[entry]=0;c.refresh_plugin_panel(entry);}return;
    }
    if(c.ui.kit_common&&std::string(c.ui.plugin_panel.name)=="Rhythmer Kit")return;''')
 patch('pages/edit_page.cpp','    if(c.track().engine==EngineKind::Plugin){if(!c.ui.edit_page[c.ui.track])soft(c,2);return;}', '''    if(c.track().engine==EngineKind::Plugin){
        if(!c.ui.edit_page[c.ui.track])soft(c,2);
        else if(c.ui.plugin_panel.design){if(c.ui.map_open)soft(c,2);else {auto& v=c.ui.plugin_panel;if(v.design_count&&v.design_pages[v.design_page].shown[3]>=0){c.ui.plugin_design_half[c.track().plugin]=uint8_t(1-v.design_half);c.refresh_plugin_panel(c.track().plugin);}}}
        return;
    }''')
 patch('pages/edit_page.cpp','    h.left.push_back(pill(juce::String(page.title).toUpperCase(), c));','    h.left.push_back(pill(juce::String(page.title).toUpperCase(), c));\n    h.left.push_back(pill("P "+juce::String(index+1)+"/"+juce::String(count),colour::sec));')
 print('Applied functional plugin pages, fixed control IDs, page map and position indicators')
if __name__=='__main__':
 import sys
 apply(Path(sys.argv[1]))
