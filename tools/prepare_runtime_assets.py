#!/usr/bin/env python3
"""Reuse pinned upstream auxiliary assets without recompiling unchanged DSP.
The application itself is built from the reviewed Rhythmer source patch.
"""
from pathlib import Path
import hashlib,json,os,shutil,sys,urllib.request,zipfile
ROOT=Path(__file__).resolve().parents[1]
CACHE=Path('/Volumes/SSD/Development/Caches/rhythmer-os/downloads')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def prepare(runtime):
 if not os.path.ismount('/Volumes/SSD'):raise RuntimeError('SSD is not mounted')
 integration=json.loads((ROOT/'config/upstream-integration.lock.json').read_text())
 if integration['upstream']=='v0.2.0':return
 spec=json.loads((ROOT/'config/upstream-stems.lock.json').read_text())
 if integration['commit']!=spec['commit']:raise RuntimeError('Auxiliary asset pin does not match integration')
 CACHE.mkdir(parents=True,exist_ok=True);archive=CACHE/spec['archive']
 if not archive.is_file() or sha(archive)!=spec['archive_sha256']:
  temp=archive.with_suffix('.download')
  with urllib.request.urlopen(spec['url'],timeout=90) as src,temp.open('wb') as out:shutil.copyfileobj(src,out)
  if sha(temp)!=spec['archive_sha256']:raise RuntimeError('Upstream release asset checksum mismatch')
  temp.replace(archive)
 output=runtime/'build/stems'
 with zipfile.ZipFile(archive) as z:
  for relative,item in spec['files'].items():
   data=z.read(item['member'])
   if hashlib.sha256(data).hexdigest()!=item['sha256']:raise RuntimeError('Stem asset mismatch: '+relative)
   path=output/relative;path.parent.mkdir(parents=True,exist_ok=True)
   if not path.is_file() or sha(path)!=item['sha256']:path.write_bytes(data)
 (output/'rhythmer-stems').chmod(0o755)
 (output/'licenses/RHYTHMER-REUSE.txt').write_text('Unchanged auxiliary separator and model from Melodee Sample '+spec['tag']+'.\nRelease: '+spec['url']+'\nThe helper filename is changed for Rhythmer lookup; its bytes are unchanged.\nOriginal license texts are retained. Corresponding sources: runtime/tools/stems/, third_party/runtime/spleeterrt/ and third_party/runtime/openblas/ in the matching SOURCE archive.\nDeezer checkpoint URL and SHA-256 are pinned in runtime/src/rhythmer/dependencies.py.\n')
 print('Pinned upstream Stems helper/model verified; original notices retained')
if __name__=='__main__':prepare(Path(sys.argv[1]).resolve())
