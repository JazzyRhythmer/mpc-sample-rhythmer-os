// SPDX-License-Identifier: AGPL-3.0-only
#include "rhythmer/pages/performance_art.inc"
void plugin_home(Paint& p,const Snapshot& s,const PluginPanel& panel,bool /*kit*/) {
    const auto name=juce::String::fromUTF8(panel.name);
    const float x=zone::pad,w=zone::width-2*zone::pad,top=zone::picture_y;
    auto preset=juce::String::fromUTF8(panel.preset);if(preset.isEmpty())preset=panel.status==PluginStatus::Loading?"Loading...":"Choose a preset";
    performance_art(p,s,name,preset,0,top+4,zone::width,132,panel.focused_pad>=0?panel.focused_pad:int(s.track().last_pad));
    auto title=plain(colour::text,18,Weight::SemiBold);
    p.fill(x-2,top,std::min(w+4,p.width(name,title)+8),23,colour::bg.withAlpha(.94f));p.text(name,x,top+1,w,21,title);
    auto preset_style=plain(colour::sec,type::small);auto lines=p.wrap(preset,preset_style,w,2);
    for(int i=0;i<lines.size();i++){float yy=top+24+i*13;p.fill(x-2,yy,std::min(w+4,p.width(lines[i],preset_style)+8),13,colour::bg.withAlpha(.94f));p.text(lines[i],x,yy,w,13,preset_style);}
    // Retired layout/page-group caption: keep the footer band clear.
    p.fill(0,top+128,zone::width,16,colour::bg);
}
