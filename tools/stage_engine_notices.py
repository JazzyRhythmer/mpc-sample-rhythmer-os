#!/usr/bin/env python3
"""Retain dependency notices beside native binaries; copy only legal texts."""
import hashlib
import json
import os
from pathlib import Path
import shutil
from engine_inventory import ROOT,WORK,ports,folder_for
if __name__=='__main__':
    if not (os.path.ismount('/Volumes/SSD') or os.path.ismount(WORK)):raise SystemExit('SSD work mount absent')
    for port in ports():
        pin=json.loads((port/'SOURCE.json').read_text());dest=folder_for(port)
        source=WORK/'source-depot-releases'/pin['id'] if port.name.startswith('move-') else port
        notices={};(dest/'third_party').mkdir(exist_ok=True)
        for folder,dirs,names in os.walk(source):
            dirs[:]=[n for n in dirs if n not in ('.git','build','dist','out','node_modules') and not (Path(folder)/n).is_symlink()]
            for name in names:
                if not (any(x in name.lower() for x in ('license','licence','copying','notice','copyright','authors','credits','licensing','acknowledg')) or 'UPSTREAM_NOTICES' in (Path(folder)/name).parts or ((Path(folder)==source or 'assets' in Path(folder).parts) and name.lower().startswith('readme'))):continue
                p=Path(folder)/name
                if p.is_symlink() or not p.is_file() or p.stat().st_size>2*1024*1024:continue
                data=p.read_bytes()
                try:data.decode('utf-8')
                except UnicodeDecodeError:continue
                rel=p.relative_to(source);out=dest/'third_party'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
                notices[rel.as_posix()]=hashlib.sha256(data).hexdigest()
        (dest/'third_party/NOTICES_INDEX.json').write_text(json.dumps(notices,indent=2)+'\n')
    print('Dependency notices staged for',len(ports()),'native ports')
