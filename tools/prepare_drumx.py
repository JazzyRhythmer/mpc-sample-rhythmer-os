#!/usr/bin/env python3
"""Import pinned JIANT DRUM-X; generate mechanical per-instance C++ scoping."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def function(text,name):
    match=re.search(r'^static [^;{}\n]*\b'+re.escape(name)+r'\s*\([^;{}]*?\)\s*(?:/\*.*?\*/\s*)?\{',text,re.M|re.S)
    if not match:raise ValueError('Original function definition not found: '+name)
    start=match.start();begin=match.end()-1;depth=1;end=begin+1
    while depth:
        if text[end]=='{':depth+=1
        if text[end]=='}':depth-=1
        end+=1
    return text[start:end]+'\n'

def generate(port):
    original=port/'original';out=port/'build';out.mkdir(parents=True,exist_ok=True)
    subprocess.run(['python3',str(original/'gen_tables.py'),str(out/'felucca_tables.h')],check=True)
    dsp=(original/'dsp.c').read_text()
    helpers='/* SPDX-License-Identifier: GPL-3.0-only; original Felucca/JIANT helpers. */\n'
    for name in ('mulq15','mulq16','clamp','sine_i','softclip','noise32'):
        helpers+=function(dsp,name)
    helpers+='typedef struct { int32_t a1, a2, a3; } tsvf_t;\n'+function(dsp,'tsvf_coef_k')
    (out/'helpers.h').write_text(helpers)
    text=(original/'drumx_voice.c').read_text()
    text=re.sub(r'^static dx_lane_t dx_kit\[8\];[^\n]*\n','',text,flags=re.M)
    text=re.sub(r'^static ', '', text,flags=re.M)
    text=text.replace('dx_kit_t DX_KITS[]','dx_kit_t DX_KITS[9]')
    text=text.replace('uint8_t dx_tone;','uint8_t dx_tone = 0;').replace('uint8_t dx_hands;','uint8_t dx_hands = 0;')
    (out/'core.h').write_text('/* Mechanical instance scoping; original DSP expressions unchanged. */\nstruct DrumXCore {\n'+text+'\n};\n')

def prepare(source):
    port=ROOT/'ports/drumx';original=port/'original';original.mkdir(parents=True,exist_ok=True)
    pin=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    assert pin=='b2c7f365dd8b8d14047d0dbe9b4edd82cc5f09ae',pin
    files=['firmware/src/drumx_voice.c','firmware/src/dsp.c','firmware/src/eng_drum.c','firmware/src/core.h','tools/gen_tables.py','LICENSE']
    for f in files:shutil.copy2(source/f,original/Path(f).name)
    shutil.copy2(source/'LICENSE',port/'LICENSE')
    (port/'SOURCE.json').write_text(json.dumps(dict(repo='https://github.com/juanjiant-bit/JIANT',commit=pin,
        files={f:hashlib.sha256((source/f).read_bytes()).hexdigest() for f in files}),indent=2)+'\n')
    params=[]
    def add(key,name,lo,hi,default,options=None):
        p=dict(key=key,name=name,type='int',min=lo,max=hi,default=default,display='int')
        if options:p.update(type='enum',options=options)
        params.append(p)
    kits=['DRUM-X','909 CLUB','808 BOOM','LOFI DUST','INDUSTRIAL','ACOUSTIC','DUB ROOTS','TECHNO RAW','BREAKS']
    add('kit','Factory Kit',0,8,0,kits)
    for k,n,l,h,d in [('morph','Morph',0,127,64),('tune','Tune',0,127,64),('color','Tone',0,127,64),
        ('decay','Decay',0,127,64),('noise','Noise',0,127,64),('fm','FM Env',0,127,0),('fold','Fold',0,127,0),
        ('tone_bp','Metal BP',0,15,0),('feedback','Feedback',0,15,0),('hands','Clap Hands',0,15,0),('volume','Volume',0,127,100)]:add(k,n,l,h,d)
    add('note_map','Note Map',0,1,0,['Rack 36-43','General MIDI'])
    lanes=['Kick','Snare','Clap','Closed Hat','Open Hat','Tom','Rim','Bell']
    for i,name in enumerate(lanes):
        for k,n,lo,hi,d in [('wave','Wave',0,3,0),('filter','Filter',0,2,0),('snap','Snap',0,1,0),
                ('pmod','Pitch Mode',0,3,0),('drive','Drive',0,1,0),('layer','Layer',0,15,0),
                ('feedback','Feedback',0,15,0),('level','Level',0,127,100),('pan','Pan',0,127,64)]:
            add(f'l{i}_{k}',name+' '+n,lo,hi,d)
        for patch in ('a','b'):
            for k in ('pitch','pmod','decay','noise','color'):add(f'l{i}_{patch}_{k}',name+' '+patch.upper()+' '+k.title(),0,127,64)
    contract={'chain_params':params,'ui_hierarchy':{'pad_layout':'drums','levels':{f'l{i}':{'name':n,'note':36+i} for i,n in enumerate(lanes)}}}
    (port/'contract.json').write_text(json.dumps(contract,indent=2)+'\n')
    cfg=dict(name='DRUM-X',vendor='JIANT',uid='GDX1',version=1000,so='rhythmer-drumx.so',module='contract.json',custom_skin=True,
        targets=['aarch64'],build=dict(root='.',sources=['drumx.cpp'],cflags=['-fwrapv'],libs=['-lm','-lpthread']))
    (port/'vst.json').write_text(json.dumps(cfg,indent=2)+'\n')
    (port/'VENDORED.md').write_text('# DRUM-X\n\nOriginal JIANT fixed-point DRUM-X voice, helpers, generator and nine factory kits. '
        'The original files and hashes are preserved. Generated C++ scoping changes globals to per-instance fields; '
        'DSP expressions and 32-sample control rate remain unchanged. The native adapter supplies MIDI, velocity, linear pan, '
        'bounded 32-frame buffering and project state. Each of the eight lanes is monophonic, as in the original. '
        'Full firmware, global FX, sequencer and ROM are not embedded.\n')

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='--generate':generate(Path(sys.argv[2]))
    else:
        if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD not mounted')
        prepare(Path(sys.argv[1]))
