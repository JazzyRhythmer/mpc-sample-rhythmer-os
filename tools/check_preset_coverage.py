#!/usr/bin/env python3
"""Compare host selections with independent pinned factory files, not host recipes."""
import hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from sound_catalog import original_names
from original_banks import elixir_kits,hortator_presets
from rhythmer_presets import programs as own_programs
ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 c=json.loads((ROOT/'config/sound-catalog.json').read_text());rows=[]
 ports={json.loads(p.read_text())['so']:p.parent for p in (ROOT/'ports').glob('*/vst.json')}
 native=json.loads((WORK/'sound-presets.json').read_text())
 for e in c['engines']:
  p=ports.get(e['library']);names=[s['name'].strip() for s in e['sounds']];source=[];assets=[];excluded=[]
  basis='Original native voice/model palette (not a factory patch bank)'
  if p:
   source=[n.strip() for n in original_names(p)]
   pin=json.loads((p/'SOURCE.json').read_text()) if (p/'SOURCE.json').is_file() else {}
   if p.name=='sophie':
    upstream=WORK/'source-depot/move-sophie/src/dsp'
    for f in (p/'dsp').rglob('*'):
     if f.is_file():assert sha(f)==sha(upstream/f.relative_to(p/'dsp'))
    assets=[dict(file='dsp/'+f.relative_to(p/'dsp').as_posix(),sha256=sha(f)) for f in (p/'dsp').rglob('*') if f.is_file()]
    basis='Byte-identical original Sophie DSP and its 16 default pad voices; no separate bank'
   for f,digest in pin.get('files',{}).items():
    local=p/'original'/f if (p/'original'/f).is_file() else p/'original'/f.removeprefix('firmware/') if p.name=='fm1-guru600' else p/'original'/Path(f).name
    assert local.is_file() and sha(local)==digest,(p.name,f,'pinned original changed')
    if any(w in f.lower() for w in ('preset','patch','p600_bank','p600_sci','.syx','.snd','sounds_conv','m2k_lib.c')):assets.append(dict(file=f,sha256=digest))
   if source:basis='Pinned original factory table, exact source order and names'
   if p.name=='fm1-prophet':
    params=json.loads((p/'contract.json').read_text())['chain_params'];expected=own_programs('prophet',params);source=[x['name'] for x in expected];basis='Original GPL Init plus 15 explicitly authored Rhythmer presets; external Sequential bank excluded'
    assert [x['values'] for x in e['sounds']]==[x['values'] for x in expected]
   for f,digest in pin.get('omitted_vendor_presets',{}).items():
    assert not (p/'original'/f).exists(),(p.name,f,'excluded bank returned')
    excluded.append(dict(file=f,sha256=digest,reason='External factory data excluded from public build; redistribution permission not established'))
   if p.name=='fm1-mono2k':
    basis='Original 96-sound SND library plus 16 standalone machine Init choices'
    excluded=[dict(name=n,reason='Original input-only FX machine; standalone instrument has no audio input') for n in ('FX-CHORS','FX-RING','FX-DYNMX')]
   if p.name=='fm1-hortator':
    full=hortator_presets();excluded=[dict(name=x['name'],reason='Requires original sample assets and sample model, absent from synthesis-only port') for x in full if x['model']=='DM_SMPL']
    source=[x['name'] for x in full if x['model']=='DM_ACID'] if e['name']=='Acid Engine' else [x['name'] for x in full if x['model']!='DM_SMPL']
    basis='Original Hortator factory bank; four sample-dependent presets explicitly excluded'
    if e['name']=='Acid Engine':
     aphex=next(x for x in c['engines'] if x['name']=='Aphex');selected=json.loads((ROOT/'config/acid-aphex-presets.json').read_text())['presets']
     for name in selected:
      original=next(x for x in aphex['sounds'] if x['name']==name);alias=next(x for x in e['sounds'] if x['name']==name)
      assert alias['source_engine']==aphex['folder'] and {k:v for k,v in alias.items() if k not in ('source_engine','source_sound','origin')}==original
     source+=selected;basis+='; selected original Aphex presets routed to the unmodified Aphex DSP'

   if p.name=='fm1-elixir':
    params=json.loads((p/'contract.json').read_text())['chain_params'];expected=own_programs('elixir',params);source=[k['name']+' / '+v['name'] for k in expected for v in e['voices']];basis='Original GPL Initkit plus four explicitly authored Rhythmer kits, each seven voices; external Erica/Hrtl kit assets excluded'
    assert [x['values'] for x in e['sounds']]==[k['values'] for k in expected for v in e['voices']]
   if p.name in ('move-braids','move-hera','move-dexed'):
    release=WORK/'source-depot-releases'/p.name[5:];module=WORK/json.loads((p/'SOURCE.json').read_text())['module_folder'];staged=WORK/'sd-stage/Rhythmer/Plugins'/e['folder']/'module'
    if p.name=='move-dexed':
     source=[]
     assert not [f for f in staged.rglob('*') if f.is_file() and not (module/f.relative_to(staged)).is_file()], 'Non-original Dexed module assets'
     for bank in sorted((release/'banks').glob('*.syx'),key=lambda p:p.name.lower()):
      data=bank.read_bytes();assert len(data)==4104 and data[:6]==bytes([240,67,0,9,32,0])
      assert sha(bank)==sha(module/'banks'/bank.name)==sha(staged/'banks'/bank.name)
      assets.append(dict(file='banks/'+bank.name,sha256=sha(bank)))
      for i in range(32):source.append(bank.stem+' / '+''.join(chr(v) if 32<=v<127 else ' ' for v in data[6+128*i+118:6+128*i+128]).strip())
     assert len(source)==1056
     assert {f.name for f in (staged/'banks').glob('*.syx')}=={a['file'].split('/')[-1] for a in assets}
    else:
     extension='*.braids' if p.name=='move-braids' else '*.xml'
     files=sorted((release/'src/presets').glob(extension))
     source=[json.loads(f.read_text())['name'] if p.name=='move-braids' else ET.parse(f).getroot().find('PROGRAM').attrib['name'] for f in files]
     for f in files:
      relative='presets/'+f.name;assert sha(f)==sha(module/relative)==sha(staged/relative);assets.append(dict(file=relative,sha256=sha(f)))
    assert native[e['library']]['names']==source
    basis='Original published bank files; source, unmodified release and staged copies match SHA-256; native names read back'
   if p.name=='move-aphex':source=next(x['options'] for x in json.loads((p/'contract.json').read_text())['chain_params'] if x['key']=='preset');basis='Original 41-preset module enum; original attack and hold retained'
   if p.name=='move-plaits':
    models=next(x['options'] for x in json.loads((p/'contract.json').read_text())['chain_params'] if x['key']=='engine');table=json.loads((p/'model-controls.json').read_text());assert table['source_commit']==pin['source_commit']
    source=models+[models[b+2]+' / '+n.strip() for b,bank in enumerate(table['fm_banks']) for n in bank];basis='Original 24-model palette and 96 embedded 6-Op programs, with source model labels and quantizer mapping'
  if source:assert names==source,(e['name'],'source order/name mismatch',len(names),len(source))
  assert names and all(names)
  assert not any('host_adjustment' in s for s in e['sounds'])
  rows.append(dict(engine=e['name'],folder=e['folder'],variant=e.get('variant',''),source_slots=len(names),exposed_sounds=len(e.get('selection',names)),basis=basis,bank_assets=assets,excluded=excluded,missing=[]))
 assert len(rows)==27 and len(c['kits'])==len(json.loads((ROOT/'config/first-release-candidates.json').read_text())['kit_presets'])
 result=dict(version=(ROOT/'VERSION').read_text().strip(),source_views=27,track_picker_entries=22,factory_kits=len(c['kits']),exposed_sounds=sum(x['exposed_sounds'] for x in rows),missing_source_names=0,explicit_exclusions=7,excluded_factory_presets=4,excluded_input_only_models=3,excluded_external_bank_assets=118,excluded_external_sound_selections=1019,original_source_selections=sum(x['exposed_sounds'] for x in rows)-43,rhythmer_authored_selections=43,policy='Original bank names/data retained except 118 excluded external assets. User-authorized Rhythmer presets are separately identified: 15 Prophet sounds and four Elixir kits / 28 voices, made from GPL Init with independent edits. No hidden envelope overrides. This report is not blanket public distribution clearance.',engines=rows)
 (ROOT/'config/preset-coverage.json').write_text(json.dumps(result,indent=2)+'\n');print('Pinned preset coverage:',result['exposed_sounds'],'selections; 4 sample dependencies and 3 input-only models documented')
 return result
if __name__=='__main__':check()
