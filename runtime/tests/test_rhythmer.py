# SPDX-License-Identifier: AGPL-3.0-only
"""Rhythmer's model, engine host, sequencer and mixer, built for the host."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ["src/rhythmer/engine/engine_info.cpp", "src/rhythmer/engine/engine_host.cpp", "src/rhythmer/engine/looper.cpp",
           "src/rhythmer/shell/bindings.cpp", "src/rhythmer/shell/loop_sheet.cpp", "src/rhythmer/engine/effects.cpp", "src/rhythmer/engine/effects_extra.cpp", "src/rhythmer/engine/master_comp.cpp", "src/rhythmer/engine/effect_info.cpp", "src/rhythmer/engine/macros.cpp",
           "src/rhythmer/engine/sampler.cpp", "src/rhythmer/engine/break_manipulator.cpp", "src/rhythmer/engine/sample_data.cpp", "src/rhythmer/engine/onsets.cpp", "src/rhythmer/engine/sfz.cpp", "src/rhythmer/engine/keygroup.cpp", "src/rhythmer/engine/exs.cpp", "src/rhythmer/engine/sf2.cpp", "src/rhythmer/engine/dspreset.cpp", "src/rhythmer/engine/stream_pager.cpp", "src/rhythmer/engine/render_pool.cpp", "src/rhythmer/shell/sample_cache.cpp",
           "src/rhythmer/model/project_file.cpp", "src/rhythmer/model/pattern.cpp", "src/rhythmer/model/note_edits.cpp", "src/rhythmer/model/smf.cpp", "src/rhythmer/model/generators.cpp", "src/rhythmer/engine/punch.cpp", "src/rhythmer/engine/print_render.cpp", "src/rhythmer/engine/print_player.cpp", "src/rhythmer/engine/audio_player.cpp", "src/rhythmer/model/print.cpp", "src/rhythmer/engine/punch_mpc.cpp", "src/rhythmer/engine/pad_fx_info.cpp", "src/rhythmer/model/sound_file.cpp",
           "src/rhythmer/shell/page_stack.cpp", "src/rhythmer/shell/button_jobs.cpp", "src/rhythmer/shell/roll.cpp",
           "src/rhythmer/shell/shift_pad_jobs.cpp", "src/rhythmer/shell/fader_job.cpp", "src/rhythmer/shell/midi_route.cpp", "src/rhythmer/shell/mtc_in.cpp",
           "src/rhythmer/shell/undo_scope.cpp", "src/rhythmer/shell/project_kits.cpp", "src/rhythmer/shell/card_access.cpp",
           "src/rhythmer/shell/pad_lights.cpp", "src/rhythmer/plugin/nam.cpp", "src/rhythmer/shell/xpm_write.cpp", "src/rhythmer/engine/loop_find.cpp",
           "src/rhythmer/engine/auto_probe.cpp", "src/rhythmer/engine/release_fit.cpp", "src/rhythmer/engine/external_notes.cpp"]


class RhythmerTests(unittest.TestCase):
    def test_layouts_bindings_engine_and_sequencer(self):
        with tempfile.TemporaryDirectory() as temp:
            binary = Path(temp) / "rhythmer"
            subprocess.run([os.environ.get("CXX", "c++"), "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
                            "-I" + str(ROOT / "src"), "-I" + str(ROOT / "base/src"), str(ROOT / "tests/rhythmer.cpp"),
                            *[str(ROOT / s) for s in SOURCES], "-o", str(binary)], check=True)
            result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("rhythmer ok", result.stdout)


if __name__ == "__main__":
    unittest.main()
