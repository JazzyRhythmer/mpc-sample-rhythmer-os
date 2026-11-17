#!/usr/bin/env python3
"""Verify the pinned foundation and its downstream source coverage, not hardware operation."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
from rename_runtime import rename_text

ROOT = Path(__file__).resolve().parents[1]
WORK = Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
FEATURES = {
    'audio_tracks': ['model/audio_track.h', 'engine/audio_player.cpp', 'shell/audio_tracks.cpp', 'shell/audio_jobs.cpp'],
    'keygroup_tracks_and_migration': ['model/keygroup_track.h', 'model/project_file.cpp', 'engine/keygroup.cpp', 'shell/mpc_project.cpp'],
    'auto_sampler': ['shell/auto_sample.cpp', 'engine/auto_probe.cpp', 'shell/print_engine.cpp', 'pages/auto_sample_page.cpp'],
    'stems': ['shell/stems.cpp', 'shell/sample_library_stems.cpp', 'shell/stems_jobs.cpp', 'pages/stems_page.cpp'],
    'streaming_and_native_rate': ['engine/sample_data.cpp', 'engine/stream_pager.cpp', 'shell/sample_decode.cpp', 'shell/sample_library.cpp', 'shell/stream_holds.h'],
    'long_recordings': ['shell/sample_record.cpp', 'shell/looper_files.cpp', 'shell/capture_jobs.cpp'],
    'mpc3_import_export': ['shell/mpc3_export.cpp', 'shell/mpc_project.cpp', 'shell/mpc_wav_slices.cpp', 'shell/mpc3_template.json'],
    'chords_and_eight_notes': ['model/progression.h', 'shell/progression_jobs.cpp', 'shell/progression_file.cpp', 'pages/keys_page.cpp', 'model/pattern.h'],
    'sequences_and_capture': ['shell/seq_layer.cpp', 'shell/scene_jobs.cpp', 'pages/scenes_page.cpp', 'pages/patterns_page.cpp'],
    'motion_mod_macro': ['shell/mod_jobs.cpp', 'pages/mod_page.cpp', 'pages/motion_page.cpp'],
    'autosave_and_save_as': ['shell/project_jobs.cpp', 'shell/project_store.cpp', 'pages/project_page.cpp'],
    'first_project_and_type_chooser': ['shell/project_kits.cpp', 'shell/new_track.cpp', 'shell/new_track.h', 'pages/stage_page.cpp'],
    'pad_bank_and_mix_controls': ['shell/pad_bank.cpp', 'shell/bindings.cpp', 'shell/erase_copy.cpp'],
    'menu_and_lessons': ['shell/menu.cpp', 'shell/menu.h', 'shell/lesson.h', 'shell/lesson_jobs.cpp', 'pages/menu_sheet.cpp'],
    'basic_full': ['shell/features.h', 'shell/settings.h', 'pages/settings_page.cpp'],
    'dialogs_and_browsers': ['shell/delete_jobs.cpp', 'shell/ask.cpp', 'shell/plugin_jobs.cpp', 'pages/samples_page.cpp', 'pages/plugins_page.cpp'],
    'screen_and_fonts': ['ui/palettes.h', 'ui/font_data.cpp', 'ui/chrome.cpp', 'shell/settings.h'],
    'card_warm_and_load_pool': ['shell/card_warm.cpp', 'shell/load_pool.cpp', 'shell/sample_library_instruments.cpp'],
    'master_and_performance_fixes': ['engine/master_comp.cpp', 'engine/sampler.cpp', 'shell/note_repeat.cpp', 'shell/shell.cpp'],
    'usb_web_mirror_update': ['web/web_app.cpp', 'web/card_files.cpp', 'shell/update.cpp', '@base/drivers/screen_mirror.cpp'],
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(runtime, output):
    if not os.path.ismount('/Volumes/SSD'):
        raise RuntimeError('SSD absent')
    if not output.resolve().is_relative_to(Path('/Volumes/SSD/Development')):
        raise RuntimeError('QA output must stay under SSD Development')
    lock = json.loads((ROOT/'config/upstream-integration.lock.json').read_text())
    vendor = ROOT/'vendor/rhythmer'
    head = subprocess.check_output(['git', '-C', str(vendor), 'rev-parse', 'HEAD'], text=True).strip()
    assert lock['upstream'] == 'v0.3.0' and head == lock['commit']
    assert sha(ROOT/lock['patch']) == lock['patch_sha256']
    for rel, expected in lock['inputs'].items():
        assert sha(ROOT/rel) == expected, 'Changed integration input: '+rel
    rows = []
    for feature, paths in FEATURES.items():
        files = []
        for rel in paths:
            if rel.startswith('@base/'):
                original = vendor/'base/src'/rel[6:]
                actual = runtime/'base/src'/rel[6:]
                expected = original.read_text()
            else:
                original = vendor/'src/melodee'/rel
                actual = runtime/'src/rhythmer'/rel
                expected = rename_text(original.read_text())
            assert actual.is_file(), 'Missing integration source: '+rel
            files.append(dict(path=rel, sha256=sha(actual), renamed_upstream_equal=actual.read_text()==expected))
        rows.append(dict(feature=feature, files=files, status='SOURCE_COVERED', hardware_verified=False))
    missing = []
    reviewed = 0
    for folder in ('src', 'tests', 'tools'):
        for original in (vendor/folder).rglob('*'):
            if not original.is_file() or '__pycache__' in original.parts:
                continue
            rel = str(original.relative_to(vendor)).replace('melodee','rhythmer').replace('Melodee','Rhythmer').replace('MELODEE','RHYTHMER')
            reviewed += 1
            if not (runtime/rel).is_file():
                missing.append(rel)
    assert not missing, 'Missing pinned upstream files: '+str(missing)
    result = dict(upstream=lock['upstream'], commit=head, reviewed_upstream_files=reviewed,
                  missing_files=missing, feature_paths=rows, patch_sha256=lock['patch_sha256'],
                  hardware_validated=False,
                  customizations=['engine filter PRESETS and separate PERFORM', 'Rhythmer Kit',
                                  'four-track GEN and engine-scoped Acid/Break', 'TRACK SETUP and empty-pad entry',
                                  'User Sound/Kit tools', 'Menu Shift+Push Back', 'monochrome default and custom artwork'])
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(f'Upstream {lock["upstream"]}: {len(rows)} feature groups, {reviewed} source files, no missing files')
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime', type=Path, default=WORK/'runtime')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    audit(args.runtime, args.output)
