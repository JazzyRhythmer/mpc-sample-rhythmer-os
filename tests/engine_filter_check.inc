// SPDX-License-Identifier: AGPL-3.0-only
static int engine_filter_check(const var& catalog,const rhythmer::SoundLoader& loader,const char* path){
    using namespace rhythmer;int checked=0,programs=0;Array<var> rows;
    for(int e=0;e<catalog["engines"].size();++e){auto entry=catalog["engines"][e];auto name=entry["name"].toString();
        if(name!="Dexed"&&name!="DRUM-X"&&name!="Plaits"&&name!="CS-1"&&name!="MONO2K")continue;
        String error;auto rack=make_sound_rack(catalog,e,loader,44100,128,error);require(bool(rack),error.toRawUTF8());
        auto flush=[&]{MemoryBlock b;rack->getStateInformation(b);return b;};auto set=[&](int i,float v){rack->getParameters()[i]->setValue(v);flush();};
        require(sound_rack_source_parameter_begin(rack.get())==9,"Missing engine output filter");
        for(int program=0;program<std::min(3,rack->getNumPrograms());++program){rack->setCurrentProgram(program);++programs;
            auto q=sound_rack_quick_parameters(rack.get());require(q[0]==6&&q[1]==7&&q[2]>=9,"First page must mirror output filter and retain a native third knob");
            require(rack->getParameters()[6]->getName(64)=="OUTPUT CUTOFF"&&rack->getParameters()[7]->getName(64)=="OUTPUT RESONANCE","Ambiguous output-filter labels");
            require(rack->getParameters()[6]->getValue()==1&&rack->getParameters()[7]->getValue()==0&&rack->getParameters()[8]->getValue()==0,"Original preset does not start with neutral output filter");
        }
        rack->setCurrentProgram(0);auto original=flush();auto before=JSON::parse(original.toString());settle_controls(*rack);double dry=play(*rack,60,128);
        rack->setStateInformation(original.getData(),int(original.getSize()));set(6,0);set(8,.5f);auto after=JSON::parse(flush().toString());settle_controls(*rack);double wet=play(*rack,60,128);
        require(dry>1e-9&&wet<dry*.85,"Engine output filter did not audibly affect the whole engine");
        require(JSON::toString(before["children"])==JSON::toString(after["children"]),"Output filter rewrote original source state");
        set(6,.63f);set(7,.25f);set(8,1);auto project=flush();set(6,.1f);rack->setStateInformation(project.getData(),int(project.getSize()));require(std::abs(rack->getParameters()[6]->getValue()-.63f)<1e-6f,"Project lost engine filter");
        const int factory=rack->getNumPrograms();set(3,1);set(4,1);auto reopened=make_sound_rack(catalog,e,loader,44100,128,error);require(bool(reopened),error.toRawUTF8());reopened->setCurrentProgram(factory);
        for(int i=6;i<9;++i){float v=i==6?.63f:i==7?.25f:1;require(std::abs(reopened->getParameters()[i]->getValue()-v)<1e-6f&&std::abs(reopened->getParameters()[i]->getDefaultValue()-v)<1e-6f,"Saved sound lost filter or reset baseline");}
        rack->setCurrentProgram(0);require(rack->getParameters()[6]->getValue()==1&&rack->getParameters()[7]->getValue()==0,"Factory program retained previous output filter");
        set(6,.25f);set(7,.65f);set(8,.5f);settle_controls(*rack);AudioBuffer<float> out(2,128);MidiBuffer midi;midi.addEvent(MidiMessage::noteOn(1,60,uint8(110)),0);rack->processBlock(out,midi);midi.clear();midi.addEvent(MidiMessage::allSoundOff(1),17);out.clear();rack->processBlock(out,midi);
        for(int c=0;c<2;++c)for(int n=17;n<128;++n)require(out.getSample(c,n)==0,"Engine output filter rings past panic MIDI offset");
        var row(new DynamicObject());row.getDynamicObject()->setProperty("engine",name);row.getDynamicObject()->setProperty("dry_energy",dry);row.getDynamicObject()->setProperty("filtered_energy",wet);rows.add(row);
        std::cout<<"OUTPUT_FILTER engine="<<name<<" dry="<<dry<<" filtered="<<wet<<" original_state=unchanged save_restore=ok panic=ok"<<std::endl;++checked;
    }
    require(checked==5,"Not all five output-filter instruments were tested");
    File(path).getSiblingFile("engine-output-filter-audit.json").replaceWithText(JSON::toString(var(rows),true));
    std::cout<<"ENGINE_FILTER engines="<<checked<<" factory_program_checks="<<programs<<" inserts=0"<<std::endl;return 0;
}
