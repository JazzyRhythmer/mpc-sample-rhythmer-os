"""Select one of four aligned song-generation groups; preserve legacy files."""
from pathlib import Path

def apply(root):
 def patch(file,before,after):
  p=root/'src/rhythmer'/file;s=p.read_text();assert s.count(before)==1,(file,before[:80],s.count(before));p.write_text(s.replace(before,after))
 patch('shell/bindings.h','GenFirst,GenLast,GenAssign,GenBars,','GenFirst,GenLast,GenAssign,GenBars,GenGroup,')
 patch('shell/bindings.cpp','            if(ui.gen8_mode==3)return {Binding{Kind::GenFirst,0,0,15,project.gen8.first},Binding{Kind::GenLast,0,0,15,project.gen8.last},Binding{Kind::GenAssign,0,0,1,project.gen8.assign}};', '''            if(ui.gen8_mode==3){
                if(project.gen8.assign)return {Binding{Kind::GenGroup,0,0,3,project.gen8.group},Binding{},Binding{Kind::GenAssign,0,0,1,project.gen8.assign}};
                return {Binding{Kind::GenFirst,0,0,15,project.gen8.first},Binding{Kind::GenLast,0,0,15,project.gen8.last},Binding{Kind::GenAssign,0,0,1,project.gen8.assign}};
            }''')
 patch('shell/context.cpp','    case Kind::GenAssign:', '    case Kind::GenGroup:project.gen8.group=uint8_t(std::clamp(value,0,3));break;\n    case Kind::GenAssign:')
 patch('pages/common.cpp','    case Kind::GenAssign:', '    case Kind::GenGroup:c.label="SONG GROUP";c.value=juce::String(1+4*b.value)+"-"+juce::String(4+4*b.value);break;\n    case Kind::GenAssign:')
 patch('pages/steps_page.cpp','else if(s.project.gen8.assign)m.title=s.ui.sheet_row==1?"T1-4 / KEEP SOUNDS":"T1-4 / NEW SOUNDS";', 'else if(s.project.gen8.assign)m.title="T"+juce::String(gen_song_first(s.project.gen8)+1)+"-"+juce::String(gen_song_first(s.project.gen8)+4)+(s.ui.sheet_row==1?" / KEEP SOUNDS":" / NEW SOUNDS");')
 patch('pages/steps_page.cpp','m.title=s.project.gen8.assign?"SONG: T1 KIT + T2-4":"MIDI: FROM - TO";', 'm.title=s.project.gen8.assign?"T"+juce::String(gen_song_first(s.project.gen8)+1)+" KIT / T"+juce::String(gen_song_first(s.project.gen8)+2)+"-"+juce::String(gen_song_first(s.project.gen8)+4):"MIDI: FROM - TO";')
 patch('shell/gen8_jobs.cpp','settings.assign?std::string("T1-4"):', 'settings.assign?"T"+std::to_string(from+1)+"-"+std::to_string(to):')
 patch('model/project_file.cpp','    return w.out;', '    at=w.begin("GNGP");w.u8(project.gen8.group);w.end(at);\n    return w.out;')
 patch('model/project_file.cpp','} else if(name=="GN9S") {', '} else if(name=="GNGP") {project->gen8.group=uint8_t(std::min<unsigned>(r.u8(),3));\n        } else if(name=="GN9S") {')
 previews=[]
 for group in range(4):
  for mode in [0,3]:
   previews.append('    {"gen-group-%d-%s",[](Shell&,Snapshot& s){s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=%d;s.project.gen8.assign=1;s.project.gen8.group=%d;}},' % (group,'setup' if mode==3 else 'main',mode,group))
 patch('tools.cpp','const Preview previews[] {','const Preview previews[] {\n'+'\n'.join(previews))
