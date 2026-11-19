#!/usr/bin/env python3
"""Integrate the sound/kit host into a generated runtime, never vendor sources."""
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
def replace(path,old,new):
    s=path.read_text()
    if s.count(old)!=1:raise RuntimeError('Sound rack anchor changed: '+str(path)+' '+old[:60])
    path.write_text(s.replace(old,new))
def apply(root):
    target=root/'src/rhythmer/plugin'
    for p in (ROOT/'extensions/plugin').glob('sound_rack.*'):shutil.copy2(p,target/p.name)
    shutil.copy2(ROOT/'extensions/plugin/kit_output_stage.h',target/'kit_output_stage.h')
    p=target/'vst2_instance.h'
    replace(p,'    // Opcodes the plug-in sent', '    bool nativeSet(const juce::String& key,const juce::String& value);\n\n    // Opcodes the plug-in sent')
    p=target/'vst2_instance.cpp'
    replace(p,'String Vst2Instance::unansweredHostOpcodes() const', '''bool Vst2Instance::nativeSet(const String& key,const String& value) {
    const char* pair[]{key.toRawUTF8(),value.toRawUTF8()};
    return dispatch(0x47720001,0,0,const_cast<void*>(static_cast<const void*>(pair)))==1;
}

String Vst2Instance::unansweredHostOpcodes() const''')
    p=target/'plugin_files.cpp'
    replace(p,'    juce::File meta(juce::String((folder / "plugin-meta.xml").string()));','''    if ((fs::is_regular_file(folder / "rhythmer-kit.json") || fs::is_regular_file(folder / "groove-kit.json"))) {
        f.name="Rhythmer Kit"; f.instrument=1; f.format=PluginFormat::Vst2; f.fixed_rate=44100;
        for(int i=0;i<64;++i) f.drums.push_back({uint8_t(36+i),"Pad "+std::to_string(i+1)});
        return true;
    }
    juce::File meta(juce::String((folder / "plugin-meta.xml").string()));''')
    replace(p,'    read_drums(f, (folder / so).string());','    read_drums(f, (folder / so).string());\n    // Percussion engines are single sounds outside Rhythmer Kit.\n    f.drums.clear();\n    if(f.name=="Elixir Kit")f.name="Elixir";\n    else if(f.name=="Hortator Kit")f.name="Hortator";\n    else if(f.name=="K-WASUB Kit")f.name="K-WASUB Drums";')
    replace(p,'        if (a.folder != b.folder) return a.folder;','''        if ((a.name=="Rhythmer Kit") != (b.name=="Rhythmer Kit")) return a.name=="Rhythmer Kit";
        if (a.folder != b.folder) return a.folder;''')
    replace(p,'    std::sort(out.begin(), out.end(), [](const PluginFile& a, const PluginFile& b) {','''    out.erase(std::remove_if(out.begin(),out.end(),[](const PluginFile& f){auto p=fs::path(f.path);auto name=p.filename().string();if(name.rfind("GROOVE - ",0)!=0)return false;auto target=name=="GROOVE - Groove Kit"?"RHYTHMER - Rhythmer Kit":"RHYTHMER - "+name.substr(9);return fs::exists(p.parent_path()/target);}),out.end());
    std::sort(out.begin(), out.end(), [](const PluginFile& a, const PluginFile& b) {''')
    p=target/'plugin_rack.cpp'
    replace(p,'#include "rhythmer/plugin/plugin_rack.h"','#include "rhythmer/plugin/plugin_rack.h"\n#include "rhythmer/plugin/sound_rack.h"\n#include <map>\n#include <numeric>')
    replace(p,'    auto file = describe_plugin(path);','''    {auto legacy=fs::path(path);auto name=legacy.filename().string();if(name.rfind("GROOVE - ",0)==0){auto target=name=="GROOVE - Groove Kit"?"RHYTHMER - Rhythmer Kit":"RHYTHMER - "+name.substr(9);auto canonical=legacy.parent_path()/target;if(fs::exists(canonical)||!fs::exists(path))path=canonical.string();}}
    auto file = describe_plugin(path);''')
    replace(p,'    Known found;\n    found.path = file.path;','''    Known found;
    found.path = file.path;
    if (file.name=="Rhythmer Kit") {found.name="Rhythmer Kit";found.instrument=1;return found;}''')
    replace(p,'    if (file.format == PluginFormat::Vst3) {\n        message_thread().start();\n        juce::VST3PluginFormatHeadless format;\n        juce::OwnedArray<juce::PluginDescription> types;\n        message_thread().run([&] { format.findAllTypesForFile(types, juce::String(staged_path(file, stage))); });\n        const juce::PluginDescription* chosen', '''    if (file.name=="Rhythmer Kit" || file.format==PluginFormat::Vst2) {
        fs::path catalog_path=fs::path(card_top)/"Plugins/RHYTHMER - Rhythmer Kit/rhythmer-kit.json";
        if(!fs::exists(catalog_path))catalog_path=fs::path(card_top)/"Plugins/GROOVE - Groove Kit/groove-kit.json";
        auto catalog=juce::JSON::parse(juce::File(catalog_path.string()).loadFileAsString());
        if(auto* object=catalog.getDynamicObject())object->setProperty("user_directory",juce::String((fs::path(card_top)/"Rhythmer/Presets").string()));
        if(auto* object=catalog.getDynamicObject())object->setProperty("legacy_user_directory",juce::String((fs::path(card_top)/"Groove/Presets").string()));
        auto engines=catalog.getProperty("engines",{});int single=-2;
        if(file.name=="Rhythmer Kit") single=-1;
        else if(auto* list=engines.getArray()) for(int i=0;i<list->size();++i)
            if((*list)[i].getProperty("folder",{}).toString().toStdString()==fs::path(file.path).filename().string()) single=i;
        if(single>=-1) {
            auto cache=std::make_shared<std::map<std::string,std::string>>();
            const std::string plugins=(fs::path(card_top)/"Plugins").string();
            SoundLoader loader=[cache,plugins,stage,rate,block](const std::string& folder,juce::String& error)->std::unique_ptr<juce::AudioPluginInstance>{
                auto it=cache->find(folder);
                if(it==cache->end()) {
                    auto original=describe_plugin((fs::path(plugins)/folder).string());
                    if(original.format!=PluginFormat::Vst2 || !original.loadable()){error="Unsupported kit engine";return {};}
                    const auto copy=stage/("child-"+std::to_string(cache->size()));std::string why;
                    if(!stage_copy(original,copy,why)){error=why;return {};}
                    it=cache->emplace(folder,staged_library(original,copy)).first;
                }
                return Vst2Instance::load(juce::File(it->second),rate,block,error);
            };
            instance=make_sound_rack(catalog,single,std::move(loader),rate,block,why);
        } else if(file.name!="Rhythmer Kit") instance=Vst2Instance::load(juce::File(library),rate,block,why);
        else why="Missing Rhythmer Kit sound catalogue";
    } else if (file.format == PluginFormat::Vst3) {
        message_thread().start();
        juce::VST3PluginFormatHeadless format;
        juce::OwnedArray<juce::PluginDescription> types;
        message_thread().run([&] { format.findAllTypesForFile(types, juce::String(staged_path(file, stage))); });
        const juce::PluginDescription* chosen''')
    replace(p,'    out.qlinks = h->qlinks;','''    const int sound_controls=sound_rack_parameter_count(h->instance.get());
    if(sound_controls>=0) {h->shown.resize(size_t(sound_controls));std::iota(h->shown.begin(),h->shown.end(),0);}
    out.qlinks = h->qlinks;''')
    replace(p,'    out.list = e.live->programs;', '    if(is_sound_rack(e.live->instance.get())&&e.live->programs.size()!=size_t(e.live->instance->getNumPrograms()))e.live->programs=named_programs(*e.live->instance);\n    out.list = e.live->programs;')
    replace(p,'    for (const auto& v : entries[entry].file.drums) {','    if(entries[entry].live&&sound_rack_drum_voices(entries[entry].live->instance.get(),out))return;\n    for (const auto& v : entries[entry].file.drums) {')
    # Native identity and project paths stay stable. Dynamic parameter pages
    # are projected by sound_rack rather than hiding controls behind Q-links.
    replace(p,'    if (file.format != PluginFormat::Vst3) { // an Open MPC skin\'s Q-Link pages first, then the rest','    if (file.format != PluginFormat::Vst3 && !is_sound_rack(handle->instance.get())) { // original Q-links')
    p=root/'src/rhythmer/shell/plugin_jobs.cpp'
    replace(p,'    split_shared_plugins();', '''    for(auto& t:project.tracks) if(t.engine==EngineKind::Plugin&&t.plugin<max_plugins) {
        const std::string path=project.plugins[t.plugin].path;
        if(path.find("RHYTHMER - Rhythmer Kit")!=std::string::npos||path.find("GROOVE - Groove Kit")!=std::string::npos){use_drum_pads(t);auto& ref=project.plugins[t.plugin];if(std::string(ref.name)=="Groove Kit")std::snprintf(ref.name,sizeof(ref.name),"Rhythmer Kit");if(std::string(t.name)=="GROOVE KIT")t.set_name("RHYTHMER KIT");}
        else if(t.layout==PadLayout::Drums){t.layout=PadLayout::Scale;if(t.octave==2)t.octave=4;}
    }
    split_shared_plugins();''')
    p=target/'plugin_panel.h'
    replace(p,'    char name[32] {};','    char name[32] {};\n    char preset[128] {};')
    replace(p,'    char text[20] {};','    char text[128] {};')
    p=target/'plugin_rack.cpp'
    replace(p,'    out.qlinks = h->qlinks;', '    put(out.preset,sizeof(out.preset),sound_rack_preset_name(h->instance.get()).toStdString());\n    out.qlinks = h->qlinks;')
    p=root/'src/rhythmer/pages/plugin_view.cpp'
    replace(p,'    constexpr float row_h = 23;', '''    if(panel.preset[0]) {
        auto style=plain(colour::text,type::body,Weight::SemiBold);
        auto lines=p.wrap(juce::String::fromUTF8(panel.preset),style,w-12,3);
        const float height=lines.size()*14.0f+2;
        p.fill(x,top,w,height,colour::surf);
        for(int i=0;i<lines.size();++i)p.text(lines[i],x+6,top+i*14,w-12,14,style);
        top+=height+2;
    }
    const float row_h = panel.preset[0]?std::min(23.0f,(zone::picture_y+zone::picture_h-top-2)/6.0f):23.0f;''')
    p=root/'src/rhythmer/shell/context.cpp'
    replace(p,'    if (!t.used()) return;\n    if (t.levels)', '''    if (!t.used()) return;
    if(t.engine==EngineKind::Plugin&&t.plugin<max_plugins&&plugins&&!t.levels&&(std::string(project.plugins[t.plugin].path).find("RHYTHMER - Rhythmer Kit")!=std::string::npos||std::string(project.plugins[t.plugin].path).find("GROOVE - Groove Kit")!=std::string::npos)) {
        unsigned slot=16*drum_bank(t)+pad;t.last_pad=uint8_t(slot);
        plugins->set_param(t.plugin,0,int(std::lround(slot*1000.0/63)));
    }
    if (t.levels)''')
    p=root/'src/rhythmer/pages/track_grid.cpp'
    replace(p,'    if (!track.used()) {\n        p.fill(x, y, cell_w, cell_h, colour::quiet, 3);\n        p.text(number, x + 6, y + 2, 24, 16, plain(colour::dim, type::body, Weight::Bold));\n        return;\n    }', '''    if (!track.used()) {
        bool selected=t==s.ui.track;
        p.fill(x,y,cell_w,cell_h,selected?colour::raised:colour::quiet,3);
        if(selected){p.ring(x+0.75f,y+0.75f,cell_w-1.5f,cell_h-1.5f,colour::text,0,1.5f);p.fill(x,y,2.5f,cell_h,colour::text);}
        p.text(number,x+6,y+2,24,16,plain(selected?colour::text:colour::dim,type::body,Weight::Bold));
        if(selected)p.text("EMPTY",x+6,y+16,cell_w-8,14,plain(colour::text,type::small));
        return;
    }''')
    replace(p,'    if (selected) p.fill(x, y, 2.5f, cell_h, c, 1);','    if(selected){p.fill(x,y,2.5f,cell_h,colour::text);p.ring(x+0.75f,y+0.75f,cell_w-1.5f,cell_h-1.5f,colour::text,0,1.5f);}')
    replace(p,'    if (!track.used()) return;', '    if (!track.used()) {p.text("EMPTY",x+6,y+22,strip_w-12,16,plain(colour::text,type::small));p.ring(x+0.5f,y+0.5f,strip_w-1,h-1,colour::text,0,1);return;}')
    p=root/'src/rhythmer/pages/common.cpp'
    replace(p,'        c.value = juce::String::fromUTF8(card.text);', '''        c.value = juce::String::fromUTF8(card.text);
        if(s.ui.plugin_panel.preset[0]&&(juce::String::fromUTF8(card.name)=="Sound"||juce::String::fromUTF8(card.name).endsWith(" Sound"))&&c.value.length()>16)c.value="NAME ABOVE";''')
    p=root/'src/rhythmer/tools.cpp'
    replace(p,'const Preview previews[] {','const Preview previews[] {\n'+r"""
    {"empty-track-cursor", [](Shell&,Snapshot& s){s.ui.page=PageId::Tracks;s.ui.track=7;s.project.tracks[7]=Track{};}},
    {"empty-track-overlay", [](Shell&,Snapshot& s){s.ui.page=PageId::Tracks;s.ui.track=11;s.project.tracks[11]=Track{};}},
    {"kit-model-label", [](Shell&,Snapshot& s){plugin_track(s,PluginStatus::Ready);auto& p=s.ui.plugin_panel;std::snprintf(p.name,sizeof(p.name),"Rhythmer Kit");std::snprintf(p.preset,sizeof(p.preset),"Hortator / Pad 3: MD TRX Closed Hat");std::snprintf(p.params[0].name,sizeof(p.params[0].name),"P03 Sound model");std::snprintf(p.params[0].text,sizeof(p.params[0].text),"MD TRX Closed Hat [CHTRX]");p.window[0]=p.params[0];}},
    {"prophet-linked-preset", [](Shell&,Snapshot& s){plugin_track(s,PluginStatus::Ready);auto& p=s.ui.plugin_panel;std::snprintf(p.name,sizeof(p.name),"Prophet");std::snprintf(p.preset,sizeof(p.preset),"Rhythmer Bright Keys");std::snprintf(p.params[0].name,sizeof(p.params[0].name),"Sound");std::snprintf(p.params[0].text,sizeof(p.params[0].text),"Rhythmer Bright Keys");p.window[0]=p.params[0];}},
    {"sound-named-preset", [](Shell&,Snapshot& s){plugin_track(s,PluginStatus::Ready);std::snprintf(s.ui.plugin_panel.preset,sizeof(s.ui.plugin_panel.preset),"MINI LEAD");}},
    {"kit-named-preset", [](Shell&,Snapshot& s){plugin_track(s,PluginStatus::Ready);std::snprintf(s.ui.plugin_panel.name,sizeof(s.ui.plugin_panel.name),"Rhythmer Kit");std::snprintf(s.ui.plugin_panel.preset,sizeof(s.ui.plugin_panel.preset),"DRUM-X / Industrial / Pad 12: High Tom");}},
""")
    p=root/'src/rhythmer/ui/knobs.cpp'
    replace(p,'        if(vw<0) vw = p.text(c.value, inner, low ? top + 23 : top + 15, room, low ? 16 : 22, shown);', '''        if(vw<0&&!low&&p.width(c.value,plain(value.colour,type::floor,Weight::Medium))>room) {
            auto style=plain(value.colour,type::floor,Weight::Medium);auto lines=p.wrap(c.value,style,room,2);
            for(int i=0;i<lines.size();++i)p.text(lines[i],inner,top+13+i*12,room,12,style);
            vw=room;
        }
        if(vw<0) vw = p.text(c.value, inner, low ? top + 23 : top + 15, room, low ? 16 : 22, shown);''')
    print('Applied single-sound/Rhythmer Kit host')
if __name__=='__main__':apply(Path(sys.argv[1]))
