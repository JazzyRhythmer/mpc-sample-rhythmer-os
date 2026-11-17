// SPDX-License-Identifier: AGPL-3.0-only
// Real SoundRack output: no externally authored substitute patches or effects.
static int website_preview(const var& catalog,const rhythmer::SoundLoader& loader,const char* path){
    auto root=File(path).getParentDirectory();auto engines=catalog["engines"];String error;Array<var> report;
    for(const char* name:{"Frodhes","Tenebrae","FMini-1"}){
        int index=-1;for(int i=0;i<engines.size();++i)if(engines[i]["name"].toString()==name)index=i;
        require(index>=0,"Missing preview source");auto rack=rhythmer::make_sound_rack(catalog,index,loader,44100,128,error);require(bool(rack),error.toRawUTF8());
        int program=0;if(String(name)=="Tenebrae")program=1;rack->setCurrentProgram(program);MemoryBlock state;rack->getStateInformation(state);
        const int frames=44100*9,beat=22050;AudioBuffer<float> out(2,128);MidiBuffer midi;std::vector<float> pcm;pcm.reserve(frames*2);
        for(int at=0;at<frames;at+=128){midi.clear();
            for(int b=0;b<16;++b){int start=b*beat/2,end=start+int(beat*.40);int note=std::array<int,8>{48,55,58,60,63,60,58,55}[b%8];
                if(String(name)=="Frodhes"){if(b%4)continue;end=start+int(beat*1.8);for(int n:{60,63,67,70}){if(start>=at&&start<at+128)midi.addEvent(MidiMessage::noteOn(1,n+(b>=8?5:0),uint8(96)),start-at);if(end>=at&&end<at+128)midi.addEvent(MidiMessage::noteOff(1,n+(b>=8?5:0)),end-at);}}
                else {if(start>=at&&start<at+128)midi.addEvent(MidiMessage::noteOn(1,note,uint8(98)),start-at);if(end>=at&&end<at+128)midi.addEvent(MidiMessage::noteOff(1,note),end-at);}}
            out.clear();rack->processBlock(out,midi);for(int f=0;f<std::min(128,frames-at);++f)for(int c=0;c<2;++c){float v=out.getSample(c,f);require(std::isfinite(v),"Non-finite preview");float edge=std::min(1.f,std::min(float(at+f)/441.f,float(frames-at-f)/2205.f));pcm.push_back(v*edge);}}
        double energy=0;float peak=0;for(float v:pcm){energy+=v*v;peak=std::max(peak,std::abs(v));}require(energy>1e-6,"Silent preview");double rms=std::sqrt(energy/pcm.size());float gain=std::min(float(.12589254/rms),float(.70794578/peak));
        String slug=String(name).toLowerCase();auto file=root.getChildFile(slug+"-preview.wav");audition_wav(file,pcm,gain);
        var item(new DynamicObject());auto* o=item.getDynamicObject();o->setProperty("engine",name);o->setProperty("preset",rack->getProgramName(program));o->setProperty("bpm",120);o->setProperty("duration",9);o->setProperty("peak",peak*gain);o->setProperty("rms",rms*gain);o->setProperty("gain",gain);o->setProperty("file",file.getFileName());report.add(item);
        std::cout<<"WEBSITE_PREVIEW "<<name<<" preset="<<rack->getProgramName(program)<<" peak="<<peak*gain<<std::endl;
    }root.getChildFile("website-previews.json").replaceWithText(JSON::toString(var(report),true));return 0;
}
