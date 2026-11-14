// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Kerem Kilic (Ellic Studio)
#pragma once
#include "rhythmer/model/smf.h"
#include "rhythmer/shell/context.h"
#include <string>

// Roadmap P4: Standard MIDI Files on the card (model/smf.h).
namespace rhythmer {

// Song's Export, MIDI file (the wheel on the sheet): Rhythmer/MIDI/<name>.mid on the card.
void export_midi(Context& c, const std::string& name);
// The browser, Push on a .mid: every note of it onto the selected track's pattern playing (one undo), as long as the
// notes (whole bars, 128 at most); a kit takes notes 36 on as its pads.
void import_midi(Context& c, const std::string& path);
} // namespace rhythmer
