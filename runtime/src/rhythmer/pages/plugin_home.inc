// SPDX-License-Identifier: AGPL-3.0-only
#include "rhythmer/pages/performance_art.inc"
void plugin_home(Paint& p,const Snapshot& s,const PluginPanel& panel,bool kit) {
    const auto name=juce::String::fromUTF8(panel.name);
    const float x=zone::pad,w=zone::width-2*zone::pad,top=zone::picture_y;
    auto preset=juce::String::fromUTF8(panel.preset);if(preset.isEmpty())preset=panel.status==PluginStatus::Loading?"Loading...":"Choose a preset";
    performance_art(p,s,name,preset,0,top+4,zone::width,132,panel.focused_pad>=0?panel.focused_pad:int(s.track().last_pad));
    auto title=plain(colour::text,18,Weight::SemiBold);
    p.fill(x-2,top,std::min(w+4,p.width(name,title)+8),23,colour::bg.withAlpha(.94f));p.text(name,x,top+1,w,21,title);
    auto preset_style=plain(colour::sec,type::small);auto lines=p.wrap(preset,preset_style,w,2);
    for(int i=0;i<lines.size();i++){float yy=top+24+i*13;p.fill(x-2,yy,std::min(w+4,p.width(lines[i],preset_style)+8),13,colour::bg.withAlpha(.94f));p.text(lines[i],x,yy,w,13,preset_style);}
    const int count=panel.layout_revision?4:2,row=s.ui.edit_row[s.ui.track]%count;
    const char* groups[]{"MIX","SENDS B / C / D","SOURCE","SAVE"};
    const int focus=panel.focused_pad>=0?panel.focused_pad:int(s.track().last_pad);
    auto scope=kit?"BANK "+juce::String::charToString(char('A'+focus/16))+" / P"+juce::String(focus+1):s.track().layout==PadLayout::Chromatic?juce::String("CHROMATIC"):juce::String("SCALE");
    auto label=scope+"   "+juce::String(row+1)+"/"+juce::String(count)+"  "+(row==2&&kit?"PAD SOURCE":row==3?(kit?"SAVE KIT":"SAVE SOUND"):groups[row]);
    p.fill(0,top+128,zone::width,16,colour::bg);p.text(label,x,top+130,w,13,plain(colour::sec,type::small));
}
