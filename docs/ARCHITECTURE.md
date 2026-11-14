# Architecture

The application uses sample-base for audio, display, hardware input, card access, startup and recovery. The project model owns sixteen tracks and their patterns; the shell submits edits to the existing engine host.

Sampler and plugin tracks retain their original playback paths. VST2/VST3 hosting and the armv7 bridge are upstream components. Plugins retain original IDs, parameters and state. Optional drum-map.json supplies missing note metadata outside the audio callback.

GEN8 and Break generation are model functions over native patterns. The shell commits generated notes through existing edit/history and pattern synchronization APIs. Generation, allocation and project serialization run outside the audio callback.

The display uses existing 320×240 layouts. Theme tokens, original boot artwork, pixel numeric glyphs and segmented gauges provide the monochrome skin.

See GEN8_BREAK.md, OPEN_MPC_COMPATIBILITY.md and SOURCE_LOCK.json for interfaces and provenance.
