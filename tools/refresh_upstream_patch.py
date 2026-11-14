#!/usr/bin/env python3
"""Record a reviewed generated runtime against the mechanically renamed origin.

Run only after resolving upstream conflicts in the SSD runtime. This does not
modify either the runtime or vendor source; build.py custom verifies replay.
"""
from pathlib import Path
import difflib,hashlib,json,sys
from rename_runtime import rename_text
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os/runtime')
ORIGIN=ROOT/'vendor/rhythmer'

def eligible(rel):
    return rel.parts[0] in ('src','tests','tools') or str(rel) in ('Makefile','docs/QUICKSTART.md','docs/GUIDE.md','docs/guide/rhythmer.md','docs/guide/gen.md','docs/guide/break-acid.md','docs/guide/install.md')

def main():
    before={}
    for file in ORIGIN.rglob('*'):
        rel=file.relative_to(ORIGIN)
        if not eligible(rel) or '.git' in rel.parts or '__pycache__' in rel.parts or not file.is_file():continue
        target=Path(str(rel).replace('melodee','rhythmer').replace('MELODEE','RHYTHMER').replace('Melodee','Rhythmer'))
        try:
            text=file.read_text()
            suffixes={'.cpp','.h','.c','.py','.sh','.md','.mk','.txt','.html','.css','.js','.svg'}
            before[target]=rename_text(text) if (file.suffix in suffixes or file.name=='Makefile') and file.name not in ('LICENSE','THIRD_PARTY.md','AGENTS.md') else text
        except UnicodeDecodeError:continue
    after={}
    for file in RUNTIME.rglob('*'):
        rel=file.relative_to(RUNTIME)
        if not eligible(rel) or '__pycache__' in rel.parts or not file.is_file():continue
        try:after[rel]=file.read_text()
        except UnicodeDecodeError:continue
    lines=[];changed=[]
    for rel in sorted(before.keys()|after.keys()):
        a=before.get(rel,'');b=after.get(rel,'')
        if a==b:continue
        if not a.endswith('\n') and a:a+='\n'
        if not b.endswith('\n') and b:b+='\n'
        lines+=difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+str(rel) if rel in before else '/dev/null',tofile='b/'+str(rel) if rel in after else '/dev/null',n=3)
        changed.append(str(rel))
    patch=ROOT/'extensions/runtime-v020.patch';patch.write_text(''.join(lines))
    inputs={}
    for folder in ('extensions','third_party/fm1-gen','third_party/fm1-break'):
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and p!=patch and '__pycache__' not in p.parts:inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    for rel in ('config/update-public-key.txt','docs/USER_MANUAL_KO_DRAFT.md','docs/GEN_WORKFLOW.md','docs/BREAK_ACID_GUIDE_KO.md','docs/SD_CARD_GUIDE.md','assets/device/mpc-sample.svg'):
        inputs[rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    result=dict(upstream='v0.2.0',commit='8880d16116ccb3c69f75fb46bf2166b16c51ef0c',patch_sha256=hashlib.sha256(patch.read_bytes()).hexdigest(),files=changed,inputs=inputs)
    (ROOT/'config/upstream-integration.lock.json').write_text(json.dumps(result,indent=2)+'\n')
    print(len(changed),'reviewed files;',patch.stat().st_size,'patch bytes')

if __name__=='__main__':main()
