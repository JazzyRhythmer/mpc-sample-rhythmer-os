"""Clear targets/actions and a round-trip Break loop browser on existing pages."""
from pathlib import Path

def apply(root):
 def patch(file,before,after):
  p=root/'src/rhythmer'/file;s=p.read_text();assert s.count(before)==1,(file,before[:80],s.count(before));p.write_text(s.replace(before,after))
 patch('pages/steps_page.cpp','if (s.ui.sheet_open) keys = SoftKeys {{"BACK", "MODE", "DO IT"}', 'if (s.ui.sheet_open) keys = SoftKeys {{"BACK", "MODE", s.ui.gen8_mode==3?"DONE":s.ui.gen8_mode==0&&s.ui.sheet_row>=4?"OPEN":"APPLY"}')
 patch('pages/steps_page.cpp','            if(s.ui.gen8_mode==3){m.count=1;m.rows[0]={"SET TRACK RANGE",{},false,false,false};m.title="K3: SOUND + MIDI / MIDI ONLY";}', '''            if(s.ui.gen8_mode==0){
                const auto target="T"+juce::String(s.ui.track+1);
                m.rows[2]={"GENERATE "+target,{},false,false,false};m.rows[3]={"MUTATE "+target,{},false,false,false};
                if(s.ui.sheet_row==2||s.ui.sheet_row==3)m.title=target+" / KEEP SOUND";
                else if(s.project.gen8.assign)m.title=s.ui.sheet_row==1?"T1-4 / KEEP SOUNDS":"T1-4 / NEW SOUNDS";
                else m.title="MIDI T"+juce::String(std::min(s.project.gen8.first,s.project.gen8.last)+1)+"-"+juce::String(std::max(s.project.gen8.first,s.project.gen8.last)+1);
            }
            if(s.ui.gen8_mode==2)m.title="T"+juce::String(s.ui.track+1)+" / 16 CHOPS";
            if(s.ui.gen8_mode==4)m.title="T"+juce::String(s.ui.track+1)+" / KEEP SOUND";
            if(s.ui.gen8_mode==3){m.count=1;m.rows[0]={"RETURN TO GEN",{},false,false,false};m.title=s.project.gen8.assign?"SONG: T1 KIT + T2-4":"MIDI: FROM - TO";}''')
 patch('pages/steps_page.cpp','    c.ui.sheet_open = true;\n}', '    c.ui.sheet_open = true;c.ui.gen8_mode=0;c.ui.sheet_row=0;\n}')
 patch('shell/context.cpp','case Kind::GenFirst:project.gen8.first=uint8_t(std::clamp(value,0,15));break;', 'case Kind::GenFirst:project.gen8.first=uint8_t(std::clamp(value,0,15));project.gen8.last=std::max(project.gen8.first,project.gen8.last);break;')
 patch('shell/context.cpp','case Kind::GenLast:project.gen8.last=uint8_t(std::clamp(value,0,15));break;', 'case Kind::GenLast:project.gen8.last=uint8_t(std::clamp(value,0,15));project.gen8.first=std::min(project.gen8.first,project.gen8.last);break;')
 patch('pages/common.cpp','case Kind::GenBars:c.label="SOURCE BARS";', 'case Kind::GenBars:c.label="LOAD BARS";')
 # Range knobs remain discoverable, but visibly describe their MIDI-only scope.
 patch('pages/common.cpp','case Kind::GenFirst:c.label="FROM TRACK";', 'case Kind::GenFirst:c.label="MIDI FROM";')
 patch('pages/common.cpp','case Kind::GenLast:c.label="TO TRACK";', 'case Kind::GenLast:c.label="MIDI TO";')
 patch('shell/bindings.cpp','    case PageId::Samples: // every list: K1 jumps, the other pots draw nothing\n', '    case PageId::Samples: // Break loop length is chosen before loading\n        if(ui.break_browse)return {Binding{Kind::GenBars,0,1,4,project.gen8.bars},Binding{},Binding{}};\n')
 patch('pages/samples_page.cpp','s.files_top ? "" : "BACK", other, "PREVIEW"', 's.files_top ? (s.ui.break_browse?"GEN":"") : "BACK", other, "PREVIEW"')
 patch('pages/samples_page.cpp','s.files_top ? KeyIcon::None : KeyIcon::Back','s.files_top&&!s.ui.break_browse ? KeyIcon::None : KeyIcon::Back')
 patch('pages/samples_page.cpp','    h.right.push_back(tag_of(s, s.ui.track));','    if(s.ui.break_browse)h.left.push_back(pill("BREAK / "+juce::String(s.project.gen8.bars)+" BARS",c));\n    h.right.push_back(tag_of(s, s.ui.track));')
 patch('pages/samples_page.cpp','void soft(Context& c, int key) {\n    if (!c.library) return;', '''void soft(Context& c, int key) {
    if(key==0&&c.ui.break_browse&&(!c.library||c.library->top())){c.open(PageId::Steps);c.ui.sheet_open=true;c.ui.gen8_mode=2;c.ui.sheet_row=5;return;}
    if (!c.library) return;''')
 patch('shell/plugin_jobs.cpp','ui.break_bars=track().break_bars;dirty=true;', 'ui.break_bars=track().break_bars;project.gen8.bars=track().break_bars;dirty=true;')
 patch('shell/plugin_jobs.cpp','BREAK: choose a loop, then source bars 1-4','BREAK: K1 bars, Push loads loop')
 patch('shell/gen_break_jobs.cpp','    ui.break_browse=false;open(PageId::Steps);notice("Loading BREAK sample");','    ui.break_browse=false;open(PageId::Steps);ui.sheet_open=true;ui.gen8_mode=2;ui.sheet_row=0;notice("Loading BREAK sample");')
 patch('shell/gen8_jobs.cpp','ui.break_browse=true;ui.break_track=ui.track;open(PageId::Samples);notice("Choose BREAK audio loop");', 'ui.break_browse=true;ui.break_track=ui.track;open(PageId::Samples);notice("K1: loop bars / Push: load");')
 # Meaningful successful-operation notice distinguishes instrument replacement
 # from MIDI-only operations; failures keep their specific existing messages.
 patch('shell/gen8_jobs.cpp','    notice(std::string(gen_menu_name(settings.genre))+(skipped?" (unready tracks skipped)":""));', '''    const auto target=action<2?(settings.assign?std::string("T1-4"):"T"+std::to_string(from+1)+"-"+std::to_string(to)):"T"+std::to_string(ui.track+1);
    notice(target+(action%2?" mutated":" generated")+(skipped?" / skipped unready":" / UNDO available"));''')

 # Additional fixtures make the distinction visible at the smallest screen.
 patch('tools.cpp','const Preview previews[] {','''const Preview previews[] {
    {"gen-track-16",[](Shell&,Snapshot& s){s.ui.page=PageId::Steps;s.ui.track=15;s.ui.sheet_open=true;s.ui.sheet_row=2;}},
    {"gen-midi-one",[](Shell&,Snapshot& s){s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.project.gen8.assign=0;s.project.gen8.first=s.project.gen8.last=11;}},
    {"gen-setup-song",[](Shell&,Snapshot& s){s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=3;}},
    {"break-browse-four",[](Shell&,Snapshot& s){s.ui.page=PageId::Samples;s.ui.break_browse=true;s.files_top=true;s.project.gen8.bars=4;}},''')
 import shutil
 source=Path(__file__).resolve().parents[1]
 shutil.copy2(source/'extensions/tools/edit_preview.inc',root/'src/rhythmer/edit_preview.inc')
 patch('tools.cpp','int boot_frames(const std::string& folder) {','#include "rhythmer/edit_preview.inc"\n\nint boot_frames(const std::string& folder) {')
 patch('tools.cpp','std::optional<int> run_tool(int argc, char** argv) {','std::optional<int> run_tool(int argc, char** argv) {\n    if(argc==4&&!std::strcmp(argv[1],"--rhythmer-edit-preview"))return edit_preview(argv[2],argv[3]);')

 from apply_gen_groups import apply as groups
 groups(root)

if __name__=="__main__":
 import sys
 apply(Path(sys.argv[1]))
