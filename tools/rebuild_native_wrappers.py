#!/usr/bin/env python3
"""Rebuild renamed product wrappers; leave every staged engine DSP untouched."""
import json,shutil
from compile_moves import compile_wrapper,ROOT,WORK
from engine_inventory import ports,folder_for
for port in ports():
 if port.name=="drumx":continue # direct-linked native engine: use compile_drumx.py
 ident=port.name.split('-',1)[1] if port.name!='drumx' else 'drumx'
 cfg=json.loads((port/'vst.json').read_text());out=compile_wrapper(port,cfg,ident)
 shutil.copy2(out/cfg['so'],folder_for(port)/cfg['so'])
 print('WRAPPER',port.name,flush=True)
