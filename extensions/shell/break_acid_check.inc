// SPDX-License-Identifier: GPL-3.0-only
    {
        EngineHost h;Shell s(h);auto& x=s.context();x.ui.track=0;x.ui.page=PageId::Edit;
        auto& t=x.track();t.engine=EngineKind::Sampler;t.break_bars=2;t.bank=0;
        SampleData a,b;a.frames=b.frames=44100;a.left.resize(a.frames);b.left.resize(b.frames);
        for(unsigned n=0;n<a.frames;n++){a.left[n]=.25f*std::sin(n*.08f);b.left[n]=.25f*std::sin(n*.13f);}
        for(unsigned i=0;i<16;i++){t.pads[i].sample=0;t.pads[i].start=a.frames*i/16;t.pads[i].end=a.frames*(i+1)/16;}
        t.pads[0].layers[0].sample=1;t.pads[0].layers[0].end=b.frames;
        auto& pattern=x.pattern();pattern.length=768;pattern.events.clear();Event gate;gate.key=36;gate.length=768;pattern.add(gate);
        h.load(x.project,x.patterns);h.offer_sample(0,&a);h.offer_sample(1,&b);h.send({Command::Type::Play});
        std::array<int32_t,256> audio{};h.render(audio.data(),128,1);
        x.ui.recording=true;x.ui.settings.rec_quantize=false;x.ui.break_perf_page=1;
        edit_page.pad(x,8,110,true);for(unsigned n=0;n<40;n++)h.render(audio.data(),128,1);edit_page.pad(x,8,0,false);
        if(steps_lane(t)!=8||key_label(t,8)!="1/16 REPEAT")return gen_failure(422,__LINE__);
        auto roll=std::find_if(pattern.events.begin(),pattern.events.end(),[](const Event& e){return e.key==8;});
        if(roll==pattern.events.end()||roll->length<2)return gen_failure(401,__LINE__);
        x.ui.page=PageId::StepEdit;x.ui.step_pads=true;x.ui.held_step=13;Event edited;edited.key=8;edited.tick=13*x.pattern().q();x.pattern().add(edited);
        step_edit_page.wheel(x,1);if(steps_lane(t)!=9||key_label(t,9)!="1/16 DOWN")return gen_failure(423,__LINE__);
        x.ui.held_step=-1;x.ui.page=PageId::Edit;
        x.ui.break_perf_page=2;edit_page.pad(x,1,110,true);h.render(audio.data(),128,1);edit_page.pad(x,1,0,false);
        if(h.break_source_of(0)!=1)return gen_failure(402,__LINE__);
        Binding variation;variation.kind=Binding::Kind::BreakPerfParam;variation.id=1;variation.min=0;variation.max=127;x.apply(variation,73);h.render(audio.data(),128,1);
        edit_page.soft(x,2);h.render(audio.data(),128,1);x.gen_break_tick();if(t.break_perf[1]||t.break_perf[2])return gen_failure(424,__LINE__);
        for(unsigned key:{8u,17u,18u})if(std::none_of(pattern.events.begin(),pattern.events.end(),[&](const Event& e){return e.key==key;}))return gen_failure(403,__LINE__);
        x.ui.recording=false;auto recorded=pattern.events;edit_page.soft(x,0);
        if(x.ui.page!=PageId::Patterns||!x.ui.sheet_open||x.ui.gen8_mode!=2)return gen_failure(404,__LINE__);
        patterns_page.soft(x,0);if(!x.ui.sheet_open||x.ui.gen8_mode)return gen_failure(405,__LINE__);
        x.gen8_action(10);if(x.ui.page!=PageId::Edit||x.ui.break_perf_page)return gen_failure(406,__LINE__);
        for(unsigned page=0;page<6;page++){auto cards=page_bindings(x.project,x.ui,x.pattern());
            for(const auto& card:cards)if(card.kind==Binding::Kind::None)return gen_failure(407,__LINE__);
            edit_page.wheel(x,1);}
        if(x.ui.break_perf_page)return gen_failure(408,__LINE__);
        h.send({Command::Type::Stop});h.render(audio.data(),128,1);t.break_source=0;
        h.load(x.project,x.patterns);h.send({Command::Type::Play});bool selected_b=false,heard=false;
        for(unsigned n=0;n<160;n++){h.render(audio.data(),128,1);selected_b|=h.break_source_of(0)==1;for(auto sample:audio)heard|=sample!=0;}
        if(!selected_b||!heard||pattern.events!=recorded)return gen_failure(409,__LINE__);
        auto saved=save_project(x.project,x.patterns);auto project=std::make_unique<Project>();auto bank=std::make_unique<PatternBank>();
        if(!load_project(saved,*project,*bank).empty()||project->tracks[0].pads[0].layers[0].sample!=1||project->tracks[0].break_perf!=t.break_perf||bank->at[0][0].events!=recorded)return gen_failure(410,__LINE__);
        std::printf("RHYTHMER_BREAK_PERF pads=16 commands=19 pages=6 recording=ok replay=ok sources=AB save_restore=ok gen_back=ok\n");
    }
    {
        EngineHost h;Shell s(h);auto& x=s.context();x.ui.page=PageId::Patterns;x.ui.sheet_open=true;x.ui.gen8_mode=4;
        x.track().engine=EngineKind::Plugin;x.track().plugin=0;std::strcpy(x.project.plugins[0].name,"Acid Engine");
        x.pattern().length=768;x.pattern().events.clear();x.track().acid_gen.seed=0xdeadbeef;
        auto song_seed=x.project.gen8.seed;x.gen8_action(12);auto first=x.pattern().events;
        if(first.empty()||x.project.gen8.seed!=song_seed||x.track().acid_gen.seed!=0xdeadbeef)return gen_failure(411,__LINE__);
        x.gen8_action(12);if(x.pattern().events!=first)return gen_failure(412,__LINE__);
        x.gen8_action(3);auto next_seed=x.track().acid_gen.seed;if(next_seed==0xdeadbeef)return gen_failure(413,__LINE__);
        x.undo();if(x.pattern().events!=first||x.track().acid_gen.seed!=0xdeadbeef)return gen_failure(414,__LINE__);
        x.redo();if(x.track().acid_gen.seed!=next_seed)return gen_failure(415,__LINE__);
        for(unsigned page=0;page<3;page++){auto cards=page_bindings(x.project,x.ui,x.pattern());
            if(cards[0].kind!=(page<2?Binding::Kind::AcidGenParam:Binding::Kind::AcidGenSeed))return gen_failure(416,__LINE__);
            patterns_page.soft(x,1);}
        if(x.ui.acid_gen_page)return gen_failure(417,__LINE__);
        auto saved=save_project(x.project,x.patterns);auto project=std::make_unique<Project>();auto bank=std::make_unique<PatternBank>();
        if(!load_project(saved,*project,*bank).empty()||project->tracks[0].acid_gen.seed!=next_seed)return gen_failure(418,__LINE__);
        patterns_page.soft(x,0);if(x.ui.gen8_mode||!x.ui.sheet_open)return gen_failure(419,__LINE__);
        auto previous_seed=x.track().acid_gen.seed;x.gen8_action(2);
        if(x.track().acid_gen.seed==previous_seed||x.project.gen8.seed!=song_seed)return gen_failure(420,__LINE__);
        x.track().acid_gen.auto_bars=1;previous_seed=x.track().acid_gen.seed;x.project.tempo=3000;
        h.load(x.project,x.patterns);h.send({Command::Type::Play});x.ui.track=3;auto edits=x.edits.size();
        std::array<int32_t,256> audio{};
        for(unsigned n=0;n<400;n++){h.render(audio.data(),128,1);x.gen_break_tick();}
        if(x.project.tracks[0].acid_gen.seed==previous_seed||x.ui.track!=3||x.project.gen8.seed!=song_seed||x.edits.size()!=edits)return gen_failure(421,__LINE__);
        std::printf("RHYTHMER_ACID settings_pages=3 seed=uint32 deterministic=ok mutate_stream=ok undo_redo=ok save_restore=ok gen_back=ok\n");
    }
