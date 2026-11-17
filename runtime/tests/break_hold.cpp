// SPDX-License-Identifier: GPL-3.0-only
#include "rhythmer/engine/break_manipulator.h"
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
using rhythmer::BreakManipulator;
static void check(bool yes,const char* what){if(!yes){std::fprintf(stderr,"BREAK_HOLD_FAIL %s\n",what);std::exit(1);}}
static double render(BreakManipulator& m,unsigned blocks=1){double e=0;for(unsigned b=0;b<blocks;b++){float l[128]{},r[128]{};m.render(l,r,128,44100);for(unsigned n=0;n<128;n++){check(std::isfinite(l[n])&&l[n]==r[n],"finite stereo");e+=l[n]*l[n];}}return e;}
int main(){
 rhythmer::SampleData loop;loop.frames=176400;loop.left.resize(loop.frames);loop.right.resize(loop.frames);for(unsigned n=0;n<loop.frames;n++)loop.left[n]=loop.right[n]=.25f*std::sin(n*.037f);
 auto setup=[&](BreakManipulator&m){m.configure(2,0);m.sources(&loop,&loop);m.transport(true,0);m.note(36,100);render(m);};
 for(unsigned fx=0;fx<16;fx++){
  BreakManipulator a,b;setup(a);setup(b);a.live_note(fx,25);b.live_note(fx,127);render(a,100);render(b,100);
  double energy=0;
  for(unsigned block=0;block<1200;block++){
   if(block%23==0){a.note(36+(block/23)%16,25+(block%100));a.off(36+(block/23+15)%16);}
   // A sequenced instance of the very same command must not release the hand.
   if(block%41==0){a.note(fx,45);a.off(fx);}
   float al[128]{},ar[128]{},bl[128]{},br[128]{};a.render(al,ar,128,44100);b.render(bl,br,128,44100);
   for(unsigned n=0;n<128;n++){check(std::isfinite(al[n]),"FX output finite");energy+=al[n]*al[n];if(fx!=2)check(std::fabs(al[n]-bl[n])<.00001f,"held FX/gain survives chopped/recorded notes");}
   if(fx==2)check(a.activity()&4,"STRETCH stays held through chop/command off");
  }
  check(energy>.000001,"each held performance effect has audio");a.live_off(fx);a.release();render(a,4);check(!(a.activity()&6),"release clears live activity");
 }
 // Recorded FX velocity likewise must not become a second master gain.
 for(unsigned fx=0;fx<16;fx++){
  BreakManipulator a,b;setup(a);setup(b);a.note(fx,25);b.note(fx,127);
  for(unsigned block=0;block<200;block++){
   float al[128]{},ar[128]{},bl[128]{},br[128]{};a.render(al,ar,128,44100);b.render(bl,br,128,44100);
   for(unsigned n=0;n<128;n++)check(std::fabs(al[n]-bl[n])<.00001f,"recorded FX velocity leaves source level unchanged");
  }
 }
 // Recorded holds themselves also survive incoming chop notes.
 {BreakManipulator m;setup(m);m.note(2,100);render(m);for(unsigned n=0;n<300;n++){m.note(36+n%16,100);m.off(36+(n+15)%16);render(m);check(m.activity()&4,"recorded STRETCH survives chops");}m.off(2);m.release();render(m);check(!(m.activity()&4),"recorded release");}
 // Last held live command wins, and releasing it returns to the previous hold.
 {BreakManipulator m;setup(m);m.live_note(2,110);render(m,100);m.live_note(0,100);render(m,100);m.live_off(0);render(m,100);check(m.activity()&4,"fallback to still-held STRETCH");m.live_off(2);m.release();render(m);check(!(m.activity()&6),"no stuck overlap");}
 // Repeated downs are idempotent; one physical up is sufficient.
 {BreakManipulator m;setup(m);for(unsigned n=0;n<300;n++)m.live_note(2,100);m.live_off(2);m.release();render(m);check(!(m.activity()&6),"duplicate down has no unbalanced gate");}
 std::puts("BREAK_HOLD_PASS effects=16 command_pressure=level_neutral live_vs_sequence=isolated chops_do_not_cancel=ok overlap=ok duplicate_down=ok release=ok");
}
