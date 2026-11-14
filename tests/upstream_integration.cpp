// SPDX-License-Identifier: AGPL-3.0-only
// Rhythmer custom state and Melodee 0.2.0 features must coexist in one project.
#include "rhythmer/model/project_file.h"
#include "rhythmer/plugin/plugin_files.h"
#include "rhythmer/plugin/plugin_panel.h"
#include "rhythmer/shell/pad_context.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
using namespace rhythmer;
void require(bool b,const char* why){if(!b)throw std::runtime_error(why);}
int main(){
    static_assert(pattern_count==128);
    auto p=std::make_unique<Project>();auto bank=std::make_unique<PatternBank>();
    p->gen8.group=3;p->gen8.assign=0;p->gen8.first=p->gen8.last=15;
    auto& br=p->tracks[0];br.engine=EngineKind::Sampler;br.break_bars=4;br.break_source=1;
    br.break_perf[0]=71;br.acid_gen.seed=0xffffffffu;br.acid_gen.slide=71;
    std::strcpy(p->samples[0].path,"/card/Samples/break.wav");br.pads[3].sample=0;br.pads[3].sends={37,0,0,99};
    p->tracks[15].engine=EngineKind::Plugin;p->tracks[15].plugin=0;p->tracks[15].pattern=127;
    std::strcpy(p->plugins[0].path,"Plugins/RHYTHMER - Rhythmer Kit");std::strcpy(p->plugins[0].name,"Rhythmer Kit");p->plugins[0].transport=false;
    Event e;e.tick=24;e.key=60;e.velocity=101;e.length=48;bank->at[15][127].add(e);
    std::array<std::vector<uint8_t>,max_plugins> state;state[0]={1,9,7,3};
    PrintTable prints;PrintRecord print;print.track=15;print.pattern=127;print.frames=128;print.pass=128;print.file="T16-H16.wav";print.sends=9;
    prints.records.push_back(print);prints.freeze[15].state=FreezeState::Deep;prints.freeze[15].set(127,true);
    auto bytes=save_project(*p,*bank,&state,&prints);
    require(std::memcmp(bytes.data(),"MELODEE1",8)==0,"Project identity changed");
    auto q=std::make_unique<Project>();auto b=std::make_unique<PatternBank>();PrintTable restored;decltype(state) back;
    require(load_project(bytes,*q,*b,nullptr,&back,&restored).empty(),"Mixed project did not load");
    require(q->gen8.group==3&&q->gen8.first==15&&q->gen8.last==15&&!q->gen8.assign,"GEN target changed");
    require(q->tracks[0].break_bars==4&&q->tracks[0].break_source==1&&q->tracks[0].break_perf[0]==71,"Break state lost");
    require(q->tracks[0].acid_gen.seed==0xffffffffu&&q->tracks[0].acid_gen.slide==71,"Acid seed/settings lost");
    require(q->tracks[0].pads[3].sends==br.pads[3].sends,"Native pad sends lost");
    require(q->tracks[15].pattern==127&&b->at[15][127].events==bank->at[15][127].events,"H16 pattern lost");
    require(!q->plugins[0].transport&&back==state&&restored==prints,"Plugin/Freeze state lost");
    PluginPanel panel;panel.entry=2;panel.design=true;panel.row=0;panel.params[1].used=true;panel.params[1].shown=72;panel.params[1].initial=321;panel.params[1].steps=9;
    auto* card=plugin_card(panel,plugin_binding(2,72));require(card==&panel.params[1],"Design-page default/reset ID mismatch");
    require(plugin_card(panel,plugin_binding(1,72))==nullptr&&plugin_card(panel,plugin_binding(2,73))==nullptr,"Stale parameter accepted");
    require(plugin_param_step(*card,0,1)==125&&plugin_param_step(*card,1000,1)==1000,"Discrete parameter step changed");
    UiState ui;ui.page=PageId::Patterns;PadFacts facts;require(pad_context(ui,br,facts,0)==PadContext::SeqLayer,"Pattern launch changed");
    ui.sheet_open=true;require(pad_context(ui,br,facts,0)==PadContext::Page,"GEN audition launched a pattern");
    PluginProgramList presets({{0,"A11 Brass",{}},{1,"Warm Strings","Factory"}});auto copy=presets;require(copy.size()==2&&copy[1].folder=="Factory","Shared presets lost names/folders");
    std::puts("upstream integration ok: H16, GEN, Acid, Break, sends, Freeze, transport, preset and page IDs");
}
