"""Final navigation polish using existing pages and handlers only."""
from pathlib import Path

def apply(root):
 def patch(file,before,after):
  p=root/'src/rhythmer'/file;s=p.read_text();assert s.count(before)==1,(file,before[:80],s.count(before));p.write_text(s.replace(before,after))
 patch('pages/steps_page.cpp','s.ui.gen8_mode==0&&s.ui.sheet_row>=4?"OPEN":"APPLY"','((s.ui.gen8_mode==0&&s.ui.sheet_row>=4)||(s.ui.gen8_mode==2&&s.ui.sheet_row==5))?"OPEN":"APPLY"')
 patch('pages/steps_page.cpp','            if(s.ui.gen8_mode==2)m.title="T"+juce::String(s.ui.track+1)+" / 16 CHOPS";', '''            if(s.ui.gen8_mode==0&&s.ui.sheet_row>=4)m.title=s.ui.sheet_row==5?"TARGET / SOUND OR MIDI":br?"LOOP / CHOP GENERATOR":acid?"ACID / TRACK GENERATOR":"PATTERN / VARIATIONS";
            if(s.ui.gen8_mode==2){
                bool ready=true;for(unsigned i=0;i<16;++i)ready&=s.track().pads[(s.track().bank%sampler_banks)*16+i].used();
                m.title="T"+juce::String(s.ui.track+1)+(ready?" / 16 CHOPS":" / LOAD A LOOP");
                if(!ready)for(unsigned i=0;i<5;++i)m.rows[i].off=true;
            }''')
 patch('shell/gen8_jobs.cpp','BREAK: Chop 16 pads in this bank','Load a loop: BROWSE SAMPLE')
 patch('pages/plugin_presets_page.cpp','{{"BACK", "", ""}, -1, c,', '{{"BACK", "", v.list.empty()?"":"LOAD"}, -1, c,')
 patch('pages/plugin_presets_page.cpp','    if (key == 0) c.open(c.ui.presets_back);','    if (key == 0) c.open(c.ui.presets_back);\n    if (key == 2) push(c);')
 patch('shell/plugin_jobs.cpp','ui.kit_common=false;ui.plugin_row[ui.presets_entry]=0;', '''ui.kit_common=false;
        const bool editing=ui.presets_back==PageId::Edit&&track().engine==EngineKind::Plugin&&track().plugin==ui.presets_entry;
        ui.plugin_row[ui.presets_entry]=editing?(ui.edit_page[ui.track]?2:ui.edit_row[ui.track]==3?1:0):0;
        plugin_panel_at=0;''')
 patch('pages/steps_page.cpp','c.ui.gen8_mode=row==5?3:br?2:acid?4:1;c.ui.sheet_row=c.ui.gen8_mode==3&&c.project.gen8.assign?c.project.gen8.group:0;return;', 'c.ui.gen8_mode=row==5?3:br?2:acid?4:1;c.ui.sheet_row=c.ui.gen8_mode==3&&c.project.gen8.assign?c.project.gen8.group:0;if(c.ui.gen8_mode==2){bool ready=true;for(unsigned i=0;i<16;++i)ready&=c.track().pads[(c.track().bank%sampler_banks)*16+i].used();if(!ready)c.ui.sheet_row=5;}return;')
 # Fixtures exercise meaning, not just clipping on the default menu row.
 patch('tools.cpp','const Preview previews[] {','''const Preview previews[] {
    {"gen-open-setup",[](Shell&,Snapshot& s){s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.sheet_row=5;}},
    {"gen-open-vary",[](Shell&,Snapshot& s){s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.sheet_row=4;}},
    {"break-empty-gen",[](Shell&,Snapshot& s){s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=2;s.ui.sheet_row=5;s.project.tracks[s.ui.track].engine=EngineKind::Sampler;s.project.tracks[s.ui.track].break_bars=2;for(auto& pad:s.project.tracks[s.ui.track].pads)pad=PadSound{};}},
    {"break-browse-open",[](Shell&,Snapshot& s){s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=2;s.ui.sheet_row=5;s.project.tracks[s.ui.track].engine=EngineKind::Sampler;s.project.tracks[s.ui.track].break_bars=2;}},''')
 print('Applied contextual GEN actions, explicit preset LOAD and consistent kit-return controls')
if __name__=='__main__':
 import sys
 apply(Path(sys.argv[1]))
