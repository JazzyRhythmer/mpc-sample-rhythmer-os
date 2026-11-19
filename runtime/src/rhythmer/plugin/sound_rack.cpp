// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 jazzy rhythmer
#include "rhythmer/plugin/sound_rack.h"
#include "rhythmer/plugin/rate_bridge.h"
#include "rhythmer/plugin/design_pages.h"
#include "rhythmer/plugin/vst2_instance.h"
#include "rhythmer/plugin/kit_filter.h"
#include "rhythmer/plugin/kit_output_stage.h"
#include <atomic>
#include <array>
#include <condition_variable>
#include <deque>
#include <mutex>
#include <thread>
#include <set>
#include <map>

namespace rhythmer {
using namespace juce;
namespace {
constexpr int pads=64, controls=1024;
var object() {return var(new DynamicObject());}
void put(var& v,const Identifier& key,const var& value){v.getDynamicObject()->setProperty(key,value);}
var get(const var& v,const Identifier& key){return v.getProperty(key,{});}
int number(const var& v,const Identifier& key,int fallback=0){auto x=get(v,key);return x.isVoid()?fallback:int(x);}
String canonical(String s){return s.replace("GROOVE - FM1","RHYTHMER - FM1").replace("GROOVE - Move","RHYTHMER - Move");}
String text(const var& v,const Identifier& key){return get(v,key).toString();}
const var& at(const var& v,int i){static const var empty;auto* a=v.getArray();return a&&i>=0&&i<a->size()?a->getReference(i):empty;}
int size(const var& v){auto* a=v.getArray();return a?a->size():0;}

struct Child {
    std::unique_ptr<AudioPluginInstance> synth;
    int engine=-1,metadata_engine=-1,sound=0,source_note=60;
    bool drums=false, silenced=false, velocity_pressure=false;
    std::vector<int> parameter_order,parameter_ordinals;
    std::vector<float> defaults; // loaded source-preset defaults; VST2 has no default-value ABI
    std::vector<String> parameter_names;
    AudioBuffer<float> audio;
    MidiBuffer midi;
    bool manual_clock=false;
    PluginRateBridge pitch;
    double pitch_ratio=1;
    std::array<bool,128> held{};
    explicit Child(std::unique_ptr<AudioPluginInstance> p):synth(std::move(p)),audio(2,128){midi.ensureSize(32768);pitch.reset(44100,44100,true,false);}
    ~Child(){synth->setPlayHead(nullptr);synth->releaseResources();}
};
struct Graph {
    std::array<std::shared_ptr<Child>,pads> routes{};
    int kit=0;
    float kit_mix_gain=1;
    std::array<int,pads> sounds{},notes{};
    std::array<std::vector<int>,pads> orders,ordinals;
    std::array<std::vector<String>,pads> names;
    std::array<bool,pads> edited{};
    KitFilterValues kit_filter{{100,0,0}},kit_filter_defaults{{100,0,0}};
    uint64_t filter_epoch=0;bool filter_edited=false;
};
struct Request {int kind,index;float value=0;std::vector<uint8_t> bytes;uint32_t revision=0;Request(int k=0,int i=0,float v=0):kind(k),index(i),value(v){}};

class Rack final:public AudioPluginInstance {
public:
    Rack(var c,int s,SoundLoader l,double r,int b):AudioPluginInstance(BusesProperties().withOutput("Output",AudioChannelSet::stereo(),true)),
        catalog(std::move(c)),single(s),base(s<0||output_filter_engine(text(engine(s),"name"))?9:6),loader(std::move(l)),rate(r),block(b){
        auto directory=text(catalog,"user_directory");
        if(directory.isNotEmpty()) {
            String folder=single<0?String():File::createLegalFileName(text(engine(single),"folder"));
            String old_folder=folder.replace("RHYTHMER - FM1","GROOVE - FM1").replace("RHYTHMER - Move","GROOVE - Move");
            user_directory=File(directory).getChildFile(single<0?"Kits":"Sounds/"+folder);
            auto old_root=text(catalog,"legacy_user_directory");
            if(old_root.isNotEmpty()){legacy_directories.push_back(File(old_root).getChildFile(single<0?"Kits":"Sounds/"+old_folder));if(folder!=old_folder)legacy_directories.push_back(File(old_root).getChildFile("Sounds/"+folder));}
            if(single>=0&&folder!=old_folder)legacy_directories.push_back(File(directory).getChildFile("Sounds/"+old_folder));
            for(int i=0;i<64;++i)if(user_file(i).existsAsFile())saved_slots.push_back(i);
        }
        if(base==9)kit_filter=std::make_unique<KitFilterStage>();
        if(single>=0){auto g=std::make_unique<Graph>();g->routes[0]=load(single,0);g->notes[0]=g->routes[0]->source_note;g->orders[0]=g->routes[0]->parameter_order;g->ordinals[0]=g->routes[0]->parameter_ordinals;g->names[0]=g->routes[0]->parameter_names;publish(std::move(g));}
        else load_kit(0);
        if(!active.load())throw std::runtime_error("No sound graph");
        for(int i=0;i<base+controls;++i)addHostedParameter(std::make_unique<Parameter>(*this,i));
        worker=std::thread([this]{run();});
    }
    ~Rack() override {
        {std::lock_guard<std::mutex> guard(lock);stopping=true;}wake.notify_all();if(worker.joinable())worker.join();
        active.store(nullptr);graphs.clear();
    }
    const String getName() const override{return single<0?"Rhythmer Kit":text(engine(single),"name");}
    void fillInPluginDescription(PluginDescription& d) const override{d.name=d.descriptiveName=getName();d.manufacturerName="jazzy rhythmer";d.pluginFormatName="Rhythmer";d.isInstrument=true;d.numOutputChannels=2;d.uniqueId=single<0?0x47724b32:0x47725332;}
    void prepareToPlay(double r,int b) override{setRateAndBufferSizeDetails(r,b);kit_output.prepare(float(r));}
    void releaseResources() override{}
    double getTailLengthSeconds() const override{return 30;}
    bool acceptsMidi() const override{return true;}
    bool producesMidi() const override{return false;}
    AudioProcessorEditor* createEditor() override{return nullptr;}
    bool hasEditor() const override{return false;}
    int getNumPrograms() override{std::lock_guard<std::mutex> guard(lock);return factory_count()+int(saved_slots.size());}
    int getCurrentProgram() override{std::lock_guard<std::mutex> guard(lock);return current_program();}
    const String getProgramName(int i) override{std::lock_guard<std::mutex> guard(lock);if(i>=factory_count()){int n=i-factory_count();return n<int(saved_slots.size())?(single<0?"User Kit ":"User Sound ")+String(saved_slots[size_t(n)]+1).paddedLeft('0',2):String();}return single<0?text(at(get(catalog,"kits"),i),"name"):sound_name(single,selection(single,i));}
    void changeProgramName(int,const String&) override{}
    void setCurrentProgram(int i) override{if(i>=0&&i<getNumPrograms()){enqueue({0,i});flush();if(single<0)change(0,0);}}
    bool drum_names(DrumVoices& result){std::lock_guard<std::mutex> guard(lock);if(single>=0)return false;auto* g=active.load();if(!g)return true;for(int i=0;i<pads;++i)if(auto c=g->routes[size_t(i)]){auto name=sound_name(c->engine,g->sounds[size_t(i)]).fromLastOccurrenceOf(" / ",false,false);if(name.isEmpty())name=sound_name(c->engine,g->sounds[size_t(i)]);std::snprintf(result.names[size_t(i)].data(),result.names[size_t(i)].size(),"%s",name.toRawUTF8());}return true;}
    String preset_name(){std::lock_guard<std::mutex> guard(lock);auto* g=active.load();if(!g)return {};String name=user_label.isNotEmpty()?user_label:single<0?text(at(get(catalog,"kits"),g->kit),"name"):sound_name(single,g->sounds[0]);if(single>=0&&user_label.isNotEmpty())name+=" / "+sound_name(single,g->sounds[0]);if(single<0)if(auto c=g->routes[size_t(focus)])name+=" / Pad "+String(focus+1)+": "+sound_name(c->engine,g->sounds[size_t(focus)]).fromLastOccurrenceOf(" / ",false,false);if(g->edited[size_t(single<0?focus:0)]||(kit_filter&&g->filter_edited))name+=" *";return name;}
    uint32_t revision(){std::lock_guard<std::mutex> guard(lock);return layout_revision;}
    std::array<int,3> kit_mix_controls(){
        std::array<int,3> out{{-1,-1,-1}};if(single>=0)return out;
        auto c=focused();if(!c)return out;
        int volume=-1,pan=-1,tune=-1,decay=-1;
        auto metadata=get(source_info(*c),"parameters");const auto& order=g_order();
        for(unsigned i=0;i<order.size();++i){auto role=text(at(metadata,order[i]),"kit_mix_role");int shown=base+int(i);
            if(role=="volume"&&volume<0)volume=shown;
            else if(role=="pan"&&pan<0)pan=shown;
            else if(role=="tune"&&tune<0)tune=shown;
            else if(role=="decay"&&decay<0)decay=shown;
        }
        if(volume<0)return out;
        out[0]=volume;out[1]=pan>=0?pan:tune>=0?tune:decay;
        out[2]=pan>=0?(tune>=0?tune:decay):(tune>=0?decay:-1);
        return out;
    }
    bool design_pages(PluginPanel& out){
        std::lock_guard<std::mutex> guard(lock);auto c=focused();if(!c&&single>=0)return false;
        auto source=c?text(source_info(*c),"name"):String("Empty");auto variant=c?text(source_info(*c),"variant"):String();if(variant.isNotEmpty())source+=" / "+variant;
        std::snprintf(out.design_source,sizeof out.design_source,"%s",source.toRawUTF8());
        if(design_cache_revision!=layout_revision){
            std::vector<PluginDesignControl> list;auto mix=kit_mix_controls();
            for(int shown:mix)if(shown>=0)list.push_back({shown,-200,"PAD MIX"});
            if(kit_filter)for(int i=6;i<9;++i)list.push_back({i,-100,single<0?"KIT FILTER":"OUTPUT FILTER"});
            const auto& order=g_order();auto metadata=c?get(source_info(*c),"parameters"):var();
            for(unsigned i=0;i<order.size();++i){if(std::find(mix.begin(),mix.end(),int(i)+base)!=mix.end())continue;auto p=at(metadata,order[i]);auto group=text(p,"edit_group");int rank=number(p,"edit_group_order",700);
                // Hortator models reuse eight slots for different functions.
                // Classify their current native names, never a stale kit label.
                auto family=text(source_info(*c),"name");auto* graph=active.load();const auto& names=graph->names[size_t(single<0?focus:0)];
                if((family=="Hortator"||family=="Acid Engine")&&i<names.size()){
                    auto n=names[i].toLowerCase();
                    if(n.contains("model")){group="MODEL";rank=0;}
                    else if(n.contains("cut")||n.contains("reso")){group="FILTER";rank=200;}
                    else if(n.contains("decay")||n.contains("sdec")||n.contains("attack")||n.contains("env")){group="ENV";rank=320;}
                    else if(n.contains("wave")||n.contains("tune")||n.contains("freq")||n.contains("sub")){group="OSC";rank=100;}
                    else if(n.contains("level")||n.contains("pan")){group="MIX";rank=600;}
                    else if(n.contains("gate")||n.contains("accnt")){group="PERFORM";rank=800;}
                    else {group="TONE";rank=150;}
                }
                list.push_back({int(i)+base,rank,group.toStdString()});
            }
            design_cache=build_plugin_design_pages(list);design_cache_revision=layout_revision;
        }
        if(design_cache.size()>out.design_pages.size())return false;
        out.design_count=uint16_t(design_cache.size());std::copy(design_cache.begin(),design_cache.end(),out.design_pages.begin());return out.design_count>0;
    }
    std::array<int,3> quick_parameters(){
        std::lock_guard<std::mutex> guard(lock);std::array<int,3> out{{-1,-1,-1}};auto c=focused();if(single<0)return {{6,7,8}};if(kit_filter){out[0]=6;out[1]=7;}if(!c)return out;
        const auto& order=g_order();auto metadata=get(source_info(*c),"parameters");auto preferred=get(source_info(*c),"quick_controls");
        auto used=[&](int shown){return std::find(out.begin(),out.end(),shown)!=out.end();};
        // The original Hortator ACID model exposes its own filter before the
        // additional per-voice insert filter. Scope this to source core slots.
        auto family=text(source_info(*c),"name");if(family=="Hortator"||family=="Acid Engine"){
            for(unsigned j=0;j<order.size();++j)if(order[j]>0&&order[j]<89){auto name=c->synth->getParameters()[order[j]]->getName(64).fromLastOccurrenceOf(" ",false,false).toUpperCase();int slot=name=="CUTOF"||name=="CUTOFF"?0:name=="RESO"||name=="RESONANCE"?1:name=="ENVMD"?2:-1;if(slot>=0)out[size_t(slot)]=base+int(j);}
        }
        for(int slot=0;slot<3;++slot){if(out[size_t(slot)]>=0)continue;auto candidates=at(preferred,slot);for(int k=0;k<size(candidates)&&out[size_t(slot)]<0;++k)for(unsigned j=0;j<order.size();++j)if(text(at(metadata,order[j]),"key")==at(candidates,k).toString()&&!used(base+int(j))){out[size_t(slot)]=base+int(j);break;}}
        for(int slot=0;slot<3;++slot)if(out[size_t(slot)]<0)for(unsigned j=0;j<order.size();++j){int shown=base+int(j);if(!used(shown)){out[size_t(slot)]=shown;break;}}
        return out;
    }
    int source_begin()const{return base;}
    bool kit_filter_index(int i)const{return base==9&&i>=6&&i<9;}
    int focused_pad(){std::lock_guard<std::mutex> guard(lock);return single<0?focus:-1;}
    int count() {std::lock_guard<std::mutex> guard(lock);auto c=focused();return base+(c?std::min(controls,int(g_order().size())):0);}
    void getStateInformation(MemoryBlock& result) override{
        flush();write_state(result);
    }
    void write_state(MemoryBlock& result){
        std::lock_guard<std::mutex> guard(lock);
        auto* g=active.load();if(!g)return;
        var root=object();put(root,"schema",2);put(root,"user_label",user_label);put(root,"user_slot",selected_user_slot);put(root,"single",single);put(root,"single_engine",single<0?String():text(engine(single),"folder"));put(root,"pad",focus);put(root,"kit",g->kit);put(root,"kit_name",text(at(get(catalog,"kits"),g->kit),"name"));put(root,"kit_mix_gain",g->kit_mix_gain);
        if(kit_filter){Array<var> values,defaults;for(int i=0;i<3;++i){values.add(int(g->kit_filter[size_t(i)]));defaults.add(int(g->kit_filter_defaults[size_t(i)]));}put(root,"kit_filter",values);put(root,"kit_filter_defaults",defaults);put(root,"kit_filter_edited",g->filter_edited);}
        Array<var> children,routes;std::vector<Child*> seen;
        for(const auto& c:g->routes){
            if(!c){routes.add(-1);continue;}
            auto found=std::find(seen.begin(),seen.end(),c.get());int id=int(found-seen.begin());
            if(found==seen.end()){
                seen.push_back(c.get());var row=object();put(row,"engine",text(source_info(*c),"folder"));put(row,"sound",c->sound);
                MemoryBlock chunk;c->synth->getStateInformation(chunk);put(row,"state",chunk.toBase64Encoding());
                Array<var> values;for(auto* p:c->synth->getParameters())values.add(p->getValue());put(row,"values",values);Array<var> defaults;for(float value:c->defaults)defaults.add(value);put(row,"reset_defaults",defaults);children.add(row);
            }
            var route=object();put(route,"child",id);put(route,"sound",g->sounds[size_t(&c-g->routes.data())]);put(route,"note",g->notes[size_t(&c-g->routes.data())]);put(route,"edited",g->edited[size_t(&c-g->routes.data())]);routes.add(route);
        }
        put(root,"children",children);put(root,"routes",routes);
        const String serialized=JSON::toString(root,true);result.replaceAll(serialized.toRawUTF8(),size_t(serialized.getNumBytesAsUTF8()));
    }
    void setStateInformation(const void* data,int n) override{
        if(!data||n<1||n>32*1024*1024)return;
        Request r{4,0};r.bytes.assign(static_cast<const uint8_t*>(data),static_cast<const uint8_t*>(data)+n);enqueue(std::move(r));flush();
    }
    void processBlock(AudioBuffer<float>& output,MidiBuffer& input) override{
        Graph* g;
        do {g=active.load(std::memory_order_seq_cst);hazard.store(g,std::memory_order_seq_cst);}while(g!=active.load(std::memory_order_seq_cst));
        output.clear();
        if(g){
            // Segment at MIDI boundaries; incoming offsets survive both the
            // original engine and the percussion tape-rate conversion.
            int cursor=0;
            for(const auto item:input){int pos=std::clamp(item.samplePosition,0,output.getNumSamples());
                if(pos>cursor)render(*g,output,cursor,pos-cursor);
                cursor=pos;const auto msg=item.getMessage();if(kit_filter&&msg.isAllSoundOff())kit_filter->silence();
                if(msg.isNoteOnOrOff()){
                    int note=msg.getNoteNumber();int slot=single<0?note-36:0;
                    if(slot>=0&&slot<pads)if(auto c=g->routes[size_t(slot)]){
                        auto m=msg;
                        if(msg.isNoteOn()){c->silenced=false;if(c->velocity_pressure)c->midi.addEvent(MidiMessage::channelPressureChange(msg.getChannel(),msg.getVelocity()),0);}
                        bool drum=c->drums;
                        if(single>=0&&drum){
                            if(msg.isNoteOn()){
                                c->held[size_t(note)]=true;
                                const double ratio=std::pow(2.0,std::clamp(note-60,-36,36)/12.0);
                                if(std::abs(ratio-c->pitch_ratio)>1e-8){c->pitch_ratio=ratio;c->pitch.reset(unsigned(std::lround(44100*ratio)),44100,true,false);}
                            }else {c->held[size_t(note)]=false;bool held=false;for(bool h:c->held)held|=h;if(held)continue;}
                        }
                        if(single<0||drum)m.setNoteNumber(g->notes[size_t(slot)]);
                        c->midi.addEvent(m,0);
                    }
                }else each(*g,[&](Child& c){if(c.manual_clock&&(msg.isMidiClock()||msg.isMidiStart()||msg.isMidiContinue()||msg.isMidiStop()))return;c.midi.addEvent(msg,0);if(msg.isAllNotesOff()||msg.isAllSoundOff())c.held.fill(false);if(msg.isAllSoundOff())c.silenced=true;});
            }
            if(cursor<output.getNumSamples())render(*g,output,cursor,output.getNumSamples()-cursor);
        }
        input.clear();hazard.store(nullptr,std::memory_order_seq_cst);
    }
    String parameter_name(int i){std::lock_guard<std::mutex> guard(lock);if(kit_filter_index(i)){static const char* names[]{"KIT CUTOFF","KIT RESONANCE","KIT FILTER TYPE"};return single<0?String(names[i-6]):String(names[i-6]).replace("KIT ","OUTPUT ");}if(i==3)return "Save slot";if(i==4)return single<0?"Save Kit":"Save Sound";if(i==5)return "Status";if(i==0)return single<0?"Pad":"Sound";if(i==1)return single<0?"P"+String(focus+1).paddedLeft('0',2)+" Engine":"Pitch reference";if(i==2)return single<0?"P"+String(focus+1).paddedLeft('0',2)+" Sound":"Pitch mode";auto c=focused();int p=i-base;String name=c&&p>=0&&p<int(g_order().size())?c->synth->getParameters()[g_order()[size_t(p)]]->getName(64):String();
        if(single<0&&c&&p>=0&&p<int(g_order().size())){auto role=text(at(get(source_info(*c),"parameters"),g_order()[size_t(p)]),"kit_mix_role");
            auto label=role=="volume"?String("Volume"):role=="pan"?String("Pan"):role=="tune"?String("Tune"):role=="decay"?String("Decay"):String();
            if(label.isNotEmpty())return "P"+String(focus+1).paddedLeft('0',2)+" "+label;
        }
        if(c&&p>=0&&p<int(g_order().size())){auto metadata=at(get(source_info(*c),"parameters"),g_order()[size_t(p)]);auto label=text(metadata,"edit_name");if(label.isNotEmpty())name=label;auto dynamic=get(metadata,"dynamic_labels");int selector=number(metadata,"dynamic_selector",-1);if(dynamic.isArray()&&selector>=0&&selector<c->synth->getParameters().size())name=at(dynamic,std::clamp(int(std::lround(c->synth->getParameters()[selector]->getValue()*(size(dynamic)-1))),0,size(dynamic)-1)).toString();}
        if(c&&(c->drums||get(source_info(*c),"voice_parameters").isObject())){int reference_note=single<0?active.load()->notes[size_t(focus)]:c->source_note;if(reference_note==60&&number(source_info(*c),"native_pitch_parameter",-1)>=0)reference_note=36;auto voice=get(source_info(*c),"voices");for(int n=0;n<size(voice);++n)if(number(at(voice,n),"note")==reference_note||number(at(voice,n),"note")==int(get(get(source_info(*c),"control_notes"),String(reference_note)))){auto prefix=text(at(voice,n),"name")+" ";if(name.startsWithIgnoreCase(prefix))name=name.substring(prefix.length());}String prefix="Pad "+String(reference_note-35)+" ";if(name.startsWithIgnoreCase(prefix))name=name.substring(prefix.length());}
        if(c){auto prefix=text(source_info(*c),"strip_voice_prefix");if(prefix.isNotEmpty()&&name.startsWithIgnoreCase(prefix))name=name.substring(prefix.length());}
        if(name.startsWithIgnoreCase("Pad ")){auto tail=name.substring(4);int space=tail.indexOfChar(' ');if(space>0&&tail.substring(0,space).containsOnly("0123456789"))name=tail.substring(space+1);}
        if(c&&c->drums){const int source=single<0?active.load()->notes[size_t(focus)]-35:c->source_note-35;
            for(const auto& prefix:{"Pad"+String(source)+" ","Voice "+String(source)+" ","V"+String(source)+" ","S"+String(source)+" "})if(name.startsWithIgnoreCase(prefix))name=name.substring(prefix.length());}
        if(name=="TUNE")name="Tune";else if(name=="DECAY")name="Decay";else if(name=="CUTOF")name="Cutoff";else if(name=="RESO")name="Resonance";else if(name=="ENVMD")name="Env Mod";else if(name=="ACCNT")name="Accent";else if(name=="WAVE")name="Wave";else if(name=="GATE")name="Gate";
        const char* expanded[][2]={{"SDEC","Sweep Decay"},{"PUNCH","Punch"},{"NOISE","Noise"},{"SUB","Sub"},{"CLIP","Clip"},{"Oscilltr","Oscillator"},{"Frequncy","Frequency"},{"Resnance","Resonance"},{"Overdriv","Overdrive"},{"SampleRt","Sample Rate"},{"Transnt","Transient"},{"PitchMod","Pitch Mod"},{"CrossMod","Cross Mod"},{"DstParam","Destination"},{"PulsWdth","Pulse Width"},{"AudioOut","Output"}};
        for(const auto& pair:expanded)if(name==pair[0])name=pair[1];
        if(name=="Model")name="Sound model";
        if(name.isEmpty()&&p>=0&&p<int(g_order().size()))name="Parameter "+String(g_order()[size_t(p)]+1);
        if(p>=0){auto* g=active.load();const auto& ordinals=g->ordinals[size_t(single<0?focus:0)];if(p<int(ordinals.size())&&ordinals[size_t(p)]>0)name+=" ("+String(ordinals[size_t(p)])+")";}
        if(c&&p>=0&&p<int(g_order().size())){auto category=text(at(get(source_info(*c),"parameters"),g_order()[size_t(p)]),"category");if(c->drums){const int source=single<0?active.load()->notes[size_t(focus)]-35:c->source_note-35;for(const auto& prefix:{"Pad "+String(source),"Pad"+String(source),"Voice "+String(source),"V"+String(source),"S"+String(source)})if(category.equalsIgnoreCase(prefix))category.clear();else if(category.startsWithIgnoreCase(prefix+" "))category=category.substring(prefix.length()+1);}
            if(single<0&&(category.equalsIgnoreCase("Master")||category.equalsIgnoreCase("General")||category.equalsIgnoreCase("FX")||category.equalsIgnoreCase("Global FX")||category.equalsIgnoreCase("EQ")||category.equalsIgnoreCase("Delay")||category.equalsIgnoreCase("Reverb")||category.equalsIgnoreCase("Output")))category="Source "+category;
            if(category.isNotEmpty()&&!name.equalsIgnoreCase(category)&&!(name=="Sound model"&&category.equalsIgnoreCase("Model"))&&!name.startsWithIgnoreCase(category+" ")){bool joined=false;for(int start=0;start<category.length();++start)if(start==0||category[start-1]==' '){auto suffix=category.substring(start);if(name.equalsIgnoreCase(suffix)||name.startsWithIgnoreCase(suffix+" ")){name=category.substring(0,start)+name;joined=true;break;}}if(!joined)name=category+" "+name;}}
        return single<0&&name.isNotEmpty()?"P"+String(focus+1).paddedLeft('0',2)+" "+name:name;}
    float parameter_value(int i){std::lock_guard<std::mutex> guard(lock);if(kit_filter_index(i)){auto* g=active.load();return g?g->kit_filter[size_t(i-6)]/float(i==8?2:100):0;}auto c=focused();if(i==3)return save_slot/63.0f;if(i==4||i==5)return 0;if(i==0)return single<0?focus/63.0f:current_program()/float(std::max(1,factory_count()+int(saved_slots.size())-1));if(i==1)return single<0&&c?c->engine/float(std::max(1,size(get(catalog,"engines"))-1)):0;if(i==2)return single<0&&c?selection_index(c->engine,current_sound())/float(std::max(1,selection_count(c->engine)-1)):0;int p=i-base;if(!c||p<0||p>=int(g_order().size()))return 0;int index=g_order()[size_t(p)];float value=c->synth->getParameters()[index]->getValue();auto meta=at(get(source_info(*c),"parameters"),index);auto choices=get(meta,"option_indices");if(size(choices)>1){int source=int(std::lround(value*(size(get(meta,"options"))-1)));for(int n=0;n<size(choices);++n)if(int(at(choices,n))==source)return n/float(size(choices)-1);return 0;}return value;}
    String parameter_text(int i){std::lock_guard<std::mutex> guard(lock);if(kit_filter_index(i)){auto* g=active.load();if(!g)return {};if(i==8){static const char* types[]{"LP","BP","HP"};return types[g->kit_filter[2]];}return String(g->kit_filter[size_t(i-6)])+" %";}auto c=focused();if(i==3)return String(save_slot+1);if(i==4)return "Turn to SAVE";if(i==5)return busy?"Working...":(last_error.isEmpty()?"Ready":last_error);if(i==0)return single<0?String(focus+1):(user_label.isNotEmpty()?user_label:c?sound_name(c->engine,current_sound()):"Empty");if(i==1)return single<0?(c?text(source_info(*c),"name")+(text(source_info(*c),"variant").isNotEmpty()?" / "+text(source_info(*c),"variant"):String()):"Empty"):"C4 / MIDI 60";if(i==2)return single<0?(c?sound_name(c->engine,current_sound()):"Empty"):(c&&c->drums?"Pitch + Length":"Key Pitch");int p=i-base;if(!c||p<0||p>=int(g_order().size()))return {};int index=g_order()[size_t(p)];auto* param=c->synth->getParameters()[index];auto native_meta=at(get(source_info(*c),"parameters"),index);if(bool(get(native_meta,"display_native_percent"))){double lo=double(get(native_meta,"minimum")),hi=double(get(native_meta,"maximum"));return String((lo+(hi-lo)*param->getValue())*100.0,0)+" %";}if(bool(get(at(get(source_info(*c),"parameters"),index),"display_percentage")))return String(param->getValue()*100,0)+" %";auto options=get(at(get(source_info(*c),"parameters"),index),"options");if(size(options)>0)return at(options,std::clamp(int(std::lround(param->getValue()*(size(options)-1))),0,size(options)-1)).toString();auto value=param->getText(param->getValue(),96);auto meta=at(get(source_info(*c),"parameters"),index);auto unit=param->getLabel().trim();if(unit.isEmpty())unit=text(meta,"unit");
        if(unit.isNotEmpty()&&!value.containsIgnoreCase(unit)&&value.trim().containsOnly("+-0123456789.eE ")){if(unit=="%"&&double(get(meta,"maximum"))<=1.0&&double(get(meta,"minimum"))>=0.0)value=String(value.getDoubleValue()*100.0,1);value+=" "+unit;}
        if(value.startsWithIgnoreCase("Pad ")){auto tail=value.substring(4);int space=tail.indexOfChar(' ');if(space>0&&tail.substring(0,space).containsOnly("0123456789"))value=(single<0?"P"+String(focus+1).paddedLeft('0',2)+" ":String())+tail.substring(space+1);}return value;}
    void change(int i,float value,uint32_t expected=0){if(!std::isfinite(value))return;value=std::clamp(value,0.0f,1.0f);if((single>=0&&(i==1||i==2))||i==5)return;if(i==4){if(value>=0.5f)enqueue({5,0});return;}if(single<0&&i==0){enqueue({1,0,value});flush();return;}if(single>=0&&i==0){enqueue({0,int(std::lround(value*(getNumPrograms()-1)))});return;}Request request{1,i,value};request.revision=expected;enqueue(std::move(request));}
private:
    static bool output_filter_engine(const String& name){
        return name=="Dexed"||name=="DRUM-X"||name=="Plaits"||name=="CS-1"||name=="MONO2K";
    }
    int parameter_steps(int i){
        std::lock_guard<std::mutex> guard(lock);auto c=focused();
        if(kit_filter_index(i))return i==8?3:101;
        if(i==0)return single<0?64:factory_count()+int(saved_slots.size());
        if(i==1)return single<0?size(get(catalog,"engines")):0;
        if(i==2)return single<0&&c?selection_count(c->engine):0;
        if(i==3)return 64;
        if(i==4||i==5)return 2;
        int at=i-base;if(!c||at<0||at>=int(g_order().size()))return 0;
        int index=g_order()[size_t(at)];auto meta=at_meta(*c,index);
        int choices=size(get(meta,"option_indices"));if(choices>1)return choices;
        int options=size(get(meta,"options"));return options>1?options:c->synth->getParameters()[index]->getNumSteps();
    }
    var at_meta(const Child& c,int index)const{return at(get(source_info(c),"parameters"),index);}
    float parameter_default(int i){
        std::lock_guard<std::mutex> guard(lock);if(kit_filter_index(i)){auto* g=active.load();return g?g->kit_filter_defaults[size_t(i-6)]/float(i==8?2:100):0;}auto c=focused();int p=i-base;
        if(!c||p<0||p>=int(g_order().size()))return 0;
        int index=g_order()[size_t(p)];float value=index<int(c->defaults.size())?c->defaults[size_t(index)]:c->synth->getParameters()[index]->getDefaultValue();
        auto meta=at_meta(*c,index);auto choices=get(meta,"option_indices");
        if(size(choices)>1){int source=int(std::lround(value*(size(get(meta,"options"))-1)));int best=0,distance=100000;
            for(int n=0;n<size(choices);++n){int d=std::abs(int(at(choices,n))-source);if(d<distance){distance=d;best=n;}}
            return best/float(size(choices)-1);
        }return std::clamp(value,0.f,1.f);
    }
    class Parameter final:public HostedParameter{
    public:Parameter(Rack& r,int i):rack(r),index(i){}
        float getValue() const override{return rack.parameter_value(index);}void setValue(float v)override{rack.change(index,v);}float getDefaultValue()const override{return rack.parameter_default(index);}
        int getNumSteps()const override{return rack.parameter_steps(index);}
        String getName(int n)const override{return rack.parameter_name(index).substring(0,n);}String getLabel()const override{return {};}
        String getParameterID()const override{return "sound_"+String(index);}String getText(float,int n)const override{return rack.parameter_text(index).substring(0,n);}float getValueForText(const String& s)const override{return s.getFloatValue();}
        bool isAutomatable()const override{return true;}
    private:Rack& rack;int index;
    };
    const var& engine(int i)const{return at(get(catalog,"engines"),i);}
    const var& source_info(const Child& c)const{return engine(c.metadata_engine);}
    int current_program()const{if(selected_user_slot>=0){auto found=std::find(saved_slots.begin(),saved_slots.end(),selected_user_slot);if(found!=saved_slots.end())return factory_count()+int(found-saved_slots.begin());}auto* g=active.load();return g?(single<0?g->kit:selection_index(single,g->sounds[0])):0;}
    int factory_count()const{return single<0?size(get(catalog,"kits")):selection_count(single);}
    File user_file(int i,bool writing=false)const{auto stem="Slot"+String(i+1).paddedLeft('0',2);auto f=user_directory.getChildFile(stem+".rhythmer.json");if(writing||f.existsAsFile())return f;auto old=user_directory.getChildFile(stem+".groove.json");if(old.existsAsFile())return old;for(const auto& directory:legacy_directories)for(auto extension:{".rhythmer.json",".groove.json"}){auto candidate=directory.getChildFile(stem+extension);if(candidate.existsAsFile())return candidate;}return f;}
    int sound_count(int e)const{return std::max(1,size(get(engine(e),"sounds")));}
    int selection_count(int e)const{auto list=get(engine(e),"selection");return list.isArray()?size(list):sound_count(e);}
    int selection(int e,int i)const{auto list=get(engine(e),"selection");return list.isArray()?int(at(list,std::clamp(i,0,size(list)-1))):i;}
    int selection_index(int e,int raw)const{auto list=get(engine(e),"selection");if(!list.isArray())return raw;for(int i=0;i<size(list);++i)if(int(at(list,i))==raw)return i;return 0;}
    String sound_name(int e,int s)const{String n=text(at(get(engine(e),"sounds"),s),"name");return n.isEmpty()?"Init":n;}
    std::shared_ptr<Child> focused()const{auto* g=active.load();return g?g->routes[size_t(single<0?focus:0)]:nullptr;}
    const std::vector<int>& g_order()const{static const std::vector<int> empty;auto* g=active.load();return g?g->orders[size_t(single<0?focus:0)]:empty;}
    int current_sound()const{auto* g=active.load();return g?g->sounds[size_t(single<0?focus:0)]:0;}
    void initial(Child& c){
        c.manual_clock=bool(get(source_info(c),"manual_clock"));
        if(auto* values=get(source_info(c),"native_initial").getDynamicObject())for(const auto& value:values->getProperties()){auto* native=dynamic_cast<Vst2Instance*>(c.synth.get());if(!native||!native->nativeSet(value.name.toString(),value.value.toString()))throw std::runtime_error("Native clock setup unavailable");}
        if(auto* values=get(source_info(c),"initial_values").getDynamicObject())for(const auto& value:values->getProperties()){
            int index=value.name.toString().getIntValue();if(index>=0&&index<c.synth->getParameters().size())c.synth->getParameters()[index]->setValue(float(value.value));
        }
    }
    void pitch_policy(Child& c){
        int pitch_parameter=number(source_info(c),"native_pitch_parameter",-1);
        if(pitch_parameter>=0&&pitch_parameter<c.synth->getParameters().size()){
            c.drums=c.synth->getParameters()[pitch_parameter]->getValue()<0.5f;
            if(!c.drums)c.source_note=60;else if(c.source_note==60)c.source_note=36;
        }
    }
    void context(Child& c,int note){
        if(!c.drums)return;
        auto metadata=get(source_info(c),"parameters");
        for(int i=0;i<size(metadata)&&i<c.synth->getParameters().size();++i){auto p=at(metadata,i);auto key=text(p,"key");
            if(key=="pad"||key=="focused_pad"||key=="ui_current_pad"){
                int minimum=number(p,"minimum"),maximum=number(p,"maximum",15);
                c.synth->getParameters()[i]->setValue(float(std::clamp(note-36,0,maximum-minimum))/std::max(1,maximum-minimum));
            }
        }
    }
    void order(Child& c){
        // All original automatable parameters remain accessible. Voice-local
        // controls sort first; the remaining original controls follow in pages.
        std::vector<int> first,rest;int voice=c.drums?c.source_note-35:0;
        String prefix="p"+String(voice).paddedLeft('0',2)+"_";
        const auto& ps=c.synth->getParameters();if(!ps.isEmpty())(void)ps[0]->getValue();auto metadata=get(source_info(c),"parameters");
        for(int i=0;i<ps.size();++i){if(!ps[i]->isAutomatable())continue;String key=text(at(metadata,i),"key");String name=ps[i]->getName(128);
            bool preset_control=false;for(int n=0;n<size(get(source_info(c),"preset_parameters"));++n)preset_control|=int(at(get(source_info(c),"preset_parameters"),n))==i;
            if(!at(metadata,i).isVoid()&&text(at(metadata,i),"name").trim().isEmpty()&&name.startsWith("Parameter "))continue;
            if(preset_control||name.trim().containsOnly("- ")||name.trim().isEmpty()||name.containsIgnoreCase("Unused")||name.startsWithIgnoreCase("Inactive Parameter"))continue;
            bool hidden=false;auto keys=get(source_info(c),"hidden_keys");for(int k=0;k<size(keys);++k)hidden|=at(keys,k).toString()==key;if(hidden)continue;
            auto dynamic=get(at(metadata,i),"dynamic_labels");int selector=number(at(metadata,i),"dynamic_selector",-1);if(dynamic.isArray()&&selector>=0&&selector<ps.size()&&at(dynamic,std::clamp(int(std::lround(ps[selector]->getValue()*(size(dynamic)-1))),0,size(dynamic)-1)).toString()=="-")continue;
            auto models=get(at(metadata,i),"active_models");
            if(models.isArray()){
                auto selector=text(source_info(c),"model_control_prefix")+String(c.source_note-35);int model=-1;
                for(int k=0;k<size(metadata)&&k<ps.size();k++)if(text(at(metadata,k),"key")==selector)model=int(std::lround(ps[k]->getValue()*(size(get(at(metadata,k),"options"))-1)));
                bool keep=false;for(int k=0;k<size(models);k++)keep|=int(at(models,k))==model;if(!keep)continue;
            }
            auto allowed=get(at(get(engine(c.engine),"sounds"),c.sound),"parameter_indices");
            if(allowed.isVoid())allowed=get(get(source_info(c),"voice_parameters"),String(c.source_note));
            if(auto* list=allowed.getArray()){bool keep=false;for(const auto& v:*list)keep|=int(v)==i;if(!keep)continue;}
            if(voice>0&&key.length()>4&&key[0]=='p'&&CharacterFunctions::isDigit(key[1])&&CharacterFunctions::isDigit(key[2])&&key[3]=='_'&&!key.startsWith(prefix))continue;
            if(bool(get(source_info(c),"focus_voice"))){
                if(key.length()>2&&key[0]=='v'&&CharacterFunctions::isDigit(key[1])&&key[2]=='_'&&int(key[1]-'0')!=voice)continue;
                if(key.startsWith("syn")&&key.substring(3).getIntValue()!=voice)continue;
            }
            if(key=="focused_pad"||key=="pad"||key=="ui_current_pad"||key=="ui_focus_level")continue;
            if((key.startsWith("rhythmer_model_")||key.startsWith("groove_model_"))&&key.substring(13).getIntValue()!=c.source_note-35)continue;
            bool local=voice>0&&(key.startsWith(prefix)||name.startsWithIgnoreCase("Pad "+String(voice)+" "));
            (local?first:rest).push_back(i);
        }
        auto sound_order=[&](int a,int b){
            auto ma=at(metadata,a),mb=at(metadata,b);
            return number(ma,"native_ui_order",number(ma,"edit_group_order",1000))<number(mb,"native_ui_order",number(mb,"edit_group_order",1000));
        };
        std::stable_sort(first.begin(),first.end(),sound_order);
        std::stable_sort(rest.begin(),rest.end(),sound_order);
        first.insert(first.end(),rest.begin(),rest.end());c.parameter_order=std::move(first);
        if(c.parameter_order.size()>controls)throw std::runtime_error("Engine exceeds sound control capacity");
        // Resolve algorithm-dependent duplicates on the worker once, not by
        // reading every native control for each of the six UI labels.
        std::map<String,int> counts,seen;std::vector<String> names;
        c.parameter_names.clear();for(int i:c.parameter_order){c.parameter_names.push_back(ps[i]->getName(64));auto meta=at(metadata,i);auto name=text(meta,"edit_name").isEmpty()?text(meta,"category")+"/"+ps[i]->getName(64):String();names.push_back(name);if(name.isNotEmpty())++counts[name];}
        c.parameter_ordinals.clear();for(const auto& name:names)c.parameter_ordinals.push_back(name.isNotEmpty()&&counts[name]>1?++seen[name]:0);

    }
    std::shared_ptr<Child> load(int e,int sound,const Child* clone=nullptr){
        if(e<0||e>=size(get(catalog,"engines")))throw std::runtime_error("Unknown sound engine");
        sound=std::clamp(sound,0,sound_count(e)-1);
        auto preset=at(get(engine(e),"sounds"),sound);
        int metadata=e;const auto alias=text(preset,"source_engine");
        if(alias.isNotEmpty()){
            metadata=-1;
            for(int i=0;i<size(get(catalog,"engines"));++i)if(text(engine(i),"folder")==alias){metadata=i;break;}
            if(metadata<0)throw std::runtime_error("Unknown preset source engine");
        }
        // Keep route identity for presets/state; use the original DSP's full metadata.
        const auto& origin=engine(metadata);
        String error;auto p=loader(text(origin,"source_folder").isNotEmpty()?text(origin,"source_folder").toStdString():text(origin,"folder").toStdString(),error);if(!p)throw std::runtime_error(error.toStdString());
        p->enableAllBuses();for(bool in:{true,false})for(int b=1;b<p->getBusCount(in);++b)p->getBus(in,b)->enable(false);
        p->prepareToPlay(rate,block);
        auto c=std::make_shared<Child>(std::move(p));c->engine=e;c->metadata_engine=metadata;c->drums=bool(get(origin,"drums"));c->sound=sound;
        c->source_note=number(preset,"note",60);if(!get(preset,"drums").isVoid())c->drums=bool(get(preset,"drums"));c->velocity_pressure=bool(get(preset,"velocity_pressure"));
        if(clone){MemoryBlock state;clone->synth->getStateInformation(state);c->synth->setStateInformation(state.getData(),int(state.getSize()));}
        else {
        for(int n=0;n<size(get(preset,"native_setup"));++n){auto pair=at(get(preset,"native_setup"),n);auto* native=dynamic_cast<Vst2Instance*>(c->synth.get());if(!native||!native->nativeSet(at(pair,0).toString(),at(pair,1).toString()))throw std::runtime_error("Native bank unavailable");}
        if(!get(preset,"native_key").isVoid()){auto* native=dynamic_cast<Vst2Instance*>(c->synth.get());if(!native||!native->nativeSet(text(preset,"native_key"),text(preset,"native_value")))throw std::runtime_error("Native preset selector unavailable");}
        else if(!get(preset,"program").isVoid())c->synth->setCurrentProgram(number(preset,"program"));
        else if(auto* values=get(preset,"values").getDynamicObject())for(const auto& value:values->getProperties()){int i=value.name.toString().getIntValue();if(i>=0&&i<c->synth->getParameters().size())c->synth->getParameters()[i]->setValue(float(value.value));}
        }
        initial(*c);
        pitch_policy(*c);
        context(*c,c->source_note);order(*c);
        if(clone)c->defaults=clone->defaults;
        else for(auto* parameter:c->synth->getParameters())c->defaults.push_back(parameter->getValue());
        return c;
    }
    template<class F>static void each(Graph& g,F f){std::array<Child*,pads> seen{};int count=0;for(auto& c:g.routes)if(c&&std::find(seen.begin(),seen.begin()+count,c.get())==seen.begin()+count){seen[size_t(count++)]=c.get();f(*c);}}
    void render(Graph& g,AudioBuffer<float>& output,int start,int length){
        for(int offset=0;offset<length;offset+=128){int n=std::min(128,length-offset);
            each(g,[&](Child& c){
                std::array<float,128> left{},right{};
                auto play=[&](float* l,float* r,unsigned frames){
                    c.audio.clear();AudioBuffer<float> sub(c.audio.getArrayOfWritePointers(),2,int(frames));c.synth->setPlayHead(getPlayHead());c.synth->processBlock(sub,c.midi);c.midi.clear();
                    std::copy_n(sub.getReadPointer(0),frames,l);std::copy_n(sub.getReadPointer(1),frames,r);
                };
                if(single>=0&&c.drums)c.pitch.render(left.data(),right.data(),unsigned(n),play);else play(left.data(),right.data(),unsigned(n));
                if(c.silenced)return;
                for(int i=0;i<n;++i){output.addSample(0,start+offset+i,left[size_t(i)]);if(output.getNumChannels()>1)output.addSample(1,start+offset+i,right[size_t(i)]);}
             });
            if(kit_filter){if(output.getNumChannels()>1)kit_filter->process(g.kit_filter,g.filter_epoch,output.getWritePointer(0,start+offset),output.getWritePointer(1,start+offset),unsigned(n));else{std::array<float,128> right{};std::copy_n(output.getReadPointer(0,start+offset),n,right.data());kit_filter->process(g.kit_filter,g.filter_epoch,output.getWritePointer(0,start+offset),right.data(),unsigned(n));}}
            if(single<0){if(g.kit_mix_gain!=1)output.applyGain(start+offset,n,g.kit_mix_gain);if(output.getNumChannels()>1)kit_output.process(output.getWritePointer(0,start+offset),output.getWritePointer(1,start+offset),unsigned(n),g.filter_epoch);else{std::array<float,128> right{};std::copy_n(output.getReadPointer(0,start+offset),n,right.data());kit_output.process(output.getWritePointer(0,start+offset),right.data(),unsigned(n),g.filter_epoch);}}
        }
    }
    void publish(std::unique_ptr<Graph> g){std::lock_guard<std::mutex> guard(lock);auto* raw=g.get();if(kit_filter&&raw->filter_epoch==0)raw->filter_epoch=++filter_sequence;auto* before=active.load();const size_t slot=size_t(single<0?focus:0);
        if(!before||before->routes[slot]==nullptr||raw->routes[slot]==nullptr||before->routes[slot]->engine!=raw->routes[slot]->engine||before->sounds[slot]!=raw->sounds[slot]||before->notes[slot]!=raw->notes[slot]||before->orders[slot]!=raw->orders[slot]||before->names[slot]!=raw->names[slot])++layout_revision;
        graphs.push_back(std::move(g));active.store(raw,std::memory_order_seq_cst);collect();}
    void collect(){auto* playing=hazard.load(std::memory_order_seq_cst);auto* now=active.load();graphs.erase(std::remove_if(graphs.begin(),graphs.end(),[&](const auto& g){return g.get()!=now&&g.get()!=playing;}),graphs.end());}
    void load_kit(int index){
        auto kit=at(get(catalog,"kits"),index);if(kit.isVoid())throw std::runtime_error("Unknown kit");
        auto g=std::make_unique<Graph>();g->kit=index;if(!get(kit,"mix_gain").isVoid())g->kit_mix_gain=float(get(kit,"mix_gain"));if(!std::isfinite(g->kit_mix_gain)||g->kit_mix_gain<=0||g->kit_mix_gain>128)throw std::runtime_error("Invalid factory kit mix gain");g->filter_epoch=++filter_sequence;
        auto routes=get(kit,"routes");for(int i=0;i<std::min(pads,size(routes));++i){auto r=at(routes,i);int e=number(r,"engine",-1),s=number(r,"sound");
            // A factory kit uses one original instance, preserving its choke
            // groups and voice allocation. An edited pad forks only on demand.
            const auto preset=at(get(engine(e),"sounds"),s);
            std::shared_ptr<Child> shared;
            for(int j=0;j<i;++j)if(auto candidate=g->routes[size_t(j)];candidate&&candidate->engine==e){
                const auto before=at(get(engine(e),"sounds"),g->sounds[size_t(j)]);
                bool same=true;for(const char* key:{"source_engine","source_sound","values","native_key","native_value","native_setup","program"})same&=JSON::toString(get(before,key))==JSON::toString(get(preset,key));
                bool lane=text(engine(e),"lane_preset_key").isNotEmpty()&&text(preset,"source_engine").isEmpty()&&text(before,"source_engine").isEmpty();
                if(lane)for(int k=0;k<i;++k)if(g->routes[size_t(k)]==candidate&&g->notes[size_t(k)]==number(preset,"note",60)&&g->sounds[size_t(k)]!=s)lane=false;
                if(!same&&!lane)continue;
                shared=candidate;
                if(!same){auto* native=dynamic_cast<Vst2Instance*>(shared->synth.get());if(!native||!native->nativeSet(text(preset,"native_key"),text(preset,"native_value")))throw std::runtime_error("Native lane preset unavailable");}
                break;
            }
            auto child=shared?shared:load(e,s);g->routes[size_t(i)]=child;g->sounds[size_t(i)]=s;
            g->notes[size_t(i)]=number(at(get(engine(e),"sounds"),s),"note",60);
            // The order is a route property, not shared mutable DSP state.
            int source=child->source_note,old_sound=child->sound;child->sound=s;child->source_note=g->notes[size_t(i)];order(*child);g->orders[size_t(i)]=child->parameter_order;g->ordinals[size_t(i)]=child->parameter_ordinals;g->names[size_t(i)]=child->parameter_names;child->source_note=source;child->sound=old_sound;

        }
        // Calibrated factory mix uses the existing voice level controls.
        // Apply after all shared factory lanes are loaded, preserving choke groups.
        for(int i=0;i<std::min(pads,size(routes));++i)if(auto child=g->routes[size_t(i)])if(auto mix=get(at(routes,i),"mix_values").getDynamicObject()){
            context(*child,g->notes[size_t(i)]);
            for(const auto& value:mix->getProperties()){int at=value.name.toString().getIntValue();float v=float(value.value);if(at<0||at>=child->synth->getParameters().size()||!std::isfinite(v)||v<0||v>1)throw std::runtime_error("Invalid factory kit mix level");child->synth->getParameters()[at]->setValue(v);}
        }
        each(*g,[](Child& c){c.defaults.clear();for(auto* p:c.synth->getParameters())c.defaults.push_back(p->getValue());});
        publish(std::move(g));
    }
    void enqueue(Request r){std::lock_guard<std::mutex> guard(lock);if(stopping)return;
        if(kit_filter_index(r.index))r.revision=0;
        if(r.kind==1&&r.index!=0&&r.revision&&r.revision!=layout_revision)return;
        if(r.kind==1&&(r.index==1||r.index==2||r.index>=base))r.revision=layout_revision;
        if(r.kind==1&&!jobs.empty()&&jobs.back().kind==1&&jobs.back().index==r.index&&jobs.back().revision==r.revision)jobs.back()=std::move(r);
        else if(jobs.size()<512)jobs.push_back(std::move(r));else {last_error="Control queue full";return;}
        wake.notify_all();
    }
    void flush(){std::unique_lock<std::mutex> guard(lock);done.wait(guard,[&]{return jobs.empty()&&!busy;});}
    void restore(const Request& r,bool user_preset=false){
        auto root=JSON::parse(String::fromUTF8(reinterpret_cast<const char*>(r.bytes.data()),int(r.bytes.size())));
        if(number(root,"schema")!=2){if(single>=0){auto* g=active.load();g->routes[0]->synth->setStateInformation(r.bytes.data(),int(r.bytes.size()));initial(*g->routes[0]);return;}throw std::runtime_error("Unsupported sound state");}
        if((get(root,"single_engine").isVoid()&&number(root,"single",-2)!=single)||(!get(root,"single_engine").isVoid()&&canonical(text(root,"single_engine"))!=(single<0?String():text(engine(single),"folder"))))throw std::runtime_error("Sound state type mismatch");
        auto rows=get(root,"children"),routes=get(root,"routes");if(size(rows)>pads||size(routes)!=pads)throw std::runtime_error("Invalid sound state size");
        std::vector<std::shared_ptr<Child>> loaded;
        for(int i=0;i<size(rows);++i){auto row=at(rows,i);int e=-1;for(int j=0;j<size(get(catalog,"engines"));++j)if(text(engine(j),"folder")==canonical(text(row,"engine")))e=j;if(e<0)throw std::runtime_error("Missing sound engine");
            auto c=load(e,number(row,"sound"));MemoryBlock chunk;if(!chunk.fromBase64Encoding(text(row,"state")))throw std::runtime_error("Invalid engine state");c->synth->setStateInformation(chunk.getData(),int(chunk.getSize()));initial(*c);pitch_policy(*c);
            auto values=get(row,"values");if(size(values)!=c->synth->getParameters().size())throw std::runtime_error("Engine controls changed");for(int j=0;j<size(values);++j){float v=float(at(values,j));if(!std::isfinite(v))throw std::runtime_error("Invalid control value");bool selector=false;for(int n=0;n<size(get(engine(e),"preset_parameters"));++n)selector|=int(at(get(engine(e),"preset_parameters"),n))==j;auto* parameter=c->synth->getParameters()[j];if(!selector&&v>=0&&v<=1&&parameter->isAutomatable()&&std::abs(parameter->getValue()-v)>.000001f)parameter->setValue(v);}auto defaults=user_preset?values:get(row,"reset_defaults");if(defaults.isArray()){if(size(defaults)!=int(c->defaults.size()))throw std::runtime_error("Invalid reset defaults");for(int j=0;j<size(defaults);++j){float value=float(at(defaults,j));if(!std::isfinite(value))throw std::runtime_error("Invalid reset default");c->defaults[size_t(j)]=value;}}order(*c);loaded.push_back(c);
        }
        auto g=std::make_unique<Graph>();g->kit=number(root,"kit");
        String saved_kit=text(root,"kit_name");if(saved_kit.isEmpty())saved_kit=at(get(catalog,"kit_order_legacy"),g->kit).toString();
        if(saved_kit.isNotEmpty())for(int i=0;i<size(get(catalog,"kits"));++i)if(text(at(get(catalog,"kits"),i),"name")==saved_kit){g->kit=i;break;}
        if(!get(root,"kit_mix_gain").isVoid()){g->kit_mix_gain=float(get(root,"kit_mix_gain"));}
        if(!std::isfinite(g->kit_mix_gain)||g->kit_mix_gain<=0||g->kit_mix_gain>128){throw std::runtime_error("Invalid saved kit mix gain");}
        g->filter_epoch=++filter_sequence;
        if(kit_filter){auto values=get(root,"kit_filter"),defaults=get(root,"kit_filter_defaults");if(!values.isVoid()){if(size(values)!=3)throw std::runtime_error("Invalid kit filter");for(int i=0;i<3;++i){int value=int(at(values,i));if(value<0||value>(i==2?2:100))throw std::runtime_error("Invalid kit filter value");g->kit_filter[size_t(i)]=int16_t(value);}}
            g->kit_filter_defaults=user_preset?g->kit_filter:KitFilterValues{{100,0,0}};if(!user_preset&&defaults.isArray()){if(size(defaults)!=3)throw std::runtime_error("Invalid kit filter reset baseline");for(int i=0;i<3;++i){int value=int(at(defaults,i));if(value<0||value>(i==2?2:100))throw std::runtime_error("Invalid kit filter default");g->kit_filter_defaults[size_t(i)]=int16_t(value);}}g->filter_edited=!user_preset&&bool(get(root,"kit_filter_edited"));}
        for(int i=0;i<pads;++i){auto route=at(routes,i);int id=route.isObject()?number(route,"child",-1):int(route);if(id<0)continue;if(id>=int(loaded.size()))throw std::runtime_error("Invalid pad route");g->routes[size_t(i)]=loaded[size_t(id)];g->sounds[size_t(i)]=number(route,"sound");g->notes[size_t(i)]=number(route,"note",60);g->edited[size_t(i)]=bool(get(route,"edited"));if(g->notes[size_t(i)]<0||g->notes[size_t(i)]>127||g->sounds[size_t(i)]<0||g->sounds[size_t(i)]>=sound_count(loaded[size_t(id)]->engine))throw std::runtime_error("Invalid saved sound route");auto& c=*loaded[size_t(id)];int source=c.source_note,old_sound=c.sound;c.sound=g->sounds[size_t(i)];c.source_note=g->notes[size_t(i)];order(c);g->orders[size_t(i)]=c.parameter_order;g->ordinals[size_t(i)]=c.parameter_ordinals;g->names[size_t(i)]=c.parameter_names;c.source_note=source;c.sound=old_sound;}
        if(single>=0&&!g->routes[0])throw std::runtime_error("Missing single sound");
        {std::lock_guard<std::mutex> guard(lock);user_label=text(root,"user_label");selected_user_slot=std::clamp(number(root,"user_slot",user_label.startsWith(single<0?"User Kit ":"User Sound ")?user_label.getTrailingIntValue()-1:-1),-1,63);if(selected_user_slot>=0)save_slot=selected_user_slot;focus=std::clamp(number(root,"pad"),0,pads-1);}
        publish(std::move(g));
    }
    void run(){
        for(;;){Request r;
            {std::unique_lock<std::mutex> guard(lock);wake.wait_for(guard,std::chrono::milliseconds(25),[&]{return stopping||!jobs.empty();});if(stopping)return;if(jobs.empty()){collect();continue;}r=std::move(jobs.front());jobs.pop_front();busy=true;}
            bool stale=false;{std::lock_guard<std::mutex> guard(lock);stale=r.kind==1&&(r.index==1||r.index==2||r.index>=base)&&r.revision!=layout_revision;}
            const bool unchanged=r.kind==1&&r.index>=6&&std::abs(parameter_value(r.index)-r.value)<.000001f;
            if(stale||unchanged){{std::lock_guard<std::mutex> guard(lock);busy=false;}done.notify_all();continue;}
            try{
                // Graph creation and original state/file operations are worker
                // work. The audio callback only reads a published graph.
                if(r.kind==5){
                    if(user_directory==File())throw std::runtime_error("No preset storage");
                    {std::lock_guard<std::mutex> guard(lock);user_label=(single<0?"User Kit ":"User Sound ")+String(save_slot+1).paddedLeft('0',2);selected_user_slot=save_slot;}
                    MemoryBlock state;write_state(state);auto file=user_file(save_slot,true);if(file.getParentDirectory().createDirectory().failed()||!file.replaceWithData(state.getData(),state.getSize()))throw std::runtime_error("Could not save preset");
                    std::lock_guard<std::mutex> guard(lock);if(kit_filter){active.load()->kit_filter_defaults=active.load()->kit_filter;active.load()->filter_edited=false;}each(*active.load(),[](Child& child){child.defaults.clear();for(auto* parameter:child.synth->getParameters())child.defaults.push_back(parameter->getValue());});if(std::find(saved_slots.begin(),saved_slots.end(),save_slot)==saved_slots.end()){saved_slots.push_back(save_slot);std::sort(saved_slots.begin(),saved_slots.end());}
                }
                else if(r.kind==0&&r.index>=factory_count()){
                    int slot=-1;{std::lock_guard<std::mutex> guard(lock);int n=r.index-factory_count();if(n<int(saved_slots.size()))slot=saved_slots[size_t(n)];}
                    if(slot<0){throw std::runtime_error("Unknown user preset");}
                    MemoryBlock state;if(user_file(slot).getSize()>32*1024*1024||!user_file(slot).loadFileAsData(state))throw std::runtime_error("Could not read preset");Request restored{4,0};restored.bytes.assign(static_cast<const uint8_t*>(state.getData()),static_cast<const uint8_t*>(state.getData())+state.getSize());restore(restored,true);{std::lock_guard<std::mutex> guard(lock);selected_user_slot=save_slot=slot;user_label=(single<0?"User Kit ":"User Sound ")+String(slot+1).paddedLeft('0',2);}
                }
                else if(r.kind==0){{std::lock_guard<std::mutex> guard(lock);user_label.clear();selected_user_slot=-1;}if(single<0)load_kit(r.index);else{auto g=std::make_unique<Graph>();g->routes[0]=load(single,selection(single,r.index));g->sounds[0]=selection(single,r.index);g->notes[0]=g->routes[0]->source_note;g->orders[0]=g->routes[0]->parameter_order;g->ordinals[0]=g->routes[0]->parameter_ordinals;g->names[0]=g->routes[0]->parameter_names;publish(std::move(g));}}
                else if(r.kind==4)restore(r);
                else {
                    if(r.index==3){std::lock_guard<std::mutex> guard(lock);save_slot=std::clamp(int(std::lround(r.value*63)),0,63);}
                    else if(kit_filter_index(r.index)){auto g=std::make_unique<Graph>(*active.load());g->kit_filter[size_t(r.index-6)]=int16_t(std::lround(r.value*(r.index==8?2:100)));g->filter_edited=g->kit_filter!=g->kit_filter_defaults;publish(std::move(g));}
                    else if(single<0&&r.index==0){
                        std::shared_ptr<Child> c;int note=60;
                        {std::lock_guard<std::mutex> guard(lock);int next=std::clamp(int(std::lround(r.value*63)),0,63);if(next!=focus)++layout_revision;focus=next;auto* g=active.load();c=g->routes[size_t(focus)];note=g->notes[size_t(focus)];}
                        if(c)context(*c,note);
                    }
                    else if(single>=0&&r.index==0){{std::lock_guard<std::mutex> guard(lock);user_label.clear();selected_user_slot=-1;}auto g=std::make_unique<Graph>();int sound=selection(single,int(std::lround(r.value*(selection_count(single)-1))));g->routes[0]=load(single,sound);g->sounds[0]=sound;g->notes[0]=g->routes[0]->source_note;g->orders[0]=g->routes[0]->parameter_order;g->ordinals[0]=g->routes[0]->parameter_ordinals;g->names[0]=g->routes[0]->parameter_names;publish(std::move(g));}
                    else {auto* old=active.load();int slot=single<0?focus:0;auto current=old->routes[size_t(slot)];auto g=std::make_unique<Graph>(*old);
                        if(single<0&&r.index==1){int e=int(std::lround(r.value*(size(get(catalog,"engines"))-1)));g->routes[size_t(slot)]=load(e,0);g->sounds[size_t(slot)]=0;g->edited[size_t(slot)]=false;g->notes[size_t(slot)]=g->routes[size_t(slot)]->source_note;g->orders[size_t(slot)]=g->routes[size_t(slot)]->parameter_order;g->ordinals[size_t(slot)]=g->routes[size_t(slot)]->parameter_ordinals;g->names[size_t(slot)]=g->routes[size_t(slot)]->parameter_names;}
                        else if(single<0&&r.index==2){if(current){int sound=selection(current->engine,int(std::lround(r.value*(selection_count(current->engine)-1))));g->routes[size_t(slot)]=load(current->engine,sound);g->sounds[size_t(slot)]=sound;g->edited[size_t(slot)]=false;g->notes[size_t(slot)]=g->routes[size_t(slot)]->source_note;g->orders[size_t(slot)]=g->routes[size_t(slot)]->parameter_order;g->ordinals[size_t(slot)]=g->routes[size_t(slot)]->parameter_ordinals;g->names[size_t(slot)]=g->routes[size_t(slot)]->parameter_names;}}
                        else if(current){int p=r.index-base;if(p>=0&&p<int(g->orders[size_t(slot)].size())){
                            int parameter=g->orders[size_t(slot)][size_t(p)];int references=0;for(const auto& c:g->routes)if(c==current)++references;
                            if(references>1){current=load(current->engine,g->sounds[size_t(slot)],current.get());g->routes[size_t(slot)]=current;}
                            auto meta=at(get(source_info(*current),"parameters"),parameter);auto choices=get(meta,"option_indices");float native_value=r.value;
                            if(size(choices)>1)native_value=float(int(at(choices,std::clamp(int(std::lround(r.value*(size(choices)-1))),0,size(choices)-1))))/std::max(1,size(get(meta,"options"))-1);
                            current->synth->getParameters()[parameter]->setValue(native_value);g->edited[size_t(slot)]=true;
                            if(number(source_info(*current),"native_pitch_parameter",-1)>=0&&parameter>0&&parameter<89&&(parameter-1)%11==0){current=load(current->engine,g->sounds[size_t(slot)],current.get());g->routes[size_t(slot)]=current;g->notes[size_t(slot)]=current->source_note;}
                            int saved_note=current->source_note,saved_sound=current->sound;current->source_note=g->notes[size_t(slot)];current->sound=g->sounds[size_t(slot)];order(*current);g->orders[size_t(slot)]=current->parameter_order;g->ordinals[size_t(slot)]=current->parameter_ordinals;g->names[size_t(slot)]=current->parameter_names;current->source_note=saved_note;current->sound=saved_sound;
                        }}
                        publish(std::move(g));
                    }
                }
                {std::lock_guard<std::mutex> guard(lock);last_error.clear();}
            }catch(const std::exception& e){std::lock_guard<std::mutex> guard(lock);last_error=e.what();}
            {std::lock_guard<std::mutex> guard(lock);busy=false;}done.notify_all();
        }
    }
    String user_label;File user_directory;std::vector<File> legacy_directories;std::vector<int> saved_slots;int save_slot=0,selected_user_slot=-1;
    uint32_t design_cache_revision=0;std::vector<PluginDesignPage> design_cache;
    var catalog;uint32_t layout_revision=1;int single,focus=0;const int base;SoundLoader loader;double rate;int block;
    std::unique_ptr<KitFilterStage> kit_filter;KitOutputStage kit_output;uint64_t filter_sequence=0;
    std::atomic<Graph*> active{nullptr};std::atomic<Graph*> hazard{nullptr};std::vector<std::unique_ptr<Graph>> graphs;
    std::mutex lock;std::condition_variable wake,done;std::deque<Request> jobs;bool stopping=false,busy=false;std::thread worker;String last_error;
};
}
std::unique_ptr<AudioPluginInstance> make_sound_rack(const var& c,int single,SoundLoader loader,double rate,int block,String& error){try{return std::make_unique<Rack>(c,single,std::move(loader),rate,block);}catch(const std::exception& e){error=e.what();return {};}}
int sound_rack_parameter_count(AudioPluginInstance* p){if(auto* r=dynamic_cast<Rack*>(p))return r->count();return -1;}
String sound_rack_preset_name(AudioPluginInstance* p){if(auto* r=dynamic_cast<Rack*>(p))return r->preset_name();return {};}
bool sound_rack_drum_voices(AudioPluginInstance* p,DrumVoices& out){if(auto* r=dynamic_cast<Rack*>(p))return r->drum_names(out);return false;}
uint32_t sound_rack_revision(AudioPluginInstance* p){if(auto* r=dynamic_cast<Rack*>(p))return r->revision();return 0;}
bool sound_rack_design_pages(AudioPluginInstance* p,PluginPanel& out){if(auto* r=dynamic_cast<Rack*>(p))return r->design_pages(out);return false;}
int sound_rack_focus(AudioPluginInstance* p){if(auto* r=dynamic_cast<Rack*>(p))return r->focused_pad();return -1;}
void sound_rack_set_parameter_checked(AudioPluginInstance* p,int index,float value,uint32_t revision){if(auto* r=dynamic_cast<Rack*>(p))r->change(index,value,revision);}
bool is_sound_rack(AudioPluginInstance* p){return dynamic_cast<Rack*>(p)!=nullptr;}
}

