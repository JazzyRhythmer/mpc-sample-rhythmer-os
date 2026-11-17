#!/usr/bin/env python3
"""Apply the reviewed pinned integration to a disposable renamed snapshot.

The pinned vendor and base are never patched. A single diff retains the new
upstream architecture; original FM-1 source remains independently pinned.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]

def apply(runtime):
    pin=subprocess.check_output(['git','-C',str(ROOT/'vendor/rhythmer'),'rev-parse','HEAD'],text=True).strip()
    lock=json.loads((ROOT/'config/upstream-integration.lock.json').read_text())
    if pin!=lock['commit']:raise RuntimeError('Upstream checkout does not match the reviewed integration lock')
    patch=ROOT/lock.get('patch', 'extensions/runtime-v020.patch')
    if hashlib.sha256(patch.read_bytes()).hexdigest()!=lock['patch_sha256']:raise RuntimeError('Integration patch changed without review')
    for rel,expected in lock['inputs'].items():
        if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=expected:raise RuntimeError('Integration input changed; refresh and verify the runtime patch: '+rel)
    subprocess.run(['git','apply','--check','--unsafe-paths',str(patch)],cwd=runtime,check=True)
    subprocess.run(['git','apply','--unsafe-paths',str(patch)],cwd=runtime,check=True)
    for name in ('fm1-gen','fm1-break'):shutil.copytree(ROOT/'third_party'/name,runtime/name,dirs_exist_ok=True)

if __name__=='__main__':apply(Path(sys.argv[1]).resolve())
