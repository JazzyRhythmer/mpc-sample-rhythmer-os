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
