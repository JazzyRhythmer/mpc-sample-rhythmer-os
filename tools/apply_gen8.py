#!/usr/bin/env python3
"""Apply small native GEN extensions to the generated SSD runtime, after naming."""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def apply(runtime):
    for folder in ('model', 'shell'):
        for source in (ROOT / 'extensions' / folder).glob('*'):
            shutil.copy2(source, runtime / 'src/rhythmer' / folder / source.name)

    source=ROOT/'third_party/fm1-gen'
    shutil.copytree(source,runtime/'fm1-gen',dirs_exist_ok=True)
    shutil.copy2(source/'bridge.h',runtime/'src/rhythmer/shell/fm1_gen_bridge.h')
    with (runtime/'Makefile').open('a') as f:f.write('\nLDLIBS += -Wl,--gc-sections\nFM1_GEN_OBJ := build/obj/fm1-gen.o\nOBJECTS += $(FM1_GEN_OBJ)\n$(TARGET): $(FM1_GEN_OBJ)\n$(FM1_GEN_OBJ): $(shell find fm1-gen -type f)\n\t@mkdir -p build/obj\n\t$(CC) -O1 -w -ffunction-sections -fdata-sections -DFM1_HOST_TEST=1 -Ifm1-gen/generated -Ifm1-gen/firmware/src -Ifm1-gen/tests -c fm1-gen/bridge.c -o $@\n')

    def replace(path, old, new):
        p = runtime / path
        text = p.read_text()
        if text.count(old) != 1:
            raise ValueError(f'{path}: expected one anchor, got {text.count(old)}: {old[:70]}')
        p.write_text(text.replace(old, new))

    replace('src/rhythmer/model/project.h', '#include "rhythmer/model/pattern.h"',
            '#include "rhythmer/model/pattern.h"\n#include "rhythmer/model/gen8.h"')
    replace('src/rhythmer/model/project.h', 'struct Project {', 'struct Project {\n    Gen8Settings gen8;')
    replace('src/rhythmer/shell/ui_state.h', 'uint8_t vary_amount = 30;',
            'uint8_t vary_amount = 30;\n    uint8_t gen8_mode = 0; // 0 GEN8, 1 original VARY, 2 BREAK')
    replace('src/rhythmer/shell/context.h', 'void vary(Variation v);', 'void vary(Variation v);\n    void gen8_action(unsigned action);')
    replace('src/rhythmer/shell/bindings.h', 'EuclidRotate, VaryAmount,', 'EuclidRotate, VaryAmount, Gen8Amount, Gen8Genre, Gen8Seed,')
    replace('src/rhythmer/shell/bindings.cpp', '#include "rhythmer/model/generators.h"',
            '#include "rhythmer/model/generators.h"\n#include "rhythmer/model/gen8_tables.h"')
    replace('src/rhythmer/shell/bindings.cpp',
            'if (ui.sheet_open) return {Binding {Kind::VaryAmount, 0, 0, 100, ui.vary_amount}, Binding {}, Binding {}};',
            '''if (ui.sheet_open) {
            if(ui.gen8_mode==1) return {Binding {Kind::VaryAmount, 0, 0, 100, ui.vary_amount}, Binding {}, Binding {}};
            return {Binding {Kind::Gen8Amount,0,0,100,project.gen8.amount},
                    Binding {Kind::Gen8Genre,0,0,int(gen8_genre_count)-1,project.gen8.genre},
                    Binding {Kind::Gen8Seed,0,0,9999,project.gen8.seed}};
        }''')
    replace('src/rhythmer/shell/context.cpp', 'case Kind::VaryAmount:',
            '''case Kind::Gen8Amount: project.gen8.amount=uint8_t(std::clamp(value,0,100)); break;
    case Kind::Gen8Genre: project.gen8.genre=uint8_t(std::clamp(value,0,58)); break;
    case Kind::Gen8Seed: project.gen8.seed=uint16_t(std::clamp(value,0,9999)); break;
    case Kind::VaryAmount:''')
    replace('src/rhythmer/pages/common.cpp', '#include <algorithm>', '#include <algorithm>\n#include "rhythmer/model/gen8_tables.h"')
    replace('src/rhythmer/pages/common.cpp', 'case Kind::VaryAmount:',
            '''case Kind::Gen8Amount: c.label="ENERGY"; c.value=juce::String(b.value); c.unit="%"; break;
    case Kind::Gen8Genre: c.label="GENRE"; c.value=gen8_genres[unsigned(b.value)%gen8_genre_count].name; break;
    case Kind::Gen8Seed: c.label="SEED"; c.value=juce::String(b.value); break;
    case Kind::VaryAmount:''')
    page = 'src/rhythmer/pages/steps_page.cpp'
    replace(page, 'SoftKeys {{"BACK", "", "DO IT"}', 'SoftKeys {{"BACK", "MODE", "DO IT"}')
    replace(page, 'm.count = unsigned(Variation::Count); m.current = s.ui.sheet_row % m.count;',
            '''if(s.ui.gen8_mode!=1) {
            static const char* gen[] {"GENERATE 8","MUTATE 8","GENERATE TRACK","MUTATE TRACK","BREAK MENU","VARIATIONS"};
            static const char* brk[] {"GENRE CHOPS","STRAIGHT","RANDOM CHOPS","MUTATE CHOPS","TAIL FILL"};
            m.count=s.ui.gen8_mode==2?5:6;
            for(unsigned i=0;i<m.count;i++) m.rows[i]={s.ui.gen8_mode==2?brk[i]:gen[i],{},false,false,false};
            m.title=s.ui.gen8_mode==2?"SELECTED BANK: 16 CHOPS":"T1-4 SYNTH / T5-8 DRUMS";
        } else m.count = unsigned(Variation::Count);
        m.current = s.ui.sheet_row % m.count;''')
    replace(page, 'wide_sheet(p, m, "VARY", c);', 'wide_sheet(p, m, s.ui.gen8_mode==1?"VARY":s.ui.gen8_mode==2?"BREAK":"GEN 8", c);')
    replace(page, 'if (c.ui.sheet_open) { c.ui.sheet_row = uint8_t(std::clamp<int>(c.ui.sheet_row + delta, 0, int(Variation::Count) - 1)); return; }',
            'if (c.ui.sheet_open) { int count=c.ui.gen8_mode==2?5:6; c.ui.sheet_row = uint8_t(std::clamp<int>(c.ui.sheet_row + delta, 0, count - 1)); return; }')
    replace(page, 'if (c.ui.sheet_open) { c.ui.sheet_open = false; c.vary(Variation(c.ui.sheet_row % unsigned(Variation::Count))); return; }',
            '''if (c.ui.sheet_open) {
        unsigned mode=c.ui.gen8_mode, row=c.ui.sheet_row;
        if(mode==0&&row>=4) {c.ui.gen8_mode=row==4?2:1;c.ui.sheet_row=0;return;}
        if(mode==1)c.vary(Variation(row%unsigned(Variation::Count)));
        else c.gen8_action(mode==2?4+row:row);
        return; // leave the sheet open: turn seed/amount, Generate or Mutate again
    }''')
    replace(page, 'if (key == 2) push(c);',
            'if (key == 1) {c.ui.gen8_mode=uint8_t((c.ui.gen8_mode+1)%3);c.ui.sheet_row=0;}\n        if (key == 2) push(c);')
    # Tagged optional section: original MELODEE1 identity and all older sections stay intact.
    replace('src/rhythmer/model/project_file.cpp', '    return w.out;',
            '''    at=w.begin("GN8S"); w.u8(2); w.u16(project.gen8.seed); w.u8(project.gen8.genre);
    w.u8(project.gen8.amount); w.u8(project.gen8.complexity); w.end(at);
    return w.out;''')
    replace('src/rhythmer/model/project_file.cpp', '} else if (name == "TRAK") {',
            '''} else if (name == "GN8S") {
            auto revision=r.u8();if(revision==1||revision==2) {
                project->gen8.seed=uint16_t(std::min<unsigned>(r.u16(),9999));
                project->gen8.genre=uint8_t(std::min<unsigned>(r.u8(),revision==1?58:60)+(revision==1?2:0));
                project->gen8.amount=uint8_t(std::min<unsigned>(r.u8(),100));
                project->gen8.complexity=uint8_t(std::min<unsigned>(r.u8(),100));
            }
        } else if (name == "TRAK") {''')
    import subprocess
    subprocess.run([sys.executable,str(ROOT/'tools/apply_gen_workflow.py'),str(runtime)],check=True)
    for filename in ['fm1_gen_bridge_test.c','test_fm1_gen_bridge.py']:shutil.copy2(ROOT/'tests'/filename,runtime/'tests'/filename)
    shutil.copy2(ROOT / 'tests/gen8.cpp', runtime / 'tests/gen8.cpp')
    shutil.copy2(ROOT / 'tests/test_gen8.py', runtime / 'tests/test_gen8.py')
    replace('tests/rhythmer.cpp', 'ui.sheet_open = true; ui.euclid_cards = false;',
            'ui.sheet_open = true; ui.euclid_cards = false; ui.gen8_mode=1; // original VARY mode')
    # Real renderer exercises every imported genre label and each added sheet at 320x240.
    previews = []
    for i in range(61):
        previews.append('    {"gen8-%02d", [](Shell&, Snapshot& s) {s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=0;s.ui.sheet_row=0;s.project.gen8.genre=%d;}},' % (i,i))
    previews += [
        '    {"break-menu", [](Shell&, Snapshot& s) {s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=2;s.ui.sheet_row=3;}},',
        '    {"vary-original", [](Shell&, Snapshot& s) {s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=1;s.ui.sheet_row=0;}},',
    ]
    previews += [
        '    {"acid-gen", [](Shell&,Snapshot& s){s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=4;s.project.tracks[s.ui.track].engine=EngineKind::Plugin;s.project.tracks[s.ui.track].plugin=0;std::strcpy(s.project.plugins[0].name,"Acid Engine");}},',
        '    {"gen-setup-range", [](Shell&, Snapshot& s) {s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=3;s.project.gen8.first=0;s.project.gen8.last=15;}},',
        '    {"gen-midi-range", [](Shell&, Snapshot& s) {s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=0;s.project.gen8.first=8;s.project.gen8.last=15;s.project.gen8.assign=0;}},',
        '    {"break-source-one", [](Shell&, Snapshot& s) {s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=2;s.project.gen8.bars=1;}},',
        '    {"break-source-four", [](Shell&, Snapshot& s) {s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=2;s.ui.sheet_row=5;s.project.gen8.bars=4;}},',
    ]
    replace('src/rhythmer/tools.cpp','const Preview previews[] {','const Preview previews[] {\n'+'\n'.join(previews))
    replace('src/rhythmer/tools.cpp','#include "rhythmer/tools.h"',
            '#include "rhythmer/tools.h"\n#include "rhythmer/shell/gen8_check.h"')
    replace('src/rhythmer/tools.cpp','std::optional<int> run_tool(int argc, char** argv) {',
            'std::optional<int> run_tool(int argc, char** argv) {\n    if(argc==2&&!std::strcmp(argv[1],"--rhythmer-gen8-check"))return gen8_shell_check();')


if __name__ == '__main__':
    apply(Path(sys.argv[1]).resolve())
