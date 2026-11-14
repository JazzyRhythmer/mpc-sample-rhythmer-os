"""Source-backed labels and ownership; native keys, ranges and DSP stay intact."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORDS={'PW':'Pulse Width','PWM_SPD':'PWM Rate','VCF_LV':'Filter Level','HP_CUT':'HP Cutoff','HP_RES':'HP Resonance','LP_CUT':'LP Cutoff','LP_RES':'LP Resonance','F_IL':'Filter Env Initial','F_AL':'Filter Env Attack Level','F_A':'Filter Env Attack','F_D':'Filter Env Decay','F_R':'Filter Env Release','V_A':'Amp Attack','V_D':'Amp Decay','V_S':'Amp Sustain','V_R':'Amp Release','IT_BRILL':'Velocity Brightness','IT_LEVEL':'Velocity Level','AT_BRILL':'Pressure Brightness','AT_LEVEL':'Pressure Level','SUB TYP':'Sub Type','NOI MOD':'Noise Mode','SQR LVL':'Square Level','SAW LVL':'Saw Level','SUB LVL':'Sub Level','PWIDTH':'Pulse Width','FDBK':'Feedback','FENV':'Filter Env','MENV':'Mod Env','VEL':'Velocity','TYP':'Type','DIV':'Division','DDIV':'Division','LVL':'Level','SDEC':'Sweep Decay','CLIP':'Clip','SWEEP':'Sweep','PUNCH':'Punch','NOISE':'Noise','SUB':'Sub','RANGE':'Range','RESO':'Resonance','SQR':'Square','ATK':'Attack','DEC':'Decay','SUS':'Sustain','REL':'Release','GLD':'Glide','DLY':'Delay','REV':'Reverb','CHO':'Chorus','AMT':'Amount','TRIG':'Trigger','SRC':'Source','DST':'Destination','VOL':'Volume','MOD':'Mod','OCT':'Octave','SEMI':'Semitone','ATT':'Attack','COMP':'Compressor','DIST':'Distortion','SAT':'Saturation','NDECAY':'Noise Decay','PMOD':'Pitch Mod','WAVE':'Wave'}
WORDS.update({'LFO_SPD':'LFO Rate','LFO_VCO':'LFO Pitch','LFO_VCF':'LFO Filter','LFO_VCA':'LFO Amp','BRILL':'Brightness','PORTA':'Portamento','GLISS':'Glissando','PBEND':'Pitch Bend','AT_SPD':'Pressure Rate','AT_VCO':'Pressure Pitch','AT_VCF':'Pressure Filter','RM_MOD':'Ring Mod Amount','RM_SPD':'Ring Mod Rate','RM_DEPTH':'Ring Mod Depth','RM_A':'Ring Mod Attack','RM_D':'Ring Mod Decay','CHO_MODE':'Chorus Mode','CHO_SPD':'Chorus Rate','CHO_DEPTH':'Chorus Depth','AAT_DELAY':'Auto Pressure Delay','AAT_RISE':'Auto Pressure Rise','AAT_LEVEL':'Auto Pressure Level','AAT_FALL':'Auto Pressure Fall','RV_MIX':'Reverb Mix','RV_SIZE':'Reverb Size','RV_DAMP':'Reverb Damping','RV_SHIM':'Reverb Shimmer','RV_SHIFT':'Reverb Shift','KB_BL':'Key Brightness Low','KB_BH':'Key Brightness High','KB_LL':'Key Level Low','KB_LH':'Key Level High','DLY_FB':'Delay Feedback','DLY_PING':'Delay Ping Pong','PH_RATE':'Phaser Rate','PH_DEPTH':'Phaser Depth','PH_FB':'Phaser Feedback','PH_MIX':'Phaser Mix','EQ_LO':'EQ Low','EQ_HI':'EQ High','DRIVE_LV':'Drive Level','TIM':'Time','SPD':'Rate','DEST':'Destination'})
ACRONYMS={'FM','AM','PWM','LFO','DCO','VCO','VCF','VCA','HPF','LPF','HP','LP','EQ','FX','MIDI','OSC','S&H','ACID','TRX','EFM','MD','CS','LPG','EG','MG','ESP'}
def readable(text):
 if text.upper() in WORDS:return WORDS[text.upper()]
 return ' '.join(WORDS.get(w.upper(),w.upper() if w.upper() in ACRONYMS else w.title()) for w in text.replace('_',' ').split())
def arrays(source):
 return {name:re.findall(r'"([^"]*)"',body) for name,body in re.findall(r'static const char \*const (\w+)\[[^\]]*\]\s*=\s*\{(.*?)\};',source,re.S)}
def prepare_parameters(name,params):
 if name in ('6W6','8W8','9W9','CW-78'):
  families={}
  for p in params:
   if p.get('owner_notes'):families.setdefault(p['key'].split('_')[0],set()).update(p['owner_notes'])
  for p in params:
   prefix=p['key'].split('_')[0]
   if not p.get('owner_notes') and prefix in families:p['owner_notes']=sorted(families[prefix])
   if p['key']=='hh_choke':p['owner_notes']=sorted(families.get('ch',set())|families.get('oh',set()))
   if p['key']=='hat_choke':p['owner_notes']=[41,47,49] # original MA/TB/MB choke group

def voice_names(name,params,drum):
 if name not in ('6W6','8W8','9W9','CW-78'):return
 titles={'bd':'Kick','sd':'Snare','lt':'Low Tom','mt':'Mid Tom','ht':'High Tom','cp':'Clap','ch':'Closed Hat','oh':'Open Hat','chh':'Closed Hat','ohh':'Open Hat','hh':'Closed Hat','cy':'Cymbal','rs':'Rim','hc':'High Conga','mc':'Mid Conga','lc':'Low Conga','cl':'Claves','ma':'Maracas','hb':'High Bongo','lb':'Low Bongo','cb':'Cowbell','tb':'Tambourine','gu':'Guiro','mb':'Metal Beat','rc':'Ride','cc':'Crash'}
 for v in drum:
  if not v['name'].startswith('Voice '):continue
  matches=[p['key'].split('_')[0] for p in params if p.get('owner_notes')==[v['note']]]
  if matches:v['name']=titles.get(matches[0],readable(matches[0]))

def enrich(entry,port,params):
 ps=entry['parameters'];name=entry['name'];hidden=entry.setdefault('hidden_keys',[])
 if name in ('6W6','8W8','9W9','CW-78'):
  hidden.extend(p['key'] for p in ps if p['key']=='mutes' or p['key'].startswith('rhy_'))
  for p,raw in zip(ps,params):
   local=bool(raw.get('owner_notes'));key=p['key'];label=p['name']
   if local and '_' in key and not key.endswith('choke'):
    label=label.split(' ',1)[1] if ' ' in label else label
   p['edit_name']=readable(label)
   p['category']='' if local else 'Source Reverb' if key.startswith('rev_') else 'Source Delay' if key.startswith('dly_') else 'Source Mixer'
   if not local and key.startswith(('rev_','dly_')):p['edit_name']=readable(label.split(' ',1)[1])
 if port and port.name=='sophie':
  for p in ps:
   p['edit_name']=re.sub(r'^Pad \d+\s+','',p['name']);p['category']=''
 if port and port.name=='fm1-cs1':
  tables=arrays((port/'original/cs1.c').read_text())
  for p in ps:
   name=p['name'];m=re.match(r'Channel (\d+) (.*)',name)
   field=m[2] if m else name
   if m:p['category']='Ch '+m[1]
   p['edit_name']=readable(field)
   table={'feet':'N_FEET','wave':'N_WAVE','lfo_wave':'N_LWAVE','lfo_sync':'N_LDIV','dly_sync':'N_DIV','cho_mode':'N_CHO','gliss':'N_ONOFF','dly_ping':'N_ONOFF'}.get(field)
   if table:p['options']=tables[table]
   if field=='feet':p['edit_name']='Range'
 if port and port.name in ('fm1-obervave','fm1-s1vave'):
  source=(port/'original/obv_params.h').read_text();tables=arrays(source)
  kinds={'K_ONOFF':['Off','On'],'K_WAVE':tables.get('WAVE_NAME'), 'K_FTYPE':tables.get('FTYPE_NAME'),'K_MODE':tables.get('MODE_NAME'),'K_LSHAPE':tables.get('LSHAPE_NAME'),'K_LPHASE':tables.get('LPHASE_NAME'),'K_TO':tables.get('TO_NAME'),'K_ARP':tables.get('ARP_NAME'),'K_DIV':tables.get('DIV_NAME'),'K_DDIV':tables.get('DDIV_NAME')}
  for kind,table in {'RANGE':'RANGE','SUBTYPE':'SUB','NOISEM':'NOISEM','PWMS':'PWMS','DRAWSW':'DRAWSW','ENVTRG':'ENVTRG','AMP':'AMP','LFOWAVE':'LFOWAVE','RISERM':'RISER','CHOM':'CHORUS','REVM':'REVERB','PMODE':'POLY','PORTAM':'PORTA','FLTCOL':'FLTCOL','FXMODE':'FXMODE'}.items():kinds['K_'+kind]=tables.get(table+'_NAME')
  defs=re.findall(r'\[P_\w+\]\s*=\s*\{\s*"[^"]+"\s*,[^,]+,[^,]+,\s*(K_\w+)\s*,',source)
  assert len(defs)==len(ps)-1,(port.name,len(defs),len(ps))
  for p,kind in zip(ps[1:],defs):
   options=kinds.get(kind)
   if options:
    if len(options)==p['maximum']-p['minimum']+1:p['options']=options
    elif kind!='K_DDIV':raise AssertionError((port.name,p['key'],kind))
   p['edit_name']=readable(p.get('edit_name',p['name']))
 if port and port.name=='fm1-kwasub':
  source=(port/'original/ksub_data.c').read_text();tables=arrays(source)
  body=source.split('static const char *const ENG_P[NENG][3] = {',1)[1].split('};',1)[0]
  models=re.findall(r'"([^"]+)"',body);extra=tables['ENG_P4'];assert len(models)==33 and len(extra)==11
  for p in ps:
   if p['index']==117:p['category']='Compressor'
   if p['index']==118:p['category']='Reverb';p['options']=tables['L_RVT']
   if p['index']==119:p['category']='Delay';p['options']=tables['L_DLT']
   raw=p['name'];label=re.sub(r'^[AB] ','',raw) if p['category'] in ('Osc A','Osc B') else re.sub(r'^\d+ ','',raw)
   p['edit_name']=readable(label)
   if p['category']=='Mod Matrix':
    slot=re.match(r'(\d+) ',raw)
    if slot:p['category']='Mod Matrix '+slot[1]
   if raw in ('A ENGINE','B ENGINE'):
    p['options']=tables['L_ENG'];p['option_indices']=[i for i,n in enumerate(tables['L_ENG']) if n!='-']
   direct={'SUB WAVE':'L_SUBW','SUB OCTAVE':'L_SUBO','SUB ROUTE':'L_ROUTE','KEY RESET':'L_ONOFF'}
   table=direct.get(raw)
   if p['category']=='Filter' and raw=='TYPE':table='L_FT'
   if p['category']=='Noise / Mix' and raw=='MODE':table='L_XMODE'
   if p['category'].startswith('LFO '):table={'SHAPE':'L_SHAPE','SYNC':'L_ONOFF','RATE / SYNC':'L_DIV','DEST':'L_DST','RETRIG':'L_TRIG'}.get(raw,table)
   if table and len(tables[table])==p['maximum']-p['minimum']+1:p['options']=tables[table]

   match=re.fullmatch(r'([AB]) P([1-4])',raw)
   if match:
    p['dynamic_selector']=1 if match[1]=='A' else 9;col=int(match[2])-1
    p['dynamic_labels']=[readable(models[i*3+col] if col<3 else extra[i]) for i in range(11)]
 if name=='TR-MPC':
  for p in ps:
   if p['key'].endswith('_fam'):p['edit_name']='Drum family'
   if p['key'].endswith('_src'):p['edit_name']='Voice type'
 for p in ps:
  if p.get('category'):p['category']=readable(p['category'])
 if port and port.name=='fm1-fm106':
  for p in ps:
   if p['name'] in ('Pulse On','Saw On','Sub On','Chorus I','Chorus II','Reverb On') and p['maximum']==1:p['options']=['Off','On']
 if port and port.name=='drumx':
  for p in ps:
   if p['key'].endswith('_wave'):p['options']=['Sine','FM','Metal','Bell'] # DXW_* in drumx_voice.c
   if p['key'].endswith('_filter'):p['options']=['Low Pass','Band Pass','High Pass'] # DXF_*
   if p['key'].endswith('_pmod') and p['maximum']==3:p['options']=['Decay','Long','Noise','Sine'] # DXM_*
 if port and port.name=='move-dexed':
  for p in ps:
   if p['key'].endswith('_osc_mode'):p['options']=['Ratio','Fixed'] # original dx7_plugin.cpp
   if p['key']=='lfo_wave':p['options']=['Triangle','Saw Down','Saw Up','Square','Sine','S&H'] # msfa/lfo.cc
 if port and port.name=='move-hera':
  for p in ps:
   if p['key']=='vca_type':p['options']=['Envelope','Gate']
   if p['key']=='pitch_range':p['options']=['-1 octave','Normal','+1 octave'] # native factors 0.5,1,2
 if port and port.name in ('fm1-fmini','fm1-guru600','fm1-prophet'):
  path=next((port/'original').rglob('params.c'));table=arrays(path.read_text()).get('N_LWAVE')
  candidates={};unsupported=set();all_tables=arrays(path.read_text());track_body=path.read_text().split('static const param_desc_t TP[P_COUNT] = {',1)[1].split('};',1)[0]
  for label,array in re.findall(r'PE\("([^"]+)",\s*(\w+)',track_body):
   values=all_tables.get(array)
   if values:
    candidates.setdefault((label,len(values)),set()).add(tuple(values))
    if array in ('N_SMODE','N_FTYPE'):unsupported.add((label,len(values)))
  boundary=117 if port.name=='fm1-prophet' else 109
  for p in ps:
   if p['index']<boundary:
    found=candidates.get((p['name'],p['maximum']-p['minimum']+1),set())
    if len(found)==1:p['options']=list(next(iter(found)))
    if (p['name'],p['maximum']-p['minimum']+1) in unsupported:hidden.append(p['key'])
   if p['index']==11 and table and p['maximum']==len(table)-1:p['options']=table
 if port and port.name=='fm1-prophet':
  table=arrays((port/'original/firmware/src/prophet_edit.h').read_text())['P5_FILTER_NAMES']
  for p in ps:
   if p['index']==145:p['edit_name']='Filter Model';p['options']=table
 if port and port.name=='fm1-kwasub':
  for p in ps:
   if p['index']==77:p['options']=tables['L_DRT']
   if p['index']==100:p['options']=tables['L_VM']
 if port and port.name=='fm1-fm106':
  named={'DCO Range':["16'","8'","4'"],'Arp Mode':['Up','Up / Down','Down'],'PWM Mode':['LFO','Manual'],'Filter Polarity':['Positive','Inverted'],'VCA Mode':['Envelope','Gate'],'FX Type':['Off','Tape']}
  for p in ps:
   if p['name'] in named:p['options']=named[p['name']]
 # Explicit source labels remain the authority for algorithm-dependent engines.
 if port and port.name not in ('fm1-hortator','fm1-elixir','fm1-mono2k','sophie','fm1-kwasub','fm1-cs1'):
  for p in ps:
   if p.get('edit_name'):p['edit_name']=readable(p['edit_name'])
 hidden[:]=sorted(set(hidden))
