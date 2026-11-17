// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 jazzy rhythmer
#include "rhythmer/shell/tempo_display.h"
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <initializer_list>
using rhythmer::TempoDisplay;
unsigned checks=0;
void check(bool ok,const char* what){++checks;if(!ok){std::fprintf(stderr,"FAIL %s\n",what);std::exit(1);}}
int main(){
 TempoDisplay d;check(d.sample(1200,0,false)==0,"internal tempo bypass");check(d.sample(1275,1,true)==1275,"true fractional acquisition");
 unsigned changes=0,last=1200;d.sample(1200,2,false);d.sample(1200,10,true);
 for(unsigned t=26;t<10010;t+=16){unsigned out=d.sample((t/96)%3==0?1199:(t/96)%3==1?1200:1201,t,true);if(out!=last)++changes;last=out;}
 check(changes==0,"plus/minus 0.1 BPM jitter does not flash");
 for(unsigned initial:{1200u,1201u}){TempoDisplay edge;edge.sample(initial,0,true);unsigned flips=0,before=initial;
  for(unsigned t=16;t<6000;t+=16){unsigned value=edge.sample(1200+(t/16)%2,t,true);flips+=value!=before;before=value;}
  check(flips==0,"rounding-boundary jitter stays stable from either initial digit");}

 for(unsigned initial:{1199u,1201u}){TempoDisplay integer;unsigned value=integer.sample(initial,0,true);
  for(unsigned t=16;t<10000;t+=16)value=integer.sample(1199+(t/64)%3,t,true);
  check(value==1200,"noisy whole BPM settles to integer even after fractional acquisition");}
 for(unsigned t=10026;t<14010;t+=16)d.sample(1201,t,true);
 check(d.sample(1201,14020,true)==1201,"sustained 0.1 BPM change remains representable");
 unsigned previous=1201,last_change=14020,max_changes=0;
 for(unsigned t=14036;t<18020;t+=16){unsigned value=d.sample(1400,t,true);if(value!=previous){if(max_changes)check(t-last_change>=250,"display changes no faster than 4 Hz");last_change=t;++max_changes;previous=value;}}
 check(previous>=1399,"real large tempo change converges");check(max_changes>0,"real change is not frozen");
 check(d.sample(900,18021,false)==0,"external off returns immediate raw-display fallback");check(d.sample(900,18022,true)==900,"reacquisition resets old average");
 check(d.sample(1275,18023,true,1)==1275,"port switch resets display state");check(d.sample(1500,22024,true,1)==1500,"screen hiatus resets stale display");
 check(d.sample(0,22025,true,1)==0,"no measurement clears display filter");
 TempoDisplay a,b;for(unsigned t=0;t<=2000;t+=10)a.sample(t?1280:1200,t,true);for(unsigned t=0;t<=2000;t+=50)b.sample(t?1280:1200,t,true);
 check(std::abs(int(a.sample(1280,2010,true))-int(b.sample(1280,2010,true)))<=2,"smoothing is time based across frame rates");
 TempoDisplay wrap;wrap.sample(1200,0xfffffff0u,true);check(wrap.sample(1200,16,true)==1200,"millisecond counter wrap safe");
 check(wrap.sample(300,100,false)==0&&wrap.sample(300,101,true)==300,"minimum tempo acquired");check(wrap.sample(3000,102,true,1)==3000,"maximum tempo acquired");
 std::printf("TEMPO_DISPLAY passed %u checks; jitter_changes=%u large_change_updates=%u\n",checks,changes,max_changes);
}
