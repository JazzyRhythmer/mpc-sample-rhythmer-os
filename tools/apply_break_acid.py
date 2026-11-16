#!/usr/bin/env python3
"""Audited FM-1 performance/Acid integration, on a generated runtime only."""
from pathlib import Path
import re,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
runtime=Path(sys.argv[1]);base=runtime/'src/rhythmer'
def patch(rel,old,new):
 p=base/rel;s=p.read_text();assert old in s,(rel,old[:90]);p.write_text(s.replace(old,new))
for folder,names in {'engine':['break_manipulator.h','break_manipulator.cpp'],'model':['acid_gen.h','acid_gen.cpp']}.items():
 for name in names:shutil.copy2(ROOT/'extensions'/folder/name,base/folder/name)
# Keep an unmodified source pin. Mechanically move file globals into per-track
# state; tables remain shared. The only DSP adaptation is the sample reader,
# loop duration and sample-rate bridge (the host supplies decoded PCM).
s=(ROOT/'third_party/fm1-break/jungle.c').read_text()
s=s.replace('#include "jungle.h"','').replace('#include "six_memory.h"','')
s=re.sub(r'^static ([^=\n]*\([^;\n]*\));\s*$', '',s,flags=re.M)
s=re.sub(r'^static ((?:FM1_AUDIO_DATA )?const [^\n]*\[[^\n]*=)',r'inline static \1',s,flags=re.M)
s=re.sub(r'^static ', '',s,flags=re.M)
s=s.replace('if (!sea || frames != 48000U || bytes != 72000U)', 'if (!sea || frames < 16U)')
s=s.replace('mix = x << 1','mix = x * 2').replace('mix << 7','mix * 128')
s=s.replace('/ 211680000U','/ (105840000ULL * source_bars)')
start=s.index('        /* Decode adjacent packed PCM12 frames together.')
end=s.index('        s = a +',start)
s=s[:start]+'''        const auto* sample=reinterpret_cast<const SampleData*>(data);
        auto pcm=[&](double n){double position=n*sample->frames/src_frames;
            unsigned a=std::min<unsigned>(unsigned(position),sample->frames-1),b=std::min(a+1,sample->frames-1);float f=float(position-a);
            float v=sample->left[a]+f*(sample->left[b]-sample->left[a]);
            if(!sample->right.empty())v=(v+sample->right[a]+f*(sample->right[b]-sample->right[a]))*.5f;
            if(!std::isfinite(v))v=0;
            return int32_t(std::clamp(std::round(v*32768.f),-32768.f,32767.f));};
        int32_t a=pcm(r->pos),b=pcm(r->pos+1);
'''+s[end:]
s=s.replace('        s = a + (((b - a) * (int32_t)(r->frac >> 9)) >> 15);','        s = sample->frames==48000U?a + (((b - a) * (int32_t)(r->frac >> 9)) >> 15):pcm(double(r->pos)+double(r->frac)/16777216.0);')
# Bound old crossfade voices against their own sample, including unequal A/B lengths.
s=s.replace('if (r->pos + 1U < frames)', 'if (r->pos + 1U < src_frames)')
h=(ROOT/'third_party/fm1-break/jungle.h').read_text()
header=h[h.index('enum {'):h.index('void jungle_init(void);')]
header=re.sub(r'/\*.*?\*/','',header,flags=re.S)
header=header.replace('JUNGLE_BPM_MIN_X10 = 400','JUNGLE_BPM_MIN_X10 = 200').replace('JUNGLE_BPM_MAX_X10 = 3200','JUNGLE_BPM_MAX_X10 = 4000')
prefix='#include <cstdint>\n#include <cstring>\n#include <algorithm>\n#define JUNGLE_AUDIO_CODE\n#define FM1_AUDIO_DATA\nnamespace rhythmer {\n'+header+'\nstruct BreakManipulator::State {\n unsigned source_bars=2;\n static void jungle_midi_out(unsigned){}\n'
(base/'engine/jungle_state.inc').write_text(prefix+s+'\n};\n}\n')
patch('engine/break_manipulator.h','#include "rhythmer/engine/sample_data.h"','#include "rhythmer/engine/sample_data.h"\n#include "rhythmer/model/sampler.h"')
patch('engine/sampler.h','#include <array>','#include <array>\n#include "rhythmer/engine/break_manipulator.h"')
patch('engine/sampler.h','    SamplerEngine();','    SamplerEngine();\n    BreakManipulator manipulator;\n    void configure_break(unsigned bars,unsigned bank){manipulator.configure(bars,bank);}')
patch('engine/sampler.h','tempo = tenths; tempo_moved = true;','tempo = tenths; tempo_moved = true; manipulator.tempo(tenths);')
patch('engine/sampler.cpp','void SamplerEngine::note_on(int key, int velocity) {','void SamplerEngine::note_on(int key, int velocity) {\n    if(manipulator.enabled()){manipulator.note(key,velocity);return;}')
patch('engine/sampler.cpp','void SamplerEngine::note_off(int key) {','void SamplerEngine::note_off(int key) {\n    if(manipulator.enabled()){manipulator.off(key);return;}')
patch('engine/sampler.cpp','void SamplerEngine::all_notes_off() {','void SamplerEngine::all_notes_off() {\n    if(manipulator.enabled())manipulator.release();')
patch('engine/sampler.cpp','void SamplerEngine::silence() {','void SamplerEngine::silence() {\n    manipulator.stop();')
patch('engine/sampler.cpp','bool SamplerEngine::sounding() const {','bool SamplerEngine::sounding() const {\n    if(manipulator.enabled())return manipulator.sounding();')
patch('engine/sampler.cpp','void SamplerEngine::set_param(int id, int value) {','void SamplerEngine::set_param(int id, int value) {\n    if(id>=100&&id<110){manipulator.param(unsigned(id-100),value);return;}')
patch('engine/sampler.cpp','void SamplerEngine::render_stereo(float* left, float* right, unsigned frames) {','''void SamplerEngine::render_stereo(float* left, float* right, unsigned frames) {
    if(manipulator.enabled()){
        unsigned first=manipulator.first_pad();
        const SampleData* a=first<sampler_pads&&samples&&pads[first].sample<sample_slots?(*samples)[pads[first].sample]:nullptr;
        const SampleData* b=samples&&pads[first].layers[0].sample<sample_slots?(*samples)[pads[first].layers[0].sample]:nullptr;
        manipulator.sources(a,b);manipulator.render(left,right,frames,dsp::sample_rate());return;
    }''')
