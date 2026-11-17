// SPDX-License-Identifier: AGPL-3.0-only
// Check every loaded program, rather than only the initial patch's controls.
static int preset_controls(const var& catalog,const rhythmer::SoundLoader& loader,const char* path){
    auto engines=catalog["engines"];Array<var> issues,quick_engines;int selections=0,controls=0;
    auto issue=[&](const String& engine,int program,const String& preset,int index,const String& name,const String& kind,float value,const String& text){
        var row(new DynamicObject());auto* o=row.getDynamicObject();o->setProperty("engine",engine);o->setProperty("program",program);o->setProperty("preset",preset);o->setProperty("index",index);o->setProperty("name",name);o->setProperty("kind",kind);o->setProperty("value",value);o->setProperty("text",text);issues.add(row);
    };
    for(int e=0;e<engines.size();++e){String error;auto rack=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(rack),error.toRawUTF8());
        const String engine=engines[e]["name"].toString();Array<var> quick_programs;
        for(int program=0;program<rack->getNumPrograms();++program){rack->setCurrentProgram(program);const auto preset=rack->getProgramName(program);std::set<String> names;quick_programs.add(quick_view(rack.get()));
            if(rack->getParameters()[6]->getName(64)=="OUTPUT CUTOFF")for(int f=6;f<9;++f)if(rack->getParameters()[f]->getValue()!=(f==6?1.f:0.f))issue(engine,program,preset,f,rack->getParameters()[f]->getName(64),"non_neutral_output_filter",rack->getParameters()[f]->getValue(),{});
            for(int p=6;p<rhythmer::sound_rack_parameter_count(rack.get());++p){auto* parameter=rack->getParameters()[p];const auto name=parameter->getName(128),display=parameter->getText(parameter->getValue(),128);float value=parameter->getValue();++controls;
                if(!std::isfinite(value)||value<0||value>1)issue(engine,program,preset,p,name,"range",value,display);
                if((name.endsWith("Reverb Send")||name.endsWith("Delay Send"))&&engine=="TR-MPC"&&!display.endsWith(" %"))issue(engine,program,preset,p,name,"send_unit",value,display);
                if(display.trim().isEmpty())issue(engine,program,preset,p,name,"blank_value",value,display);
                if(name.trim().isEmpty()||name.startsWith("Parameter ")||name.containsIgnoreCase("Inactive"))issue(engine,program,preset,p,name,"label",value,display);
                auto words=StringArray::fromTokens(name," ","");for(int w=1;w<words.size();++w)if(words[w].containsOnly("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")&&words[w].equalsIgnoreCase(words[w-1]))issue(engine,program,preset,p,name,"repeated_word",value,display);
                if(!names.insert(name).second)issue(engine,program,preset,p,name,"duplicate_label",value,display);
            }++selections;
        }quick_engines.add(quick_programs);std::cout<<"PRESET_CONTROLS "<<engine<<" selections="<<rack->getNumPrograms()<<" cumulative_issues="<<issues.size()<<std::endl;
    }
    var result(new DynamicObject());auto* o=result.getDynamicObject();o->setProperty("selections",selections);o->setProperty("controls",controls);o->setProperty("issues",issues);File(path).getSiblingFile("preset-control-audit.json").replaceWithText(JSON::toString(result,true));File(path).getSiblingFile("preset-quick-inspect.json").replaceWithText(JSON::toString(var(quick_engines),true));
    std::cout<<"PRESET_CONTROL_TOTAL selections="<<selections<<" controls="<<controls<<" issues="<<issues.size()<<std::endl;return issues.size()?1:0;
}

