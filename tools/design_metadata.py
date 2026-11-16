"""Presentation-only groups. Stable native indices and parameter values stay intact."""
import re
ORDER={'MODEL':0,'OSC':10,'TONE':15,'FILTER':20,'FILTER ENV':30,'AMP ENV':31,'ENV':32,'MOD ENV':33,'LFO':40,'MOD MATRIX':44,'MOD':45,'FX':50,'MIX':60,'VOICE':70,'PERFORM':80}
def group(p,engine):
 key=p.get('key','').lower();label=p.get('edit_name',p.get('name','')).lower();cat=p.get('category','').lower()
 # Six operators and dual channels retain their original signal-path identity.
 op=re.search(r'(?:operator|op)\s*(\d)',cat)
 if op:return ('OP'+op[1]+(' ENV' if 'env' in cat else ' KEYS' if 'kbd' in cat else ''),100+int(op[1])*3+(1 if 'env' in cat else 2 if 'kbd' in cat else 0))
 osc=re.fullmatch(r'osc\s+([ab12])',cat)
 if osc:return ('OSC '+osc[1].upper(),100+{'a':1,'b':2,'1':1,'2':2}[osc[1]])
 base=None
 if cat.startswith('source '):return ('SOURCE FX',850)
 if 'mod matrix' in cat:base='MOD MATRIX'
 elif 'patchbay' in cat:base='PATCHBAY'
 elif cat.startswith('mod env'):return (cat.upper(),330+int(re.search(r'\d+',cat)[0]) if re.search(r'\d+',cat) else 330)
 elif 'filter env' in cat:base='FILTER ENV'
 elif 'pitch eg' in cat:base='PITCH ENV'
 elif cat.startswith('lfo') or 'track lfo' in cat:
  n=re.search(r'\d+',cat);return ('LFO'+(' '+n[0] if n else ''),400+int(n[0]) if n else 400)
 elif cat in ('arp','arpeggiator','performance','motion'):base='PERFORM'
 elif cat in ('delay','reverb','chorus','phaser','compressor','distortion','insert','global fx','mod fx','fx','effects'):return (cat.upper().replace('GLOBAL FX','FX'),500+{'delay':2,'reverb':3,'chorus':1,'compressor':5}.get(cat,0))
 # Names come from the original contract, enriched with readable source labels.
 text=' '.join((key,label,cat))
 if base is None:
  if re.search(r'\b(model|algorithm|machine)\b',text) or key.endswith('_model'):base='MODEL'
  elif 'filter env' in label or re.search(r'vcf.*(attack|decay|sustain|release)',label):base='FILTER ENV'
  elif re.search(r'\b(attack|decay|sustain|release|hold|tail|envelope)\b',label) or re.search(r'(?:^|_)(?:atk|dcy|sus|rel|decay|e[12]_)',key) or cat in ('amp env','env','envelopes','envelope','velocity eg'):base='AMP ENV' if 'amp' in cat or 'amp ' in label else 'ENV'
  elif re.search(r'\b(cutoff|resonance|filter|hpf|lpf|vcf)\b',text) and 'lfo' not in label:base='FILTER'
  elif 'ring_' in key:base='RING FX'
  elif re.search(r'\b(reverb|delay|chorus|phaser|compressor|drive|crush|distortion|fx)\b',text) or key.startswith(('rev_','dly_','fx_')):base='FX'
  elif 'lfo' in text or key.startswith('mg_'):base='LFO'
  elif cat.startswith(('osc','dco','vco')) or re.search(r'\b(oscillator|wave|pulse|pwm|range|detune|harmonics|fine|sub)\b',label):base='OSC'
  elif cat in ('mixer','noise / mix','output') or re.search(r'\b(level|volume|pan|mix)\b',label):base='MIX'
  elif re.search(r'\b(arp|gate|swing|prob|quantize|root|scale|legato|bend|glide|portamento|octave|velocity|pressure)\b',label):base='PERFORM'
  elif 'mod' in text or cat=='random':base='MOD'
  elif engine in ('Sophie','DRUM-X','Hortator','Acid Engine') or cat in ('tone','lpg','timbre','morph'):base='TONE'
  else:base='VOICE'
 order=ORDER.get(base,49 if base=='PATCHBAY' else 50 if base=='RING FX' else 34)
 channel=re.fullmatch(r'ch\s*(\d+)',cat)
 if channel:return ('CH'+channel[1]+' '+base, order*10+int(channel[1]))
 return base,order*10

