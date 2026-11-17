#!/usr/bin/env python3
"""Record a reviewed generated runtime against the mechanically renamed origin.

Run only after resolving upstream conflicts in the SSD runtime. This does not
modify either the runtime or vendor source; build.py custom verifies replay.
"""
from pathlib import Path
import argparse,difflib,hashlib,json,subprocess,sys
from rename_runtime import rename_text
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os/runtime')
ORIGIN=ROOT/'vendor/rhythmer'

def eligible(rel):
    return rel.parts[0] in ('src','tests','tools') or str(rel).startswith('docs/guide/') or str(rel) in ('Makefile','docs/QUICKSTART.md','docs/GUIDE.md','docs/guide/rhythmer.md','docs/guide/gen.md','docs/guide/break-acid.md','docs/guide/install.md')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--runtime',type=Path,default=RUNTIME)
    parser.add_argument('--origin',type=Path,default=ORIGIN)
    parser.add_argument('--tag')
    parser.add_argument('--commit')
    parser.add_argument('--lock',type=Path,default=ROOT/'config/upstream-integration.lock.json')
    args=parser.parse_args()
    runtime=args.runtime.resolve();origin=args.origin.resolve()
    commit=args.commit or subprocess.check_output(['git','-C',str(origin),'rev-parse','HEAD'],text=True).strip()
    tag=args.tag or subprocess.check_output(['git','-C',str(origin),'describe','--tags','--exact-match','HEAD'],text=True).strip()
    if not tag.startswith('v') or len(commit)!=40:raise RuntimeError('Exact upstream version and commit required')
    before={}
    for file in origin.rglob('*'):
        rel=file.relative_to(origin)
        if not eligible(rel) or '.git' in rel.parts or '__pycache__' in rel.parts or not file.is_file():continue
        target=Path(str(rel).replace('melodee','rhythmer').replace('MELODEE','RHYTHMER').replace('Melodee','Rhythmer'))
        try:
            text=file.read_text()
            suffixes={'.cpp','.h','.c','.py','.sh','.md','.mk','.txt','.html','.css','.js','.svg'}
            before[target]=rename_text(text) if (file.suffix in suffixes or file.name=='Makefile') and file.name not in ('LICENSE','THIRD_PARTY.md','AGENTS.md') else text
        except UnicodeDecodeError:continue
    after={}
    for file in runtime.rglob('*'):
        rel=file.relative_to(runtime)
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
    patch=ROOT/('extensions/runtime-'+tag.replace('.','')+'.patch');patch.write_text(''.join(lines))
    inputs={}
    for folder in ('extensions','third_party/fm1-gen','third_party/fm1-break'):
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and p!=patch and '__pycache__' not in p.parts:inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    for rel in ('config/update-public-key.txt','docs/USER_MANUAL_KO_DRAFT.md','docs/GEN_WORKFLOW.md','docs/BREAK_ACID_GUIDE_KO.md','docs/SD_CARD_GUIDE.md','assets/device/mpc-sample.svg','config/upstream-stems.lock.json','tools/prepare_runtime_assets.py'):
        inputs[rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in sorted((ROOT/'docs').glob('*.md')):
        inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    inputs['tools/sync_runtime_guides.py']=hashlib.sha256((ROOT/'tools/sync_runtime_guides.py').read_bytes()).hexdigest()
    result=dict(upstream=tag,commit=commit,patch=str(patch.relative_to(ROOT)),patch_sha256=hashlib.sha256(patch.read_bytes()).hexdigest(),files=changed,inputs=inputs)
    args.lock.write_text(json.dumps(result,indent=2)+'\n')
    print(len(changed),'reviewed files;',patch.stat().st_size,'patch bytes')

if __name__=='__main__':main()