static int control_roundtrip(const var& catalog,const rhythmer::SoundLoader& loader,const char* path){
    auto engines=catalog["engines"];Array<var> issues;int checks=0,contexts=0;
    auto add=[&](const String& e,int program,const String& name,const String& kind,float a,float b){var row(new DynamicObject());auto* o=row.getDynamicObject();o->setProperty("engine",e);o->setProperty("program",program);o->setProperty("name",name);o->setProperty("kind",kind);o->setProperty("before",a);o->setProperty("after",b);issues.add(row);};
    for(int e=0;e<engines.size();++e){String error;auto rack=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(rack),error.toRawUTF8());String label=engines[e]["name"].toString();std::set<int> programs{0,rack->getNumPrograms()/2,rack->getNumPrograms()-1};
        for(int program:programs){rack->setCurrentProgram(program);MemoryBlock initial;rack->getStateInformation(initial);std::map<String,float> expected;
            for(int p=6;p<rhythmer::sound_rack_parameter_count(rack.get());++p)expected[rack->getParameters()[p]->getName(128)]=rack->getParameters()[p]->getValue();
            for(int p=6;p<rhythmer::sound_rack_parameter_count(rack.get());++p){auto* parameter=rack->getParameters()[p];String name=parameter->getName(128);float value=parameter->getValue();parameter->setValue(value);MemoryBlock sync;rack->getStateInformation(sync);++checks;
                if(parameter->getName(128)!=name)add(label,program,name,"noop_layout",value,parameter->getValue());
                else if(std::abs(value-parameter->getValue())>.0001f)add(label,program,name,"noop_value",value,parameter->getValue());
            }
            for(int p=6;p<rhythmer::sound_rack_parameter_count(rack.get());++p){auto* parameter=rack->getParameters()[p];auto found=expected.find(parameter->getName(128));if(found==expected.end())add(label,program,parameter->getName(128),"noop_added",0,parameter->getValue());else if(std::abs(found->second-parameter->getValue())>.0001f)add(label,program,parameter->getName(128),"noop_coupled",found->second,parameter->getValue());}
            MemoryBlock unchanged;rack->getStateInformation(unchanged);if(initial!=unchanged)add(label,program,"Sound state","noop_state",0,1);
            rack->setStateInformation(initial.getData(),int(initial.getSize()));
            for(int p=6;p<rhythmer::sound_rack_parameter_count(rack.get());++p){auto* parameter=rack->getParameters()[p];auto found=expected.find(parameter->getName(128));if(found==expected.end())add(label,program,parameter->getName(128),"restore_added",0,parameter->getValue());else if(std::abs(found->second-parameter->getValue())>.0001f)add(label,program,parameter->getName(128),"restore_value",found->second,parameter->getValue());}
            ++contexts;
        }std::cout<<"CONTROL_ROUNDTRIP "<<label<<" cumulative_issues="<<issues.size()<<std::endl;
    }var result(new DynamicObject());result.getDynamicObject()->setProperty("contexts",contexts);result.getDynamicObject()->setProperty("checks",checks);result.getDynamicObject()->setProperty("issues",issues);File(path).getSiblingFile("control-roundtrip-audit.json").replaceWithText(JSON::toString(result,true));std::cout<<"CONTROL_ROUNDTRIP_TOTAL contexts="<<contexts<<" controls="<<checks<<" issues="<<issues.size()<<std::endl;return issues.size()?1:0;
}
static int signal_quality(const var& catalog,const rhythmer::SoundLoader& loader,const char* path){
    auto engines=catalog["engines"];Array<var> rows;AudioBuffer<float> out(2,128);MidiBuffer midi;
    for(int e=0;e<engines.size();++e){String error;auto rack=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(rack),error.toRawUTF8());
        for(int program=0;program<rack->getNumPrograms();++program){rack->setCurrentProgram(program);double sum=0,dc=0;float peak=0;int clip=0;const int frames=44100;for(int at=0;at<frames;at+=128){out.clear();midi.clear();if(!at)midi.addEvent(MidiMessage::noteOn(1,60,uint8(110)),0);if(at==22016)midi.addEvent(MidiMessage::noteOff(1,60),0);rack->processBlock(out,midi);for(int n=0;n<std::min(128,frames-at);++n)for(int ch=0;ch<2;++ch){float v=out.getSample(ch,n);require(std::isfinite(v),"Signal quality non-finite");peak=std::max(peak,std::abs(v));sum+=v*v;dc+=v;if(std::abs(v)>=1)++clip;}}
            midi.clear();midi.addEvent(MidiMessage::allSoundOff(1),0);rack->processBlock(out,midi);var row(new DynamicObject());auto* o=row.getDynamicObject();o->setProperty("engine",engines[e]["name"]);o->setProperty("program",program);o->setProperty("preset",rack->getProgramName(program));o->setProperty("peak",peak);o->setProperty("rms",std::sqrt(sum/(frames*2)));o->setProperty("dc",dc/(frames*2));o->setProperty("clip_ratio",clip/double(frames*2));rows.add(row);
        }std::cout<<"SIGNAL_QUALITY "<<engines[e]["name"].toString()<<" programs="<<rack->getNumPrograms()<<std::endl;
        File(path).getSiblingFile("signal-quality-audit.json").replaceWithText(JSON::toString(var(rows),true));
    }return 0;
}