def enrich(entry):
 for p in entry['parameters']:
  title,order=group(p,entry['name']);name=p.get('edit_name',p.get('name',''));raw=p.get('name','').upper()
  if entry['name']=='FMini-1' and p.get('category')=='FM Patch':
   # Original eng_fmini.c FG_* layout and ui_fmini.c panel definitions.
   m=re.fullmatch(r'([RWL])([123])',raw)
   if m:
    what={'R':'Range','W':'Wave','L':'Level'}[m[1]];p['edit_name']='OSC '+m[2]+' '+what
    title='MIX' if m[1]=='L' else 'OSC '+m[2];order=600 if m[1]=='L' else 100+int(m[2])*10
    if m[1]=='R':p['options']=['LO',"32'","16'","8'","4'","2'"]
    if m[1]=='W':p['options']=['Triangle','Shark','Saw','Square','Wide Pulse','Narrow Pulse','Sine']
   elif raw in ('F2','F3'):p['edit_name']='OSC '+raw[1]+' Detune';title='OSC '+raw[1];order=100+int(raw[1])*10
   elif raw=='LN':p['edit_name']='Noise Level';title='MIX';order=600
   elif raw=='TUNE':p['edit_name']='Master Tune';title='VOICE';order=700
   elif raw=='MMIX':p['edit_name']='Mod Source Mix';title='MOD';order=450
   elif raw=='KBD':p['edit_name']='Key Tracking';title='FILTER';order=200
   elif raw=='GLID':p['edit_name']='Glide Time';title='PERFORM';order=800
   elif raw.startswith(('DC2','DC3','BPM')) or raw in ('SW1','SW2','SLOT'):title='PATCH DATA';order=900
   elif raw in ('F.DEC','F.SUS'):p['edit_name']='Filter '+('Decay' if raw=='F.DEC' else 'Sustain');title='FILTER ENV';order=300
  if entry['name']=='Guru-600' and p.get('category')=='Synth':
   rename={'A WAV':'OSC A Wave','B WAV':'OSC B Wave','A FRQ':'OSC A Frequency','B FRQ':'OSC B Frequency','RES':'Resonance'}
   p['edit_name']=rename.get(raw,name)
   if raw.startswith(('A ','B ')):title='OSC '+raw[0];order=100+(raw[0]=='B')
   elif raw=='RES':title='FILTER';order=200
  if entry['name']=='Prophet' and p.get('category')=='Macro':
   names={'TUNA':'Tune A','TUNB':'Tune B','PWA':'Pulse Width A','PWB':'Pulse Width B','MIXA':'Level A','MIXB':'Level B','RES':'Resonance'}
   p['edit_name']=names.get(raw,name)
   if raw in ('TUNA','PWA') or raw=='FREQ A':title='OSC A';order=100
   elif raw in ('TUNB','PWB') or raw=='FREQ B':title='OSC B';order=101
   elif raw.startswith('MIX'):title='MIX';order=600
   elif raw=='RES':title='FILTER';order=200
  if p.get('category')=='Global FX':
   labels={'CRT':'Chorus Rate','CDP':'Chorus Depth','COLR':'Delay Color','SIZE':'Reverb Size','DAMP':'Reverb Damping','TIME':'Delay Time','FEEDBACK':'Delay Feedback','MIX':'Delay Mix'}
   if raw in labels:
    p['edit_name']=labels[raw];title='CHORUS' if raw in ('CRT','CDP') else 'REVERB' if raw in ('SIZE','DAMP') else 'DELAY';order={'CHORUS':501,'DELAY':502,'REVERB':503}[title]
  assert len(title)<=25
  p['edit_group']=title;p['edit_group_order']=order


