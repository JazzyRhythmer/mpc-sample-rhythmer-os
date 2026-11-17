"""Copy named upstream legal texts verbatim into the staged native packages."""
from pathlib import Path
import json,os,shutil
from engine_inventory import ports,folder_for,WORK
LEGAL=('license','licence','copying','notice','copyright','authors','credits','licensing','acknowledg')
def stage():
 for port in ports():
  pin=json.loads((port/'SOURCE.json').read_text())
  source=(port/'original' if pin.get('source_built') else WORK/'source-depot-releases'/pin['id']) if port.name.startswith('move-') else port
  target=folder_for(port)/'third_party'
  for folder,dirs,names in os.walk(source):
   dirs[:]=[n for n in dirs if n not in ('.git','build','dist','out','node_modules') and not (Path(folder)/n).is_symlink()]
   for name in names:
    p=Path(folder)/name
    if p.is_symlink() or not p.is_file() or p.stat().st_size>2*1024*1024:continue
    if not (any(k in name.lower() for k in LEGAL) or 'UPSTREAM_NOTICES' in p.parts or ((p.parent==source or 'assets' in p.parts) and name.lower().startswith('readme'))):continue
    try:p.read_text()
    except (UnicodeDecodeError,OSError):continue
    dst=target/p.relative_to(source);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
 print('Staged original legal texts for',len(ports()),'native packages')
if __name__=='__main__':stage()