static void settle_controls(AudioPluginInstance& synth){AudioBuffer<float> output(2,128);MidiBuffer midi;for(int i=0;i<64;++i){output.clear();synth.processBlock(output,midi);}}
static int kit_ownership(const var& catalog,const rhythmer::SoundLoader& loader,const char* path,bool model_only=false,String kit_filter={}){
    String error;auto rack=rhythmer::make_sound_rack(catalog,-1,loader,44100,128,error);require(bool(rack),error.toRawUTF8());Array<var> issues;int checked=0;
    auto child=[](const var& state,int pad){return state["children"][int(state["routes"][pad]["child"])];};
    int pass=std::getenv("RHYTHMER_QA_PASS")?std::atoi(std::getenv("RHYTHMER_QA_PASS")):0;
    for(int sequence=0;!model_only&&sequence<rack->getNumPrograms();++sequence){int program=pass==2?rack->getNumPrograms()-1-sequence:pass==3?(sequence*13+7)%rack->getNumPrograms():sequence;if(kit_filter.isNotEmpty()&&rack->getProgramName(program)!=kit_filter)continue;rack->setCurrentProgram(program);
        for(int step=0;step<16;++step){int pad=pass==2?15-step:pass==3?(step*5+10)%16:step;rack->getParameters()[0]->setValue(pad/63.f);MemoryBlock state;rack->getStateInformation(state);auto before=JSON::parse(state.toString());int target=6,best=-1;String prefix="P"+String(pad+1).paddedLeft('0',2)+" ";
            for(int p=rhythmer::sound_rack_source_parameter_begin(rack.get());p<rhythmer::sound_rack_parameter_count(rack.get());++p){auto name=rack->getParameters()[p]->getName(128);require(name.startsWith(prefix),"Kit ownership label mismatch");int score=(name==prefix+"Volume"||name==prefix+"Level"||name.endsWith(" Voice Level")||name.endsWith(" Voice Volume"))?100:name.endsWith(" Level")||name.endsWith(" Volume")?10:0;if(name.contains("Source "))score=0;if(score>best){best=score;target=p;}}
            require(best==100,"Kit audio check cannot identify the source voice gain");settle_controls(*rack);double sounding=play(*rack,36+pad,64);rack->getStateInformation(state);before=JSON::parse(state.toString());

            require(target<rhythmer::sound_rack_parameter_count(rack.get()),"Kit pad has no writable controls");auto* parameter=rack->getParameters()[target];auto name=parameter->getName(128);std::vector<int> gains{target};auto source_engine=child(before,pad)["engine"].toString();if(source_engine.contains("elixir"))for(int p=rhythmer::sound_rack_source_parameter_begin(rack.get());p<rhythmer::sound_rack_parameter_count(rack.get());++p){auto label=rack->getParameters()[p]->getName(128);if(label.endsWith("Transient Volume")||label.endsWith("FX Volume"))gains.push_back(p);}for(int gain:gains)rack->getParameters()[gain]->setValue(0);MemoryBlock edited;rack->getStateInformation(edited);auto after=JSON::parse(edited.toString());bool target_changed=JSON::toString(child(before,pad)["values"])!=JSON::toString(child(after,pad)["values"]);
            auto report=[&](const String& kind,int affected){var row(new DynamicObject());auto* o=row.getDynamicObject();o->setProperty("kit",rack->getProgramName(program));o->setProperty("pad",pad+1);o->setProperty("control",name);o->setProperty("kind",kind);o->setProperty("affected_pad",affected+1);issues.add(row);};
            if(!target_changed)report("target_unchanged",pad);
            for(int other=0;other<16;++other)if(other!=pad&&JSON::toString(child(before,other))!=JSON::toString(child(after,other)))report("other_pad_changed",other);
            rack->setStateInformation(edited.getData(),int(edited.getSize()));MemoryBlock restored;rack->getStateInformation(restored);auto roundtrip=JSON::parse(restored.toString());settle_controls(*rack);double muted=play(*rack,36+pad,64);if(sounding<=1e-7||muted>sounding*.01){report("voice_gain_audio_mismatch",pad);auto* detail=issues.getReference(issues.size()-1).getDynamicObject();detail->setProperty("before_energy",sounding);detail->setProperty("after_energy",muted);}
            for(int other=0;other<16;++other)if(JSON::toString(child(after,other))!=JSON::toString(child(roundtrip,other)))report("restore_changed",other);
            rack->setStateInformation(state.getData(),int(state.getSize()));++checked;
        }std::cout<<"KIT_OWNERSHIP "<<rack->getProgramName(program)<<" cumulative_issues="<<issues.size()<<std::endl;
    }
    int hortator=-1;for(int n=0;n<catalog["engines"].size();++n)if(catalog["engines"][n]["name"].toString()=="Hortator")hortator=n;require(hortator>=0,"Missing Hortator");
    int acid=-1,model_steps=0;
    for(int pad=0;pad<16;++pad){rack->getParameters()[0]->setValue(pad/63.f);rack->getParameters()[1]->setValue(hortator/float(catalog["engines"].size()-1));MemoryBlock sync;rack->getStateInformation(sync);rack->getParameters()[2]->setValue(0);rack->getStateInformation(sync);
        int parameter=-1;for(int p=rhythmer::sound_rack_source_parameter_begin(rack.get());p<rhythmer::sound_rack_parameter_count(rack.get());++p)if(rack->getParameters()[p]->getName(128).containsIgnoreCase("Sound model"))parameter=p;require(parameter>=0,"Kit model missing");auto* control=rack->getParameters()[parameter];float kick=control->getValue();model_steps=control->getNumSteps();
        if(acid<0)for(int n=0;n<model_steps;++n){control->setValue(n/float(model_steps-1));rack->getStateInformation(sync);if(control->getText(0,128).startsWithIgnoreCase("ACID")){acid=n;break;}}require(acid>=0,"Native Acid model missing");
        control->setValue(acid/float(model_steps-1));rack->getStateInformation(sync);auto state=JSON::parse(sync.toString());require(int(state["routes"][pad]["note"])==60,"Kit model change retained drum trigger pitch for Acid");require(play(*rack,36+pad)>1e-7,"Kit Acid model silent");
        control->setValue(kick);rack->getStateInformation(sync);state=JSON::parse(sync.toString());require(int(state["routes"][pad]["note"])==36,"Kit model change retained Acid pitch for drum");require(play(*rack,36+pad)>1e-7,"Kit drum model silent");
    }
    std::cout<<"KIT_MODEL_ROUTE pads=16 drum_to_acid_C4=ok acid_to_drum=ok"<<std::endl;
    var result(new DynamicObject());result.getDynamicObject()->setProperty("model_route_checks",16);result.getDynamicObject()->setProperty("pad_checks",checked);result.getDynamicObject()->setProperty("issues",issues);File(path).getSiblingFile("kit-ownership-audit.json").replaceWithText(JSON::toString(result,true));std::cout<<"KIT_OWNERSHIP_TOTAL pads="<<checked<<" voice_gain_audio_checked=all issues="<<issues.size()<<std::endl;return issues.size()?1:0;
}

