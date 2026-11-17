# RHYTHMER OS 0.2.0 — verification scope

The foundation is Melodee Sample v0.3.0 by Kerem Kiliç (Ellic Studio), on the pinned sample-base revision. This document records the packaged build’s software checks. Publication and downloads are listed on the installation page. 

The acceptance receipt binds the runtime hash, integration patch, native-library hashes and source inputs. Packaging rejects a changed runtime or changed accepted input. The current catalogue contains 22 picker entries, 27 source views, 36 complete kits and 2,888 selections, including 43 separately identified authored selections. The excluded external Prophet Sequential and Elixir Erica/Hrtl banks remain excluded. No commercial break recordings are bundled.

Runtime validation covers the Linux ARM64 unit suite, audio self-test, original Acid/Break reference comparisons, real plug-in loading and preset restoration, and fresh-process workflow checks. The navigation matrix exercises 1,248 Basic/Full contexts; the track suite has 309 assertions. Plug-in checks map 1,510 sound-design controls and verify that front-page controls and EDIT share the same values. Kit checks cover pad ownership, gain, whole-kit filter and state round trips. Stems has a real four-output inference fixture; export checks cover MPC 3 tracks and copied source files.

Break checks cover source loading, dry and synchronised preview, 1–4-bar preparation, A/B replacement, cancellation, owner-track changes, GEN/performance round trips, Undo/Redo and project reload. The audio matrix has 384 deterministic cases. Acid keeps its generation algorithm, internal seed stream and two settings pages without seed UI. General GEN retains its separate visible seed and four-track groups.

Screen checks render 504 states at native and doubled resolution for each of eight fonts. Text fit is measured. The final checks also exercise random surface input and repeated fresh-process navigation/GEN/Break flows. Sanitizers cover the host wrapper and relevant standalone reference tests, not every native DSP library.

RHYTHMER's Menu maps SHIFT + encoder push to B1 BACK; plain push still selects. The engine filter controls remain on PRESETS and stay linked to EDIT. Separate DJ FILTER / ECHO / SPACE macros remain on PERFORM. Native pad lessons retain their expected TRIM/TUNE order without removing the normal filter-first SOUND page.

Install the full SD ZIP for all plug-ins, kits and presets. UPDATE contains the app only. Corresponding-source companions, licences, checksums and the signed autorun manifest accompany the installation.  

## Illustrated manual and empty-pad navigation

The English website manual is a single illustrated document with First Groove video/guide, essential controls, system structure and chapters. Legacy language/control/map URLs redirect to this document. First Groove uses Rhythmer Kit, FMini-1, FM-106, Acid Engine and Break Engine examples.

A short encoder push on a normal sampler track’s empty SOUND/TRIM pad opens its sample browser even when every pad is empty. SAMPLE SELECT and SAMPLE RECORD retain the upstream direct browser/input-recording paths. True EMPTY tracks retain type cards; TRACKS → TRACK SETUP changes an existing track’s type. Loaded pads, layered pads, other editor pages, held encoder MENU, recording and Freeze protections retain their existing behavior.

Focused verification: 311 track-workflow assertions, 1,248 navigation contexts / 9,538 assertions, audio self-test, native web-server tests and embedded-guide link checks. The earlier broad engine/audio and three regression receipts remain tied to their recorded runtimes; this UI/documentation revision does not change DSP or engine presets. 
