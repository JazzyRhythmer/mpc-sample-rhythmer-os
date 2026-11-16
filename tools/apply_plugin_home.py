"""A small common engine landing page, using existing mixer and sound cards."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
def apply(root):
 def patch(file,old,new):
  p=root/'src/rhythmer'/file;s=p.read_text();assert s.count(old)==1,(file,old[:90],s.count(old));p.write_text(s.replace(old,new))
 target=root/'src/rhythmer/pages/plugin_home.inc';shutil.copy2(ROOT/'extensions/pages/plugin_home.inc',target)
 shutil.copy2(ROOT/'extensions/pages/performance_art.inc',root/'src/rhythmer/pages/performance_art.inc')
 patch('pages/stage_page.cpp','namespace rhythmer {','namespace rhythmer {\n#include "rhythmer/pages/performance_art.inc"')
 patch('pages/stage_page.cpp','    float sx = x_of(region_from), ex = x_of(region_to);','''    if(t.break_bars)performance_art(p,s,"Break Engine","User loop",wx,wy,ww,wh,int(t.last_pad),0.17f);
    float sx = x_of(region_from), ex = x_of(region_to);''')
 patch('pages/common.h','ui::HeaderItem tag_of(const Snapshot& s, unsigned track);','juce::String track_display_name(const Snapshot& s,unsigned track);\nui::HeaderItem tag_of(const Snapshot& s, unsigned track);')
 patch('pages/common.cpp','ui::HeaderItem tag_of(const Snapshot& s, unsigned track) {', '''juce::String track_display_name(const Snapshot& s,unsigned track) {
    const auto& t=s.project.tracks[track%track_count];auto label=t.used()?name_case(t.name):juce::String("Empty");
    if(t.engine==EngineKind::Plugin&&t.plugin<max_plugins){
        auto original=juce::String::fromUTF8(s.project.plugins[t.plugin].name);auto stored=juce::String::fromUTF8(t.name);
        if(original.isNotEmpty()&&(stored.equalsIgnoreCase(original)||stored.equalsIgnoreCase(original.substring(0,int(sizeof(t.name))-1))))label=original;
    }
    return label;
}

ui::HeaderItem tag_of(const Snapshot& s, unsigned track) {''')
 patch('pages/common.cpp','t.used() ? name_case(t.name) : "Empty",','track_display_name(s,track),')
 patch('pages/track_grid.cpp','p.wrap(name_case(track.name), name, iw, 2)','p.wrap(track_display_name(s,t), name, iw, 2)')
 patch('pages/stage_page.cpp','p.text(name_case(juce::String(t.name)), px, top + 4, 140, 20, p.fit(name_case(juce::String(t.name)),','p.text(track_display_name(s,s.ui.track), px, top + 4, 140, 20, p.fit(track_display_name(s,s.ui.track),')
 patch('pages/edit_page.cpp','#include "rhythmer/ui/widgets.h"','#include "rhythmer/ui/widgets.h"\n#include "rhythmer/plugin/plugin_rack.h"')
 patch('pages/edit_page.cpp','void draw(Paint& p, const Snapshot& s) {','#include "rhythmer/pages/plugin_home.inc"\n\nvoid draw(Paint& p, const Snapshot& s) {')
 patch('pages/edit_page.cpp','        frame(p,s,{{"PLUG-INS",presets?"PRESETS":"",kit?(s.ui.kit_common?"PAD EDIT":"KIT MIX"):""},-1,c},h);', '''        bool home=s.ui.edit_page[s.ui.track]==0;
        frame(p,s,{{home?"PLUG-INS":"MAIN",presets?"PRESETS":"",home?(kit?"EDIT PAD":"EDIT SOUND"):kit?(s.ui.kit_common?"PAD EDIT":"KIT MIX"):""},-1,c},h);
        if(home&&ours&&panel.status==PluginStatus::Ready){plugin_home(p,s,panel,kit);return;}''')
 patch('pages/edit_page.cpp','        if(key==2&&c.ui.plugin_panel.entry==c.track().plugin', '''        if(key==0&&c.ui.edit_page[c.ui.track]){c.back();return;}
        if(key==2&&!c.ui.edit_page[c.ui.track]){
            c.ui.edit_page[c.ui.track]=1;c.ui.kit_common=false;
            if(c.track().plugin<max_plugins){c.ui.plugin_row[c.track().plugin]=std::min<unsigned>(c.ui.plugin_panel.layout_revision?2:0,c.ui.plugin_panel.rows?c.ui.plugin_panel.rows-1:0);if(c.plugins)c.plugins->panel(c.track().plugin,c.ui.plugin_row[c.track().plugin],c.ui.plugin_panel);}
            c.plugin_panel_at=0;return;
        }
        if(key==2&&c.ui.plugin_panel.entry==c.track().plugin''')
 patch('pages/edit_page.cpp','void plugin_rows(Context& c, int delta) {', '''void plugin_rows(Context& c, int delta) {
    if(!c.ui.edit_page[c.ui.track]){
        const int count=c.ui.plugin_panel.layout_revision?4:2;
        c.ui.edit_row[c.ui.track]=uint8_t((int(c.ui.edit_row[c.ui.track])+delta%count+count)%count);
        if(c.track().plugin<max_plugins){auto& row=c.ui.plugin_row[c.track().plugin];row=c.ui.edit_row[c.ui.track]==3?1:0;if(c.plugins)c.plugins->panel(c.track().plugin,row,c.ui.plugin_panel);}
        c.plugin_panel_at=0;return;
    }''')
 patch('pages/edit_page.cpp','    c.ui.plugin_panel.row = row;','    c.ui.plugin_panel.row = row;\n    if(c.plugins)c.plugins->panel(entry,row,c.ui.plugin_panel);')
 patch('pages/edit_page.cpp','void push(Context& c) {','void push(Context& c) {\n    if(c.track().engine==EngineKind::Plugin){if(!c.ui.edit_page[c.ui.track])soft(c,2);return;}')
 patch('shell/bindings.cpp','    case PageId::Edit: {','''    case PageId::Edit: {
        if(track.engine==EngineKind::Plugin&&!ui.edit_page[ui.track]){
            const unsigned row=ui.edit_row[ui.track]%4;
            if(row==0)return {Binding{Kind::Level,0,0,127,track.mix.level},Binding{Kind::Pan,0,-50,50,track.mix.pan},Binding{Kind::Send,0,0,100,track.mix.sends[0]}};
            if(row==1)return {Binding{Kind::Send,1,0,100,track.mix.sends[1]},Binding{Kind::Send,2,0,100,track.mix.sends[2]},Binding{Kind::Send,3,0,100,track.mix.sends[3]}};
            return plugin_cards(ui,track.plugin);
        }''')
 patch('shell/context.cpp','void Context::open(PageId page) {','''void Context::open(PageId page) {
    if(page==PageId::Edit&&track().engine==EngineKind::Plugin&&ui.page!=PageId::PluginPresets){
        ui.edit_page[ui.track]=0;ui.edit_row[ui.track]=0;ui.kit_common=false;
        if(track().plugin<max_plugins){ui.plugin_row[track().plugin]=0;}plugin_panel_at=0;
    }''')
 patch('shell/context.cpp','void Context::back() {','''void Context::back() {
    if(ui.page==PageId::Edit&&track().engine==EngineKind::Plugin&&ui.edit_page[ui.track]){
        ui.edit_page[ui.track]=0;ui.kit_common=false;
        if(track().plugin<max_plugins){auto& row=ui.plugin_row[track().plugin];row=ui.edit_row[ui.track]==3?1:0;if(plugins)plugins->panel(track().plugin,row,ui.plugin_panel);}plugin_panel_at=0;return;
    }''')
 # Actual edit-label renders must remain on the parameter page, not the home.
 patch('tools.cpp','s.ui.kit_common=true;}},','s.ui.kit_common=true;s.ui.edit_page[s.ui.track]=1;}},')
 patch('tools.cpp','const Preview previews[] {','''const Preview previews[] {
    {"break-performance-wave",[](Shell&,Snapshot& s){on_stage(s,3,0,0);s.project.tracks[3].break_bars=2;s.sample=break_sample();s.playing=true;s.meters[3]=.65f;stage_voice(s,0,7,96000,.9f);}},
    {"plugin-home-sophie",[](Shell&,Snapshot& s){plugin_track(s,PluginStatus::Ready);s.ui.plugin_panel.layout_revision=1;s.project.tracks[s.ui.track].set_name("Sophie");std::snprintf(s.ui.plugin_panel.name,sizeof(s.ui.plugin_panel.name),"Sophie");std::snprintf(s.ui.plugin_panel.preset,sizeof(s.ui.plugin_panel.preset),"Factory / Metallic Kick");s.meters[s.ui.track]=0.6f;}},
    {"plugin-home-aphex",[](Shell&,Snapshot& s){plugin_track(s,PluginStatus::Ready);s.ui.plugin_panel.layout_revision=1;s.project.tracks[s.ui.track].set_name("Aphex");std::snprintf(s.ui.plugin_panel.name,sizeof(s.ui.plugin_panel.name),"Aphex");std::snprintf(s.ui.plugin_panel.preset,sizeof(s.ui.plugin_panel.preset),"Acid Squelch");s.meters[s.ui.track]=0.4f;s.ui.edit_row[s.ui.track]=1;}},
    {"plugin-home-kit-pad11",[](Shell&,Snapshot& s){plugin_track(s,PluginStatus::Ready);s.ui.plugin_panel.layout_revision=1;s.project.tracks[s.ui.track].set_name("Rhythmer Kit");std::snprintf(s.ui.plugin_panel.name,sizeof(s.ui.plugin_panel.name),"Rhythmer Kit");std::snprintf(s.ui.plugin_panel.preset,sizeof(s.ui.plugin_panel.preset),"Elixir / Modal Kit / Pad 11: Percussion");s.ui.plugin_panel.focused_pad=10;s.meters[s.ui.track]=0.8f;}},''')
 patch('plugin/plugin_rack.cpp','    out.layout_revision=sound_rack_revision(h->instance.get());', '    if(!out.preset[0]&&h->instance->getNumPrograms()>0)put(out.preset,sizeof(out.preset),h->instance->getProgramName(h->instance->getCurrentProgram()).toStdString());\n    out.layout_revision=sound_rack_revision(h->instance.get());')
 patch('shell/context.cpp','    ui.track = uint8_t(t % track_count);', '    ui.track = uint8_t(t % track_count);\n    if(ui.page==PageId::Edit&&track().engine==EngineKind::Plugin){ui.edit_page[ui.track]=0;ui.edit_row[ui.track]=0;ui.kit_common=false;if(track().plugin<max_plugins)ui.plugin_row[track().plugin]=0;plugin_panel_at=0;}')
 patch('shell/plugin_jobs.cpp','    plugin_panel_at=0;\n    dirty = true;', '    if(shown==0&&ui.plugin_panel.entry==entry&&ui.plugin_panel.focused_pad>=0){for(auto& t:project.tracks)if(t.engine==EngineKind::Plugin&&t.plugin==entry){t.last_pad=uint8_t(ui.plugin_panel.focused_pad);t.bank=uint8_t(ui.plugin_panel.focused_pad/16);t.last_note=uint8_t(36+ui.plugin_panel.focused_pad);}}\n    plugin_panel_at=0;\n    dirty = true;')
 patch('ui/knobs.cpp','        if(vw<0&&!low&&p.width(c.value,plain(value.colour,type::floor,Weight::Medium))>room) {','        bool tall_value=false;\n        if(vw<0&&!low&&p.width(c.value,plain(value.colour,type::floor,Weight::Medium))>room) {')
 patch('ui/knobs.cpp','auto lines=p.wrap(c.value,style,room,2);\n            for(int i=0;i<lines.size();++i)p.text(lines[i],inner,top+13+i*12,room,12,style);','auto lines=p.wrap(c.value,style,room,3);tall_value=lines.size()>2;float line_h=tall_value?11.0f:12.0f;\n            for(int i=0;i<lines.size();++i)p.text(lines[i],inner,top+13+i*line_h,room,line_h,style);')
 patch('ui/knobs.cpp','float gy = top + 40, fill =', 'float gy = top + (tall_value?48:40), fill =')
 print('Applied common engine home, four common-control pages and input-driven geometric sculptures')
if __name__=='__main__':
 import sys
 apply(Path(sys.argv[1]))