patch('engine/engine_host.cpp','    slot.sampler.set_trims(track.zone_trims);','    slot.sampler.configure_break(track.engine==EngineKind::Sampler?track.break_bars:0,track.bank);\n    slot.sampler.set_trims(track.zone_trims);')
patch('model/project.h','#include "rhythmer/model/gen8.h"','#include "rhythmer/model/gen8.h"\n#include "rhythmer/model/acid_gen.h"')
patch('model/project.h','struct Track {','struct Track {\n    AcidGenSettings acid_gen;')
patch('model/project_file.cpp','    return w.out;','''    at=w.begin("ACGN");for(const auto& t:project.tracks){const auto& a=t.acid_gen;
        w.u8(a.density);w.u8(a.accent);w.u8(a.slide);w.u8(a.octaves);w.u8(a.octave);w.u8(a.auto_bars);w.u32(a.seed);}w.end(at);
    return w.out;''')
patch('model/project_file.cpp','} else if(name=="GNGP") {','''} else if(name=="ACGN") {for(auto& t:project->tracks){auto& a=t.acid_gen;
        a.density=std::min<unsigned>(r.u8(),100);a.accent=std::min<unsigned>(r.u8(),100);a.slide=std::min<unsigned>(r.u8(),100);
        a.octaves=std::clamp<unsigned>(r.u8(),1,3);a.octave=std::min<unsigned>(r.u8(),4);a.auto_bars=std::min<unsigned>(r.u8(),16);a.seed=r.u32();}
        } else if(name=="GNGP") {''')
patch('shell/gen8_jobs.cpp','#include <mutex>','#include <mutex>\n#include "rhythmer/engine/engine_host.h"\n#include <chrono>\n#include "rhythmer/model/acid_gen.h"')
p=base/'shell/gen8_jobs.cpp';s=p.read_text();start=s.index('            made=p;made.events.clear();made.euclids.clear();unsigned count=');end=s.index('\n        }',start)
s=s[:start]+'''            auto& acid=project.tracks[t].acid_gen;
            made=acid_generate_pattern(p,acid,action%2,project.root,scales()[project.scale%scales().size()].mask);'''+s[end:];p.write_text(s)

