// SPDX-License-Identifier: AGPL-3.0-only
// Render every inspected state; capture_rows only reduces duplicate PNG writes.
#include "rhythmer/pages/performance_art.inc"
int edit_preview(const std::string& folder,const std::string& inventory) {
    EngineHost host;Shell shell(host);board_project(shell);
    auto data=juce::JSON::parse(juce::File(inventory).loadFileAsString());
    unsigned written=0,saved=0,issues_count=0;
    for(int engine=0;engine<data.size();++engine){
        auto item=data[engine],parameters=item["parameters"];
        auto s=std::make_unique<Snapshot>();shell.snapshot(*s,100000);s->ui=UiState{};s->now=100000;s->ui.page=PageId::Edit;s->ui.track=0;s->ui.edit_page[0]=bool(item["home"])?0:1;s->meters[0]=float(item["meter"]);s->now=uint32_t(int(item.getProperty("at",100000)));
        s->project.tracks[0].last_note=uint8_t(int(item.getProperty("note",60)));s->held_keys.fill(-1);if(bool(item["held"]))s->held_keys[0]=s->project.tracks[0].last_note;
        s->project.tracks[0].engine=EngineKind::Plugin;s->project.tracks[0].plugin=0;
        auto name=item["engine"].toString();s->project.tracks[0].set_name(name.toRawUTF8());std::snprintf(s->project.plugins[0].name,sizeof s->project.plugins[0].name,"%s",name.toRawUTF8());
        auto& panel=s->ui.plugin_panel;panel.layout_revision=1;panel.focused_pad=int16_t(int(item.getProperty("focused_pad",-1)));panel.entry=0;panel.status=PluginStatus::Ready;panel.instrument=true;panel.rows=uint16_t((parameters.size()+2)/3);panel.programs=uint16_t(item["programs"].size());
        std::snprintf(panel.name,sizeof panel.name,"%s",name.toRawUTF8());
        std::snprintf(panel.preset,sizeof panel.preset,"%s",item["programs"][0].toString().toRawUTF8());
        const bool browser=bool(item["preset_browser"]),art=bool(item["art_only"]);
        auto pages=item["design_pages"];
        const bool design=!browser&&!art&&!bool(item["home"])&&pages.isArray();
        if(design){std::snprintf(panel.design_source,sizeof panel.design_source,"%s",item["design_source"].toString().toRawUTF8());panel.design=true;panel.design_count=uint16_t(pages.size());for(int i=0;i<pages.size();++i){auto v=pages[i];auto& p=panel.design_pages[size_t(i)];std::snprintf(p.title,sizeof p.title,"%s",v["title"].toString().toRawUTF8());p.part=uint16_t(int(v["part"]));p.parts=uint16_t(int(v["parts"]));for(int n=0;n<6;++n)p.shown[size_t(n)]=int16_t(int(v["shown"][n]));}}
        if(browser){s->ui.page=PageId::PluginPresets;s->ui.presets_back=PageId::Edit;s->ui.presets_entry=0;s->presets.entry=0;std::vector<PluginProgram> programs;for(int i=0;i<item["programs"].size();++i)programs.push_back({i,item["programs"][i].toString().toStdString(),{}});s->presets.list=PluginProgramList(std::move(programs));}
        for(unsigned row=0;row<(browser?unsigned(item["programs"].size()):art?1u:bool(item["home"])?4u:design?std::max(1u,bool(item["page_map"])?unsigned(panel.design_count):unsigned(panel.design_count)*2):panel.rows);++row){
            if(browser){s->ui.presets_cursor=uint16_t(row);s->presets.current=int(row);}
            panel.row=uint16_t(row);s->ui.edit_row[0]=uint8_t(row);if(bool(item["home"]))panel.row=row==3?1:0;panel.window_first=uint16_t((panel.row?panel.row-1:0)*3);panel.params={};panel.window={};
            auto read=[&](int index,PluginPanelParam& p){if(index<0||index>=parameters.size())return;auto v=parameters[index];p.used=true;p.shown=int16_t(index);std::snprintf(p.name,sizeof p.name,"%s",v["name"].toString().toRawUTF8());std::snprintf(p.text,sizeof p.text,"%s",v["text"].toString().toRawUTF8());p.value=int16_t(std::lround(float(v["value"])*plugin_param_max));};
            for(unsigned n=0;n<3;n++)read(int(panel.row*3+n),panel.params[n]);
            for(unsigned n=0;n<6;n++)read(int(panel.window_first+n),panel.window[n]);
            if(design){
                panel.params={};panel.window={};s->ui.map_open=bool(item["page_map"]);s->ui.map_cursor=uint8_t(row);
                panel.design_page=uint16_t(s->ui.map_open?0:row/2);panel.design_half=uint8_t(row%2);
                if(panel.design_count){const auto& p=panel.design_pages[panel.design_page];if(p.shown[3]<0)panel.design_half=0;
                    for(unsigned n=0;n<6;++n)read(p.shown[n],panel.window[n]);
                    for(unsigned n=0;n<3;++n)panel.params[n]=panel.window[panel.design_half*3+n];
                }
                auto bindings=page_bindings(s->project,s->ui,s->pattern);
                for(unsigned n=0;n<3;++n){if(s->ui.map_open){if(bindings[n].kind!=Binding::Kind::None)return 31;}
                    else if(panel.params[n].used){if(bindings[n].kind!=Binding::Kind::PluginParam||int(plugin_binding_shown(bindings[n].id))!=panel.params[n].shown)return 32;ui::KnobCard card;describe_card(*s,bindings[n],card);if(card.value!=panel.params[n].text||card.label!=juce::String(n+1))return 33;}
                    else if(bindings[n].kind!=Binding::Kind::None)return 34;
                }
            }
            for(int scale:{1,2}){
                juce::Image image(juce::Image::ARGB,screen_width*scale,screen_height*scale,true);std::vector<ui::TextIssue> issues;ui::audit_text(scale==1?&issues:nullptr);
                {juce::Graphics g(image);g.addTransform(juce::AffineTransform::scale(float(scale)));if(art){g.fillAll(ui::colour::bg);ui::Paint painter(g);performance_art(painter,*s,name,item["programs"][0].toString(),0,0,320,140,panel.focused_pad);}else draw(g,*s);}ui::audit_text(nullptr);
                for(const auto& i:issues){
                    bool literal=false;
                    if(i.size>=ui::type::floor&&i.needed<=i.box+.5f&&(i.text.contains("...")||i.text.contains(juce::String::fromUTF8("\xe2\x80\xa6"))))
                        for(int n=0;n<item["programs"].size();++n)literal|=item["programs"][n].toString().contains(i.text);
                    // Original names such as DX7 NOW-YOU... contain literal dots.
                    // Keep their measured width/font checks and exact spelling.
                    if(literal)continue;
                    std::printf("EDIT_TEXT %s row=%u \"%s\" size=%.1f\n",name.toRawUTF8(),row,i.text.toRawUTF8(),double(i.size));++issues_count;
                }
                bool capture=item["capture_rows"].isVoid();if(auto* rows=item["capture_rows"].getArray())for(const auto& n:*rows)capture|=int(n)==int(row);
                if(capture||!issues.empty()){char file[100];std::snprintf(file,sizeof file,"/engine-%02d-row-%03u%s.png",engine,row,scale==2?"@2x":"");save_png(image,folder+file);++saved;}
            }++written;
        }
    }
    std::printf("RHYTHMER_EDIT_PREVIEW engines=%d pages=%u saved=%u text_issues=%u\n",data.size(),written,saved,issues_count);return !written||issues_count?1:0;
}
