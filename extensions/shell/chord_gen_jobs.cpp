// SPDX-License-Identifier: GPL-3.0-only
#include "rhythmer/shell/context.h"
#include "rhythmer/engine/engine_host.h"
#include "rhythmer/model/chord_gen_access.h"
#include "rhythmer/model/scales.h"
#include "rhythmer/shell/track_copy.h"
namespace rhythmer {
Gen8Voice gen_track_voice(Context&,unsigned);
void Context::chord_gen_action(bool mutate){
 if(!chord_gen_available(project,ui.track)){notice("CHORD GEN: select an instrument");return;}
 if(host_recording()){notice("Stop recording before CHORD GEN");return;}
 if(host.song_playing()){notice("Stop song before CHORD GEN");return;}
 if(frozen_edit(ui.track))return;
 close_gesture();Edit edit;edit.what=mutate?"Mutate chords":"Generate chords";
 edit.tracks_before.push_back({ui.track,track_state(*this,ui.track)});
 auto& settings=track().chord_gen;settings.seed=settings.seed*1664525u+1013904223u;if(!mutate)settings.harmony=settings.seed;
 auto voice=gen_track_voice(*this,ui.track);
 // One selected drum sound can be transposed, but a monophonic engine gets
 // successive chord tones rather than an inaudible simultaneous stack.
 unsigned root=settings.local?settings.root:project.root,scale=settings.local?settings.scale:project.scale;
 pattern()=generate_chords(pattern(),settings,voice,root,scale,project.bar_ticks(),mutate);
 sync_pattern(ui.track,track().pattern);dirty=true;
 edit.tracks_after.push_back({ui.track,track_state(*this,ui.track)});edits.push(std::move(edit));
 notice(std::string(voice.mono?"CHORD ARP / ":"CHORDS / ")+std::to_string(settings.bars)+" BARS / UNDO");
}
}