patch('engine/sampler.cpp','void SamplerEngine::sample_gone(uint16_t slot) {','void SamplerEngine::sample_gone(uint16_t slot) {\n    if(manipulator.enabled()){manipulator.stop();manipulator.sources(nullptr,nullptr);}')
patch('engine/sampler.cpp','    if(manipulator.enabled()){manipulator.note(key,velocity);return;}','    if(manipulator.enabled()){\n        unsigned first=manipulator.first_pad();\n        const auto* a=samples&&pads[first].sample<sample_slots?(*samples)[pads[first].sample]:nullptr;\n        const auto* b=samples&&pads[first].layers[0].sample<sample_slots?(*samples)[pads[first].layers[0].sample]:nullptr;\n        manipulator.sources(a,b);manipulator.note(key,velocity);return;}')

# Acid controls are per track and do not borrow the song GEN controls.
patch('shell/ui_state.h','uint8_t gen8_mode = 0;','uint8_t acid_gen_page=0,break_perf_page=0;bool break_load_b=false;\n    uint8_t gen8_mode = 0;')
patch('shell/bindings.h','EuclidRotate, VaryAmount,','EuclidRotate, VaryAmount, AcidGenParam, AcidGenSeed, BreakPerfParam,')
patch('shell/bindings.cpp','if(ui.gen8_mode==4)return {Binding{Kind::Gen8Amount,0,0,100,project.gen8.amount},Binding{Kind::VaryAmount,0,0,100,project.gen8.complexity},Binding{Kind::Gen8Seed,0,0,9999,project.gen8.seed}};', '''if(ui.gen8_mode==4){const auto& a=track.acid_gen;
                if(ui.acid_gen_page%3==0)return {Binding{Kind::AcidGenParam,0,0,100,a.density},Binding{Kind::AcidGenParam,1,0,100,a.accent},Binding{Kind::AcidGenParam,2,0,100,a.slide}};
                if(ui.acid_gen_page%3==1)return {Binding{Kind::AcidGenParam,3,1,3,a.octaves},Binding{Kind::AcidGenParam,4,0,4,a.octave},Binding{Kind::AcidGenParam,5,0,16,a.auto_bars}};
                return {Binding{Kind::AcidGenSeed,0,1,2147483647,int(a.seed&0x7fffffff)},Binding{},Binding{}};
            }''')
patch('shell/context.cpp','    case Kind::Param:', '''    case Kind::AcidGenParam:{auto& a=t.acid_gen;switch(b.id){case 0:a.density=value;break;case 1:a.accent=value;break;case 2:a.slide=value;break;case 3:a.octaves=value;break;case 4:a.octave=value;break;case 5:a.auto_bars=value;break;}dirty=true;break;}
    case Kind::AcidGenSeed:t.acid_gen.seed=uint32_t(value);dirty=true;break;
    case Kind::BreakPerfParam:t.break_perf[unsigned(b.id)%10]=uint16_t(value);if(b.id==6&&t.break_perf[7]>value*10){t.break_perf[7]=uint16_t(value*10);send({Type::Param,ui.track,0,107,int16_t(value*10)});}send({Type::Param,ui.track,0,uint16_t(100+b.id),int16_t(value)});dirty=true;break;
    case Kind::Param:''')
patch('pages/common.cpp','    case Kind::Param:', '''    case Kind::AcidGenParam:{static const char* names[]={"DENSITY","ACCENT","SLIDE","OCTAVES","BASE OCTAVE","AUTO MUTATE"};c.label=names[unsigned(b.id)%6];c.value=b.id==5&&!b.value?"OFF":juce::String(b.value);c.unit=b.id<3?"%":b.id==5&&b.value?"BARS":"";break;}
    case Kind::AcidGenSeed:c.label="SEED";c.value=juce::String(juce::int64(s.track().acid_gen.seed));break;
    case Kind::BreakPerfParam:{static const char* names[]={"ORBIT","VARIATION","DRIFT","DJ FILTER","LOOP HOLD","TAIL FILL","GRAIN","SPLICE","SLOW","PLAY MODE"};c.label=names[unsigned(b.id)%10];c.value=b.id==9?(b.value?"CHOP":"LOOP"):b.id==7?juce::String(b.value/10.0,1):b.id>=6?juce::String(b.value):b.id>=4?(b.value?"ON":"OFF"):b.id==3?(b.value==64?"OPEN":b.value<64?"LP "+juce::String(b.value):"HP "+juce::String(b.value-64)):juce::String(b.value);c.unit=b.id==6?"ms":b.id==7?"ms":b.id==8?"x":"";break;}
    case Kind::Param:''')
