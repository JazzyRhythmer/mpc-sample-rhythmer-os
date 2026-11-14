// SPDX-License-Identifier: AGPL-3.0-only
// Owner review: one held reference note for exactly half a second per patch.
static int preset_audition(const var& catalog,const rhythmer::SoundLoader& loader,const char* path){
    auto root=File(path).getParentDirectory();Array<var> all;String error;
    for(const char* engine:{"Prophet","Elixir"}){
        auto engines=catalog["engines"];int e=-1;for(int n=0;n<engines.size();++n)if(engines[n]["name"].toString()==engine)e=n;
        require(e>=0,"Missing audition engine");auto rack=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(rack),error.toRawUTF8());
        std::vector<int16_t> pcm;Array<var> cues;const int gate=22050,gap=6615;AudioBuffer<float> out(2,128);MidiBuffer midi;
        for(int p=0;p<rack->getNumPrograms();++p){rack->setCurrentProgram(p);MemoryBlock loaded;rack->getStateInformation(loaded);
            var cue(new DynamicObject());auto* c=cue.getDynamicObject();c->setProperty("index",p+1);c->setProperty("name",rack->getProgramName(p));c->setProperty("start_seconds",pcm.size()/88200.0);c->setProperty("hold_seconds",.5);cues.add(cue);
            for(int at=0;at<gate;at+=128){out.clear();midi.clear();if(!at)midi.addEvent(MidiMessage::noteOn(1,60,uint8(100)),0);rack->processBlock(out,midi);
                for(int n=0;n<std::min(128,gate-at);++n)for(int ch=0;ch<2;++ch){float v=out.getSample(ch,n);require(std::isfinite(v),"Audition non-finite");float fade=std::min(1.0f,float(gate-at-n)/88.0f);pcm.push_back(int16_t(std::lround(std::clamp(v*fade,-1.0f,1.0f)*32767)));}}
            midi.clear();midi.addEvent(MidiMessage::noteOff(1,60),0);midi.addEvent(MidiMessage::allSoundOff(1),0);rack->processBlock(out,midi);
            if(p+1<rack->getNumPrograms())pcm.insert(pcm.end(),size_t(gap)*2,0);
        }
        auto filename=String(engine).toLowerCase()+"-C4-500ms.wav";auto f=root.getChildFile(filename);std::ofstream stream(f.getFullPathName().toStdString(),std::ios::binary);
        auto u16=[&](uint16_t v){stream.put(char(v));stream.put(char(v>>8));};auto u32=[&](uint32_t v){u16(uint16_t(v));u16(uint16_t(v>>16));};
        stream.write("RIFF",4);u32(uint32_t(36+pcm.size()*2));stream.write("WAVEfmt ",8);u32(16);u16(1);u16(2);u32(44100);u32(176400);u16(4);u16(16);stream.write("data",4);u32(uint32_t(pcm.size()*2));for(auto v:pcm)u16(uint16_t(v));stream.close();require(bool(stream),"Audition WAV write failed");
        var item(new DynamicObject());item.getDynamicObject()->setProperty("engine",engine);item.getDynamicObject()->setProperty("file",filename);item.getDynamicObject()->setProperty("note","C4 / MIDI 60");item.getDynamicObject()->setProperty("velocity",100);item.getDynamicObject()->setProperty("duration_seconds",pcm.size()/88200.0);item.getDynamicObject()->setProperty("cues",cues);all.add(item);
        std::cout<<"AUDITION "<<engine<<" presets="<<rack->getNumPrograms()<<" seconds="<<pcm.size()/88200.0<<std::endl;
    }
    root.getChildFile("preset-audition.json").replaceWithText(JSON::toString(var(all),true));return 0;
}
static void audition_wav(const File& file,const std::vector<float>& samples,float gain=1){
    std::ofstream stream(file.getFullPathName().toStdString(),std::ios::binary);auto u16=[&](uint16_t v){stream.put(char(v));stream.put(char(v>>8));};auto u32=[&](uint32_t v){u16(uint16_t(v));u16(uint16_t(v>>16));};
    stream.write("RIFF",4);u32(uint32_t(36+samples.size()*2));stream.write("WAVEfmt ",8);u32(16);u16(1);u16(2);u32(44100);u32(176400);u16(4);u16(16);stream.write("data",4);u32(uint32_t(samples.size()*2));for(float v:samples){require(std::isfinite(v),"Musical preview non-finite");u16(uint16_t(int16_t(std::lround(std::clamp(v*gain,-1.0f,1.0f)*32767))));}stream.close();require(bool(stream),"Musical preview write failed");
}
static int musical_audition(const var& catalog,const rhythmer::SoundLoader& loader,const char* path){
    auto root=File(path).getParentDirectory();auto engines=catalog["engines"];String error;int e=-1;for(int n=0;n<engines.size();++n)if(engines[n]["name"].toString()=="Prophet")e=n;require(e>=0,"Missing Prophet");
    auto synth=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(synth),error.toRawUTF8());std::vector<float> chords;Array<var> cues;AudioBuffer<float> out(2,128);MidiBuffer midi;
    for(int p=0;p<synth->getNumPrograms();++p){synth->setCurrentProgram(p);MemoryBlock loaded;synth->getStateInformation(loaded);var cue(new DynamicObject());cue.getDynamicObject()->setProperty("name",synth->getProgramName(p));cue.getDynamicObject()->setProperty("start_seconds",chords.size()/88200.0);cues.add(cue);
        for(int at=0;at<22050;at+=128){out.clear();midi.clear();if(!at)for(int note:{60,64,67,71})midi.addEvent(MidiMessage::noteOn(1,note,uint8(92)),0);synth->processBlock(out,midi);for(int f=0;f<std::min(128,22050-at);++f)for(int c=0;c<2;++c)chords.push_back(out.getSample(c,f)*std::min(1.0f,float(22050-at-f)/88));}
        midi.clear();for(int note:{60,64,67,71})midi.addEvent(MidiMessage::noteOff(1,note),0);midi.addEvent(MidiMessage::allSoundOff(1),0);synth->processBlock(out,midi);if(p+1<synth->getNumPrograms())chords.insert(chords.end(),13230,0);
    }
    float chord_peak=0;for(float v:chords)chord_peak=std::max(chord_peak,std::abs(v));float chord_gain=std::min(1.0f,.9f/std::max(chord_peak,.0001f));audition_wav(root.getChildFile("prophet-Cmaj7-500ms.wav"),chords,chord_gain);
    auto kit=rhythmer::make_sound_rack(catalog,-1,loader,44100,128,error);require(bool(kit),error.toRawUTF8());std::vector<float> drums;Array<var> kit_cues;
    struct Hit {int frame,note,velocity;};std::vector<Hit> hits;
    auto add=[&](int step,int pad,int velocity){int frame=int(std::lround(step*44100*.125));hits.push_back({frame,36+pad,velocity});hits.push_back({frame+2646,36+pad,0});};
    for(int bar=0;bar<2;++bar){for(int s:{0,8})add(bar*16+s,0,104);for(int s:{4,12}){add(bar*16+s,1,92);add(bar*16+s,2,45);}for(int s=0;s<16;s+=2)add(bar*16+s,3,s%4?68:53);for(int s:{7,15})add(bar*16+s,4,57);for(int s:{3,11})add(bar*16+s,6,42);if(bar){add(27,0,90);add(30,5,66);for(int s:{21,29})add(s,8,52);}}
    add(0,7,42);std::stable_sort(hits.begin(),hits.end(),[](const Hit& a,const Hit& b){return a.frame<b.frame;});
    for(int p=0;p<kit->getNumPrograms();++p){if(!kit->getProgramName(p).startsWith("Elixir / "))continue;kit->setCurrentProgram(p);MemoryBlock loaded;kit->getStateInformation(loaded);if(!drums.empty())drums.insert(drums.end(),35280,0);
        var cue(new DynamicObject());cue.getDynamicObject()->setProperty("name",kit->getProgramName(p));cue.getDynamicObject()->setProperty("start_seconds",drums.size()/88200.0);kit_cues.add(cue);size_t next=0;
        for(int at=0;at<176400;at+=128){midi.clear();while(next<hits.size()&&hits[next].frame<at+128){auto h=hits[next++];if(h.frame>=at)midi.addEvent(h.velocity?MidiMessage::noteOn(1,h.note,uint8(h.velocity)):MidiMessage::noteOff(1,h.note),h.frame-at);}out.clear();kit->processBlock(out,midi);for(int f=0;f<std::min(128,176400-at);++f)for(int c=0;c<2;++c)drums.push_back(out.getSample(c,f)*std::min(1.0f,float(176400-at-f)/220));}
        midi.clear();midi.addEvent(MidiMessage::allSoundOff(1),0);kit->processBlock(out,midi);
    }
    require(kit_cues.size()==5,"Expected Initkit and four Elixir kits");float peak=0;for(float v:drums){require(std::isfinite(v),"Kit preview non-finite");peak=std::max(peak,std::abs(v));}float gain=std::min(1.0f,.9f/std::max(peak,.0001f));audition_wav(root.getChildFile("elixir-kits-120bpm.wav"),drums,gain);
    var report(new DynamicObject());auto* r=report.getDynamicObject();r->setProperty("prophet_chord","C4 E4 G4 B4 / Cmaj7");r->setProperty("prophet",cues);r->setProperty("prophet_gain",chord_gain);r->setProperty("bpm",120);r->setProperty("bars_per_kit",2);r->setProperty("elixir",kit_cues);r->setProperty("elixir_gain",gain);r->setProperty("elixir_raw_peak",peak);root.getChildFile("musical-audition.json").replaceWithText(JSON::toString(report,true));std::cout<<"MUSICAL_AUDITION Prophet="<<cues.size()<<" Elixir_kits="<<kit_cues.size()<<" peak="<<peak<<" common_gain="<<gain<<std::endl;return 0;
}
