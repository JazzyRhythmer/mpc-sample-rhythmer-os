// SPDX-License-Identifier: AGPL-3.0-only
struct ClockProbe {int playing=0,stopped=0;double bpm=0,ppq=0;bool release_had_clock=false;};
class ProbeGain final:public HostedAudioProcessorParameter {
public:
    float value=.25f;
    float getValue()const override{return value;}void setValue(float v)override{value=v;}float getDefaultValue()const override{return .25f;}
    String getName(int)const override{return "Gain";}String getLabel()const override{return {};}
    String getParameterID()const override{return "gain";}String getText(float v,int)const override{return String(v);}
    float getValueForText(const String& s)const override{return s.getFloatValue();}
};
class ClockFixture final:public AudioPluginInstance {
public:
    ClockProbe& probe;ProbeGain* gain;
    explicit ClockFixture(ClockProbe& p):AudioPluginInstance(BusesProperties().withOutput("Out",AudioChannelSet::stereo(),true)),probe(p){auto parameter=std::make_unique<ProbeGain>();gain=parameter.get();addHostedParameter(std::move(parameter));}
    const String getName()const override{return "Clock fixture";}
    void fillInPluginDescription(PluginDescription& d)const override{d.name=getName();d.isInstrument=true;d.numOutputChannels=2;}
    void prepareToPlay(double r,int b)override{setRateAndBufferSizeDetails(r,b);}
    void releaseResources()override{probe.release_had_clock|=getPlayHead()!=nullptr;}
    void processBlock(AudioBuffer<float>& out,MidiBuffer&)override{
        if(auto* head=getPlayHead())if(auto p=head->getPosition()){
            if(p->getIsPlaying())++probe.playing;else ++probe.stopped;
            probe.bpm=p->getBpm().orFallback(0);probe.ppq=p->getPpqPosition().orFallback(0);
        }
        for(int c=0;c<out.getNumChannels();++c)FloatVectorOperations::fill(out.getWritePointer(c),gain->value*.1f,out.getNumSamples());
    }
    double getTailLengthSeconds()const override{return 0;}bool acceptsMidi()const override{return true;}bool producesMidi()const override{return false;}
    AudioProcessorEditor* createEditor()override{return nullptr;}bool hasEditor()const override{return false;}
    int getNumPrograms()override{return 1;}int getCurrentProgram()override{return 0;}
    void setCurrentProgram(int)override{gain->value=.375f;}
    const String getProgramName(int)override{return "Source program";}void changeProgramName(int,const String&)override{}
    void getStateInformation(MemoryBlock& out)override{out.replaceAll(&gain->value,sizeof(float));}
    void setStateInformation(const void* bytes,int n)override{if(n==int(sizeof(float)))std::memcpy(&gain->value,bytes,sizeof(float));}
};
class FixtureClock final:public AudioPlayHead {
public:PositionInfo p;Optional<PositionInfo> getPosition()const override{return p;}
};
int transport_check(){
    ScopedJuceInitialiser_GUI init;
    ClockProbe probe;String error;
    auto catalog=JSON::parse(R"({"engines":[{"name":"Clock fixture","folder":"fixture","sounds":[{"name":"Source program","program":0}]}]})");
    auto rack=rhythmer::make_sound_rack(catalog,0,[&](const std::string&,String&){return std::make_unique<ClockFixture>(probe);},44100,128,error);
    require(bool(rack),error.toRawUTF8());require(rhythmer::sound_rack_parameter_count(rack.get())==7,"Fixture parameter missing");
    auto* parameter=rack->getParameters()[6];require(std::abs(parameter->getDefaultValue()-.375f)<1e-6f,"Reset lost loaded source program value");
    parameter->setValue(.8f);MemoryBlock state;rack->getStateInformation(state);require(std::abs(parameter->getValue()-.8f)<1e-6f,"Fixture edit lost");
    require(std::abs(parameter->getDefaultValue()-.375f)<1e-6f,"Edit changed source default");
    FixtureClock clock;clock.p.setBpm(137.0);clock.p.setPpqPosition(3.5);clock.p.setIsPlaying(true);rack->setPlayHead(&clock);
    AudioBuffer<float> audio(2,128);MidiBuffer midi;rack->processBlock(audio,midi);
    require(probe.playing==1&&probe.bpm==137.0&&probe.ppq==3.5,"Child lost transport/time");
    clock.p.setIsPlaying(false);rack->processBlock(audio,midi);require(probe.stopped==1,"Child lost Stop");
    rack->setPlayHead(nullptr);rack.reset();require(!probe.release_had_clock,"Released child retained outer clock");
    std::cout<<"TRANSPORT source_default=ok edit_default=stable play_stop=ok bpm_ppq=ok clock_lifetime=ok"<<std::endl;return 0;
}
