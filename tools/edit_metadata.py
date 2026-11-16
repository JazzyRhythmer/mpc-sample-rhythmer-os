"""Sound-edit presentation metadata derived from pinned control descriptions.

Only host labels/visibility change. Native parameter keys and state stay intact.
"""
from collections import Counter
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')

# Ranges follow the native boundaries in ports/common/*_native.c. They identify
# repeated original panels; never renumber the native parameter itself.
GROUPS={
 'fm1-obervave':[(1,4,'Osc 1'),(5,12,'Osc 2'),(13,20,'Filter'),(21,24,'Filter Env'),(25,28,'Amp Env'),(29,38,'LFO'),(39,47,'Voice'),(48,52,'Arp'),(53,55,'Chorus'),(56,59,'Delay'),(60,63,'Reverb')],
 'fm1-kwasub':[(1,8,'Osc A'),(9,16,'Osc B'),(17,20,'Sub'),(21,26,'Noise / Mix'),(27,33,'Filter'),(34,37,'Amp Env'),(38,41,'Filter Env'),(42,45,'Pitch Env'),(46,54,'LFO 1'),(55,63,'LFO 2'),(64,75,'Mod Matrix'),(76,79,'Drive'),(80,83,'Lo-Fi'),(84,87,'Chorus'),(88,92,'Delay'),(93,96,'Reverb'),(97,103,'Output'),(104,111,'Motion'),(112,116,'Compressor'),(117,124,'Mod FX'),(125,130,'Sample'),(131,138,'Output'),(139,139,'Osc A'),(140,140,'Osc B')],
 'fm1-mono2k':[(1,8,'Machine'),(9,16,'Amp'),(17,24,'Filter'),(25,26,'EQ'),(27,36,'FX'),(37,38,'Track'),(39,42,'Arp'),(43,50,'LFO 1'),(51,58,'LFO 2'),(59,66,'LFO 3'),(67,70,'Mod FX')],
}
EXPAND={'ATK':'Attack','DEC':'Decay','SUS':'Sustain','REL':'Release','LVL':'Level','FLT':'Filter','PIT':'Pitch','SHP':'Shape','PHS':'Phase','SWG':'Swing','SCL':'Scale','QNT':'Quantize','TRN':'Transpose','VCE':'Voice Mode','GLD':'Glide','GLMOD':'Glide Mode','PRIO':'Priority','ALLOC':'Allocation','DTUNE':'Detune','SRC':'Source','DST':'Destination','AMT':'Amount','CUTOF':'Cutoff','CUT':'Cutoff','RESO':'Resonance','FDBK':'Feedback','DLY':'Delay','REV':'Reverb','CHO':'Chorus','CHRD':'Chord','VOIC':'Voicing','Oscilltr':'Oscillator','Frequncy':'Frequency','Resnance':'Resonance','Overdriv':'Overdrive','SampleRt':'Sample Rate','Transnt':'Transient','PitchMod':'Pitch Mod','CrossMod':'Cross Mod','DstParam':'Destination','PulsWdth':'Pulse Width','AudioOut':'Output','Veloc':'Velocity'}

def expand(name):
 return ' '.join(EXPAND.get(w,w) for w in name.split())