patch('pages/steps_page.cpp','m.count=s.ui.gen8_mode==4?2:6;', 'm.count=s.ui.gen8_mode==4?3:6;')
patch('pages/steps_page.cpp','m.rows[1]={"MUTATE ACID",{},false,false,false};','m.rows[1]={"MUTATE ACID",{},false,false,false};m.rows[2]={"REPLAY SEED",{},false,false,false};')
patch('pages/steps_page.cpp','if(s.ui.gen8_mode==4)m.title="T"+juce::String(s.ui.track+1)+" / KEEP SOUND";', 'if(s.ui.gen8_mode==4)m.title="T"+juce::String(s.ui.track+1)+" / SETTINGS "+juce::String(s.ui.acid_gen_page%3+1)+" OF 3";')
patch('pages/steps_page.cpp','c.ui.gen8_mode==4?2:6','c.ui.gen8_mode==4?3:6')
patch('pages/steps_page.cpp','if(mode==4){c.gen8_action(2+row);return;}', '''if(mode==4){
            c.gen8_action(row==2?12:row==1?3:2);return;
        }''')
patch('pages/steps_page.cpp','if (key == 1) {c.ui.gen8_mode=', 'if(key==1&&c.ui.gen8_mode==4){c.ui.acid_gen_page=uint8_t((c.ui.acid_gen_page+1)%3);return;}\n        if (key == 1) {c.ui.gen8_mode=')
patch('shell/gen8_jobs.cpp','    close_gesture();', '''    if(action!=13)close_gesture();
    if((action==2||action==3||action==12||action==13)&&voice_for(*this,ui.track).acid){
        if(host.song_playing()){notice("Stop song before ACID GEN");return;}
        if(pattern().steps()>64){notice("ACID GEN: use 1-64 steps");return;}
        const bool automatic=action==13,mutate=action==3||automatic;
        Edit edit;edit.what=mutate?"Mutate ACID":"Generate ACID";
        if(!automatic)edit.tracks_before.push_back({ui.track,track_state(*this,ui.track)});
        if(action==2){auto& seed=track().acid_gen.seed;
            auto ms=uint32_t(std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());
            seed=(ms^uint32_t(host.blocks_rendered())*2654435761u^seed)*1664525u+1013904223u;if(!seed)seed=1;}
        pattern()=acid_generate_pattern(pattern(),track().acid_gen,mutate,project.root,scales()[project.scale%scales().size()].mask);
        sync_pattern(ui.track,track().pattern);dirty=true;
        if(!automatic){edit.tracks_after.push_back({ui.track,track_state(*this,ui.track)});edits.push(std::move(edit));}
        if(!automatic)notice(action==3?"303 MUTATED":action==12?"303 SEED REPLAY":"NEW 303 LINE");
        return;
    }''')

# BRK PERF preserves native sample/kit support outside Break tracks.
patch('model/project.h','    AcidGenSettings acid_gen;','    AcidGenSettings acid_gen;\n    std::array<uint16_t,10> break_perf{{0,0,0,64,0,0,38,100,4,1}};uint8_t break_source=0;')
patch('model/project_file.cpp','    at=w.begin("ACGN");','    at=w.begin("BRPF");for(const auto& t:project.tracks)for(auto v:t.break_perf)w.u16(v);w.end(at);\n    at=w.begin("ACGN");')
patch('model/project_file.cpp','} else if(name=="ACGN") {','} else if(name=="BRPF") {for(auto& t:project->tracks)for(unsigned i=0;i<10;i++){unsigned lo=i==6?3:i==7?1:i==8?2:0,hi=i==4||i==5||i==9?1:i==6?80:i==7?std::min<unsigned>(300,t.break_perf[6]*10):i==8?4:127;t.break_perf[i]=uint16_t(std::clamp<unsigned>(r.u16(),lo,hi));}\n        } else if(name=="ACGN") {')
patch('engine/engine_host.cpp','    slot.sampler.set_trims(track.zone_trims);','    for(unsigned i=0;i<10;i++)slot.sampler.manipulator.param(i,track.break_perf[i]);\n    slot.sampler.manipulator.initial_source(track.break_source);\n    slot.sampler.set_trims(track.zone_trims);')
patch('shell/bindings.cpp','    case PageId::Edit: {','''    case PageId::Edit: {
        if(track.engine==EngineKind::Sampler&&track.break_bars){
            unsigned page=ui.break_perf_page%6;
            if(page==5)return {Binding{Kind::Level,0,0,127,track.mix.level},Binding{Kind::Pan,0,-50,50,track.mix.pan},Binding{Kind::Send,0,0,100,track.mix.sends[0]}};
            static constexpr unsigned ids[5][3]={{0,3,4},{0,3,4},{9,4,3},{1,2,5},{6,7,8}};std::array<Binding,3> result{};
            for(unsigned i=0;i<3;i++){unsigned id=ids[page][i];int lo=id==6?3:id==7?1:id==8?2:0,hi=id==4||id==5||id==9?1:id==6?80:id==7?std::min<int>(300,track.break_perf[6]*10):id==8?4:127;result[i]=Binding{Kind::BreakPerfParam,int(id),lo,hi,int(track.break_perf[id])};}return result;
        }''')
