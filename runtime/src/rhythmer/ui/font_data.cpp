// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Kerem Kilic (Ellic Studio)
// Rubik and the faces Settings > SCREEN > Font offers (each SIL Open Font
// License 1.1, by its own authors, except Rhythmer Pixel, Rhythmer's own,
// drawn into build/deps by tools/gen_pixel_font.py), embedded so the binary carries them to the MPC and
// to host previews. src/rhythmer/dependencies.py fetches the pinned files; the
// assembler reads them from the build folder (make runs at the repository root).
#include "rhythmer/ui/font_data.h"

asm(R"(
    .section .rodata
    .balign 16
    .global rhythmer_rubik_start
rhythmer_rubik_start:
    .incbin "build/deps/rubik/Rubik-VF.ttf"
    .global rhythmer_rubik_end
rhythmer_rubik_end:
    .balign 16
    .global rhythmer_intertight_start
rhythmer_intertight_start:
    .incbin "build/deps/fonts/intertight/face.ttf"
    .global rhythmer_intertight_end
rhythmer_intertight_end:
    .balign 16
    .global rhythmer_atkinson_start
rhythmer_atkinson_start:
    .incbin "build/deps/fonts/atkinsonhyperlegiblenext/face.ttf"
    .global rhythmer_atkinson_end
rhythmer_atkinson_end:
    .balign 16
    .global rhythmer_spacegrotesk_start
rhythmer_spacegrotesk_start:
    .incbin "build/deps/fonts/spacegrotesk/face.ttf"
    .global rhythmer_spacegrotesk_end
rhythmer_spacegrotesk_end:
    .balign 16
    .global rhythmer_plex_start
rhythmer_plex_start:
    .incbin "build/deps/fonts/ibmplexsans/face.ttf"
    .global rhythmer_plex_end
rhythmer_plex_end:
    .balign 16
    .global rhythmer_manrope_start
rhythmer_manrope_start:
    .incbin "build/deps/fonts/manrope/face.ttf"
    .global rhythmer_manrope_end
rhythmer_manrope_end:
    .balign 16
    .global rhythmer_pixel_start
rhythmer_pixel_start:
    .incbin "build/deps/fonts/rhythmerpixel/RhythmerPixel.ttf"
    .global rhythmer_pixel_end
rhythmer_pixel_end:
    .balign 16
    .global rhythmer_vt323_start
rhythmer_vt323_start:
    .incbin "build/deps/fonts/vt323/face.ttf"
    .global rhythmer_vt323_end
rhythmer_vt323_end:
    .balign 16
    .global rhythmer_pixelnarrow_start
rhythmer_pixelnarrow_start:
    .incbin "build/deps/fonts/rhythmerpixel/RhythmerPixelNarrow.ttf"
    .global rhythmer_pixelnarrow_end
rhythmer_pixelnarrow_end:
    .previous
)");