def enrich(entry,port,contract):
 ps=entry['parameters'];levels=contract.get('ui_hierarchy',{}).get('levels',{})
 if port.name=='fm1-mono2k':
  # Three internal destination-track selectors are fixed to this instance.
  entry.setdefault('hidden_keys',[]).extend(('p43','p51','p59'))
 groups={};labels={}
 for key,level in levels.items():
  if key=='root':continue
  group=level.get('label',level.get('name',key))
  # Static group identity, not the current mutable value in a page title.
  group=re.sub(r':.*$','',group)
  for p in level.get('params',[]):
   k=p if isinstance(p,str) else p.get('key')
   if not k:continue
   groups.setdefault(k,group)
   if isinstance(p,dict) and (p.get('label') or p.get('name')):labels.setdefault(k,p.get('label',p.get('name')))
 for p in ps:
  key=p['key'];p['category']=expand(p.get('category') or groups.get(key,''))
  if key in labels and not port.name.startswith('fm1-'):p['edit_name']=labels[key]
  if port.name.startswith('fm1-'):
   if port.name not in ('fm1-mono2k','fm1-hortator','fm1-elixir'):p['edit_name']=expand(p['name'])
   for lo,hi,group in GROUPS.get(port.name,[]):
    if lo<=p['index']<=hi:p['category']=group
 # The FM-1 track block is followed by the native instrument panel. Firmware
 # sequence/arp/drum-map fields are not run by these synthesis-only boundaries.
 if port.name in ('fm1-fmini','fm1-guru600','fm1-prophet'):
  n=117 if port.name=='fm1-prophet' else 109
  for p in ps:
   i=p['index']
   if i<n:
    if 1<=i<=8:p['category']='Track Amp'
    elif 10<=i<=17:p['category']='Track LFO'
    elif p['name'] in ('SRC1','DST1','AMT1','SRC2','DST2','AMT2','SRC3','DST3','AMT3','SRC4','DST4','AMT4'):p['category']='Mod Matrix'
    elif p['name'] in ('ATK','DEC','SUS','REL','LVL'):
     # Four five-control envelopes immediately after the mod matrix.
     start=62
     p['category']='Mod Env '+str((i-start)//5+1)
    else:p['category']='Track'
   elif port.name=='fm1-prophet':
    for lo,hi,g in [(117,127,'Macro'),(128,138,'Osc'),(139,141,'Mixer'),(142,145,'Filter'),(146,156,'LFO'),(157,161,'Poly Mod'),(162,167,'Performance'),(168,175,'Envelope'),(176,181,'Voice'),(182,183,'Global')]:
     if lo<=i<=hi:p['category']=g
   elif port.name=='fm1-fmini':p['category']='FM Patch' if i<137 else 'Global FX'
   else:p['category']='Synth' if i<117 else 'Global FX'
  hidden=entry.setdefault('hidden_keys',[])
  # Native firmware sequences are absent from the port: keep synth and FX.
  start,end=(18,33)
  hidden.extend(p['key'] for p in ps if start<=p['index']<=end)
  # The source drum note mapper and chord sequencer are not sound controls.
  a,b=(82,92) if port.name=='fm1-prophet' else (82,91)
  hidden.extend(p['key'] for p in ps if a<=p['index']<=b)
  if port.name!='fm1-prophet':hidden.extend(p['key'] for p in ps if p['index'] in (9,95))
  else:hidden.extend(p['key'] for p in ps if p['index']==9)
 # Select the full named bank once, via Sound/PRESETS. Original browser/file
 # actions otherwise change the backing bank without updating that selector.
 # Only add a context where names would otherwise collide. Already-qualified
 # names retain their compact source spelling.
 for p in ps:
  key=p['key'];name=p.get('edit_name',p['name'])
  if p['name'] in ('FX Routing','FX Return','Reverb Type'):p['category']='Global FX';p['edit_name']=p['name']
  if p['name'] in ('Velocity Sensitivity','Native Arp Enable'):p['category']='Performance';p['options']=['Off','On']
  if not p['category'] and not key.startswith(('groove_model_','rhythmer_model_')) and '_' in key and not re.match(r'^p\d+$',key):
   prefix=key.rsplit('_',1)[0].replace('_',' ')
   p['category']=prefix.title()
 counts=Counter((p.get('category',''),p.get('edit_name',p['name'])) for p in ps)
 seen=Counter()
 for p in ps:
  name=p.get('edit_name',p['name']);pair=(p.get('category',''),name)
  if name and counts[pair]>1 and port.name not in ('fm1-mono2k','fm1-hortator','fm1-elixir'):
   seen[pair]+=1;p['edit_name']=name+' '+str(seen[pair])
 for p in ps:
  if p['type']=='canvas':entry['hidden_keys'].append(p['key'])
 entry['hidden_keys']=sorted(set(entry.get('hidden_keys',[])))