namespace rhythmer { std::array<int,3> sound_rack_quick_parameters(AudioPluginInstance* p){if(auto* r=dynamic_cast<Rack*>(p))return r->quick_parameters();return {{-1,-1,-1}};} }

namespace rhythmer {int sound_rack_source_parameter_begin(AudioPluginInstance* p){if(auto* r=dynamic_cast<Rack*>(p))return r->source_begin();return 0;}}

namespace rhythmer {juce::String sound_rack_source_name(AudioPluginInstance* p){if(auto* r=dynamic_cast<Rack*>(p);r&&r->focused_pad()>=0)return r->parameter_text(1);return {};}}

namespace rhythmer {
std::vector<int> sound_rack_edit_order(AudioPluginInstance* synth){
    const int count=sound_rack_parameter_count(synth);std::vector<int> result;
    if(count<0)return result;
    for(int i=0;i<std::min(6,count);++i)result.push_back(i);
    PluginPanel panel;
    if(sound_rack_focus(synth)>=0&&sound_rack_design_pages(synth,panel)){
        for(unsigned page=0;page<panel.design_count;++page){
            const auto& ids=panel.design_pages[page].shown;
            for(unsigned row=0;row<2;++row){
                if(ids[row*3]<0)continue;
                for(unsigned k=0;k<3;++k)result.push_back(ids[row*3+k]);
            }
        }
    }else for(int i=6;i<count;++i)result.push_back(i);
    return result;
}
}
