#!/usr/bin/env python3
"""Engine-scoped GEN navigation. Applied after workflow compatibility fields."""
from pathlib import Path
import sys
p=Path(sys.argv[1])/'src/rhythmer/pages/steps_page.cpp'
s=p.read_text()
s=s.replace('"GENERATE RANGE","MUTATE RANGE"','"GENERATE SONG","MUTATE SONG"').replace('"BREAK MENU","VARIATIONS"','"ENGINE GEN","GEN SETUP"')
s=s.replace('m.count=s.ui.gen8_mode==2?6:6;', '''bool br=s.track().engine==EngineKind::Sampler&&s.track().break_bars;
            bool acid=s.track().engine==EngineKind::Plugin&&s.track().plugin<max_plugins&&std::string(s.project.plugins[s.track().plugin].name)=="Acid Engine";
            m.count=s.ui.gen8_mode==4?2:6;''')
s=s.replace('m.title=s.ui.gen8_mode==2?', '''if(s.ui.gen8_mode==0&&!s.project.gen8.assign){m.rows[0]={"GENERATE MIDI",{},false,false,false};m.rows[1]={"MUTATE MIDI",{},false,false,false};}
            if(s.ui.gen8_mode==0)m.rows[4]={br?"BREAK GEN":acid?"ACID GEN":"VARIATIONS",{},false,false,false};
            if(s.ui.gen8_mode==4){m.rows[0]={"GENERATE ACID",{},false,false,false};m.rows[1]={"MUTATE ACID",{},false,false,false};}
            m.title=s.ui.gen8_mode==4?"HORTATOR ACID / TRACK":s.ui.gen8_mode==2?''')
s=s.replace('" SOUND + MIDI":" MIDI ONLY")','" SOUND + MIDI":" MIDI ONLY")').replace('"GEN 8"','"GEN"')
s=s.replace('s.ui.gen8_mode==3?"GEN SETUP":','s.ui.gen8_mode==4?"ACID GEN":s.ui.gen8_mode==3?"GEN SETUP":')
s=s.replace('int count=c.ui.gen8_mode==3?1:6;', 'int count=c.ui.gen8_mode==3?1:c.ui.gen8_mode==4?2:6;')
s=s.replace('if(mode==0&&row>=4) {c.ui.gen8_mode=row==4?2:1;c.ui.sheet_row=0;return;}', '''if(mode==0&&row>=4) {
            bool br=c.track().engine==EngineKind::Sampler&&c.track().break_bars;
            bool acid=c.track().engine==EngineKind::Plugin&&c.track().plugin<max_plugins&&std::string(c.project.plugins[c.track().plugin].name)=="Acid Engine";
            c.ui.gen8_mode=row==5?3:br?2:acid?4:1;c.ui.sheet_row=0;return;
        }
        if(mode==4){c.gen8_action(2+row);return;}''')
s=s.replace('if (key == 0) c.ui.sheet_open = false;', 'if(key==0){if(c.ui.gen8_mode){c.ui.gen8_mode=0;c.ui.sheet_row=0;}else c.ui.sheet_open=false;}')
s=s.replace('c.ui.gen8_mode=uint8_t((c.ui.gen8_mode+1)%4);','c.ui.gen8_mode=c.ui.gen8_mode==0?1:c.ui.gen8_mode==1?3:0;')
s=s.replace('"T"+juce::String(s.project.gen8.first+1)+"-"+juce::String(s.project.gen8.last+1)+(s.project.gen8.assign?" SOUND + MIDI":" MIDI ONLY")','(s.project.gen8.assign?juce::String("T1 KIT / T2-4 INSTRUMENTS"):"T"+juce::String(s.project.gen8.first+1)+"-"+juce::String(s.project.gen8.last+1)+" MIDI ONLY")')
p.write_text(s)
file=Path(sys.argv[1])/'src/rhythmer/shell/shell.cpp';text=file.read_text().replace('    auto bindings = page_bindings(*project_, ui_, context_.pattern());','''    const auto& selected=project_->tracks[ui_.track];
    const bool break_gen=selected.engine==EngineKind::Sampler&&selected.break_bars;
    const bool acid_gen=selected.engine==EngineKind::Plugin&&selected.plugin<max_plugins&&std::string(project_->plugins[selected.plugin].name)=="Acid Engine";
    if((ui_.gen8_mode==2&&!break_gen)||(ui_.gen8_mode==4&&!acid_gen)){ui_.gen8_mode=0;ui_.sheet_row=0;}
    auto bindings = page_bindings(*project_, ui_, context_.pattern());''');file.write_text(text)
# Preserve original EXPLORE / RANDOM / genre menu order.
for rel in ['shell/bindings.cpp','shell/context.cpp','model/project_file.cpp']:
    file=Path(sys.argv[1])/'src/rhythmer'/rel;text=file.read_text().replace('int(gen8_genre_count)-1','int(gen8_genre_count)+1').replace('0,58','0,60').replace('0, 58','0, 60');file.write_text(text)
file=Path(sys.argv[1])/'src/rhythmer/pages/common.cpp';text=file.read_text().replace('gen8_genres[unsigned(b.value)%gen8_genre_count].name','b.value==0?"EXPLORE":b.value==1?"RANDOM":gen8_genres[(unsigned(b.value)-2)%gen8_genre_count].name');file.write_text(text)


file=Path(sys.argv[1])/'src/rhythmer/shell/bindings.cpp';text=file.read_text().replace('            if(ui.gen8_mode==3)return', '            if(ui.gen8_mode==4)return {Binding{Kind::Gen8Amount,0,0,100,project.gen8.amount},Binding{Kind::VaryAmount,0,0,100,project.gen8.complexity},Binding{Kind::Gen8Seed,0,0,9999,project.gen8.seed}};\n            if(ui.gen8_mode==3)return');file.write_text(text)
file=Path(sys.argv[1])/'src/rhythmer/shell/context.cpp';text=file.read_text().replace('case Kind::VaryAmount:', 'case Kind::VaryAmount: if(ui.gen8_mode==4){project.gen8.complexity=uint8_t(std::clamp(value,0,100));break;}');file.write_text(text)
file=Path(sys.argv[1])/'src/rhythmer/pages/common.cpp';text=file.read_text().replace('case Kind::VaryAmount:', 'case Kind::VaryAmount: if(s.ui.gen8_mode==4){c.label="ACCENT";c.value=juce::String(b.value);c.unit="%";break;}');file.write_text(text)

file=Path(sys.argv[1])/'src/rhythmer/pages/common.cpp';text=file.read_text().replace('#include "rhythmer/model/gen8_tables.h"','#include "rhythmer/model/gen8_tables.h"\n#include "rhythmer/model/gen_menu_order.h"').replace('b.value==0?"EXPLORE":b.value==1?"RANDOM":gen8_genres[(unsigned(b.value)-2)%gen8_genre_count].name','gen_menu_name(unsigned(b.value))');file.write_text(text)
file=Path(sys.argv[1])/'src/rhythmer/model/project_file.cpp';text=file.read_text().replace('#include "rhythmer/model/project_file.h"','#include "rhythmer/model/project_file.h"\n#include "rhythmer/model/gen_menu_order.h"').replace('project->gen8.genre=uint8_t(std::min<unsigned>(r.u8(),revision==1?58:60)+(revision==1?2:0));','unsigned genre=std::min<unsigned>(r.u8(),revision==1?58:60);if(revision==1){unsigned at=0;while(at<59&&gen_fm1_menu[at]!=genre)++at;genre=at+2;}project->gen8.genre=uint8_t(genre);');file.write_text(text)