static int plaits_controls(const var& catalog,const rhythmer::SoundLoader& loader,const char* path){
    auto engines=catalog["engines"];int e=-1;for(int n=0;n<engines.size();++n)if(engines[n]["name"].toString()=="Plaits")e=n;require(e>=0,"Missing Plaits");String error;auto rack=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(rack),error.toRawUTF8());require(rack->getNumPrograms()==120,"Missing embedded 6-Op programs");
    auto table=JSON::parse(File::getSpecialLocation(File::currentExecutableFile).getSiblingFile("plaits-model-controls.json").loadFileAsString());require(table.isObject(),"Missing original model controls");
    for(int program=0;program<120;++program){rack->setCurrentProgram(program);int model=program<24?program:2+(program-24)/32;std::set<String> names;for(int p=6;p<rhythmer::sound_rack_parameter_count(rack.get());++p)names.insert(rack->getParameters()[p]->getName(128));
        for(int col=0;col<3;++col){if(col==0&&model>=2&&model<=4)continue;String expected=table["labels"][model][col].toString();bool found=false;for(auto name:names)found|=name==expected||name.endsWith(" "+expected);require(found,("Wrong model control: "+String(model)+" / "+expected).toRawUTF8());}
        bool fm=false;for(auto name:names)fm|=name.contains("FM Amount");require(fm==!(model>=2&&model<=4),"Inactive FM Amount displayed for 6-Op");
        if(program>=24){int bank=(program-24)/32,index=(program-24)%32;String expected=table["fm_banks"][bank][index].toString();require(rack->getProgramName(program).endsWith(expected.trim()),"FM browser name mismatch");for(auto name:names)require(!name.endsWith(" Preset")&&name!="Preset","Duplicate internal FM preset selector remains in EDIT");MemoryBlock state;rack->getStateInformation(state);auto saved=JSON::parse(state.toString());float raw=float(saved["children"][0]["values"][1]);require(std::clamp(int(raw*1.02f*32),0,31)==index,"FM name maps to a different source program");require(play(*rack,60)>1e-7,"Embedded FM preset silent");}
    }
    std::cout<<"PLAITS_CONTROLS models=24 original_fm_programs=96 names_and_quantizer=ok duplicate_selector=hidden inactive_FM=hidden"<<std::endl;return 0;
}

