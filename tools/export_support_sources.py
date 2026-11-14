#!/usr/bin/env python3
"""Archive exact Debian source packages for the shipped support libraries."""
from pathlib import Path
import concurrent.futures as cf,hashlib,json,os,time,urllib.parse,urllib.request,zipfile
ROOT=Path(__file__).resolve().parents[1];WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os');CACHE=Path('/Volumes/SSD/Development/Caches/rhythmer-os/debian-sources');OUT=Path('/Volumes/SSD/Development/Archives/rhythmer-os')
def request(url):
    for attempt in range(4):
        try:return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Rhythmer-corresponding-source/1'}),timeout=90)
        except Exception:
            if attempt==3:raise
            time.sleep(attempt+1)
def getjson(url):
    with request(url) as r:return json.load(r)
def acquire(item):
    package,version=item;quote=lambda x:urllib.parse.quote(x,safe='')
    info=getjson(f'https://snapshot.debian.org/mr/package/{quote(package)}/{quote(version)}/srcfiles');rows=[]
    for record in info['result']:
        sha=record['hash'];meta=getjson(f'https://snapshot.debian.org/mr/file/{sha}/info')['result'][0];name=meta['name'];dest=CACHE/sha/name;dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.is_file() or hashlib.sha1(dest.read_bytes()).hexdigest()!=sha:
            temporary=dest.with_name(name+'.part')
            with request('https://snapshot.debian.org/file/'+sha) as r,temporary.open('wb') as f:
                while chunk:=r.read(1024*1024):f.write(chunk)
            assert hashlib.sha1(temporary.read_bytes()).hexdigest()==sha,(package,name,'source digest mismatch');os.replace(temporary,dest)
        rows.append(dict(package=package,version=version,name=name,sha1=sha,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,url='https://snapshot.debian.org/file/'+sha,path=dest))
    print('Corresponding support source:',package,version,len(rows),'files',flush=True);return rows

def main():
    if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD absent')
    binaries=[];packages=set()
    for line in (WORK/'runtime/build/support-source-packages.txt').read_text().splitlines():
        name,version,source,revision=line.split();binaries.append(dict(binary=name,version=version,source=source,source_version=revision));packages.add((source,revision))
    # Cross packages contain build rules; include the underlying GNU sources too.
    packages.update({('glibc','2.36-8'),('gcc-12','12.2.0-14')})
    rows=[]
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(acquire,sorted(packages)):rows+=result
    version=(ROOT/'VERSION').read_text().strip();target=OUT/('RHYTHMER-OS-'+version+'-SUPPORT-SOURCE.zip');OUT.mkdir(parents=True,exist_ok=True)
    manifest=dict(binaries=binaries,sources=[{k:v for k,v in x.items() if k!='path'} for x in rows],policy='Unmodified Debian source packages and cross-build rules for support-pack runtime libraries. Compiler/runtime sources are included alongside library sources. Original package terms remain.')
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_STORED) as z:
        for row in rows:z.write(row['path'],'sources/'+row['package']+'/'+row['name'])
        z.writestr('SOURCE_PACKAGES.json',json.dumps(manifest,indent=2)+'\n')
        z.writestr('README.txt','Corresponding sources for the Debian libraries embedded in the Rhythmer plug-in support pack.\nSOURCE_PACKAGES.json maps shipped binary versions to their original source packages, hashes and URLs.\nCross-build rules and the underlying GNU C Library/GCC sources are included.\nExtract each .dsc with its matching tar files using dpkg-source -x. Original copyright and licence terms are in each package.\n')
    with zipfile.ZipFile(target) as z:assert z.testzip() is None
    sha=hashlib.sha256(target.read_bytes()).hexdigest();target.with_suffix('.zip.sha256').write_text(sha+'  '+target.name+'\n')
    receipt=dict(file=target.name,sha256=sha,packages=len(packages),files=len(rows),bytes=target.stat().st_size,binary_versions=binaries)
    (WORK/'support-source-export.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='binary_versions'}))
if __name__=='__main__':main()
