// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 jazzy rhythmer
static int acid_aliases(const var& catalog,const rhythmer::SoundLoader& loader){
    auto engines=catalog["engines"];int acid=-1,aphex=-1;
    for(int i=0;i<engines.size();++i){auto name=engines[i]["name"].toString();if(name=="Acid Engine")acid=i;if(name=="Aphex")aphex=i;}
    require(acid>=0&&aphex>=0,"Missing Acid/Aphex");String error;
    auto rack=rhythmer::make_sound_rack(catalog,acid,loader,44100,128,error);require(bool(rack),error.toRawUTF8());
    require(rack->getNumPrograms()==12,"Expected four original Acid and eight original Aphex choices");
    auto identity=[](AudioPluginInstance* p){rhythmer::PluginPanel panel;require(rhythmer::sound_rack_design_pages(p,panel),"Missing source design pages");return String(panel.design_source);};
    int aliases=0;
    for(int i=4;i<12;++i){
        rack->setCurrentProgram(i);auto row=engines[acid]["sounds"][i];const int original=int(row["source_sound"]);
        auto direct=rhythmer::make_sound_rack(catalog,aphex,loader,44100,128,error);require(bool(direct),error.toRawUTF8());direct->setCurrentProgram(original);
        require(rack->getProgramName(i)==direct->getProgramName(original),"Original Aphex name changed");
        require(identity(rack.get())=="Aphex","Alias source identity incorrect");
        require(rhythmer::sound_rack_parameter_count(rack.get())==rhythmer::sound_rack_parameter_count(direct.get()),"Wrong source control count");
        const int count=rhythmer::sound_rack_parameter_count(rack.get());
        for(int p=6;p<count;++p){auto* a=rack->getParameters()[p];auto* b=direct->getParameters()[p];require(a->getName(128)==b->getName(128),"Wrong source parameter name");require(std::abs(a->getValue()-b->getValue())<1e-6,"Alias changed original preset values");}
        require(rhythmer::sound_rack_quick_parameters(rack.get())==rhythmer::sound_rack_quick_parameters(direct.get()),"Alias quick filters mismatch");
        for(int note:{36,48,60,72,84})require(play(*rack,note)>1e-7,"Aphex Acid preset/note silent");
        auto quick=rhythmer::sound_rack_quick_parameters(rack.get());require(quick[0]>=6&&quick[1]>=6,"Missing Aphex cutoff/resonance");
        rack->getParameters()[quick[0]]->setValue(.43f);MemoryBlock state;rack->getStateInformation(state);
        auto restored=rhythmer::make_sound_rack(catalog,acid,loader,44100,128,error);require(bool(restored),error.toRawUTF8());restored->setStateInformation(state.getData(),int(state.getSize()));
        require(restored->getCurrentProgram()==i&&identity(restored.get())=="Aphex","Project restore lost alias identity");
        require(std::abs(restored->getParameters()[quick[0]]->getValue()-.43f)<.002f,"Project restore lost Aphex cutoff");
        require(play(*restored,60)>1e-7,"Restored alias silent");
        rack->getParameters()[3]->setValue(i/63.f);rack->getParameters()[4]->setValue(1);rack->getStateInformation(state);
        auto saved=rhythmer::make_sound_rack(catalog,acid,loader,44100,128,error);require(bool(saved),error.toRawUTF8());saved->setCurrentProgram(12+i-4);
        require(identity(saved.get())=="Aphex","User Sound lost source engine");
        require(std::abs(saved->getParameters()[quick[0]]->getValue()-.43f)<.002f,"User Sound lost source controls");
        require(play(*saved,60)>1e-7,"User Sound alias silent");
        rack->setCurrentProgram(0);require(identity(rack.get())=="Acid Engine"&&play(*rack,60)>1e-7,"Return to Hortator Acid failed");
        std::cout<<"ACID_ALIAS "<<row["name"].toString()<<" source_controls="<<count-6<<" pitch=5 project_restore=ok user_sound=ok"<<std::endl;++aliases;
    }
    auto kit=rhythmer::make_sound_rack(catalog,-1,loader,44100,128,error);require(bool(kit),error.toRawUTF8());MemoryBlock sync;
    kit->getParameters()[0]->setValue(10/63.f);kit->getStateInformation(sync);
    kit->getParameters()[1]->setValue(acid/float(engines.size()-1));kit->getStateInformation(sync);
    kit->getParameters()[2]->setValue(4/11.f);kit->getStateInformation(sync);
    require(rhythmer::sound_rack_focus(kit.get())==10&&rhythmer::sound_rack_source_name(kit.get())=="Aphex","Hybrid alias lost pad/source identity");{var view(new DynamicObject());design_view(view,kit.get(),true);}
    auto restored_kit=rhythmer::make_sound_rack(catalog,-1,loader,44100,128,error);require(bool(restored_kit),error.toRawUTF8());restored_kit->setStateInformation(sync.getData(),int(sync.getSize()));
    require(rhythmer::sound_rack_focus(restored_kit.get())==10&&rhythmer::sound_rack_source_name(restored_kit.get())=="Aphex","Hybrid alias restore lost pad/source identity");{var view(new DynamicObject());design_view(view,restored_kit.get(),true);}
    std::cout<<"ACID_ALIAS_HYBRID pad=11 source=Aphex restore=ok"<<std::endl;
    std::cout<<"ACID_ALIASES passed="<<aliases<<std::endl;return 0;
}
