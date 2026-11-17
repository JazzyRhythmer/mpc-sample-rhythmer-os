#!/usr/bin/env python3
"""Small macOS entry point; build storage and Linux VM live on the SSD."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import time
import subprocess as sp

ROOT = Path(__file__).resolve().parents[1]
WORK = Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
DOCKER = '/Volumes/SSD/Development/Toolchains/rhythmer-os/bin/docker'
IGNORE = shutil.ignore_patterns('.git', 'build', 'dist', '__pycache__', '*.pyc')


def check():
    if not os.path.ismount('/Volumes/SSD'):
        raise SystemExit('SSD is not mounted; no internal fallback')
    if not Path(DOCKER).is_file():
        raise SystemExit('Read docs/BUILD.md to initialise the SSD Linux environment')


def copy_sources(app=True, destination=None):
    check()
    if app:
        runtime = destination or WORK / 'runtime'
        # This is a generated snapshot, never the user's source checkout.
        for name in ('src', 'tests', 'tools', 'docs', 'release', 'assets', '.githooks'):
            generated = runtime / name
            if generated.is_dir():
                shutil.rmtree(generated)
        shutil.copytree(ROOT / 'vendor/rhythmer', runtime, ignore=IGNORE, dirs_exist_ok=True)
    for folder in ('ports', 'tools', 'tests', 'config', 'vendor/mpc-vst-plugins'):
        destination = WORK / 'plugins' / folder
        # Synchronise generated source snapshots; retain accepted build outputs.
        if destination.is_dir():
            for old in destination.rglob('*'):
                rel = old.relative_to(destination)
                if any(part in ('build', '__pycache__') for part in rel.parts): continue
                if not (ROOT / folder / rel).exists() and old.is_file(): old.unlink()
        shutil.copytree(ROOT / folder, destination, ignore=IGNORE, dirs_exist_ok=True)


def container(command, ports=False, subdir='runtime'):
    check()
    cwd = WORK / ('plugins' if ports else subdir)
    extra=[]
    if os.environ.get('RHYTHMER_GEN_CARD'):
        card=Path(os.environ['RHYTHMER_GEN_CARD']).resolve()
        if not card.is_relative_to(Path('/Volumes/SSD/Development')):
            raise RuntimeError('GEN fixture must stay on the development SSD')
        extra=['-e','RHYTHMER_GEN_CARD='+str(card)]
    sp.run([DOCKER, 'run', '--rm', '--platform', 'linux/arm64',
            '-v', str(WORK) + ':' + str(WORK),
            '-v', str(WORK) + ':/Volumes/SSD/Development/BuildCache/groove-os', '-v', str(cwd) + ':/work',
            '-w', '/work', '-e', 'PYTHONDONTWRITEBYTECODE=1',
            '-e', 'RHYTHMER_VERSION=' + (ROOT / 'VERSION').read_text().strip(), *extra, 'rhythmer-builder', 'sh', '-ec', command], check=True)


def snapshot_times():
    """Keep unchanged final-source mtimes so regenerating a snapshot reuses objects."""
    root = WORK / 'runtime'
    kept = {}
    for folder in ('src','tests','tools','assets','fm1-gen','docs','Makefile'):
        for p in ([root/folder] if (root/folder).is_file() else (root/folder).rglob('*')):
            if p.is_file():
                stat = p.stat()
                kept[str(p.relative_to(root))] = (hashlib.sha256(p.read_bytes()).digest(),stat.st_atime_ns,stat.st_mtime_ns)
    return kept


def restore_times(kept):
    # Lima's clock can run ahead of macOS. Changed generated sources must be
    # newer than existing objects; copying host mtimes can silently reuse old code.
    root=WORK/'runtime'
    newest=max((p.stat().st_mtime_ns for p in (root/'build/obj').rglob('*.o') if p.is_file()),default=0)
    changed_time=max(time.time_ns(),newest)+1_000_000_000
    for folder in ('src','tests','tools','assets','fm1-gen','docs','Makefile'):
        for p in ([root/folder] if (root/folder).is_file() else (root/folder).rglob('*')):
            if not p.is_file():continue
            old=kept.get(str(p.relative_to(root)))
            if old and hashlib.sha256(p.read_bytes()).digest()==old[0]:
                os.utime(p,ns=(old[1],old[2]))
            else:os.utime(p,ns=(changed_time,changed_time))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target', choices=['prepare', 'baseline', 'ports', 'custom'])
    target = parser.parse_args().target
    check()
    if target == 'prepare':
        copy_sources()
    if target == 'baseline':
        copy_sources(destination=WORK / 'baseline')
        sp.run(['python3', 'tools/dependencies.py'], cwd=WORK / 'baseline', check=True)
        # One job keeps JUCE inside the small VM's memory budget.
        container('make -j1 && python3 -m unittest discover -s tests -v && '
                  'build/melodee --self-test build/test.wav && build/melodee --melodee-monkey', subdir='baseline')
    elif target == 'ports':
        copy_sources(app=False)
        container('python3 tools/compile_ports.py', ports=True)
    elif target == 'custom':
        from check_release_selection import check as check_selection
        check_selection()
        from stage_test_catalog import stage as stage_test_catalog
        stage_test_catalog()
        os.environ.setdefault("RHYTHMER_GEN_CARD", str(WORK / "sd-stage"))
        kept = snapshot_times()
        copy_sources()
        sp.run(['python3', str(ROOT / 'tools/rename_runtime.py'), str(WORK / 'runtime')], check=True)
        sp.run(['python3', str(ROOT / 'tools/apply_upstream.py'), str(WORK / 'runtime')], check=True)
        sp.run(['python3', str(ROOT / 'tools/sync_runtime_guides.py'), str(WORK / 'runtime')], check=True)
        sp.run(['python3', 'tools/dependencies.py'], cwd=WORK / 'runtime', check=True)
        from prepare_runtime_assets import prepare as prepare_assets
        prepare_assets(WORK / 'runtime')
        restore_times(kept)
        container('make -j1 && python3 -m unittest discover -s tests -v && '
                  'build/rhythmer --self-test build/rhythmer-self-test.wav && '
                  'build/rhythmer --rhythmer-navigation-check && '
                  'build/rhythmer --rhythmer-track-check && '
                  'build/rhythmer --rhythmer-gen8-check && '
                  'build/rhythmer --rhythmer-monkey && '
                  'mkdir -p build/rhythmer-preview && build/rhythmer --rhythmer-preview build/rhythmer-preview && '
                  'python3 tools/sync_guide_screens.py build/rhythmer-preview docs/images/screens && make -j1 && '
                  'build/rhythmer --self-test build/rhythmer-self-test.wav && '
                  'cp build/rhythmer build/rhythmer.release && strip --strip-unneeded build/rhythmer.release && '
                  'sha256sum build/rhythmer > build/rhythmer.release.source-sha256')
