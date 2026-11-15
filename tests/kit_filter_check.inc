// SPDX-License-Identifier: AGPL-3.0-only
static int kit_filter_check(const var& catalog,const rhythmer::SoundLoader& loader,const char* path){
    using namespace rhythmer;
    { // An untouched factory kit must not be coloured by the added filter.
        KitFilterStage stage;std::array<float,128> left{},right{},expected_l{},expected_r{};
        for(int n=0;n<128;++n){left[size_t(n)]=std::sin(float(n)*.31f)*.7f;right[size_t(n)]=std::cos(float(n)*.17f)*.6f;}
        expected_l=left;expected_r=right;stage.process({{100,0,0}},1,left.data(),right.data(),128);
        require(left==expected_l&&right==expected_r,"Neutral Kit filter changes original PCM");
        require(!effect_needs_memory(EffectKind::Filter),"Kit filter unexpectedly needs delay memory");
    }
    String error;auto rack=make_sound_rack(catalog,-1,loader,44100,128,error);
    auto other=make_sound_rack(catalog,-1,loader,44100,128,error);require(bool(rack)&&bool(other),error.toRawUTF8());
    auto flush=[&]{MemoryBlock state;rack->getStateInformation(state);return JSON::parse(state.toString());};
    auto set=[&](int p,float value){rack->getParameters()[p]->setValue(value);flush();};
    const int factory=rack->getNumPrograms();int pads=0;
    for(int program=0;program<factory;++program){rack->setCurrentProgram(program);
        require(rack->getParameters()[6]->getValue()==1&&rack->getParameters()[7]->getValue()==0&&rack->getParameters()[8]->getValue()==0,"Factory Kit filter must start neutral");
        for(int pad=0;pad<16;++pad){set(0,pad/63.f);auto q=sound_rack_quick_parameters(rack.get());require(q==std::array<int,3>{{6,7,8}}&&sound_rack_source_parameter_begin(rack.get())==9,"Kit global filter follows source-pad indices");++pads;}
    }
    rack->setCurrentProgram(0);int audible=0;
    for(int pad=0;pad<16;++pad){
        set(6,1);set(7,0);set(8,0);settle_controls(*rack);double dry=play(*rack,36+pad,96);
        auto before=flush();set(6,0);set(8,.5f);auto after=flush();settle_controls(*rack);double filtered=play(*rack,36+pad,96);
        require(dry>1e-7&&filtered<dry*.7,"Whole-kit BP filter did not affect the played destination pad");
        for(int child=0;child<before["children"].size();++child)require(JSON::toString(before["children"][child]["values"])==JSON::toString(after["children"][child]["values"]),"Kit filter rewrote a source patch");
        ++audible;
    }
    require(other->getParameters()[6]->getValue()==1&&other->getParameters()[7]->getValue()==0&&other->getParameters()[8]->getValue()==0,"Kit instances share filter settings");
    // A global knob remains global while pads (including an empty pad) change.
    auto revision=sound_rack_revision(rack.get());set(0,63.f/63.f);
    sound_rack_set_parameter_checked(rack.get(),6,.55f,revision);flush();
    require(std::abs(rack->getParameters()[6]->getValue()-.55f)<1e-6f&&sound_rack_parameter_count(rack.get())==9,"Global Kit filter lost edits on an empty/stale-focus pad");
    set(0,10.f/63.f);set(6,.63f);set(7,.25f);set(8,1);
    auto source_before=flush();set(2,.05f);auto source_after=flush();
    require(JSON::toString(source_before["kit_filter"])==JSON::toString(source_after["kit_filter"]),"Replacing a pad sound reset the whole-kit filter");
    set(3,1);set(4,1);
    auto reopened=make_sound_rack(catalog,-1,loader,44100,128,error);require(bool(reopened),error.toRawUTF8());
    require(reopened->getNumPrograms()==factory+1,"Saved Kit filter preset was not listed");reopened->setCurrentProgram(factory);
    for(int p=6;p<9;++p){float expected=p==6?.63f:p==7?.25f:1.f;require(std::abs(reopened->getParameters()[p]->getValue()-expected)<1e-6f,"Kit preset lost global filter settings");require(std::abs(reopened->getParameters()[p]->getDefaultValue()-expected)<1e-6f,"Saved Kit filter reset baseline is wrong");}
    MemoryBlock project_state;reopened->getStateInformation(project_state);reopened->getParameters()[6]->setValue(.1f);MemoryBlock sync;reopened->getStateInformation(sync);
    reopened->setStateInformation(project_state.getData(),int(project_state.getSize()));require(std::abs(reopened->getParameters()[6]->getValue()-.63f)<1e-6f,"Project state lost Kit filter");
    // Hard stop is sample-accurate through the Kit's own filter state too.
    rack->setCurrentProgram(0);set(6,.25f);set(7,.65f);set(8,.5f);settle_controls(*rack);
    AudioBuffer<float> output(2,128);MidiBuffer midi;midi.addEvent(MidiMessage::noteOn(1,36,uint8(110)),0);rack->processBlock(output,midi);
    midi.clear();midi.addEvent(MidiMessage::allSoundOff(1),17);output.clear();rack->processBlock(output,midi);
    for(int ch=0;ch<2;++ch)for(int n=17;n<128;++n)require(output.getSample(ch,n)==0,"Kit filter rings after hard stop's MIDI offset");
    var report(new DynamicObject());auto* o=report.getDynamicObject();o->setProperty("factory_kits",factory);o->setProperty("pad_scope_checks",pads);o->setProperty("audible_pad_checks",audible);o->setProperty("neutral_pcm_exact",true);o->setProperty("insert_slots_used",0);o->setProperty("preset_project_reset",true);o->setProperty("panic_midi_offset",17);
    File(path).getSiblingFile("kit-engine-filter-audit.json").replaceWithText(JSON::toString(report,true));
    std::cout<<"KIT_ENGINE_FILTER kits="<<factory<<" scope_pads="<<pads<<" audible_pads="<<audible<<" neutral_pcm=exact source_patches=unchanged instances=independent preset_project_reset=ok empty_pad=ok panic_offset=17 inserts=0"<<std::endl;return 0;
}