struct SignalStats{double peak=0,rms=0,dc=0;};
static SignalStats measured_signal(AudioPluginInstance& synth,int frames){AudioBuffer<float> out(2,128);MidiBuffer midi;SignalStats s;double energy=0,sum=0;for(int at=0;at<frames;at+=128){out.clear();midi.clear();if(!at)midi.addEvent(MidiMessage::noteOn(1,60,uint8(110)),0);if(at==22016&&frames==44100)midi.addEvent(MidiMessage::noteOff(1,60),0);synth.processBlock(out,midi);for(int f=0;f<std::min(128,frames-at);++f)for(int c=0;c<2;++c){float v=out.getSample(c,f);require(std::isfinite(v),"Review non-finite signal");s.peak=std::max(s.peak,double(std::abs(v)));energy+=v*v;sum+=v;}}s.rms=std::sqrt(energy/(frames*2));s.dc=sum/(frames*2);return s;}
static int quality_review(const var& catalog,const rhythmer::SoundLoader& loader,const char* path){
    const File parent=File(path).getParentDirectory();auto candidates=JSON::parse(parent.getChildFile("signal-quality-audit.json").loadFileAsString());require(candidates.isArray(),"Missing signal quality scan");auto engines=catalog["engines"];Array<var> results;
    for(auto row:*candidates.getArray()){if(float(row["peak"])>=.005f&&std::abs(float(row["dc"]))<=.05f&&float(row["clip_ratio"])<=.005f)continue;
        int e=-1;for(int n=0;n<engines.size();++n)if(engines[n]["name"].toString()==row["engine"].toString())e=n;require(e>=0,"Unknown quality source");String error;auto rack=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(rack),error.toRawUTF8());int program=int(row["program"]);rack->setCurrentProgram(program);auto r=measured_signal(*rack,44100);
        auto config=engines[e];auto sound=config["sounds"][config["selection"].isArray()?int(config["selection"][program]):program];auto folder=config["source_folder"].toString();if(folder.isEmpty())folder=config["folder"].toString();auto native=loader(folder.toStdString(),error);require(bool(native),error.toRawUTF8());native->enableAllBuses();native->prepareToPlay(44100,128);auto* vst=dynamic_cast<rhythmer::Vst2Instance*>(native.get());
        if(auto* setup=sound["native_setup"].getArray())for(auto pair:*setup)require(vst&&vst->nativeSet(pair[0].toString(),pair[1].toString()),"Review bank select failed");
        if(!sound["native_key"].isVoid())require(vst&&vst->nativeSet(sound["native_key"].toString(),sound["native_value"].toString()),"Review source select failed");else if(!sound["program"].isVoid())native->setCurrentProgram(int(sound["program"]));else if(auto* values=sound["values"].getDynamicObject())for(const auto& value:values->getProperties())native->getParameters()[value.name.toString().getIntValue()]->setValue(float(value.value));
        if(auto* values=config["initial_values"].getDynamicObject())for(const auto& value:values->getProperties())native->getParameters()[value.name.toString().getIntValue()]->setValue(float(value.value));
        auto direct=measured_signal(*native,44100);var result(new DynamicObject());auto* o=result.getDynamicObject();o->setProperty("engine",row["engine"]);o->setProperty("preset",row["preset"]);o->setProperty("program",program);o->setProperty("rack_peak",r.peak);o->setProperty("module_peak",direct.peak);o->setProperty("rack_rms",r.rms);o->setProperty("module_rms",direct.rms);o->setProperty("rack_dc",r.dc);o->setProperty("module_dc",direct.dc);
        if(float(row["peak"])<.005f){rack->setCurrentProgram(program);const bool slow=row["engine"].toString()=="Aphex";auto held=measured_signal(*rack,44100*(slow?32:4));o->setProperty("held_seconds",slow?32:4);o->setProperty("held_peak",held.peak);o->setProperty("held_rms",held.rms);}
        results.add(result);parent.getChildFile("signal-quality-review.json").replaceWithText(JSON::toString(var(results),true));std::cout<<"QUALITY_REVIEW "<<row["engine"].toString()<<" / "<<row["preset"].toString()<<" rack="<<r.peak<<" module="<<direct.peak<<std::endl;
    }return 0;
}
