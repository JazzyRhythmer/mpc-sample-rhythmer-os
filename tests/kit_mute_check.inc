// SPDX-License-Identifier: AGPL-3.0-only
static int kit_mute_audio(const var& catalog,const rhythmer::SoundLoader& loader) {
    String error;auto kit=rhythmer::make_sound_rack(catalog,-1,loader,44100,128,error);require(bool(kit),error.toRawUTF8());int checks=0;
    for(int program=0;program<kit->getNumPrograms();++program){kit->setCurrentProgram(program);MemoryBlock before;kit->getStateInformation(before);
        for(int pad=0;pad<16;++pad){rhythmer::sound_rack_set_pad_mutes(kit.get(),uint64_t(1)<<pad);
            require(play(*kit,36+pad,32)<1e-12,"Muted pad produced new audio");++checks;
        }
        rhythmer::sound_rack_set_pad_mutes(kit.get(),1);require(play(*kit,37)>1e-7,"Muting pad 1 silenced pad 2");++checks;
        rhythmer::sound_rack_set_pad_mutes(kit.get(),0);require(play(*kit,36)>1e-7,"Unmuted pad 1 remained silent");++checks;
        MemoryBlock after;kit->getStateInformation(after);require(before==after,"Mute altered kit preset state or parameters");++checks;
    }
    auto single=rhythmer::make_sound_rack(catalog,0,loader,44100,128,error);require(bool(single),error.toRawUTF8());rhythmer::sound_rack_set_pad_mutes(single.get(),~uint64_t(0));require(play(*single,60)>1e-7,"Kit mute leaked into standalone engine");++checks;
    std::cout<<"KIT_MUTE_AUDIO_OK checks="<<checks<<" kits="<<kit->getNumPrograms()<<" all sixteen pads,independent-voices,preset-integrity=ok\n";return 0;
}
