// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Kerem Kilic (Ellic Studio)
#pragma once
#include <array>
#include <cstddef>
#include "rhythmer/ui/faces.h"

// The embedded variable font files (font_data.cpp): Rubik, the design's, and
// the faces Settings > SCREEN > Font offers. Every weight comes from a face's
// wght axis.
extern "C" const unsigned char rhythmer_rubik_start[], rhythmer_rubik_end[], rhythmer_intertight_start[], rhythmer_intertight_end[],
    rhythmer_atkinson_start[], rhythmer_atkinson_end[], rhythmer_spacegrotesk_start[], rhythmer_spacegrotesk_end[],
    rhythmer_plex_start[], rhythmer_plex_end[], rhythmer_manrope_start[], rhythmer_manrope_end[],
    rhythmer_pixel_start[], rhythmer_pixel_end[],
    rhythmer_vt323_start[], rhythmer_vt323_end[], rhythmer_pixelnarrow_start[], rhythmer_pixelnarrow_end[];

namespace rhythmer::ui {
struct FaceData { const unsigned char* start; const unsigned char* end; };
inline const std::array<FaceData, faces.size()> face_data {{
    {rhythmer_rubik_start, rhythmer_rubik_end},
    {rhythmer_intertight_start, rhythmer_intertight_end},
    {rhythmer_atkinson_start, rhythmer_atkinson_end},
    {rhythmer_spacegrotesk_start, rhythmer_spacegrotesk_end},
    {rhythmer_plex_start, rhythmer_plex_end},
    {rhythmer_manrope_start, rhythmer_manrope_end},
    {rhythmer_pixel_start, rhythmer_pixel_end},
    {rhythmer_vt323_start, rhythmer_vt323_end},
    {rhythmer_pixelnarrow_start, rhythmer_pixelnarrow_end},
}};
}
