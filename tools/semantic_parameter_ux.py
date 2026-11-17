"""Final presentation reconciliation after original FM-1 panel ownership.

The original native keys/ranges/state remain intact. Grouping must use the
final category, not the category that preceded source-panel reconstruction.
"""
import re

def enrich(engine):
    name=engine['name']
    for p in engine['parameters']:
        raw=p['name'];cat=p.get('category','');upper=cat.upper()
        if name=='Tenebrae' and p.get('type')=='float' and p.get('unit')=='%':
            p['display_native_percent']=True
        if name=='Frodhes':
            if p['index']==25 and p.get('dynamic_labels'):p['dynamic_labels'][5]='Hand Mute'
            if 54<=p['index']<=58:p['edit_group']='MOTOR';p['edit_group_order']=410
        if name not in ('FMini-1','Guru-600','Prophet'):continue
        if raw=='POL' and 'LFO' in upper:
            p['edit_name']='Polarity';p['options']=['Bipolar','Unipolar']
        if raw in ('KBD','KEY') and upper=='FILTER' and p['minimum']==0 and p['maximum']==2:
            p['edit_name']='Key Tracking';p['options']=['Off','Half','Full']
        if upper=='SLICER':
            p['edit_name']={'SLCR':'Mode','PAT':'Pattern'}.get(raw,p.get('edit_name',raw))
            p['edit_group']='SLICER';p['edit_group_order']=480
        if upper in ('LFO','LFO SETTINGS','LFO DESTINATION') or upper.startswith('TRACK LFO'):
            p['edit_group']='EXTRA LFO' if name=='Prophet' else 'LFO'
            p['edit_group_order']=410 if name=='Prophet' else 400
        if upper=='SYNTH LFO':p['edit_group']='SYNTH LFO';p['edit_group_order']=400
        if upper in ('FLT ENV','FILTER ENV'):
            p['edit_group']='FILTER ENV';p['edit_group_order']=300
        if upper=='ENV':p['edit_group']='AMP ENV';p['edit_group_order']=310
        if upper=='ENV DESTINATION':p['edit_group']='ENV MOD';p['edit_group_order']=350
        if re.fullmatch(r'(SRC|DST|AMT)[1-4]',raw):
            p['category']='Mod '+raw[-1];p['edit_group']='MOD MATRIX';p['edit_group_order']=440
        if name=='FMini-1':
            osc=re.fullmatch(r'OSC ([123])',upper)
            if osc:
                p['edit_group']='OSC '+osc[1];p['edit_group_order']=100+int(osc[1])*10
                if raw.endswith(' On'):p['edit_name']='Enabled'
            if raw in ('L1','L2','L3'):
                p['category']='OSC';p['edit_group']='OSC LEVELS';p['edit_group_order']=190
            if raw in ('LN','Noise On','Pink Noise'):
                p['category']='Noise';p['edit_group']='NOISE';p['edit_group_order']=195
        # mel_family_native.c native_tempo overwrites this every audio block.
        # Project tempo is the editable authority, not a second synth BPM dial.
        if name=='Prophet' and raw=='BPM' and upper=='GLOBAL':
            engine.setdefault('hidden_keys',[]).append(p['key'])
    if 'hidden_keys' in engine:engine['hidden_keys']=sorted(set(engine['hidden_keys']))
