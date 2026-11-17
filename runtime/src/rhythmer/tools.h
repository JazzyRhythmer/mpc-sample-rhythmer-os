// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Kerem Kilic (Ellic Studio)
#pragma once
#include <optional>

// Rhythmer's one-shot host tools, for build checks and design review. None
// opens the MPC's audio, display or control surface.
//   --rhythmer-preview DIR [PAGE...]  draws pages to DIR/<page>.png at 320 x 240
//                                    and DIR/<page>@2x.png at the boards' 640 x 480.
//                                    Pages: stage keys sounds edit soundmap mod touch mix steps roll
//                                    notesheet motion patterns song songzoom
//                                    songclip songshift length rack sends bus fxpick
//                                    pads samples trim chop levels record
//                                    project filesheet tempo arp chord capture
//                                    pad play envelope filter follow cloud shift exit
//                                    Fails when text is drawn under 11 px, wider than
//                                    its box, or a header's two sides meet.
//   --rhythmer-sound FILE.wav         plays the starting project for two bars and
//                                    checks it sounds and stays inside full scale
//   --self-test FILE.wav             the same check, under the name device.py and
//                                    the SD boot run before leaving the stock app
//   --rhythmer-boot DIR               draws the boot animation to DIR/boot-NNN.png, 30 a second
//   --rhythmer-bench ROUNDS [PAGE...] times drawing each page, ROUNDS draws apiece
//   --rhythmer-dsp-bench [KEY=VALUE...] a busy project rendered a block a period at real-time priority, with
//                                    the render workers: block times and CPU (src/rhythmer/dsp_bench.cpp)
//   --rhythmer-print-spike MODE [KEY=VALUE...] freeze plan F0: a track rendered by a second engine host
//                                    (equal, speed, plugin, stream; src/rhythmer/print_spike.cpp)
//   --mpc-import FILE.xpj|.xpm|.xty  reads an MPC Sample project or an MPC program and prints what came across
//   --mpc-install FILE.xpn DIR       installs an MPC expansion into DIR/<its title>
//   --instrument-read FILE           reads an .sfz, .xpm, .xty or .exs as the sample library does
//   --mpc-track PROGRAM.xpm FILE.xty writes MPC 3's track file of a keygroup program in "<name>_[TrackData]" beside it
//                                    and prints its zones, their samples found
//   --rhythmer-monkey [SEED COUNT MOVES]  random presses, holds and releases of every control
//                                    (src/rhythmer/monkey.cpp); fails when a layer, a note, a
//                                    held step or pattern outlives the hand that held it
// Returns the exit code, or nothing when argv names neither.
namespace rhythmer {
std::optional<int> run_tool(int argc, char** argv);
int monkey(unsigned first, unsigned seeds, unsigned moves); // --rhythmer-monkey: seeds first.., the failures' moves printed
int dsp_bench(int argc, char** argv); // --rhythmer-dsp-bench
int print_spike(int argc, char** argv); // --rhythmer-print-spike
}
