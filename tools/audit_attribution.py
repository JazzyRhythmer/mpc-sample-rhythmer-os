#!/usr/bin/env python3
"""Compare staged notices to pinned sources; inventory SPDX origins without legal clearance."""
from pathlib import Path
import hashlib,json,os,re
from engine_inventory import ROOT,WORK,ports,folder_for

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD absent')
 result=[]
 for port in ports():
  pin=json.loads((port/'SOURCE.json').read_text());source=(port/'original' if pin.get('source_built') else WORK/'source-depot-releases'/pin['id']) if port.name.startswith('move-') else port;stage=folder_for(port);expected={};spdx={};copyrights=set()
  for folder,dirs,names in os.walk(source):
   dirs[:]=[n for n in dirs if n not in ('.git','build','dist','out','node_modules') and not (Path(folder)/n).is_symlink()]
   for name in names:
    p=Path(folder)/name
    if p.is_symlink() or not p.is_file() or p.stat().st_size>2*1024*1024:continue
    try:text=p.read_text()
    except (UnicodeDecodeError,OSError):continue
    rel=p.relative_to(source).as_posix()
    if any(x in name.lower() for x in ('license','licence','copying','notice','copyright','authors','credits','licensing','acknowledg')) or 'UPSTREAM_NOTICES' in p.parts or ((p.parent==source or 'assets' in p.parts) and name.lower().startswith('readme')):expected[rel]=sha(p)
    ids=sorted(set(re.findall(r'SPDX-License-Identifier:\s*([^\r\n*]+)',text)))
    if ids:spdx[rel]=ids
    for line in text.splitlines():
     if re.search(r'copyright\s*(?:\(c\)|©|[12][0-9]{3})',line,re.I):copyrights.add(line.strip()[:300])
  missing=[n for n,h in expected.items() if not (stage/'third_party'/n).is_file() or sha(stage/'third_party'/n)!=h]
  result.append(dict(id=port.name,source=pin.get('repo',pin.get('url')),revision=pin.get('commit',pin.get('revision')),notice_files=len(expected),missing_or_changed=missing,spdx_files=spdx,copyright_lines=sorted(copyrights)))
 out=dict(scope=str(len(result))+' native source trees and staged named legal texts; SPDX inventory is not a dependency-license clearance',license_audit_complete=False,ports=result,missing_notice_count=sum(len(x['missing_or_changed']) for x in result))
 target=WORK/'attribution-inventory.json';target.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(ports=len(result),notice_files=sum(x['notice_files'] for x in result),missing=out['missing_notice_count'],spdx_files=sum(len(x['spdx_files']) for x in result))))
 assert not out['missing_notice_count'],'Required source notices missing or changed'
if __name__=='__main__':run()