shutil.copy2(ROOT/'extensions/pages/break_performance.inc',base/'pages/break_performance.inc')
patch('pages/edit_page.cpp','#include "rhythmer/pages/plugin_design.inc"','#include "rhythmer/pages/plugin_design.inc"\n#include "rhythmer/pages/break_performance.inc"')
patch('pages/edit_page.cpp','void draw(Paint& p, const Snapshot& s) {','void draw(Paint& p, const Snapshot& s) {\n    if(break_home(s)){break_performance(p,s);return;}')
patch('pages/edit_page.cpp','void wheel(Context& c, int delta) {','void wheel(Context& c, int delta) {\n    if(break_home(c)){c.ui.break_perf_page=uint8_t((c.ui.break_perf_page+delta%6+6)%6);return;}')
patch('pages/edit_page.cpp','void soft(Context& c, int key) {','''void soft(Context& c, int key) {
    if(break_home(c)){
        if(key==0){c.open(PageId::Steps);c.ui.sheet_open=true;c.ui.gen8_mode=2;c.ui.sheet_row=6;return;}
        if(key==1){c.ui.break_load_b=c.ui.break_perf_page%6==2;c.ui.break_browse=true;c.ui.break_track=c.ui.track;c.open(PageId::Samples);c.notice(c.ui.break_load_b?"Choose loop B":"Choose loop A");return;}
        if(key==2){c.key(18,127,true);c.key(18,0,false);c.track().break_perf[1]=c.track().break_perf[2]=0;c.notice("STRAIGHT RETURN");return;}
    }''')
patch('pages/edit_page.cpp','void push(Context& c) {','void push(Context& c) {\n    if(break_home(c)){c.ui.break_perf_page=uint8_t((c.ui.break_perf_page+1)%6);return;}')
patch('pages/edit_page.cpp','const PageSpec edit_page {draw, play_pad,','const PageSpec edit_page {draw, break_pad,')
patch('shell/gen_break_jobs.cpp','    unsigned bars=std::clamp<unsigned>(ui.break_bars,1,4);','    unsigned bars=std::clamp<unsigned>(ui.break_bars,1,4);')
patch('shell/gen_break_jobs.cpp','    Edit edit;edit.what="Load BREAK";edit.track=uint8_t(at);','''    if(ui.break_load_b&&project.tracks[at].break_bars){
        Edit edit;edit.what="Load BREAK B";edit.track=uint8_t(at);edit.track_before=std::make_unique<TrackState>(track_state(*this,at));
        auto next=std::make_unique<TrackState>(*edit.track_before);auto& t=next->track;
        auto& layer=t.pads[t.bank*16].layers[0];layer.sample=uint16_t(slot);layer.start=0;layer.end=sample.frames;
        restore_track(*this,at,*next);edit.track_after=std::move(next);edits.push(std::move(edit));dirty=true;ui.break_load_b=false;
        ui.track=uint8_t(at);open(PageId::Edit);ui.edit_page[at]=0;ui.break_perf_page=2;notice("BREAK B ready");return;
    }
    ui.break_load_b=false;
    Edit edit;edit.what="Load BREAK";edit.track=uint8_t(at);''')

patch('pages/steps_page.cpp','"TAIL FILL","BROWSE SAMPLE"','"TAIL FILL","BROWSE SAMPLE","BRK PERF"')
patch('pages/steps_page.cpp','m.count=s.ui.gen8_mode==4?3:6;','m.count=s.ui.gen8_mode==4?3:s.ui.gen8_mode==2?7:6;')
patch('pages/steps_page.cpp','c.ui.gen8_mode==4?3:6','c.ui.gen8_mode==4?3:c.ui.gen8_mode==2?7:6')
patch('shell/gen8_jobs.cpp','    if(host_recording())', '''    if(action==10&&track().engine==EngineKind::Sampler&&track().break_bars){ui.sheet_open=false;open(PageId::Edit);ui.edit_page[ui.track]=0;ui.break_perf_page=0;return;}
    if(host_recording())''')
