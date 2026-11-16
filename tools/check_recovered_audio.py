"""Confirm restored control paths alter native output in independent processes."""
from pathlib import Path
import json,subprocess as sp,os
ROOT=Path(__file__).resolve().parents[1];WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os');probe=WORK/'plugins/native_signal_probe'
sp.run(['gcc','-O2',str(ROOT/'tools/probe_native_signal.c'),'-ldl','-o',str(probe)],check=True)
rows=[]
def run(ident,values,note):
 p=ROOT/'ports'/('fm1-'+ident);data=sp.check_output([str(probe),str(p/'build/dsp.so'),*[f'{k}={v}' for k,v in values.items()]],text=True,env=dict(os.environ,RHYTHMER_NOTE=str(note)))
 return json.loads(data.split('SIGNAL ',1)[1])
def check(ident,name,base,changed,note=60):
 a=run(ident,base,note);b=run(ident,dict(base,**changed),note);assert a['energy']>0 and b['energy']>0,(ident,name,'silent');assert a['hash']!=b['hash'],(ident,name,'did not reach audio');rows.append(dict(engine=ident,control=name,baseline=a,changed=b,passed=True));print('AUDIO',ident,name,'PASS',flush=True)
def byname(ident,values):
 p=ROOT/'ports'/('fm1-'+ident);ps=json.loads((p/'contract.json').read_text())['chain_params'];mapping={x['name']:x['key'] for x in ps};return {mapping[k]:v for k,v in values.items()}
def h(name,changed):check('hortator',name,{},byname('hortator',changed),36)
h('filter',{'Kick Filter Type':1,'Kick Filter Cutoff':24})
h('resonator',{'Kick Resonator Model':1,'Kick Resonator Mix':110,'Kick Resonator Decay':100})
h('insert',{'Kick Insert Type':1,'Kick Insert Mix':127,'Kick Insert A':110})
h('LFO',{'Kick LFO 1 Destination':9,'Kick LFO 1 Depth':64,'Kick LFO 1 Rate':110,'Kick LFO 1 Wave':1})
h('slicer',{'Kick Slicer Mode':1,'Kick Slicer Depth':127})
h('delay send',{'Kick Delay Send':127,'Delay Mix':127})
h('reverb send',{'Kick Reverb Send':127,'Reverb Size':100})
check('fmini','fine detune',{},byname('fmini',{'OSC 2 Detune Cents':213}))
check('fmini','drive type',byname('fmini',{'DST':100}),byname('fmini',{'Drive Type':1}))
check('fmini','chorus type',byname('fmini',{'CHO':127}),byname('fmini',{'Chorus Type':2}))
check('fmini','reverb type',byname('fmini',{'REV':127}),byname('fmini',{'Reverb Type':4}))
check('guru600','reverb type',byname('guru600',{'REV':127}),byname('guru600',{'Reverb Type':1}))
check('prophet','shared FX',{'p109':127,'p185':127},{'p186':7,'p187':127,'p188':80,'p189':80})
check('fm106','native arp',{},byname('fm106',{'Native Arp Enable':1}))
(WORK/'ui-native-rework/recovered-audio.json').write_text(json.dumps(rows,indent=2)+'\n')
