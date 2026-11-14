#!/usr/bin/env python3
"""Pin source checkouts at the exact tags of original DSP release binaries."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess

WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
DEST=WORK/'source-depot-releases'
DEST.mkdir(parents=True,exist_ok=True)


def fetch(item):
    ident=item['id'];out={'id':ident,'repo':item['repo'],'tag':item.get('tag')}
    target=DEST/ident
    try:
        if not (target/'.git').exists():
            cmd=['git','-c','url.https://github.com/.insteadOf=git@github.com:',
                 'clone','--filter=blob:none','--depth','1','--branch',item['tag'],
                 '--recurse-submodules','--shallow-submodules','https://github.com/'+item['repo']+'.git',str(target)]
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=300,
                             env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GIT_ALLOW_PROTOCOL='https'))
            if p.returncode:raise RuntimeError(p.stderr[-1500:])
        out['commit']=subprocess.check_output(['git','-C',str(target),'rev-parse','HEAD'],text=True).strip()
        out['submodules']=subprocess.check_output(['git','-C',str(target),'submodule','status','--recursive'],text=True).strip()
        out['root_licenses']=[p.name for p in target.iterdir() if p.is_file() and p.name.lower().startswith(('license','copying'))]
        out['status']='pinned'
    except Exception as e:out.update(status='source-failed',error=str(e))
    print(ident,out['status'],flush=True);return out


if __name__=='__main__':
    if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD not mounted')
    items=[i for i in json.loads((WORK/'move-release-inventory.json').read_text()) if i['status']=='downloaded' and 'move-'+i['id'] in json.loads((Path(__file__).resolve().parents[1]/'config/first-release-candidates.json').read_text())['active_ports']]
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch,items))
    (WORK/'move-source-inventory.json').write_text(json.dumps(results,indent=2)+'\n')