patch('shell/context.h','    void gen_break_tick();','    void gen_break_tick();\n    uint32_t acid_auto_bar=~0u;')
patch('shell/gen_break_jobs.cpp','void Context::gen_break_tick(){','''void Context::gen_break_tick(){
    unsigned bar=host.ticks()/384;
    if(!host.playing())acid_auto_bar=~0u;
    else if(bar!=acid_auto_bar){acid_auto_bar=bar;
        if(bar&&!host_recording()&&!host.song_playing()){
            auto selected=ui.track;
            for(unsigned t=0;t<track_count;t++){const auto& tr=project.tracks[t];
                if(tr.engine==EngineKind::Plugin&&tr.plugin<max_plugins&&std::string(project.plugins[tr.plugin].name)=="Acid Engine"&&tr.acid_gen.auto_bars&&bar%tr.acid_gen.auto_bars==0&&!tr.mix.mute&&patterns.at[t][tr.pattern].steps()<=64){ui.track=uint8_t(t);gen8_action(13);}}
            ui.track=selected;
        }
    }''')

patch('shell/gen_break_jobs.cpp','#include <cmath>','#include <cmath>\n#include "rhythmer/engine/engine_host.h"')
shutil.copytree(ROOT/'third_party/fm1-break',runtime/'fm1-break',dirs_exist_ok=True)
for name in ('break_reference.c','acid_reference.c','break_acid.cpp','test_break_acid.py'):shutil.copy2(ROOT/'tests'/name,runtime/'tests'/name)

patch('model/project_file.cpp','    at=w.begin("ACGN");','    at=w.begin("BRSR");for(const auto& t:project.tracks)w.u8(t.break_source);w.end(at);\n    at=w.begin("ACGN");')
patch('model/project_file.cpp','} else if(name=="ACGN") {','} else if(name=="BRSR") {for(auto& t:project->tracks)t.break_source=r.u8()%2;\n        } else if(name=="ACGN") {')
patch('engine/engine_host.h','    bool playing() const','    unsigned break_source_of(unsigned t)const{return slots[t%track_count].sampler.manipulator.source();}\n    bool playing() const')
patch('shell/gen_break_jobs.cpp','    unsigned bar=host.ticks()/384;','    for(unsigned t=0;t<track_count;t++)if(project.tracks[t].break_bars)project.tracks[t].break_source=uint8_t(host.break_source_of(t));\n    unsigned bar=host.ticks()/384;')

patch('engine/engine_host.cpp','    if (out_mode[t] == 1) return true;', '    if(slots[t].kind==EngineKind::Sampler&&slots[t].sampler.manipulator.enabled()&&key<int(sampler_first_note))return false;\n    if (out_mode[t] == 1) return true;')
shutil.copy2(ROOT/'extensions/shell/break_acid_check.inc',base/'shell/break_acid_check.inc')
patch('shell/gen8_check.h','    std::printf("RHYTHMER_GEN8_SHELL', '    #include "rhythmer/shell/break_acid_check.inc"\n    std::printf("RHYTHMER_GEN8_SHELL')
previews=[]
for page in range(6):
 previews.append('    {"break-perf-%d",[](Shell&,Snapshot& s){s.ui.page=PageId::Edit;s.ui.break_perf_page=%d;s.project.tracks[s.ui.track].engine=EngineKind::Sampler;s.project.tracks[s.ui.track].break_bars=2;s.ui.held_pads=1<<6;}},' % (page,page))
for page in range(3):
 previews.append('    {"acid-settings-%d",[](Shell&,Snapshot& s){s.ui.page=PageId::Steps;s.ui.sheet_open=true;s.ui.gen8_mode=4;s.ui.acid_gen_page=%d;s.project.tracks[s.ui.track].engine=EngineKind::Plugin;s.project.tracks[s.ui.track].plugin=0;std::strcpy(s.project.plugins[0].name,"Acid Engine");s.project.tracks[s.ui.track].acid_gen.seed=0xdeadbeef;}},' % (page,page))
patch('tools.cpp','const Preview previews[] {','const Preview previews[] {\n'+'\n'.join(previews))

patch('shell/gen_break_jobs.cpp','ui.break_bars=project.gen8.bars;','ui.break_bars=ui.break_load_b?project.tracks[ui.break_track].break_bars:project.gen8.bars;')

