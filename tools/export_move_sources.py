#!/usr/bin/env python3
"""Stream corresponding native Move source into a separate, history-free ZIP."""
import hashlib
import json
import os
from pathlib import Path
import zipfile
from engine_inventory import ROOT,WORK,ports
from privacy import findings,PATTERNS
OUTPUT=Path('/Volumes/SSD/Development/Archives/rhythmer-os')
SKIP={'.git','.github','AGENTS.md','CLAUDE.md','.claude','.codex','node_modules','__pycache__','build','dist','out','.DS_Store'}
def main():
    if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD not mounted')
    version=(ROOT/'VERSION').read_text().strip();target=OUTPUT/('RHYTHMER-OS-'+version+'-MOVE-SOURCE.zip')
    manifest={};changes={};pins=[];count=0
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for port in ports():
            if not port.name.startswith('move-'):continue
            pin=json.loads((port/'SOURCE.json').read_text());pins.append(pin)
            source=WORK/'source-depot-releases'/pin['id']
            for folder,dirs,names in os.walk(source):
                dirs[:]=sorted(n for n in dirs if n not in SKIP and not (Path(folder)/n).is_symlink())
                for name in sorted(names):
                    p=Path(folder)/name;rel=p.relative_to(source)
                    if p.is_symlink() or name in SKIP or name.startswith('.env') or p.suffix.lower() in ('.pem','.key','.p12','.pyc','.zip','.gz','.xz','.7z','.exe','.dll','.so','.dylib','.o','.a'):continue
                    data=p.read_bytes();path='third_party/move/'+pin['id']+'/'+rel.as_posix()
                    if data[:4] in (b'\x7fELF',b'\xcf\xfa\xed\xfe',b'\xce\xfa\xed\xfe',b'\xca\xfe\xba\xbe') or data[:2]==b'MZ':continue
                    issues=findings(path,data,False)
                    if issues==['personal-home']:
                        try:data.decode('utf-8')
                        except UnicodeDecodeError:raise RuntimeError('Private path in binary source asset: '+path)
                        changes[path]=dict(original_sha256=hashlib.sha256(data).hexdigest(),change='Generic build/example home path replaced; DSP expressions unchanged')
                        data=PATTERNS['personal-home'].sub(b'/upstream-home/',data)
                        issues=findings(path,data,False)
                    if issues:raise RuntimeError('Source privacy check failed: '+path+': '+','.join(issues))
                    item=zipfile.ZipInfo(path,(2026,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
                    item.external_attr=(0o100755 if name.endswith(('.sh','.py')) else 0o100644)<<16
                    archive.writestr(item,data);manifest[path]=hashlib.sha256(data).hexdigest();count+=1
            print('Source exported:',pin['id'],flush=True)
        archive.writestr('SOURCE_PINS.json',json.dumps(pins,indent=2)+'\n')
        archive.writestr('EXPORT_CHANGES.json',json.dumps(changes,indent=2)+'\n')
        archive.writestr('SHA256SUMS',''.join(d+'  '+n+'\n' for n,d in sorted(manifest.items())))
    with zipfile.ZipFile(target) as archive:
        if archive.testzip():raise RuntimeError('Source ZIP corruption')
    sha=hashlib.sha256(target.read_bytes()).hexdigest();target.with_suffix('.zip.sha256').write_text(sha+'  '+target.name+'\n')
    receipt=dict(file=target.name,sha256=sha,files=count,source_repositories=len(pins),privacy_passed=True,home_path_examples_normalized=len(changes))
    (WORK/'move-source-export.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