def original_panel_order(entry):
 from pathlib import Path
 import json
 folders={"FMini-1":"fm1-fmini","Guru-600":"fm1-guru600","Prophet":"fm1-prophet"}
 folder=folders.get(entry["name"])
 rows=[]
 if folder:
  path=Path(__file__).resolve().parents[1]/"ports"/folder/"source-panels.json"
  if path.is_file():rows=json.loads(path.read_text())
 by_key={p["key"]:p for p in entry["parameters"]};seen=set()
 for row in rows:
  key=row["key"]
  if key in seen or key not in by_key:continue
  seen.add(key);p=by_key[key];p["source_panel"]=row["panel"]
  p["native_ui_order"]=row["family"]*10000+row["order"]
  p["category"]=row["panel"].replace("LFO 2","LFO Settings").replace("INSERT 2","Insert Mix").replace("P5 ","").replace("EDIT ","Tone ").replace("ENV DEST","Env Destination").replace("LFO DEST","LFO Destination")
  if entry['name']=='Prophet':
   if row['panel']=='P5 LFO':p['category']='Synth LFO'
   elif row['panel'].startswith('LFO'):p['category']='Track '+p['category']
 for p in entry["parameters"]:
  if "native_ui_order" in p:continue
  group=p["edit_group"].upper();order=p["edit_group_order"]
  family=1 if "ENV" in group else 2 if "LFO" in group or (group=="MOD" or group.startswith("MOD ")) else 3 if group in ("FX","DELAY","REVERB","CHORUS","SOURCE FX","INSERT","SLICER","RING FX","COMPRESSOR") else 4 if group in ("PERFORM","PATCH DATA") else 0
  p["native_ui_order"]=family*10000+order

 if entry['name'] in ('FMini-1','Guru-600','Prophet'):
  from presentation_metadata import arrays
  path=Path(__file__).resolve().parents[1]/'ports'/folders[entry['name']]/'original/firmware/src/params.c'
  tables=arrays(path.read_text())
  for p in entry['parameters']:
   raw=p['name'];m=re.fullmatch(r'(SRC|DST|AMT)([1-4])',raw)
   if m:
    what={'SRC':'Source','DST':'Destination','AMT':'Amount'}[m[1]]
    p['edit_name']=what;p['category']='Mod Matrix '+m[2];p['native_ui_order']=20500+int(m[2])*3+{'SRC':0,'DST':1,'AMT':2}[m[1]]
    if m[1] in ('SRC','DST'):p['options']=tables['N_MSRC' if m[1]=='SRC' else 'N_MDST']
   if entry['name']=='FMini-1':
    rename={'EMPH':'Resonance','CNTR':'Env Amount','F.ATK':'Attack','F.DEC':'Decay','F.SUS':'Sustain','DST':'Drive','SLCR':'Mode','PAT':'Pattern','INSRT':'Type','ESYNC':'Time Sync','POL':'Polarity','INS A':'Control A','INS B':'Control B','INS C':'Control C'}
    if raw in rename:p['edit_name']=rename[raw]
    if raw in ('CUT','EMPH','CNTR'):p['category']='Filter'
    if raw in ('F.ATK','F.DEC','F.SUS'):p['category']='Filter Env'
    if raw=='SLOT':entry['hidden_keys'].append(p['key'])
    if p['category']=='Env Destination' and raw=='ESYNC':p['edit_name']='Time Sync'

 if entry['name'] in ('FMini-1','Guru-600','Prophet'):
  ps=entry['parameters'];allowed={r['key'] for r in rows}
  boundary=next(p['index'] for p in ps if (entry['name']=='FMini-1' and p['name']=='R1') or (entry['name']=='Guru-600' and p['name']=='A WAV') or (entry['name']=='Prophet' and p['name']=='CUT' and p['minimum']==-63))
  for p in ps:
   i=p['index'];raw=p['name']
   supported=p['key'] in allowed or i==1 or bool(re.fullmatch(r'(SRC|DST|AMT)[1-4]',raw))
   if 0<i<boundary and not supported:entry['hidden_keys'].append(p['key'])
   if entry['name']=='Prophet' and (2<=i<=8 or 97<=i<=108 or 112<=i<=116):entry['hidden_keys'].append(p['key'])
   if entry['name']=='FMini-1':
    if raw in ('F2','F3','SW1','SW2','DC2L','DC2H','DC3L','DC3H','BPML','BPMH'):entry['hidden_keys'].append(p['key'])
    if raw.startswith('OSC ') and raw.endswith('Detune Cents'):p['category']=raw[:5];p['edit_name']='Detune';p['unit']='ct';p['native_ui_order']=100+int(raw[4])*10+3
    if raw.startswith('OSC ') and raw.endswith(' On'):p['category']=raw[:5];p['edit_name']='On';p['native_ui_order']=100+int(raw[4])*10+4
    if raw in ('Noise On','Pink Noise'):p['category']='Mixer';p['edit_name']=raw;p['native_ui_order']=180
    if raw in ('Mod to Osc','Mod to Filter','LFO Square'):p['category']='LFO';p['edit_name']=raw;p['native_ui_order']=20200
    if raw in ('Mod Wheel','Pitch Bend Range','Glide On'):p['category']='Performance';p['edit_name']=raw;p['native_ui_order']=40000
    if raw in ('Filter Release','Release Follows Decay'):p['category']='Filter Env';p['edit_name']=raw.replace('Filter ','');p['native_ui_order']=10100
    for prefix in ('Drive','Chorus','Delay','Reverb'):
     if raw.startswith(prefix+' '):p['category']=prefix;p['edit_name']=raw[len(prefix)+1:];p['native_ui_order']=30000+{'Drive':20,'Chorus':40,'Delay':60,'Reverb':80}[prefix]
   if entry['name']=='Prophet' and i>=186:
    lane=(i-186)//5+1;field=(i-186)%5;p['category']='Shared FX '+str(lane);p['edit_name']=['Type','Mix','Rate','Character','Tone'][field];p['native_ui_order']=31000+lane*10+field
    # Original audio-only IDs retain holes for the retired/MIDI effects.
    # Four drive shapes need distinct names in a flat parameter list.
    if field==0:
     p['options']=list(tables['N_AUDIO_FX'])
     p['options'][12:16]=['Soft Drive','Hard Drive','Fold Drive','Fuzz Drive']
     p['option_indices']=[n for n,label in enumerate(p['options']) if label]
    if field in (2,3,4):
     p['dynamic_selector']=186+(lane-1)*5
     labels=[['Rate']*20,['Character','Depth','Depth','Focus','Jitter','Bite','Repeat','Decay','Damping','Depth','','','Tone','Tone','Tone','Tone','Alias','Depth','Depth','Depth'],['Tone']*20][field-2]
     if field==2:
      labels[7:9]=['Size','Size']
      labels[12:16]=['Drive']*4
      labels[16]='Bits'
     if field==4:
      labels=['-']*20
      labels[7]=labels[8]='Wet Tone'
      for n in (17,18,19):labels[n]='Resonance'
     labels[0]='-'
     p['dynamic_labels']=labels
  entry['hidden_keys']=sorted(set(entry['hidden_keys']))
