// SPDX-License-Identifier: AGPL-3.0-only
static int kit_mix_check(const var& catalog,rhythmer::SoundLoader loader){
 String error;auto rack=rhythmer::make_sound_rack(catalog,-1,loader,44100,128,error);require(bool(rack),error.toRawUTF8());require(rack->getProgramName(0)=="K-WASUB / 909","Default kit order");unsigned pads=0;float maximum=0;
 for(int kit=0;kit<catalog["kits"].size();kit++){
  rack->setCurrentProgram(kit);MemoryBlock saved;rack->getStateInformation(saved);auto state=JSON::parse(String::fromUTF8((const char*)saved.getData(),int(saved.getSize())));require(std::abs(float(state["kit_mix_gain"])-float(catalog["kits"][kit]["mix_gain"]))<1e-4f,"Kit gain not saved");
  for(int pad=0;pad<16;pad++){
   AudioBuffer<float> out(2,128);MidiBuffer midi;midi.addEvent(MidiMessage::allSoundOff(1),0);out.clear();rack->processBlock(out,midi);midi.clear();midi.addEvent(MidiMessage::noteOn(1,36+pad,uint8(127)),0);double energy=0;
   for(int block=0;block<140;block++){out.clear();rack->processBlock(out,midi);midi.clear();for(int ch=0;ch<2;ch++)for(int f=0;f<128;f++){auto x=out.getSample(ch,f);require(std::isfinite(x),"Nonfinite kit output");maximum=std::max(maximum,std::abs(x));energy+=x*x;}}
   require(energy>1e-10,("Silent pad "+String(kit)+":"+String(pad)).toRawUTF8());pads++;
  }
  auto reopened=rhythmer::make_sound_rack(catalog,-1,loader,44100,128,error);require(bool(reopened),error.toRawUTF8());reopened->setStateInformation(saved.getData(),int(saved.getSize()));MemoryBlock restored;reopened->getStateInformation(restored);auto after=JSON::parse(String::fromUTF8((const char*)restored.getData(),int(restored.getSize())));require(state["kit_mix_gain"]==after["kit_mix_gain"],"Kit trim restore");require(state["kit_name"]==after["kit_name"],"Kit order restore");
  std::cout<<"KIT_MIX "<<kit<<" "<<rack->getProgramName(kit)<<" pads=16 state=PASS peak="<<maximum<<std::endl;
 }
 require(maximum<=.92001f,"Kit ceiling exceeded");std::cout<<"SAMPLE_KIT_MIX_PASS kits=36 pads="<<pads<<" peak="<<maximum<<" state=PASS"<<std::endl;return 0;
}
