// SPDX-License-Identifier: AGPL-3.0-only
// Measure the authored patches through the real host, including note-off/tails.
static int authored_check(const var& catalog,const rhythmer::SoundLoader& loader,const char* path){
    Array<var> rows;auto engines=catalog["engines"];String error;unsigned checked=0;
    for(int e=0;e<engines.size();++e){if(engines[e]["name"].toString()!="Prophet"&&engines[e]["name"].toString()!="Elixir")continue;
        auto rack=rhythmer::make_sound_rack(catalog,e,loader,44100,128,error);require(bool(rack),error.toRawUTF8());
        auto sounds=engines[e]["sounds"];
        for(int program=0;program<rack->getNumPrograms();++program){if(!sounds[program]["origin"].toString().startsWith("Rhythmer original"))continue;
            rack->setCurrentProgram(program);AudioBuffer<float> out(2,128);MidiBuffer midi;double sum=0,tail=0;float peak=0;int onset=-1;unsigned clipped=0;
            const bool melodic=engines[e]["name"].toString()=="Prophet";const int gate=44100,frames=44100*3;
            for(int at=0;at<frames;at+=128){midi.clear();if(at==0){midi.addEvent(MidiMessage::noteOn(1,60,uint8(100)),0);if(melodic){midi.addEvent(MidiMessage::noteOn(1,64,uint8(92)),0);midi.addEvent(MidiMessage::noteOn(1,67,uint8(88)),0);}}
                if(at<=gate&&gate<at+128){for(int key:{60,64,67})midi.addEvent(MidiMessage::noteOff(1,key),gate-at);}
                out.clear();rack->processBlock(out,midi);
                for(int f=0;f<128&&at+f<frames;++f)for(int c=0;c<2;++c){float v=out.getSample(c,f);require(std::isfinite(v),"Authored patch non-finite");peak=std::max(peak,std::abs(v));sum+=v*v;clipped+=std::abs(v)>=.9999f;if(onset<0&&std::abs(v)>.001f)onset=at+f;if(at+f>=frames-4410)tail+=v*v;}
            }
            double rms=std::sqrt(sum/(frames*2)),tail_rms=std::sqrt(tail/8820);
            var row(new DynamicObject());auto* o=row.getDynamicObject();o->setProperty("engine",engines[e]["name"]);o->setProperty("preset",rack->getProgramName(program));o->setProperty("peak",peak);o->setProperty("rms",rms);o->setProperty("onset_ms",onset*1000.0/44100);o->setProperty("tail_rms",tail_rms);o->setProperty("clipped_samples",int(clipped));rows.add(row);
            File(path).getSiblingFile("authored-audio.json").replaceWithText(JSON::toString(var(rows),true));
            std::cout<<"AUTHORED "<<engines[e]["name"].toString()<<" / "<<rack->getProgramName(program)<<" peak="<<peak<<" onset_ms="<<onset*1000.0/44100<<" tail_rms="<<tail_rms<<" clip="<<clipped<<std::endl;
            require(onset>=0&&onset<44100/2&&rms>1e-5,"Authored patch has a slow/silent onset");require(peak<1.2f&&clipped<128,"Authored patch clipping");require(tail_rms<.02,"Authored patch tail too long");++checked;
        }
    }
    require(checked==43,"Authored bank coverage changed");return 0;
}