p=runtime/'tests/test_rhythmer.py';s=p.read_text();s=s.replace('"src/rhythmer/engine/sampler.cpp",','"src/rhythmer/engine/sampler.cpp", "src/rhythmer/engine/break_manipulator.cpp",');p.write_text(s)

patch('shell/ui_state.h','bool break_load_b=false;','bool break_load_b=false,break_pending_b=false;')
patch('shell/gen_break_jobs.cpp','ui.break_pending=slot;','ui.break_pending=slot;ui.break_pending_b=ui.break_load_b;')
patch('shell/gen_break_jobs.cpp','if(ui.break_load_b&&project.tracks[at].break_bars)','if(ui.break_pending_b&&project.tracks[at].break_bars)')
patch('shell/gen8_jobs.cpp','ui.break_browse=true;ui.break_track=ui.track;','ui.break_load_b=false;ui.break_browse=true;ui.break_track=ui.track;')

patch('pages/samples_page.cpp','if(key==0&&c.ui.break_browse&&(!c.library||c.library->top())){c.open(PageId::Steps);','if(key==0&&c.ui.break_browse&&(!c.library||c.library->top())){if(c.ui.break_load_b){c.ui.break_load_b=false;c.open(PageId::Edit);c.ui.break_perf_page=2;return;}c.open(PageId::Steps);')
patch('pages/edit_page.cpp','c.ui.break_track=c.ui.track;c.open(PageId::Samples);','c.ui.break_track=c.ui.track;if(c.ui.break_load_b)c.project.gen8.bars=c.track().break_bars;c.open(PageId::Samples);')

# Filter value text uses the original cutoff table, rather than an opaque 0-127.
source=(ROOT/'third_party/fm1-break/jungle.c').read_text();table=re.search(r'static const uint16_t filter_hz\[128\] = \{(.*?)\};',source,re.S).group(1)
(base/'model/break_filter.h').write_text('#pragma once\n// SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception\nnamespace rhythmer { inline constexpr unsigned break_filter_hz[128]={'+table+'}; }\n')
patch('pages/common.cpp','#include <algorithm>','#include <algorithm>\n#include "rhythmer/model/break_filter.h"')
patch('pages/common.cpp','"LP "+juce::String(b.value):"HP "+juce::String(b.value-64)','"LP "+juce::String(break_filter_hz[b.value]):"HP "+juce::String(break_filter_hz[b.value])')
patch('pages/common.cpp','c.unit=b.id==6?"ms":b.id==7?"ms":b.id==8?"x":"";','c.unit=b.id==3&&b.value!=64?"Hz":b.id==6?"ms":b.id==7?"ms":b.id==8?"x":"";')

patch('shell/bindings.cpp','    case PageId::Samples:','    case PageId::Samples:\n        if(ui.break_browse&&ui.break_load_b)return {};')
patch('pages/samples_page.cpp','s.ui.break_browse?"GEN":""','s.ui.break_browse?(s.ui.break_load_b?"PERF":"GEN"):""')

patch('pages/steps_page.cpp','s.ui.gen8_mode==1?"SETUP":"GEN"','s.ui.gen8_mode==1?"SETUP":s.ui.gen8_mode==4?"SETTINGS":"GEN"')
patch('pages/steps_page.cpp','s.ui.gen8_mode==2&&s.ui.sheet_row==5','s.ui.gen8_mode==2&&s.ui.sheet_row>=5')

shutil.copy2(ROOT/'extensions/model/break_commands.h',base/'model/break_commands.h')
for rel in ('pages/edit_page.cpp','pages/steps_page.cpp','shell/step_edit.cpp','pages/roll_page.cpp'):
 p=base/rel;s=p.read_text();s='#include "rhythmer/model/break_commands.h"\n'+s;p.write_text(s)
