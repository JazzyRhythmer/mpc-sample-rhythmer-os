#!/usr/bin/env python3
"""Inventory original published Move DSP modules; never executes their installers.

Usage: fetch_move_candidates.py CANDIDATES.json
Downloaded modules remain candidates until source/license and host acceptance.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tarfile
import urllib.request

WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
CACHE=Path('/Volumes/SSD/Development/Caches/rhythmer-os/move-originals')


def download(item):
    ident=item['id'];repo=item['github_repo'];folder=CACHE/ident;folder.mkdir(parents=True,exist_ok=True)
    result={'id':ident,'repo':repo,'status':'unreviewed'}
    try:
        api=folder/'release.json'
        if not api.exists():
            req=urllib.request.Request('https://api.github.com/repos/'+repo+'/releases/latest',headers={'User-Agent':'rhythmer-source-audit'})
            with urllib.request.urlopen(req,timeout=30) as r:api.write_bytes(r.read())
        release=json.loads(api.read_text());assets=release['assets']
        asset=next((a for a in assets if a['name']==item['asset_name']),None)
        if asset is None:raise ValueError('No matching original module archive')
        archive=folder/asset['name']
        if not archive.exists():
            part=archive.with_suffix(archive.suffix+'.part')
            with urllib.request.urlopen(asset['browser_download_url'],timeout=60) as r,part.open('wb') as out:shutil.copyfileobj(r,out)
            part.replace(archive)
        sha=hashlib.sha256(archive.read_bytes()).hexdigest()
        if asset.get('digest') and asset['digest']!='sha256:'+sha:raise ValueError('GitHub asset digest mismatch')
        result.update(tag=release['tag_name'],url=asset['browser_download_url'],sha256=sha,bytes=archive.stat().st_size,
                      digest_checked=bool(asset.get('digest')))
        dest=WORK/'move-originals'/ident;dest.mkdir(parents=True,exist_ok=True)
        with tarfile.open(archive) as tar:
            if sum(m.size for m in tar.getmembers())>512*1024*1024:raise ValueError('Archive exceeds extraction bound')
            for m in tar.getmembers():
                rel=Path(m.name)
                if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe archive path')
                if not m.isfile():continue
                p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True)
                with tar.extractfile(m) as src,p.open('wb') as out:shutil.copyfileobj(src,out)
        modules=[]
        for meta in dest.rglob('module.json'):
            d=json.loads(meta.read_text());dsp=meta.parent/d.get('dsp','dsp.so')
            if dsp.is_file():modules.append({'folder':str(meta.parent.relative_to(WORK)),'dsp':dsp.name,'api':d.get('api_version'),
                                             'license':d.get('license'),'name':d.get('name'),'version':d.get('version')})
        result['modules']=modules
        result['status']='downloaded' if modules else 'no-dsp-found'
    except Exception as e:result.update(status='fetch-failed',error=str(e))
    print(ident,result['status'],flush=True);return result


if __name__=='__main__':
    if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD not mounted')
    items=json.loads(Path(sys.argv[1]).read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(download,items))
    (WORK/'move-release-inventory.json').write_text(json.dumps(results,indent=2)+'\n')
    print('Inventory:',len(results),'candidates; no automatic acceptance',flush=True)
