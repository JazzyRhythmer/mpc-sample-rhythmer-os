// SPDX-License-Identifier: AGPL-3.0-only
// One functional page, six bounded controls, persistent page and row position.
juce::String design_title(const PluginDesignPage& page){return juce::String(page.title)+(page.parts>1?" "+juce::String(page.part)+"/"+juce::String(page.parts):juce::String());}
void plugin_design(Paint& p,const Snapshot& s){
    const auto& v=s.ui.plugin_panel;float x=zone::pad,y=zone::picture_y,w=zone::width-2*zone::pad;
    if(!v.design_count){
        p.text("P"+juce::String(v.focused_pad+1).paddedLeft('0',2)+" / EMPTY PAD",x,y+18,w,22,plain(colour::text,type::body,Weight::Bold));
        p.text("MAIN > SOURCE",x,y+58,w,18,plain(colour::sec,type::body));
        p.text("Choose an engine and sound",x,y+82,w,16,plain(colour::dim,type::small));return;
    }
    if(s.ui.map_open){
        unsigned cursor=std::min<unsigned>(s.ui.map_cursor,v.design_count-1),first=cursor<2?0:std::min(cursor-2,v.design_count>5?unsigned(v.design_count-5):0);
        p.text("PAGES",x,y,w-75,18,plain(colour::text,type::body,Weight::Bold));
        p.text(juce::String(cursor+1)+" / "+juce::String(v.design_count),x+w-75,y,75,18,plain(colour::sec,type::small),juce::Justification::centredRight);
        for(unsigned i=0;i<5&&first+i<v.design_count;++i){unsigned at=first+i;ListRow r;r.number=juce::String(at+1).paddedLeft('0',2);r.name=design_title(v.design_pages[at]);r.current=at==cursor;r.accent=colour::text;if(at==v.design_page)r.fact_icon=Icon::Check;list_row(p,x,y+21+i*21,w,r);}
        p.text("TURN: CHOOSE   PUSH: OPEN",x,y+130,w,12,plain(colour::dim,type::small));return;
    }
    const auto& page=v.design_pages[v.design_page];auto title=design_title(page);
    p.text(title,x,y,w-75,18,p.fit(title,plain(colour::text,type::body,Weight::Bold),w-75,type::floor));
    p.text(juce::String(v.design_page+1)+" / "+juce::String(v.design_count),x+w-75,y,75,18,plain(colour::sec,type::small),juce::Justification::centredRight);
    p.fill(x,y+19,w,2,colour::line);p.fill(x,y+19,w*float(v.design_page+1)/v.design_count,2,colour::sec);
    juce::String scope=v.focused_pad>=0?"P"+juce::String(v.focused_pad+1).paddedLeft('0',2)+" / ":juce::String();
    auto preset=juce::String::fromUTF8(v.preset);int split=preset.lastIndexOf(" / Pad ");
    if(v.focused_pad>=0&&split>=0){int colon=preset.indexOf(split,": ");if(colon>=0)preset=preset.substring(0,split)+" / "+preset.substring(colon+2);}
    if(v.focused_pad>=0&&v.design_source[0]){scope+=juce::String::fromUTF8(v.design_source);if(split>=0)preset=preset.fromLastOccurrenceOf(" / ",false,false);scope+=" / ";}
    scope+=preset;auto caption_style=plain(colour::sec,type::small);auto lines=p.wrap(scope,caption_style,w,2);
    for(int i=0;i<lines.size();++i)p.text(lines[i],x,y+24+i*11,w,11,caption_style);
    constexpr float top=49,rh=37;float cw=(w-16)/3;
    for(unsigned k=0;k<6;++k){const auto& card=v.window[k];if(!card.used)continue;bool active=k/3==v.design_half;float cx=x+8+(k%3)*(cw+4),cy=y+top+(k/3)*rh;
        p.fill(cx,cy,cw-1,rh-3,active?colour::panel:colour::surf);if(active)p.fill(cx,cy,2,rh-3,colour::text);
        auto name=juce::String::fromUTF8(card.name);if(v.focused_pad>=0&&name.startsWith("P")&&name.substring(1,3).containsOnly("0123456789")&&name[3]==' ')name=name.substring(4);
        if(name.startsWithIgnoreCase("Source "))name=name.substring(7);
        if(name.startsWithIgnoreCase("Global FX "))name=name.substring(10);
        auto group=juce::String(page.title);
        if(group.startsWith("CH")&&name.startsWithIgnoreCase("Ch ")){int end=name.indexOfChar(3,' ');if(end>=0)name=name.substring(end+1);}
        if(group.startsWith("OP")){
            auto number=juce::String(group.substring(2).getIntValue());
            for(const auto& prefix:{"Operator "+number+" ","Op"+number+" Envelope ","Op"+number+" Kbd Scale "})if(name.startsWithIgnoreCase(prefix))name=name.substring(prefix.length());
        }
        if(group=="MODEL"&&name.startsWithIgnoreCase("Machine "))name=name.substring(8);
        if(name.startsWithIgnoreCase(group+" "))name=name.substring(group.length()+1);
        for(const char* prefix:{"Global FX ","Performance ","Filter Env ","Amp Env "}){
            if((group=="FX"||group=="PERFORM"||group.endsWith("FILTER ENV")||group.endsWith("AMP ENV"))&&name.startsWithIgnoreCase(prefix))name=name.substring(int(std::char_traits<char>::length(prefix)));
        }
        auto style=plain(active?colour::text:colour::sec,type::small,active?Weight::SemiBold:Weight::Regular);auto labels=p.wrap(name,style,cw-8,2);
        if(labels.joinIntoString("").removeCharacters(" ").length()<name.removeCharacters(" ").length()){style=plain(active?colour::text:colour::sec,type::floor,Weight::Medium);labels=p.wrap(name,style,cw-8,2);}
        for(int i=0;i<labels.size();++i)p.text(labels[i],cx+5,cy+i*11,cw-8,11,style);
        p.fill(cx+5,cy+28,cw-10,2,colour::line);p.fill(cx+5,cy+28,(cw-10)*card.value/plugin_param_max,2,active?colour::text:colour::mid);
    }
    p.text("A",x,y+top+9,8,12,plain(v.design_half==0?colour::text:colour::dim,type::floor,Weight::Bold));
    if(page.shown[3]>=0)p.text("B",x,y+top+rh+9,8,12,plain(v.design_half?colour::text:colour::dim,type::floor,Weight::Bold));
    p.text(page.shown[3]>=0?"PUSH: ROW A/B   -/+: PAGE":"ROW A   -/+: PAGE",x,y+130,w,12,plain(colour::dim,type::small));
}
