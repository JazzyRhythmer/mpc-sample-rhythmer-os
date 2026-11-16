#!/usr/bin/env python3
"""Rename generated plugin artifacts without changing DSP bytes or stable UIDs."""
import json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
def migrate():
 if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD absent')
 for old in sorted((WORK/'move-stage/Plugins').glob('GROOVE - *')):
  target=old.with_name(old.name.replace('GROOVE - ','RHYTHMER - ',1))
  if target.exists():continue # never replace an accepted newer engine with its legacy backup
  shutil.copytree(old,target)
  for p in list(target.glob('groove*.so')):p.rename(p.with_name(p.name.replace('groove','rhythmer',1)))
  p=target/'plugin-meta.xml'
  if p.is_file():p.write_text(p.read_text().replace('GROOVE - ','RHYTHMER - ').replace('groove-','rhythmer-'))
 print('Renamed native staging folders; original backups retained outside new package inventory')
if __name__=='__main__':migrate()
