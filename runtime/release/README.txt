Rhythmer {version} for the Akai MPC Sample
==========================================

Rhythmer is a 16-track groovebox that runs on the MPC Sample in place of the
stock app: one track per pad, each a kit of samples, a VST3, LV2,
CLAP or VST2 instrument, or a MIDI track. Patterns, scenes and a song, a
looper, a mixer and effect chains that take plug-in effects.

Rhythmer changes nothing on the MPC itself, only files on the microSD card.
If it fails to start, or crashes, the stock MPC app comes back. Back up the
card before you install it.


Requirements
------------
- MPC Sample on firmware 1.3.0.12 exactly. On any other firmware Rhythmer
  does not start and the stock app keeps running.
- A microSD card for the MPC (the one you already use is fine).


Install
-------
1. Back up the card. If it already has a folder named "autorun" at its top
   level (MPC Sample Plugins uses one, for example), move it somewhere
   safe: Rhythmer's replaces it.
2. Unzip the release. It holds one folder, "autorun". Copy that folder to
   the top level of the card. Do not edit or rename anything inside it:
   the MPC refuses an autorun whose files changed.
3. Put the card in the MPC and switch it on. The stock app starts first;
   a few seconds later Rhythmer takes over the screen.

Projects are saved on the card in Rhythmer/Projects. Put samples in a
folder named "Samples" at the top level of the card.

Plug-ins: put VST3, LV2 and CLAP plug-ins built for 64-bit ARM Linux, VST2
plug-ins built for 64-bit or 32-bit ARM Linux, and Open MPC plug-ins, in
the folder "Rhythmer/Plugins" on the card (make a folder named "Plugins"
inside the "Rhythmer" folder). Earlier versions read a "Plugins" folder at
the top level of the card: move its contents into "Rhythmer/Plugins";
saved projects find them there. Or install a plug-in's zip without moving
the card: on http://melodee.local, Device, drop it on Plug-ins and press
Install. Rhythmer's own synths,
Melodee Poly, Melodee PD and Melodee Chip, are free downloads:
https://github.com/keremimo/mpc-vst-melodee-poly/releases/latest
https://github.com/keremimo/mpc-vst-melodee-pd/releases/latest
https://github.com/keremimo/mpc-vst-melodee-chip/releases/latest

New to Rhythmer? The quickstart, with pictures of each screen:
https://github.com/keremimo/melodee-sample/blob/main/docs/QUICKSTART.md
The user guide, with every page and control:
https://github.com/keremimo/melodee-sample/blob/main/docs/GUIDE.md


Update
------
1. Download the new release zip. Do not unzip it.
2. Copy the zip to the top level of the card (Project > SD card access,
   or a card reader). Or, with the MPC connected to a computer by USB-C
   and Rhythmer running, open http://melodee.local (or
   http://192.168.155.1), choose the zip under Update and press Send.
3. When Rhythmer asks "Update to <version>?", press B3 (INSTALL). Rhythmer
   saves the project, installs the new version on the card and restarts.
Only official, signed releases are offered. If the update fails, the card
is not changed. The previous version stays in autorun/rhythmer.prev.
Version v0.1.0 and earlier cannot update this way: install the next
version by hand, as described under Install.


Back to the stock app
---------------------
- Press Power briefly. On the Exit screen, press B3 (MPC APP): Rhythmer
  saves the project and the stock app runs until the next time the MPC is
  switched on.
- To stop Rhythmer starting at all, delete the "autorun" folder from the
  card (and put back any autorun folder you moved away).


Reporting problems
------------------
Say what you pressed, what you saw and the version (Settings, ABOUT,
press B3 for the credits, or the line below). After a crash, add the
report Rhythmer wrote to the card's "Rhythmer/Crashes" folder. If Rhythmer
did not start at all, check that the firmware is 1.3.0.12 and that the
autorun folder sits at the top level of the card.
Issues: https://github.com/keremimo/melodee-sample/issues


Version and source
------------------
Rhythmer {version}, source commit {commit}
Source code: {source}
Built on sample-base: https://github.com/keremimo/sample-base

Rhythmer is free software under the GNU Affero General Public License,
version 3 (licenses/LICENSE-AGPL-3.0.txt, in this folder). It uses JUCE
under the AGPLv3 and embeds the Rubik typeface under the SIL Open Font
License 1.1; see licenses/. Not affiliated with or endorsed by inMusic or
Akai Professional.
