// SPDX-License-Identifier: AGPL-3.0-only
#include "rhythmer/plugin/sound_rack.h"
#include "rhythmer/plugin/vst2_instance.h"
#include "rhythmer/plugin/plugin_files.h"
#include "rhythmer/plugin/plugin_support.h"
#include "rhythmer/model/project_file.h"
#include <filesystem>
#include <iostream>
#include <cmath>
#include <stdexcept>
#include <set>
#include <atomic>
#include <thread>
#include <fstream>
using namespace juce;
static void require(bool b,const char* why){if(!b)throw std::runtime_error(why);}
static double play(AudioPluginInstance& synth,int note,int blocks=128){AudioBuffer<float> out(2,128);MidiBuffer midi;midi.addEvent(MidiMessage::noteOn(1,note,uint8(110)),7);double energy=0;for(int b=0;b<blocks;++b){out.clear();synth.processBlock(out,midi);midi.clear();for(int c=0;c<2;++c)for(int f=0;f<128;++f){float v=out.getSample(c,f);require(std::isfinite(v),"Non-finite sound");energy+=v*v;}}midi.addEvent(MidiMessage::noteOff(1,note),0);midi.addEvent(MidiMessage::allSoundOff(1),0);synth.processBlock(out,midi);return energy;}
static void design_view(var& view,AudioPluginInstance* synth,bool state_check=false){
    MemoryBlock before;if(state_check)synth->getStateInformation(before);
    rhythmer::PluginPanel panel;require(rhythmer::sound_rack_design_pages(synth,panel),"Missing functional design pages");
    Array<var> pages;std::set<int> reached;
    for(unsigned i=0;i<panel.design_count;++i){const auto& p=panel.design_pages[i];require(p.title[0]&&p.part&&p.part<=p.parts,"Invalid page title or position");Array<var> ids;
        for(int id:p.shown){ids.add(id);if(id<0)continue;require(id>=6&&id<rhythmer::sound_rack_parameter_count(synth),"Page reached a host control or an invalid parameter");require(reached.insert(id).second,"A design control appears on more than one page");}
        var row(new DynamicObject());auto* o=row.getDynamicObject();o->setProperty("title",p.title);o->setProperty("part",int(p.part));o->setProperty("parts",int(p.parts));o->setProperty("shown",ids);pages.add(row);
    }
    require(int(reached.size())==rhythmer::sound_rack_parameter_count(synth)-6,"A sound control is missing from functional pages");
    if(state_check){MemoryBlock after;synth->getStateInformation(after);require(before==after,"Reading design pages changed the sound state");}
    view.getDynamicObject()->setProperty("design_pages",pages);view.getDynamicObject()->setProperty("design_source",panel.design_source);
}
#include "sound_transport.inc"
#include "authored_presets.inc"
#include "preset_audition.inc"
int main(int argc,char** argv){try{
    if(argc>3&&String(argv[3])=="transport")return transport_check();
    require(argc>=3,"catalogue and Plugins required");ScopedJuceInitialiser_GUI init;
    require(rhythmer::ensure_plugin_support(),"Plugin support not available");
    var catalog=JSON::parse(File(argv[1]).loadFileAsString());auto engines=catalog["engines"];
    const File user(File(argv[1]).getParentDirectory().getChildFile("tmp/sound-presets-"+Uuid().toString()));catalog.getDynamicObject()->setProperty("user_directory",user.getFullPathName());
    const std::filesystem::path root(argv[2]);int loads=0;
    rhythmer::SoundLoader loader=[&](const std::string& folder,String& error)->std::unique_ptr<AudioPluginInstance>{++loads;auto file=rhythmer::describe_plugin((root/folder).string());return rhythmer::Vst2Instance::load(File(file.library),44100,128,error);};
    const auto listed=rhythmer::list_plugins(root.string());int kits=0;for(const auto& f:listed)kits+=f.name=="Rhythmer Kit";
    require(kits==1&&!listed.empty()&&listed.front().name=="Rhythmer Kit","Renamed kit duplicated or not sorted first");
    require(std::any_of(listed.begin(),listed.end(),[](const auto& f){return f.name=="Acid Engine";}),"Missing Acid Engine picker entry");
    require(std::any_of(listed.begin(),listed.end(),[](const auto& f){return f.name=="Break Engine";}),"Missing Break Engine picker entry");
    for(const auto& f:listed)require(std::filesystem::path(f.path).filename().string().rfind("GROOVE - ",0)!=0,"Legacy folder duplicated the renamed browser entry");
    for(const auto& f:listed)require(!f.kit_only,"Kit-only engine leaked into picker");
    require(listed.size()==20,"Plugin picker differs from selected release");
    int hidden=0;
    for(const auto& e:*engines.getArray()){
        auto f=rhythmer::describe_plugin((root/e["folder"].toString().toStdString()).string());
        bool kit_only=bool(e["kit_only"]);require(f.kit_only==kit_only,"Kit visibility differs from catalogue");require(f.loadable(),"Kit-only source no longer loadable by saved path");hidden+=kit_only;
        if(e["name"].toString()=="Elixir")require(!kit_only&&std::any_of(listed.begin(),listed.end(),[](const auto& f){return f.name=="Elixir";}),"Elixir must remain standalone");
    }
    require(hidden==7,"Unexpected kit-only source count");
    String error;
    if(argc>3&&String(argv[3])=="musical")return musical_audition(catalog,loader,argv[1]);
    if(argc>3&&String(argv[3])=="audition")return preset_audition(catalog,loader,argv[1]);
    if(argc>3&&String(argv[3])=="authored")return authored_check(catalog,loader,argv[1]);
    if(argc>3&&String(argv[3])=="demo") {
        int e=-1;for(int i=0;i<engines.size();++i)if(engines[i]["name"].toString()=="Prophet")e=i;
        require(e>=0,"Missing Prophet");auto rack=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(rack),error.toRawUTF8());
        int program=-1;for(int i=0;i<rack->getNumPrograms();++i)if(rack->getProgramName(i)=="Warm Strings")program=i;
        require(program>=0,"Rhythmer Warm Strings missing");rack->setCurrentProgram(program);
        const int frames=44100*8;std::vector<int16_t> pcm(size_t(frames)*2);double energy=0;AudioBuffer<float> out(2,128);MidiBuffer midi;
        for(int at=0;at<frames;at+=128){midi.clear();if(at==0)for(int note:{48,55,60,64})midi.addEvent(MidiMessage::noteOn(1,note,uint8(100)),0);if(at==128*((44100*6)/128))for(int note:{48,55,60,64})midi.addEvent(MidiMessage::noteOff(1,note),0);out.clear();rack->processBlock(out,midi);
            for(int f=0;f<std::min(128,frames-at);++f)for(int c=0;c<2;++c){float v=out.getSample(c,f);require(std::isfinite(v),"Demo contains non-finite audio");energy+=v*v;pcm[size_t((at+f)*2+c)]=int16_t(std::lround(std::clamp(v,-1.0f,1.0f)*32767));}}
        require(energy>1e-7,"Rhythmer Warm Strings demo silent");auto file=File(argv[1]).getSiblingFile("prophet-rhythmer-warm-strings.wav");std::ofstream wav(file.getFullPathName().toStdString(),std::ios::binary);
        auto u32=[&](uint32_t v){for(int i=0;i<4;++i)wav.put(char((v>>(i*8))&255));};auto u16=[&](uint16_t v){wav.put(char(v&255));wav.put(char(v>>8));};
        wav.write("RIFF",4);u32(36+frames*4);wav.write("WAVEfmt ",8);u32(16);u16(1);u16(2);u32(44100);u32(44100*4);u16(4);u16(16);wav.write("data",4);u32(frames*4);for(auto v:pcm)u16(uint16_t(v));wav.close();require(bool(wav),"Demo file write failed");
        std::cout<<"PROPHET_ORIGINAL_DEMO bank_programs="<<rack->getNumPrograms()<<" selected="<<program<<" name="<<rack->getProgramName(program)<<" energy="<<energy<<std::endl;return 0;
    }
    if(argc>3&&String(argv[3])=="inspect") {
        Array<var> rows;
        for(int e=0;e<engines.size();++e){
            if(argc>4&&engines[e]["name"].toString()!=String(argv[4])&&engines[e]["folder"].toString()!=String(argv[4]))continue;
            auto rack=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(rack),error.toRawUTF8());
            var row(new DynamicObject());auto* o=row.getDynamicObject();o->setProperty("engine",engines[e]["name"]);o->setProperty("folder",engines[e]["folder"]);o->setProperty("variant",engines[e]["variant"]);
            Array<var> programs,parameters;
            auto sounds=engines[e]["sounds"],selection=engines[e]["selection"];
            int expected=selection.isArray()?selection.size():sounds.size();require(rack->getNumPrograms()==expected,"Factory count differs from source catalogue");
            for(int n=0;n<rack->getNumPrograms();n++){
                auto name=rack->getProgramName(n);auto raw=selection.isArray()?int(selection[n]):n;
                require(name==sounds[raw]["name"].toString(),("Preset name/index mismatch: "+engines[e]["name"].toString()+" / "+String(n)).toRawUTF8());programs.add(name);
            }
            std::set<String> visible_names;
            for(int n=0;n<rhythmer::sound_rack_parameter_count(rack.get());n++){
                auto* p=rack->getParameters()[n];var v(new DynamicObject());auto* q=v.getDynamicObject();
                if(n>=6){auto name=p->getName(47),value=p->getText(p->getValue(),128);require(name.isNotEmpty()&&!name.startsWith("Parameter ")&&!name.containsIgnoreCase("Inactive"),"Invalid edit label");require(visible_names.insert(name).second,("Duplicate visible edit label: "+engines[e]["name"].toString()+" / "+name).toRawUTF8());require(value.isNotEmpty(),("Blank edit value: "+name).toRawUTF8());}
                q->setProperty("index",n);q->setProperty("name",p->getName(128));q->setProperty("text",p->getText(p->getValue(),128));q->setProperty("value",p->getValue());parameters.add(v);
            }
            o->setProperty("programs",programs);o->setProperty("parameters",parameters);design_view(row,rack.get(),true);rows.add(row);
            File(argv[1]).getSiblingFile("edit-inspect.json").replaceWithText(JSON::toString(var(rows),true));
            std::cout<<"INSPECT "<<engines[e]["name"].toString()<<" presets="<<programs.size()<<" controls="<<parameters.size()<<std::endl;
        }return 0;
    }
    if(argc>3&&String(argv[3])=="playback") {
        Array<var> report;int failures=0;
        for(int e=0;e<engines.size();++e){
            if(argc>4&&engines[e]["name"].toString()!=String(argv[4])&&engines[e]["folder"].toString()!=String(argv[4]))continue;
            auto rack=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(rack),error.toRawUTF8());Array<var> patches;
            for(int program=0;program<rack->getNumPrograms();++program){
                rack->setCurrentProgram(program);Array<var> probes;
                const auto program_name=rack->getProgramName(program);
                for(int note:{48,60,61,62,63,64,65,66,67,68,69,70,71,84}){
                    double energy=play(*rack,note);bool retry=energy<1e-7;
                    if(retry){auto fresh=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(fresh),error.toRawUTF8());fresh->setCurrentProgram(program);const bool slow=program_name=="Endless Hold"||program_name=="Slow Evolution"||program_name=="Tape Hiss Drone"||program_name=="Modular Hum";energy=play(*fresh,note,slow?11025:1024);}
                    var probe(new DynamicObject());auto* q=probe.getDynamicObject();q->setProperty("note",note);q->setProperty("energy",energy);q->setProperty("long_fresh_retry",retry);probes.add(probe);
                    if(energy<1e-7){++failures;std::cout<<"SILENT_NOTE "<<engines[e]["name"].toString()<<" / "<<rack->getProgramName(program)<<" note="<<note<<std::endl;}
                }
                var patch(new DynamicObject());auto* q=patch.getDynamicObject();q->setProperty("index",program);q->setProperty("name",rack->getProgramName(program));q->setProperty("notes",probes);patches.add(patch);
            }
            var row(new DynamicObject());auto* q=row.getDynamicObject();q->setProperty("engine",engines[e]["name"]);q->setProperty("folder",engines[e]["folder"]);q->setProperty("programs",patches);report.add(row);
            File(argv[1]).getSiblingFile("chromatic-playback.json").replaceWithText(JSON::toString(var(report),true));
            std::cout<<"PLAYBACK "<<engines[e]["name"].toString()<<" programs="<<patches.size()<<" cumulative_silent_notes="<<failures<<std::endl;
        }
        return failures?1:0;
    }
    if(argc>3&&String(argv[3])=="audit") {
        Array<var> rows;
        for(int e=0;e<engines.size();++e){
            if(argc>4&&engines[e]["name"].toString()!=String(argv[4])&&engines[e]["folder"].toString()!=String(argv[4]))continue;
            auto folder=engines[e]["source_folder"].toString();if(folder.isEmpty())folder=engines[e]["folder"].toString();
            auto synth=loader(folder.toStdString(),error);require(bool(synth),error.toRawUTF8());
            synth->enableAllBuses();synth->prepareToPlay(44100,128);
            auto* native=dynamic_cast<rhythmer::Vst2Instance*>(synth.get());
            MemoryBlock initial;synth->getStateInformation(initial);
            auto sounds=engines[e]["sounds"];const bool programs=false; // The full catalogue includes multi-bank selectors beyond VST programs.
            const int total=programs?synth->getNumPrograms():sounds.size();int silent=0;
            Array<var> patches;
            for(int k=0;k<total;++k){
                if(std::getenv("RHYTHMER_AUDIT_VERBOSE"))std::cout<<"PATCH "<<k<<" "<<(programs?synth->getProgramName(k):sounds[k]["name"].toString())<<std::endl;
                if(const char* only=std::getenv("RHYTHMER_AUDIT_INDICES")){String selected=","+String(only)+",";if(!selected.contains(","+String(k)+","))continue;}
                if(std::getenv("RHYTHMER_AUDIT_FRESH")){synth->releaseResources();synth.reset();synth=loader(folder.toStdString(),error);require(bool(synth),error.toRawUTF8());synth->enableAllBuses();synth->prepareToPlay(44100,128);native=dynamic_cast<rhythmer::Vst2Instance*>(synth.get());}
                synth->setStateInformation(initial.getData(),int(initial.getSize()));
                auto sound=programs?var():sounds[k];String name;
                if(programs){synth->setCurrentProgram(k);name=synth->getProgramName(k);}
                else{
                    name=sound["name"].toString();
                    for(int j=0;j<sound["native_setup"].size();++j){auto pair=sound["native_setup"][j];require(native&&native->nativeSet(pair[0].toString(),pair[1].toString()),"Native bank dispatch failed");}
                    if(!sound["native_key"].isVoid())require(native&&native->nativeSet(sound["native_key"].toString(),sound["native_value"].toString()),"Native preset dispatch failed");
                    else if(!sound["program"].isVoid())synth->setCurrentProgram(int(sound["program"]));
                    else if(auto* values=sound["values"].getDynamicObject())for(const auto& value:values->getProperties()){int i=value.name.toString().getIntValue();synth->getParameters()[i]->setValue(float(value.value));}
                }
                if(auto* values=engines[e]["initial_values"].getDynamicObject())for(const auto& v:values->getProperties()){int p=v.name.toString().getIntValue();if(p>=0&&p<synth->getParameters().size())synth->getParameters()[p]->setValue(float(v.value));}
                Array<var> energy;double sum=0;
                for(int note:{36,48,60,72,84}){if(bool(sound["velocity_pressure"])) {AudioBuffer<float> out(2,128);MidiBuffer pressure;pressure.addEvent(MidiMessage::channelPressureChange(1,110),0);synth->processBlock(out,pressure);}double v=play(*synth,(sound["drums"].isVoid()?bool(engines[e]["drums"]):bool(sound["drums"]))?int(sound["note"]):note,std::getenv("RHYTHMER_AUDIT_SECONDS")?std::clamp(std::atoi(std::getenv("RHYTHMER_AUDIT_SECONDS")),1,60)*44100/128:std::getenv("RHYTHMER_AUDIT_LONG")?1024:128);energy.add(v);sum+=v;}
                var patch(new DynamicObject());auto* o=patch.getDynamicObject();o->setProperty("index",k);o->setProperty("name",name);o->setProperty("energy",energy);o->setProperty("silent",sum<1e-7);silent+=sum<1e-7;patches.add(patch);
            }
            var row(new DynamicObject());auto* o=row.getDynamicObject();o->setProperty("engine",engines[e]["name"]);o->setProperty("folder",engines[e]["folder"]);o->setProperty("variant",engines[e]["variant"]);o->setProperty("presets",total);o->setProperty("silent",silent);o->setProperty("patches",patches);rows.add(row);
            File(argv[1]).getSiblingFile("preset-audit.json").replaceWithText(JSON::toString(var(rows),true));
            std::cout<<"AUDIT "<<engines[e]["name"].toString()<<" presets="<<total<<" silent="<<silent<<std::endl;
        }
        return 0;
    }
    Array<var> dynamic_views;
    if(argc==3||String(argv[3])=="singles")for(int i=0;i<engines.size();++i){
        if(argc>4&&engines[i]["name"].toString()!=String(argv[4])&&engines[i]["folder"].toString()!=String(argv[4]))continue;
        auto sound=rhythmer::make_sound_rack(catalog,i,loader,44100,128,error);require(bool(sound),error.toRawUTF8());
        const int count=rhythmer::sound_rack_parameter_count(sound.get());require(count>3,"Missing sound-design controls");
        if(sound->getName()=="Sophie")for(int p=6;p<count;++p){auto n=sound->getParameters()[p]->getName(128);require(!n.startsWith("P01 ")&&!n.contains("Metal Metal"),"Sophie source pad context leaked into single sound");}
        if(sound->getName()=="6W6"){bool tone=false;for(int p=6;p<count;++p)tone|=sound->getParameters()[p]->getName(128)=="Tone"||sound->getParameters()[p]->getName(128).startsWith("SD ");require(!tone,"6W6 snare tone leaked into kick editor");}

        require(sound->getNumPrograms()>1||((sound->getName()=="Prophet"||sound->getName()=="Elixir")&&sound->getNumPrograms()>=1),"Only Init remains unexpectedly in sound presets");require(sound->getProgramName(0).isNotEmpty(),"Unnamed preset");


        // These three FM-1 engines change the available names with algorithms.
        if((sound->getName()=="K-WASUB"&&!bool(engines[i]["drums"]))||sound->getName()=="MONO2K"||sound->getName()=="Hortator"||sound->getName()=="Elixir"){
            for(int program=0;program<sound->getNumPrograms();program++){
                sound->setCurrentProgram(program);std::set<String> seen;
                for(int p=6;p<rhythmer::sound_rack_parameter_count(sound.get());p++){
                    auto* control=sound->getParameters()[p];auto name=control->getName(128);
                    require(name.isNotEmpty()&&!name.containsIgnoreCase("Inactive"),"Inactive algorithm control remains visible");require(seen.insert(name).second,("Ambiguous algorithm control: "+name).toRawUTF8());
                }
                var view(new DynamicObject());auto* o=view.getDynamicObject();o->setProperty("engine",sound->getName());o->setProperty("folder",engines[i]["folder"]);o->setProperty("selected_program",program);Array<var> names,params;names.add(rhythmer::sound_rack_preset_name(sound.get()));o->setProperty("programs",names);
                for(int n=0;n<rhythmer::sound_rack_parameter_count(sound.get());++n){auto* p=sound->getParameters()[n];var v(new DynamicObject());v.getDynamicObject()->setProperty("name",p->getName(128));v.getDynamicObject()->setProperty("text",p->getText(p->getValue(),128));v.getDynamicObject()->setProperty("value",p->getValue());params.add(v);}o->setProperty("parameters",params);design_view(view,sound.get());dynamic_views.add(view);
            }sound->setCurrentProgram(0);
        }

        if(sound->getName()=="K-WASUB"&&!bool(engines[i]["drums"])){
            int selector=-1;for(int p=6;p<rhythmer::sound_rack_parameter_count(sound.get());++p)if(sound->getParameters()[p]->getName(128).endsWith("A Engine"))selector=p;
            require(selector>=0,"Missing K-WASUB oscillator selector");const char* expected[]={"ANALOG","CS","WAVE","FM","PHASE","SYNC","808","GROWL","ADDITIVE"};
            for(int n=0;n<9;n++){sound->getParameters()[selector]->setValue(n/8.0f);MemoryBlock ready;sound->getStateInformation(ready);require(sound->getParameters()[selector]->getText(0,128)==expected[n],"Reserved K-WASUB algorithm exposed or native index drift");require(std::abs(sound->getParameters()[selector]->getValue()-n/8.0f)<0.0001f,"K-WASUB selector cursor drift");}sound->setCurrentProgram(0);
        }
        std::cout<<"PLAY "<<sound->getName()<<std::endl;require(play(*sound,60)>1e-7,"Single sound silent");
        MemoryBlock state;sound->getStateInformation(state);require(state.getSize()>0,"Empty single state");
        if(sound->getName()=="DRUM-X"||sound->getName()=="Hortator"||sound->getName()=="K-WASUB Drums")for(int p=6;p<count;++p){auto name=sound->getParameters()[p]->getName(128);require(!name.startsWithIgnoreCase("Snare "),"Another drum voice leaked into a single kick");}
        if(sound->getName()=="Hortator"){require(sound->getNumPrograms()==147,"Original Hortator bank incomplete");int acid=-1;for(int n=0;n<sound->getNumPrograms();++n)if(sound->getProgramName(n)=="SQUELCH")acid=n;require(acid>=0,"Original Hortator acid missing");sound->setCurrentProgram(acid);require(sound->getParameters()[2]->getText(0,128)=="Key Pitch","Hortator acid lacks native key tracking");require(play(*sound,60)>1e-7,"Hortator acid silent");sound->setCurrentProgram(0);}

        if(sound->getName()=="Acid Engine"){for(int program=0;program<sound->getNumPrograms();program++){sound->setCurrentProgram(program);for(int key:{36,48,60,72,84})require(play(*sound,key)>1e-7,"Hortator Acid preset/pitch silent");}sound->setCurrentProgram(0);for(int p=6;p<rhythmer::sound_rack_parameter_count(sound.get());p++){auto* parameter=sound->getParameters()[p];require(!parameter->getName(128).containsIgnoreCase("Model"),"Acid-only view exposes drum model selector");if(parameter->getName(128)=="Wave")require(parameter->getText(parameter->getValue(),128).isNotEmpty(),"Acid wave enum is not named");}}
        if(sound->getName()=="Elixir")require(count<150,"All Elixir voices leaked into single-sound controls");
        sound->getParameters()[count-1]->getName(128); // final original control remains reachable
        sound->setStateInformation(state.getData(),int(state.getSize()));auto status=sound->getParameters()[5]->getText(0,128);require(status=="Ready",("Single state restore failed: "+status).toRawUTF8());

        std::cout<<"SINGLE "<<sound->getName()<<" controls="<<count<<" presets="<<sound->getNumPrograms()<<std::endl;
    }
    if(dynamic_views.size())File(argv[1]).getSiblingFile("dynamic-edit-inspect.json").replaceWithText(JSON::toString(var(dynamic_views),true));
    if(argc==3||String(argv[3])=="kits"){
        auto kit=rhythmer::make_sound_rack(catalog,-1,loader,44100,128,error);require(bool(kit),error.toRawUTF8());
        Array<var> factory_views;
        for(int k=0;k<kit->getNumPrograms();++k){
            int before=loads;kit->setCurrentProgram(k);std::set<int> engine_ids;for(const auto& r:*catalog["kits"][k]["routes"].getArray())engine_ids.insert(int(r["engine"]));require(loads-before>=int(engine_ids.size())&&loads-before<=int(engine_ids.size())*4,"Factory kit exceeds bounded native sharing groups");
            MemoryBlock kit_state;kit->getStateInformation(kit_state);auto kit_json=JSON::parse(kit_state.toString());
            for(int pad=0;pad<16;++pad){auto route=catalog["kits"][k]["routes"][pad];int e=int(route["engine"]),s=int(route["sound"]);if(engines[e]["name"].toString()!="Hortator")continue;
                auto original=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(original),error.toRawUTF8());original->setCurrentProgram(s);MemoryBlock source;original->getStateInformation(source);auto expected=JSON::parse(source.toString())["children"][0]["values"];
                auto actual=kit_json["children"][int(kit_json["routes"][pad]["child"])]["values"];int note=int(engines[e]["sounds"][s]["note"]),lane=-1;const int native_notes[]{36,38,39,42,46,45,37,49};for(int n=0;n<8;++n)if(native_notes[n]==note)lane=n;require(lane>=0,"Invalid Hortator source lane");
                for(int n=1+lane*11;n<1+(lane+1)*11;++n)require(std::abs(float(expected[n])-float(actual[n]))<1e-6f,("Kit replaced original factory data: "+kit->getProgramName(k)+" pad="+String(pad+1)).toRawUTF8());
            }
            for(int pad=0;pad<16;++pad){
                kit->getParameters()[0]->setValue(pad/63.0f);std::set<String> seen;
                String prefix="P"+String(pad+1).paddedLeft('0',2)+" ";
                for(int p=6;p<rhythmer::sound_rack_parameter_count(kit.get());p++){
                    auto* control=kit->getParameters()[p];auto label=control->getName(47);
                    require(label.startsWith(prefix),"Kit edit label differs from pressed destination pad");
                    require(seen.insert(label).second,("Ambiguous kit edit label: "+kit->getProgramName(k)+" / "+label).toRawUTF8());
                    require(control->getText(control->getValue(),128).isNotEmpty(),("Blank kit edit value: "+label).toRawUTF8());
                }
                var view(new DynamicObject());auto* o=view.getDynamicObject();o->setProperty("engine","Rhythmer Kit");o->setProperty("kit",k);o->setProperty("focused_pad",pad);Array<var> names,controls;names.add(rhythmer::sound_rack_preset_name(kit.get()));o->setProperty("programs",names);
                for(int n=0;n<rhythmer::sound_rack_parameter_count(kit.get());++n){auto* p=kit->getParameters()[n];var v(new DynamicObject());v.getDynamicObject()->setProperty("name",p->getName(128));v.getDynamicObject()->setProperty("text",p->getText(p->getValue(),128));v.getDynamicObject()->setProperty("value",p->getValue());controls.add(v);}o->setProperty("parameters",controls);design_view(view,kit.get(),pad==0);factory_views.add(view);
                if(play(*kit,36+pad,32)<=1e-7){std::cerr<<kit->getProgramName(k)<<" pad="<<pad+1<<std::endl;throw std::runtime_error("Kit pad silent");}}
            std::cout<<"KIT "<<kit->getProgramName(k)<<std::endl;
        }
        File(argv[1]).getSiblingFile("factory-kit-edit-inspect.json").replaceWithText(JSON::toString(var(factory_views),true));
        Array<var> empty_views;kit->setCurrentProgram(0);
        for(int pad:{16,63}){
            kit->getParameters()[0]->setValue(pad/63.0f);MemoryBlock state;kit->getStateInformation(state);rhythmer::PluginPanel panel;
            require(!rhythmer::sound_rack_design_pages(kit.get(),panel)&&panel.design_count==0&&rhythmer::sound_rack_parameter_count(kit.get())==6,"Empty pad retained another pad's design controls");
            var view(new DynamicObject());auto* o=view.getDynamicObject();o->setProperty("engine","Rhythmer Kit");o->setProperty("focused_pad",pad);Array<var> programs;programs.add(rhythmer::sound_rack_preset_name(kit.get()));o->setProperty("programs",programs);o->setProperty("parameters",Array<var>{});o->setProperty("design_pages",Array<var>{});empty_views.add(view);
        }
        File(argv[1]).getSiblingFile("empty-pad-inspect.json").replaceWithText(JSON::toString(var(empty_views),true));
        for(int pad=0;pad<16;++pad){kit->getParameters()[0]->setValue(pad/63.0f);{MemoryBlock ready;kit->getStateInformation(ready);}String prefix="P"+String(pad+1).paddedLeft('0',2)+" ";for(int p=6;p<rhythmer::sound_rack_parameter_count(kit.get());++p){auto* parameter=kit->getParameters()[p];require(parameter->getName(128).startsWith(prefix),"Selected pad number differs from edit control");require(!parameter->getText(parameter->getValue(),128).startsWithIgnoreCase("Pad "),"Native source pad number leaked into destination text");}}
        kit->getParameters()[0]->setValue(1.0f/63.0f);{MemoryBlock ready;kit->getStateInformation(ready);}for(int p=6;p<rhythmer::sound_rack_parameter_count(kit.get());++p)require(kit->getParameters()[p]->getName(128).startsWith("P02 "),"Kit controls missing focused pad number");
        kit->getParameters()[0]->setValue(0);{MemoryBlock ready;kit->getStateInformation(ready);}
        auto old_revision=rhythmer::sound_rack_revision(kit.get());kit->getParameters()[0]->setValue(1.0f/63.0f);
        MemoryBlock expected_stale;kit->getStateInformation(expected_stale);
        require(rhythmer::sound_rack_revision(kit.get())!=old_revision,"Pad focus did not invalidate old controls");
        rhythmer::sound_rack_set_parameter_checked(kit.get(),6,0.123f,old_revision);
        MemoryBlock rejected;kit->getStateInformation(rejected);require(rejected==expected_stale,"Old pad cards modified the newly focused pad");
        kit->getParameters()[0]->setValue(0);
        // Every source is also inspected in the longer P11 destination labels.
        Array<var> kit_views;kit->getParameters()[0]->setValue(10.0f/63.0f);
        for(int e=0;e<engines.size();++e){
            kit->getParameters()[1]->setValue(e/float(engines.size()-1));MemoryBlock ready;kit->getStateInformation(ready);
            require(kit->getParameters()[5]->getText(0,128)=="Ready","Kit source failed to load");require(play(*kit,46)>1e-7,"Kit engine source silent");
            var view(new DynamicObject());Array<var> params,programs;programs.add(rhythmer::sound_rack_preset_name(kit.get()));std::set<String> seen;
            for(int n=0;n<rhythmer::sound_rack_parameter_count(kit.get());n++){
                auto* control=kit->getParameters()[n];auto name=control->getName(47);auto text=control->getText(control->getValue(),128);
                if(n>=6){require(name.startsWith("P11 "),"Kit source control does not follow pad 11");require(seen.insert(name).second,("Ambiguous P11 label: "+engines[e]["name"].toString()+" / "+name).toRawUTF8());require(text.isNotEmpty(),("Blank P11 value: "+name).toRawUTF8());}
                var value(new DynamicObject());value.getDynamicObject()->setProperty("name",name);value.getDynamicObject()->setProperty("text",text);value.getDynamicObject()->setProperty("value",control->getValue());params.add(value);
            }
            view.getDynamicObject()->setProperty("engine","Rhythmer Kit");view.getDynamicObject()->setProperty("focused_pad",10);view.getDynamicObject()->setProperty("programs",programs);view.getDynamicObject()->setProperty("parameters",params);design_view(view,kit.get());kit_views.add(view);
            std::cout<<"PAD ENGINE "<<engines[e]["name"].toString()<<std::endl;
        }
        File(argv[1]).getSiblingFile("kit-edit-inspect.json").replaceWithText(JSON::toString(var(kit_views),true));
        kit->setCurrentProgram(0);MemoryBlock before;kit->getStateInformation(before);
        // Pad 1 changes engine; pad 2 must retain its original engine and chunk.
        int sophie=-1;for(int i=0;i<engines.size();++i)if(engines[i]["name"].toString()=="Sophie")sophie=i;
        require(sophie>=0,"Missing Sophie");kit->getParameters()[1]->setValue(sophie/float(engines.size()-1));
        MemoryBlock edited;kit->getStateInformation(edited);
        auto saved=JSON::parse(edited.toString());require(saved["children"].size()>=2,"Pad override replaced other pads");
        require(play(*kit,36)>1e-7&&play(*kit,37)>1e-7,"Mixed kit silent");
        const auto serialized=edited;
        kit->setCurrentProgram(0);kit->setStateInformation(serialized.getData(),int(serialized.getSize()));
        MemoryBlock roundtrip;kit->getStateInformation(roundtrip);
        require(JSON::toString(JSON::parse(roundtrip.toString()),true)==JSON::toString(JSON::parse(serialized.toString()),true),"Kit state changed on restore");
        // The existing project encoder must retain the complete mixed kit state.
        auto project=std::make_unique<rhythmer::Project>();auto patterns=std::make_unique<rhythmer::PatternBank>();
        project->tracks[0].engine=rhythmer::EngineKind::Plugin;project->tracks[0].plugin=0;
        std::snprintf(project->plugins[0].path,rhythmer::plugin_path_length,"Plugins/RHYTHMER - Rhythmer Kit");
        std::array<std::vector<uint8_t>,rhythmer::max_plugins> states;states[0].assign(static_cast<const uint8_t*>(serialized.getData()),static_cast<const uint8_t*>(serialized.getData())+serialized.getSize());
        auto bytes=rhythmer::save_project(*project,*patterns,&states);std::array<std::vector<uint8_t>,rhythmer::max_plugins> restored;
        require(rhythmer::load_project(bytes,*project,*patterns,nullptr,&restored).empty(),"Project roundtrip failed");require(restored[0]==states[0],"Project changed kit state");
        // Edit a sound parameter after a pad override, save a reusable preset,
        // and load it in a new rack (not just the same running instance).
        kit->getParameters()[6]->setValue(0.35f);MemoryBlock designed;kit->getStateInformation(designed);
        kit->getParameters()[3]->setValue(1.0f/63.0f);kit->getParameters()[4]->setValue(1);
        MemoryBlock flushed;kit->getStateInformation(flushed);
        require(user.getChildFile("Kits/Slot02.rhythmer.json").existsAsFile(),"User kit file missing");
        auto fresh=rhythmer::make_sound_rack(catalog,-1,loader,44100,128,error);require(bool(fresh),error.toRawUTF8());
        require(fresh->getProgramName(fresh->getNumPrograms()-1)=="User Kit 02","Saved kit not listed");
        fresh->setCurrentProgram(fresh->getNumPrograms()-1);MemoryBlock reopened;fresh->getStateInformation(reopened);
        auto expected=JSON::parse(designed.toString());expected.getDynamicObject()->setProperty("user_label","User Kit 02");expected.getDynamicObject()->setProperty("user_slot",1);require(JSON::toString(JSON::parse(reopened.toString()),true)==JSON::toString(expected,true),"Saved kit did not restore edited controls");
        require(play(*fresh,36)>1e-7&&play(*fresh,37)>1e-7,"Reopened user kit silent");
        fresh.reset();
        std::atomic<bool> stop{false};std::atomic<bool> finite{true};
        std::thread audio([&]{AudioBuffer<float> out(2,128);MidiBuffer midi;midi.ensureSize(8192);unsigned n=0;while(!stop.load()){midi.clear();midi.addEvent(MidiMessage::noteOn(1,36+int(n++%8),uint8(100)),0);kit->processBlock(out,midi);for(int c=0;c<2;++c)for(int f=0;f<128;++f)if(!std::isfinite(out.getSample(c,f)))finite=false;}});
        for(int i=0;i<12;++i){kit->setCurrentProgram(i%3);kit->getParameters()[0]->setValue((i%16)/63.0f);kit->getParameters()[6]->setValue((i%7)/7.0f);MemoryBlock snap;kit->getStateInformation(snap);}
        stop=true;audio.join();require(finite.load(),"Concurrent kit edits produced non-finite audio");
        user.deleteRecursively();
        std::cout<<"Mixed engine kit, independent pad controls, user preset file, full state and project roundtrip passed"<<std::endl;
    }
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<std::endl;return 1;}}
