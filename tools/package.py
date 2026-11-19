#!/usr/bin/env python3
"""Assemble a local development SD zip using Melodee's existing boot/recovery.

No device access, firmware patching, installation, or public upload occurs.
"""
import hashlib
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess as sp
import xml.etree.ElementTree as ET
import zipfile
from privacy import verify
from engine_inventory import validate as accepted_engines

ROOT = Path(__file__).resolve().parents[1]
WORK = Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
CACHE = Path('/Volumes/SSD/Development/Caches/rhythmer-os/downloads')
OUTPUT = Path('/Volumes/SSD/Development/Archives/rhythmer-os')
VERSION = (ROOT / 'VERSION').read_text().strip()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def assemble(stage_only=False):
    if not os.path.ismount('/Volumes/SSD'):
        raise SystemExit('SSD is not mounted')
    from check_release_selection import check
    check()
    from check_preset_coverage import check as check_original_banks
    check_original_banks()
    from check_public_banks import check as check_public_banks
    check_public_banks()
    app = WORK / 'runtime'
    for name in ('boot_logo.cpp', 'boot_backdrop.cpp'):
        data = (app / 'src/rhythmer/ui' / name).read_text()
        if 'CC0-1.0' not in data or 'Rhythmer OS original' not in data:
            raise SystemExit('Replace reserved upstream boot assets before packaging')
    spec = importlib.util.spec_from_file_location('upstream_release', app / 'tools/make_release.py')
    release = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(release)
    commit = sp.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    stamp=app / 'build/rhythmer.release.source-sha256'
    if not stamp.is_file() or stamp.read_text().split()[0] != digest((app/'build/rhythmer').read_bytes()):
        raise SystemExit('Run tools/build.py custom: release binary must come from the current tested build')
    sound_receipt=json.loads((ROOT/'config/sound-host.lock.json').read_text())
    if sound_receipt['version']!=VERSION or sound_receipt['runtime_sha256']!=digest((app/'build/rhythmer').read_bytes()):
        raise RuntimeError('Sound host acceptance does not match this runtime')
    for name,expected in sound_receipt['files'].items():
        if digest((ROOT/name).read_bytes())!=expected:raise RuntimeError('Sound host changed after acceptance: '+name)
    files = release.collect(app / 'build/rhythmer.release', 'v'+VERSION, commit)
    # Product guide names our developer and correctly scopes this local build;
    # upstream's unmodified-release issue/source wording is not ours.
    files[release.PACKAGE + '/README.txt'] = (ROOT / 'docs/INSTALL_020_EN.md').read_bytes()
    files['README.txt'] = (ROOT / 'docs/INSTALL_020_EN.md').read_bytes()
    downloads = json.loads((ROOT / 'config/releases.lock.json').read_text())
    for item in downloads:
        if item['repo'] == 'keremimo/melodee-sample':
            continue  # this binary was rebuilt with our own boot art
        archive = CACHE / item['asset']
        if digest(archive.read_bytes()) != item['sha256']:
            raise RuntimeError('Download checksum mismatch: ' + item['asset'])
        with zipfile.ZipFile(archive) as z:
            metas = [n for n in z.namelist() if n.endswith('/plugin-meta.xml')]
            if len(metas) != 1:
                raise RuntimeError('Ambiguous portable plugin folder')
            prefix = metas[0].rsplit('/', 1)[0] + '/'
            folder = Path(prefix.rstrip('/')).name
            for name in z.namelist():
                if not name.startswith(prefix) or name.endswith('/'):
                    continue
                rel = Path(name[len(prefix):])
                if rel.is_absolute() or '..' in rel.parts:
                    raise RuntimeError('Unsafe archive entry')
                files['Plugins/' + folder + '/' + rel.as_posix()] = z.read(name)
        # Upstream plugin zips omit licence texts: supply them explicitly.
        if item['repo'] == 'sd88me/mpc-vst-TR-MPC':
            files['Plugins/' + folder + '/LICENSE-GPL-3.0.txt'] = (
                ROOT / 'LICENSES/TR-MPC-GPL-3.0.txt').read_bytes()
            if item['asset'].startswith('TR-MPC-'):
                files['Plugins/' + folder + '/drum-map.json'] = (ROOT / 'config/tr-mpc-drum-map.json').read_bytes()
            else:
                classic = json.loads((ROOT / 'config/classic-drum-maps.json').read_text())
                name = item['asset'].split('-1.3.1-')[0]
                files['Plugins/' + folder + '/drum-map.json'] = (json.dumps(classic[name], indent=2) + '\n').encode()
        else:
            files['Plugins/' + folder + '/LICENSE-AGPL-3.0.txt'] = (ROOT / 'vendor/rhythmer/LICENSE').read_bytes()
        files['Plugins/' + folder + '/Open-MPC-MIT-LICENSE.txt'] = (ROOT / 'vendor/mpc-vst-plugins/LICENSE').read_bytes()
        files['Plugins/' + folder + '/SOURCE.json'] = (json.dumps(item, indent=2) + '\n').encode()
    for short in ('sophie',):
        port = ROOT / 'ports' / short
        cfg = json.loads((port / 'vst.json').read_text())
        prefix = 'Plugins/' + cfg['vendor'] + ' - VST - ' + cfg['name'] + '/'
        built = WORK / 'plugins/ports' / short / 'build'
        files[prefix + cfg['so']] = (built / cfg['so']).read_bytes()
        xml = ET.fromstring((built / 'pluginlist-entry.xml').read_text())
        xml.set('file', '%payload-path%/' + prefix.removeprefix('Plugins/') + cfg['so'])
        files[prefix + 'plugin-meta.xml'] = ET.tostring(xml, encoding='utf-8')
        for name in ('LICENSE', 'NOTICE', 'VENDORED.md'):
            if (port / name).is_file():
                files[prefix + name] = (port / name).read_bytes()
        files[prefix + 'Open-MPC-MIT-LICENSE.txt'] = (ROOT / 'vendor/mpc-vst-plugins/LICENSE').read_bytes()
    native=accepted_engines()
    for item in native:
        folder=WORK/'move-stage/Plugins'/item['folder']
        for p in folder.rglob('*'):
            if p.is_file():files['Plugins/'+item['folder']+'/'+p.relative_to(folder).as_posix()]=p.read_bytes()
    for p in (WORK/'sample-stage').rglob('*'):
        if p.is_file():files[p.relative_to(WORK/'sample-stage').as_posix()]=p.read_bytes()
    catalog=(ROOT/'config/sound-catalog.json').read_bytes()
    files['Plugins/RHYTHMER - Rhythmer Kit/rhythmer-kit.json']=catalog
    for engine in json.loads(catalog)['engines']:
        files['Plugins/'+engine['folder']+'/rhythmer-source-name.json']=(json.dumps({'name':engine['name']})+'\n').encode()
        if engine.get('kit_only'):files['Plugins/'+engine['folder']+'/rhythmer-kit-only.json']=b'{"kit_only":true}\n'
    files['Plugins/RHYTHMER - Break Engine/rhythmer-break.json']=(ROOT/'config/break-engine.json').read_bytes()
    files['Plugins/RHYTHMER - Acid Engine/rhythmer-acid.json']=b'{"name":"Acid Engine","source":"Hortator ACID / Aphex"}\n'
    support_receipt=json.loads((WORK/'support-source-export.json').read_text())
    support_archive=OUTPUT/support_receipt['file']
    if not support_archive.is_file() or digest(support_archive.read_bytes())!=support_receipt['sha256']:raise RuntimeError('Corresponding support-library source is missing or changed')
    source_receipt=json.loads((WORK/'move-source-export.json').read_text())
    source_archive=OUTPUT/source_receipt['file']
    if not source_archive.is_file() or digest(source_archive.read_bytes())!=source_receipt['sha256']:
        raise RuntimeError('Corresponding Move source ZIP is missing or changed')
    upstream=json.loads((ROOT/'config/upstream-integration.lock.json').read_text())
    status = {
        'product': 'Rhythmer OS', 'version': VERSION, 'source_commit': commit,
        'runtime_sha256': digest((app/'build/rhythmer').read_bytes()),
        'release_binary_sha256': digest((app/'build/rhythmer.release').read_bytes()),
        'distribution': 'public-beta' if os.environ.get('RHYTHMER_PUBLIC_RELEASE') == '1' else 'local-beta-installation-candidate',
        'release_tag': os.environ.get('RHYTHMER_RELEASE_TAG'),
        'developer': 'jazzy rhythmer',
        'instagram': 'https://www.instagram.com/jazzyrhythmer/',
        'youtube': 'https://www.youtube.com/@jazzyrhythmer',
        'origin': 'Melodee by Kerem Kilic (Ellic Studio)',
        'beta': True, 'hardware_validated': False, 'hardware_validation': 'Pending owner beta testing', 'public_release': os.environ.get('RHYTHMER_PUBLIC_RELEASE') == '1',
        'upstream': {'melodee': upstream['upstream'], 'commit': upstream['commit'], 'base': '7e2d15d9ca086608b942599f6471a82f48c139f7'},
        'behavior_changes': ['branding and monochrome UI', 'original FM-1 four-track GEN and engine-scoped Acid/Break actions', 'single-sound and Rhythmer Kit plugin host', 'named presets and selected empty-track indication', '22 track entries and seven kit-only source variants', 'native PRESETS/EDIT, source-ordered sound controls, focused-pad editing, host mixer and stale-card protection'],
        'mechanical_rename': {'source': 'src/rhythmer', 'namespace': 'rhythmer', 'class': 'RhythmerApp',
                              'binary': 'rhythmer', 'sd_runtime': 'autorun/rhythmer'},
        'features': {
            'Sends_Access': 'MIX B2 SENDS stays visible in BASIC; CANCEL keeps the current mode/page, ENABLE FULL persists the native setting and opens track SENDS; repeat, shifted actions, Back and lesson restrictions retained',
            'Project_Save': 'First SAVE and SAVE AS choose a folder/name; SAVE updates the current manual file; OPEN/NEW use SAVE/DISCARD/CANCEL; one separate recovery entry per project under Rhythmer/Autosave; Project home SHIFT+B3 opens RECOVERY',
            'New_Engines': 'Frodhes original 57 programs; Tenebrae eight oscillator models and 164 programs; FMini-1 original 2.6.0 engine and 200 programs',
            'Pad_Mix': 'Selected pad native Volume first, related controls aligned by three; whole-kit filter next; native sound parameters and saved states retained',
            'Break_Audition': 'Original or synchronised dry preview, independent from track state; source replacement preserves patterns and performance settings; explicit source-bar confirmation and undo',
            'Tempo_Display': 'Stabilised external MIDI tempo presentation; actual sync algorithm unchanged',
            'Break_Workflow': 'BREAK GEN stays open after initial load; CANCEL/Shift+Push prevents assignment; completion respects dismissed menus and selected tracks; Pattern Hold and stretched-hit operating hints; saved DSP controls unchanged',
            'Acid_Sources': 'Four original Hortator ACID presets plus eight original Aphex presets, using their original DSP, source filter/edit controls and saved state; no authored patch values',
            'Preset_Browsing': 'Encoder and Minus/Plus wrap in the current preset list and main PRESETS face; includes User Sound/User Kit; absolute pot positions and load timing unchanged',
            'Empty_Pad_Start': 'Native Sample Kit SOUND/TRIM Push on an empty selected pad opens its SAMPLES browser, including an entirely empty Sample Kit; engine-less tracks retain native type selection; recording/Freeze, loaded pads and Break controls retained',
            'Sound_Tools': 'Stage EDIT Push opens PAD SOURCE or SAVE; K1 slot, K2 save, Status Ready; PRESETS reloads User Sound/User Kit; Back restores edit position',
            'Plugin_Transport': 'Forwarded to native child engines; Shift+B3 on Edit',
            'Pad_Sends': 'Native Sample Kit pads A-D; Rhythmer Kit retains track-level sends',
            'Sophie': 'Original 16-pad DSP; common Open MPC wrapper',
            'TR-MPC': 'Unmodified upstream prebuilt; four-family modular kit only',
            'Generator': 'Original FM-1 GEN: select tracks 1-4, 5-8, 9-12 or 13-16; first track Rhythmer Kit, next three instruments/MIDI; original genre order and seeded streams, recent-eight seed reroll, MONK excluded from automatic assignment; MIDI-only T1-16 range or one track; Undo/Redo; engine-scoped Acid and Break',
            'Chord_Generator': 'Independent CHORD GEN; existing GENERATE Tn and MUTATE Tn retained; five three-knob pages for genre, progression, chord changes, bars, rhythm, chord color, energy, Block/Arp/Strum, gate, voicing, register, play rate and project/local key/scale; selected pattern only; one Undo',
            'Kit_Generator': 'Single-track Rhythmer Kit generation uses genre-specific drum parts; same-genre drum tables when an arrangement omits drums; genres with no drum vocabulary retain the existing pattern and show no drum part',
            'Break': 'Browse 1-4-bar loops; tempo sync and 16 chops; genre/straight/random/mutate/fill; six-page BRK PERF with 19 roll/source commands, A/B/Return, recording/replay and saved state; no bundled audio',
            'Skin': 'Monochrome solid geometric startup, vector marks without a wordmark backplate, numeric glyphs and segmented gauges; 22 distinct pitch/sustain-reactive sculptures',
            'Startup': 'Official MPC Sample vector device mark, minimal pixel Rhythmer OS vector wordmark and four unlabeled abstract machine panels and eased vector-letter animation',
            'Native_instruments': str(len(native))+' native ports plus Sophie and five original drum packages; source and host receipts in NATIVE_ENGINES_LOCK.json',
            'Single_sound': '27 engine source views (26 original engines plus Hortator Acid) play one selected sound; named presets and source-ordered sound-design controls. Percussion uses C4-referenced tape pitch; melodic engines retain native MIDI/polyphony.',
            'Drum_kits': f"Rhythmer Kit: {len(json.loads((ROOT/'config/sound-catalog.json').read_text())['kits'])} named presets, every preset fills pads 1-16; original voices plus original Sophie supplementary percussion",
            'Hybrid': 'Rhythmer Kit supports per-pad engine/sound changes, independent sound design, 64-pad routing, user preset slots and complete project state',
            'TB-3PO': 'Original FM-1 TB-3PO and scale-mask wrapper integrated for Acid GEN',
            'Turing_Grids': 'Not integrated',
        },
        'known_limits': ['No device/listening/latency/USB/mirror/install-restart/rollback validation',
                         'Use the complete 0.2.0 SD package for its matching engines and catalogue; signed UPDATE changes autorun only',
                         'Rhythmer Kit has track sends, not native sample-pad send buses',
                         'Open MPC third-party wrapper serialises DSP with a mutex; hard real-time audit remains',
                         'Pad engine selection covers the 27 curated views backed by 26 aarch64 VST2 instruments; external VST3/armv7 plugins are not Rhythmer Kit sources',
                         'Single percussion tape pitch changes the shared sound tail and duration; it does not add independent pitched drum voices'],
    }
    files['RHYTHMER_OS.json'] = (json.dumps(status, indent=2) + '\n').encode()
    files['README-RHYTHMER-OS.txt'] = (ROOT / 'docs/SD_CARD_GUIDE.md').read_bytes()
    files['SOURCE_LOCK.json'] = (ROOT / 'docs/SOURCE_LOCK.json').read_bytes()
    files['RELEASES_LOCK.json'] = (ROOT / 'config/releases.lock.json').read_bytes()
    files['NATIVE_ENGINES_LOCK.json']=(ROOT/'config/native-engines.lock.json').read_bytes()
    files['SOUND_HOST_LOCK.json']=(ROOT/'config/sound-host.lock.json').read_bytes()
    files['ENGINE_PROFILES.json']=(ROOT/'config/engine-profiles.json').read_bytes()
    files['PRESET_COVERAGE.json']=(ROOT/'config/preset-coverage.json').read_bytes()
    files['ANIMATION_PROFILES.json']=(ROOT/'config/animation-profiles.json').read_bytes()
    files['DRUM_KITS.json']=(ROOT/'config/drum-kits.json').read_bytes()
    for image in ('essential-controls.png','os-structure.png'):
        files['Documentation/'+image]=(ROOT/'assets/manual'/image).read_bytes()
    files['CORRESPONDING_SOURCE.json']=(json.dumps(dict(runtime_and_ports='RHYTHMER-OS-'+VERSION+'-SOURCE.zip',move_sources=source_receipt,support_libraries=support_receipt),indent=2)+'\n').encode()
    offline=WORK/'manual-020-offline'
    manual_manifest=json.loads((offline/'guide-020-source.json').read_text())
    for page,entry in manual_manifest.items():
        if digest((ROOT/'docs'/entry['source']).read_bytes())!=entry['source_sha256']:
            raise RuntimeError('Offline manual is stale: '+page)
    for path in offline.rglob('*'):
        if path.is_file():files['Documentation/'+path.relative_to(offline).as_posix()]=path.read_bytes()
    files['Documentation/LICENSE.txt']=(ROOT/'vendor/rhythmer/LICENSE').read_bytes()
    for name in ('MANUAL_020_EN.md','FIRST_GROOVE_020_EN.md','QUICK_REFERENCE_020_EN.md','SYSTEM_MAP_020_EN.md','INSTALL_020_EN.md'):
        files['Documentation/'+name]=(ROOT/'docs'/name).read_bytes()
    files['THIRD_PARTY_NOTICES.md'] = (ROOT / 'THIRD_PARTY_NOTICES.md').read_bytes()
    files['JUCE_COMPONENTS.spdx.json']=(app/'build/deps/JUCE/JUCE.spdx.json').read_bytes()
    files['CREDITS_AUDIT.md']=(ROOT/'docs/CREDITS_AUDIT.md').read_bytes()
    files['FM1_LINEAGE_KO.md']=(ROOT/'docs/FM1_LINEAGE_KO.md').read_bytes()
    for folder in ('extensions','third_party/jiant-gen','third_party/fm1-gen','third_party/fm1-break'):
        for p in (ROOT/folder).rglob('*'):
            if p.is_file():files['RHYTHMER-GEN-SOURCE/'+p.relative_to(ROOT).as_posix()]=p.read_bytes()
    files['OPEN_MPC_COMPATIBILITY.md'] = (ROOT/'docs/OPEN_MPC_COMPATIBILITY.md').read_bytes()
    for name in ('RELEASE_020_NOTES_EN.md','TRACK_WORKFLOW.md','RHYTHMER_PRESETS.md','UPSTREAM_030.md','ORIGINAL_PRESET_AUDIT_KO.md','HORTATOR_KITS_KO.md','BREAK_ACID_GUIDE_KO.md','BREAK_WORKFLOW.md','PARAMETER_PAGES.md','NATIVE_PLUGIN_WORKFLOW.md','NATIVE_CONTROL_COVERAGE.md','FINAL_UI_AUDIT.md','VERIFICATION.md','GEN8_BREAK.md','DESIGN.md','ENGINE_REGISTRY.md','DRUM_KITS.md','BETA_READINESS.md','SOUND_KIT_GUIDE.md','GEN_WORKFLOW.md','REBRAND.md','SOUND_FIXES_BETA4.md'):
        files['Documentation/Reference/'+name]=(ROOT/'docs'/name).read_bytes()
    files['DEVICE_MARK_NOTICE.md']=(ROOT/'assets/device/NOTICE.md').read_bytes()
    # New installs use the canonical folder. The host also resolves legacy beta paths.
    files={('Rhythmer/'+name if name.startswith('Plugins/') else name):data for name,data in files.items()}
    from sign_update import sign
    sign(files)
    for name, data in files.items():
        release.scan(name, data)
    verify(files)
    files['SHA256SUMS'] = ''.join(digest(data) + '  ' + name + '\n'
                                for name, data in sorted(files.items())).encode()
    if stage_only:
        stage = WORK / 'sd-stage'
        for name, data in files.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        print('Staged generated development files at', stage)
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    target = OUTPUT / ('RHYTHMER-OS-'+VERSION+'-SD.zip')
    timestamp = int(sp.check_output(['git', '-C', str(ROOT), 'log', '-1', '--format=%ct'], text=True))
    release.write_zip(files, target, timestamp)
    # The native updater installs autorun only and preserves plug-ins/projects.
    update_target=OUTPUT/('RHYTHMER-OS-'+VERSION+'-UPDATE.zip')
    release.write_zip({n:b for n,b in files.items() if n.startswith('autorun/')},update_target,timestamp)
    update_target.with_suffix('.zip.sha256').write_text(digest(update_target.read_bytes())+'  '+update_target.name+'\n')
    target.with_suffix('.zip.sha256').write_text(digest(target.read_bytes()) + '  ' + target.name + '\n')
    # Verify every archive entry, not just the outer zip checksum.
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:
            raise RuntimeError('Corrupt zip')
        for name, data in files.items():
            if z.read(name) != data:
                raise RuntimeError('Archive mismatch: ' + name)
    check_public_banks([target,update_target])
    print(target)
    print(str(len(files)) + ' files; ' + str(target.stat().st_size) + ' bytes')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage-only', action='store_true')
    assemble(parser.parse_args().stage_only)