patch('shell/context.cpp','    auto& t = track();\n    if (t.arp) {','    auto& t = track();\n    if(down&&t.engine==EngineKind::Sampler&&t.break_bars)t.last_note=uint8_t(k);\n    if (t.arp) {')
patch('shell/step_lane.h','    if (t.levels) return -1;','    if(t.engine==EngineKind::Sampler&&t.break_bars)return t.last_note;\n    if (t.levels) return -1;')
patch('shell/step_edit.cpp','std::string key_label(const Track& t, int key) {','std::string key_label(const Track& t, int key) {\n    if(t.engine==EngineKind::Sampler&&t.break_bars)return break_event_label(key);')
patch('pages/steps_page.cpp','    int in_hand = lane_event(', '    if(s.track().engine==EngineKind::Sampler&&s.track().break_bars)step="STEP "+juce::String(highlight+1)+" / "+juce::String(break_event_label(s.track().last_note));\n    int in_hand = lane_event(')
patch('pages/steps_page.cpp','        bool kit = t.engine == EngineKind::Sampler;','        if(t.engine==EngineKind::Sampler&&t.break_bars){\n            int order[35];for(int i=0;i<16;i++)order[i]=int(sampler_first_note+t.bank*16+i);for(int i=0;i<19;i++)order[i+16]=i;\n            int index=0;for(int i=0;i<35;i++)if(order[i]==steps_lane(t))index=i;\n            int to=order[std::clamp(index+delta,0,34)];unsigned st=unsigned(c.ui.held_step);\n            if(to!=steps_lane(t)&&!step_velocity(pattern,st,to)&&move_lane(pattern,st,steps_lane(t),uint8_t(to))){t.last_note=uint8_t(to);c.sync_pattern(c.ui.track,t.pattern);}\n            c.ui.held_edited=true;return;\n        }\n        bool kit = t.engine == EngineKind::Sampler;')
patch('pages/roll_page.cpp','            if (pad < 0 || (key - int(ui.roll_key)) % 2) continue;','            if(track.break_bars&&key>=0&&key<19){\n                if((key-int(ui.roll_key))%2)continue;\n                auto label=key<16?"R"+juce::String(key+1):key==16?juce::String("A"):key==17?juce::String("B"):juce::String("RT");\n                p.text(label,0,top+r*row_h-2,gutter-4,row_h+3,plain(key==int(ui.roll_key)?c:colour::dim,type::small,Weight::SemiBold),juce::Justification::centredRight);continue;\n            }\n            if (pad < 0 || (key - int(ui.roll_key)) % 2) continue;')
patch('pages/roll_page.cpp','juce::String(note_name(focused->key))','juce::String(key_label(track,focused->key))')
patch('shell/gen_break_jobs.cpp','t.set_name("BREAK");','t.set_name("BREAK");t.last_note=uint8_t(sampler_first_note+t.bank*16);')

patch('engine/engine_host.cpp','void EngineHost::render_engine(unsigned t, Slot& slot, unsigned at, unsigned frames) {','void EngineHost::render_engine(unsigned t, Slot& slot, unsigned at, unsigned frames) {\n    if(slot.kind==EngineKind::Sampler&&slot.sampler.manipulator.enabled())slot.sampler.manipulator.transport(is_playing.load(std::memory_order_relaxed),tick_count.load(std::memory_order_relaxed));')

patch('shell/gen8_check.h','#include "rhythmer/pages/pages.h"','#include "rhythmer/pages/pages.h"\n#include "rhythmer/shell/step_edit.h"\n#include "rhythmer/shell/step_lane.h"')
patch('shell/gen8_jobs.cpp','        notice("BREAK: "+std::string(gen_menu_name(settings.genre)));','        if(action<=6)track().last_note=map.slices[0];\n        notice("BREAK: "+std::string(gen_menu_name(settings.genre)));')
patch('tools.cpp','const Preview previews[] {','const Preview previews[] {\n    {"break-seq-roll",[](Shell&,Snapshot& s){s.ui.page=PageId::Steps;s.project.tracks[0].engine=EngineKind::Sampler;s.project.tracks[0].break_bars=2;s.project.tracks[0].last_note=8;}},')

patch('shell/ui_state.h','uint8_t acid_gen_page=0,break_perf_page=0;','std::array<unsigned,track_count> break_feedback_seen{};\n    uint8_t acid_gen_page=0,break_perf_page=0;')
patch('engine/engine_host.h','    unsigned break_source_of(unsigned t)const','    bool break_feedback(unsigned t,unsigned& version,unsigned& variation,unsigned& drift)const{return slots[t%track_count].sampler.manipulator.feedback(version,variation,drift); }\n    unsigned break_source_of(unsigned t)const')
patch('shell/gen_break_jobs.cpp','    unsigned bar=host.ticks()/384;','    for(unsigned t=0;t<track_count;t++)if(project.tracks[t].break_bars){unsigned variation=0,drift=0;if(host.break_feedback(t,ui.break_feedback_seen[t],variation,drift)){project.tracks[t].break_perf[1]=uint16_t(variation);project.tracks[t].break_perf[2]=uint16_t(drift);}}\n    unsigned bar=host.ticks()/384;')
