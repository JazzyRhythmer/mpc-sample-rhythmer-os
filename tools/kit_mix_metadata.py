"""Identify existing native voice-mix controls; never substitute a source master.

Only presentation changes. Native parameter indices, values and routing remain
unchanged. A missing native control is not replaced by an unrelated knob.
"""
import re

def enrich(engine):
    name=engine['name']
    single_volume={'CS-1':'p60','FM-106':'p16','FMini-1':'p1',
        'Guru-600':'p1','K-WASUB':'p99','MONO2K':'p14','OberVave':'p46',
        'Prophet':'p1','S1Vave':'p56','Aphex':'volume','Braids':'volume',
        'Dexed':'output_level','Hera':'volume','Frodhes':'p37','Tenebrae':'level','Acid Engine':'p10'}
    roles={'level':'volume','volume':'volume','pan':'pan','panning':'pan',
           'tune':'tune','pitch':'tune','decay':'decay'}
    for p in engine['parameters']:
        p.pop('kit_mix_role',None)
        key=p['key'];role=None
        if engine['drums'] and name=='K-WASUB' and key=='p1':p['category']='Source Output'
        if not engine['drums']:
            if key==single_volume.get(name):role='volume'
        elif name=='DRUM-X':
            m=re.fullmatch(r'l\d+_(level|pan)',key)
            if m:role=roles[m[1]]
        elif name=='Elixir':
            label=p.get('edit_name',p['name']).lower()
            if p.get('category')=='Voice' and label in ('volume','panning'):role=roles[label]
            elif p.get('category')=='Velocity EG' and label=='decay':role='decay'
        elif name=='Sophie':
            m=re.fullmatch(r'p\d\d_(level|tune|decay)',key)
            if m:role=roles[m[1]]
        elif name in ('Hortator','K-WASUB'):
            m=re.fullmatch(r'(?:Kick|Snare|Clap|Closed Hat|Open Hat|Tom|Rim|Cymbal|Percussion) (Level|Pan|Tune|TUNE|Decay|DECAY)',p.get('edit_name',p['name']))
            if m and (name!='Hortator' or m[1].lower() in ('level','pan')):role=roles[m[1].lower()]
        elif name=='TR-MPC':
            m=re.fullmatch(r's\d\d_(level|pan|tune|decay)',key)
            if m:role=roles[m[1]]
        elif name in ('6W6','8W8','9W9','CW-78') and not p.get('category'):
            m=re.fullmatch(r'.+_(level|volume|tune|pitch|decay)',key)
            if m:role=roles[m[1]]
        if role:p['kit_mix_role']=role
