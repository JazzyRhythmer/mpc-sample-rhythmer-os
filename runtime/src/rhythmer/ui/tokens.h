// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Kerem Kilic (Ellic Studio)
#pragma once
#include <juce_graphics/juce_graphics.h>
#include "rhythmer/ui/shades.h"
#include <array>
#include <cstdint>

// Rhythmer's design tokens at device size (the boards are drawn at 2x: halve
// them). RHYTHMER monochrome palette, numbered tracks, and the four fixed zones of
// every screen.
namespace rhythmer::ui {

inline juce::Colour hex(uint32_t rgb, float alpha = 1) { return juce::Colour(0xff000000u | rgb).withAlpha(alpha); }

namespace colour {
inline const juce::Colour bg = hex(0x000000), panel = hex(0x101010), surf = hex(0x171717), raised = hex(0x262626),
    quiet = hex(0x0A0A0A), line = hex(0x383838), text = hex(0xFFFFFF), sec = hex(0xE0E0E0), mid = hex(0xB8B8B8),
    dim = hex(0x888888), rec = hex(0xFFFFFF), amber = hex(0xD0D0D0), play = hex(0xFFFFFF);

inline const juce::Colour ice = hex(0xD8D8D8);
}

// Track colours 1-16 with their knob shades, and the Looper's L1-L4: ui/shades.h (the pads use them too).
inline juce::Colour track_colour(unsigned /*track*/) { return colour::text; }
inline juce::Colour knob_shade(unsigned /*track*/, unsigned /*knob*/) { return colour::text; }
inline juce::Colour loop_colour(unsigned /*loop*/) { return colour::text; }
inline juce::Colour loop_shade(unsigned /*loop*/, unsigned /*knob*/) { return colour::text; }

// Zones, top to bottom, at device size.
namespace zone {
constexpr int width = 320, height = 240, pad = 6;
constexpr int soft_y = 0, soft_h = 22;
constexpr int header_y = 22, header_h = 22;
constexpr int picture_y = 44, picture_h = 144;
constexpr int knobs_y = 188, knobs_h = 52;
}

// Type sizes in device pixels. Readable at arm's length on the 320 x 240
// panel: nothing is drawn under `floor`, and Paint::fit never shrinks below
// it. Where a page runs out of room it shows fewer things at a time instead.
namespace type {
constexpr float floor = 11;
constexpr float caps = 11, soft = 11, small = 11, body = 13, value = 22, title = 20, list = 15, bpm = 15;
constexpr float caps_tracking = 0.06f; // letter spacing of capitals, in em
}

// How strongly something sits behind an overlay: CSS opacity .35 over BG.
constexpr float behind_overlay = 0.65f;

} // namespace rhythmer::ui
