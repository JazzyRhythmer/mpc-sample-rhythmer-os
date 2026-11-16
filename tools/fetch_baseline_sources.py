#!/usr/bin/env python3
"""Pin corresponding source at each reused MPC instrument release tag."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess as sp
ROOT=Path(__file__).resolve().parents[1]
DEST=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os/baseline-source-depot')
def fetch(item):
    ident=item['repo'].replace('/','_')+'_'+item['tag'];out=DEST/ident
    env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GIT_ALLOW_PROTOCOL='https')
    if not (out/'.git').exists():
        sp.run(['git','-c','url.https://github.com/.insteadOf=git@github.com:','clone','--depth','1','--branch',item['tag'],
            '--recurse-submodules','--shallow-submodules','https://github.com/'+item['repo']+'.git',str(out)],check=True,env=env,capture_output=True,timeout=300)
    commit=sp.check_output(['git','-C',str(out),'rev-parse','HEAD'],text=True).strip()
    modules=sp.check_output(['git','-C',str(out),'submodule','status','--recursive'],text=True).splitlines()
    print('Pinned',ident,commit[:10],flush=True)
    return dict(id=ident,repo=item['repo'],tag=item['tag'],commit=commit,submodules=modules,folder=ident)
def main():
    if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD not mounted')
    DEST.mkdir(parents=True,exist_ok=True)
    items=[x for x in json.loads((ROOT/'config/releases.lock.json').read_text()) if x['repo']!='keremimo/melodee-sample']
    unique={(x['repo'],x['tag']):x for x in items}
    with ThreadPoolExecutor(max_workers=2) as pool:pins=list(pool.map(fetch,unique.values()))
    (ROOT/'config/baseline-source.lock.json').write_text(json.dumps(pins,indent=2)+'\n')
if __name__=='__main__':main()
