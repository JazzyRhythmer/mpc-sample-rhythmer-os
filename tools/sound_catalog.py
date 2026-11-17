#!/usr/bin/env python3
"""Describe original engines for the single-sound and Rhythmer Kit host views.

No DSP or legacy plugin identities are changed. All indices refer to the
original VST parameter order; selectors use their original normalized range.
"""
import json

from edit_metadata import enrich
import presentation_metadata as presentation
import quick_metadata
import design_metadata
import kit_mix_metadata
import semantic_parameter_ux
import source_synth_metadata
from rhythmer_presets import programs as own_programs
from original_banks import elixir_kits,hortator_presets,mono2k_models,mono2k_library
import re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WORK = Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')

def voices(data):
    result = {}
    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get('note'), int):
                result.setdefault(x['note'], x.get('name', 'Voice'))
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(data)
    return [{'note': n, 'name': v} for n, v in result.items() if 0 <= n <= 127]

def role(voice):
    name=voice['name'].lower()
    for priority,words in enumerate((('kick','bass drum'),('snare',),('clap',),('closed','pedal','hh cl'),('open',),('tom','conga'),('rim','stick'),('crash','cymbal','ride','bell'))):
        if any(word in name for word in words):return priority
    return 8

def original_names(port):
    if not port:return []
    if port.name in ('fm1-frodhes','move-tenebrae'):return [s['name'] for s in source_synth_metadata.bank(port)]
    if port.name=='fm1-mono2k':return mono2k_models()+[x['name'] for x in mono2k_library()]
    simple={
        'fm1-fmini':('firmware/src/eng_fmini_presets.h','static const preset_t FMINI_PRESETS'),
        'fm1-obervave':('obv_patches.h','static const factory_t FACTORY'),
        'fm1-s1vave':('obv_patches.h','static const factory_t FACTORY'),
        'fm1-fm106':('fm106_presets.h','static const fm106_preset_t FM106_PRESETS'),
        'fm1-guru600':('firmware/src/p600_bank.h','static const preset_t P600_PRESETS'),
        'fm1-kwasub':('ksub_data.c','static const preset_t FACTORY'),
    }
    if port.name in simple:
        file,marker=simple[port.name];source=(port/'original'/file).read_text().split(marker,1)[1].split('};',1)[0]
        names=re.findall(r'(?:\{\s*|PR\()"([^"]+)"\s*,',source)
        return names
    if port.name=='fm1-cs1':
        source=(port/'original/cs1.c').read_text().split('static const sound_t SOUNDS[]',1)[1].split('#define NSOUND',1)[0]
        return re.findall(r'\.name\s*=\s*"([^"]+)"',source)+re.findall(r'\.name\s*=\s*"([^"]+)"',(port/'original/cs1_sounds_conv.h').read_text())
    if port.name=='fm1-prophet':
        return ['INIT PROPHET']
    return []

def hortator_models():
    source=(ROOT/'ports/fm1-hortator/original/dmodels.c').read_text().split('static const char *const N_MODEL',1)[1].split('};',1)[0]
    codes=[n for n in re.findall(r'"([^"]+)"',source) if n!='SAMPL']
    full={'BD':'Kick','SD':'Snare','TM':'Tom','CG':'Conga','CP':'Clap','RS':'Rim','CB':'Cowbell','CH':'Closed Hat','OH':'Open Hat','CY':'Cymbal','SH':'Shaker','CL':'Claves','B2':'Bass Drum 2','HH':'Hi-Hat'}
    def label(n):
        if n=='ACID':return 'ACID Bassline'
        for family in ('TRX','EFM'):
            if n.endswith(family):return 'MD '+family+' '+full.get(n[:-len(family)],n)+' ['+n+']'
        return {'K808':'808 Kick','K909':'909 Kick','S808':'808 Snare','S909':'909 Snare','C808':'808 Clap','C909':'909 Clap'}.get(n,n)
    return [label(n) for n in codes]

def generate():
    registry = []
    preset_metadata=json.loads((WORK/'sound-presets.json').read_text()) if (WORK/'sound-presets.json').is_file() else {}
    kits = json.loads((ROOT/'config/drum-kits.json').read_text())['factory_kits']
    ports = {json.loads(p.read_text())['so']: p.parent for p in (ROOT/'ports').glob('*/vst.json')}
    for folder in sorted((WORK/'sd-stage/Plugins').iterdir(),key=lambda p:p.name.replace('RHYTHMER - ','GROOVE - ',1)):
        allowed=json.loads((ROOT/'config/first-release-candidates.json').read_text())['engine_folders']
        if folder.name not in allowed or folder.name=='RHYTHMER - Acid Engine':continue
        meta = folder/'plugin-meta.xml'
        if not meta.is_file(): continue
        xml = ET.parse(meta).getroot()
        if xml.tag != 'PLUGIN': xml = xml.find('PLUGIN')
        so = Path(xml.attrib['file']).name
        port = ports.get(so)
        params = []
        config = {}
        if port:
            config = json.loads((port/'vst.json').read_text())
            contract = json.loads((port/config.get('module','contract.json')).read_text())
            ordered = (port/'params.lock').read_text().splitlines() if (port/'params.lock').is_file() else []
            bykey = {p['key']:p for p in contract.get('chain_params',[]) if 'key' in p}
            params = [bykey.get(k, {'key':k}) for k in ordered]
        if port and port.name=='fm1-elixir':
            descriptions=json.loads((ROOT/'config/elixir-parameter-metadata.json').read_text())
            if len(descriptions)!=len(params):raise RuntimeError('Elixir parameter metadata count changed')
            for parameter,description in zip(params,descriptions):
                parameter['category']=description.get('category','')
                if parameter.get('key')!='p0':parameter['options']=description.get('options',[])
        baseline=json.loads((ROOT/'config/baseline-parameters.json').read_text()).get(so) if (ROOT/'config/baseline-parameters.json').is_file() else None
        if baseline:params=baseline['parameters']
        drum = voices(json.loads((folder/'drum-map.json').read_text())) if (folder/'drum-map.json').is_file() else []
        if so == 'sophie.so':
            names = ['Kick','Rim','Snare','Clap','Snare 2','Low Tom','Closed Hat','Floor Tom','Pedal Hat','Mid Tom','Open Hat','Low Mid','High Mid','Crash','High Tom','Ride']
            drum = [{'note':36+i,'name':n} for i,n in enumerate(names)]
        classic={
            '6W6':[36,37,43,40,41,38,255,42],
            '8W8':[36,37,47,49,50,38,44,51],
            '9W9':[36,37,42,43,44,38,41,45],
            'CW-78':[36,37,255,39,255,255,38,40],
            'TR-MPC':list(range(36,44)),
        }.get(xml.attrib.get('name'))
        if classic:
            for lane,note in enumerate(classic):
                for voice in drum:
                    if voice['note']==note:voice['name']=['Kick','Snare','Clap','Closed Hat','Open Hat','Tom','Rim','Cymbal'][lane]
        presentation.prepare_parameters(xml.attrib.get("name"),params)
        presentation.voice_names(xml.attrib.get("name"),params,drum)
        sounds = []
        engine_kits = [k for k in kits if port and k['port'] == port.name]
        native=preset_metadata.get(so) or preset_metadata.get(so.replace('rhythmer-','groove-',1))
        if drum and native and native['count'] and not engine_kits:
            engine_kits=[dict(name=name or 'Kit '+str(i),index=i,native_key=native['selector']) for i,name in enumerate(native['names'])]
        if port and port.name=='fm1-elixir':
            engine_kits=[dict(name=k['name'],index=0,selector='p0',own_values=k['values'],origin=k['origin']) for k in own_programs('elixir',params)]
        drum=sorted(drum,key=role)
        if drum:
            for kit in engine_kits or [{'name':'Factory','index':0}]:
                routes=[]
                selector = kit.get('selector')
                indices = [i for i,p in enumerate(params) if p.get('key') == selector]
                selectors = {}
                if indices:
                    p = params[indices[0]]
                    top = len(p.get('options',[]))-1 if p.get('options') else p.get('max',1)
                    selectors[str(indices[0])] = kit['index']/max(1,top)
                selectors.update(kit.get('own_values',{}))
                for v,voice in enumerate(drum):
                    routes.append(len(sounds))
                    sound=dict(name=(kit['name']+' / ' if engine_kits else '')+voice['name'], note=voice['note'], values=selectors,**({'origin':kit['origin']} if kit.get('origin') else {}))
                    if kit.get('native_key'):sound.update(native_key=kit['native_key'],native_value=str(kit['index']))
                    sounds.append(sound)
        else:
            if native:
                for i,name in enumerate(native['names']):
                    sounds.append(dict(name=name or 'Preset '+str(i),note=60,native_key=native['selector'],native_value=str(native.get('programs',list(range(native['count'])))[i]),**({'native_setup':native['setups'][i]} if 'setups' in native else {})))
            selected = config.get('programs',{}).get('param')
            candidates = [(i,p) for i,p in enumerate(params) if p.get('key') == selected] if selected else []
            if not candidates:
                candidates = [(i,p) for i,p in enumerate(params) if any(w in (p.get('key','')+' '+p.get('name','')).lower() for w in ('preset','program','sound recipe','patch recipe')) and (p.get('options') or p.get('type') in ('int','integer'))]
            if not candidates and not native:
                candidates=[(i,p) for i,p in enumerate(params) if (p.get('key') in ('machine','model','engine') and p.get('options')) or (port and port.name=='fm1-mono2k' and i==0)]
            if port and port.name=='fm1-mono2k':candidates=[(0,params[0])]
            if candidates and not native:
                index,p = candidates[0]
                options = p.get('options') or []
                low,high = (0,len(options)-1) if options else (int(p.get('min',0)),int(p.get('max',0)))
                names=original_names(port)
                if port and port.name=='fm1-mono2k':names=mono2k_models()
                if names and len(names)!=high-low+1:raise RuntimeError('Original preset name count changed: '+port.name)
                for value in range(low, min(high+1,low+1024)):
                    sounds.append(dict(name=names[value-low] if names else options[value] if options else 'Preset '+str(value), note=60, values={str(index):(value-low)/max(1,high-low)}))

            if not sounds:sounds.append(dict(name='Init',note=60,values={},origin='Original engine initialization; no factory bank'))
        if port and port.name=='fm1-hortator':
            models=hortator_models()
            for i,p in enumerate(params):
                if 0<i<89 and (i-1)%11==0:p['options']=models
            originals=[x for x in hortator_presets() if x['model']!='DM_SMPL']
            sounds=[dict(name=x['name'],note=x['note'],native_key='p90',native_value=str(i),origin='Original Hortator factory bank',source_model=x['model']) for i,x in enumerate(originals)]
        if port and port.name=='fm1-mono2k':
            sounds=[dict(name=n,note=60,values={'0':i/15},origin='Original machine Init') for i,n in enumerate(mono2k_models())]
            roles={'CAT_KICK':0,'CAT_SNARE':1,'CAT_HATS':3,'CAT_PERC':7}
            for i,row in enumerate(mono2k_library()):
                drums=row['category'] in roles
                sounds.append(dict(name=row['name'],note=row['root'] if drums else 60,drums=drums,native_key='p72',native_value=str(i),origin='Original MONO2K SND library',source_root=row['root'],source_category=row['category'],**({'gen_role':4 if row['name']=='OPENHAT' else 7 if row['name'] in ('RIDE','CRASH') else roles[row['category']]} if drums else {})))
        # The three original MPC synths expose real VST programs rather than native selectors.
        program_file=ROOT/'config/baseline-programs.json'
        if not drum and program_file.is_file():
            programs=json.loads(program_file.read_text()).get(so,[])
            if programs:sounds=[dict(name=name,program=i,note=60) for i,name in enumerate(programs)]
        if port and port.name in ('fm1-frodhes','move-tenebrae'):sounds=source_synth_metadata.bank(port)
        if port and port.name=='move-plaits':
            table=json.loads((port/'model-controls.json').read_text());models=params[0]['options']
            for bank,names in enumerate(table['fm_banks']):
                sounds.extend(dict(name=models[bank+2]+' / '+name.strip(),note=60,native_setup=[['engine',str(bank+2)]],native_key='harmonics',native_value=str((i+.5)/(32*1.02)),origin='Original embedded Plaits 6-Op bank') for i,name in enumerate(names))
        if port and port.name=='fm1-prophet':sounds=[dict(x,note=60) for x in own_programs('prophet',params)]
        entry = dict(folder=folder.name, library=so, name=xml.attrib.get('name',folder.name), drums=bool(drum), voices=drum,
                     sounds=sounds, kit_names=[k['name'] for k in engine_kits],parameters=[dict(index=i,key=p.get('key',''),name=p.get('name',''),category=p.get('category',''),options=p.get('options',[]),type=p.get('type',''),unit=p.get('unit',''),minimum=p.get('min',0),maximum=p.get('max',len(p.get('options',[]))-1)) for i,p in enumerate(params)])
        entry['preset_parameters']=[i for i,p in enumerate(params) if p.get('name','').strip().lower() in ('factory program','factory preset','sound recipe','patch recipe') or any(sound.get('native_key')==p.get('key') for sound in sounds)]
        entry['preset_parameters'].extend(config.get('preset_parameters',[]))
        if port and port.name=='move-plaits':entry['preset_parameters']=[i for i in entry['preset_parameters'] if i!=1]
        if port and port.name=='fm1-hortator':
            entry['preset_parameters'].extend([0,89,90]);entry['native_pitch_parameter']=89;entry['lane_preset_key']='p90'
        if not drum:
            selectors=[next(iter(s['values'])) for s in sounds if len(s.get('values',{}))==1]
            if len(selectors)>1 and len(set(selectors))==1:entry['preset_parameters'].append(int(selectors[0]))

        if port and port.name=='fm1-mono2k':entry['preset_parameters']=[i for i in entry['preset_parameters'] if i!=0]
        if drum and params:
            owners=json.loads((ROOT/'config/elixir-parameter-owners.json').read_text()) if port and port.name=='fm1-elixir' else None
            for sound in sounds:
                note=sound['note'];indices=[]
                selected_name=next((v['name'] for v in drum if v['note']==note),'')
                scope_note=36 if port and port.name=='fm1-hortator' and note==60 else note
                for i,p in enumerate(params):
                    key=p.get('key','');name=p.get('name','');owner=None
                    if owners is not None:
                        owner=owners[i];wanted={36:0,45:1,47:2,38:3,49:4,42:5,46:5}[note]
                        if owner>=0 and owner!=wanted:continue
                    if port and port.name=='drumx':
                        m=re.match(r'l(\d+)_',key)
                        if m and int(m[1])!=note-36:continue
                    if port and port.name in ('fm1-hortator','fm1-kwasub-kit'):
                        if any(name.startswith(v['name']+' ') and v['note']!=scope_note for v in drum):continue
                    m=re.match(r'(?:pv|v|pad|s)(\d+)_',key)
                    if m and int(m[1])!=note-35:
                        control_note=entry.get('control_notes',{}).get(str(note),note)
                        if int(m[1])!=control_note-35 or key.endswith('_tune'):continue
                    if key in ('kit','p0') and (key=='kit' or port and port.name in ('fm1-elixir','fm1-hortator','fm1-kwasub-kit')):continue
                    if p.get('owner_notes') and note not in p['owner_notes']:continue
                    if key in ('note_map','ui_focus_level','ui_current_voice','ui_focus','link'):continue
                    if entry['name']=='TR-MPC' and key.startswith(('e_','edit_','rnd_')):continue

                    if key.startswith(('rnd_kit','save_kit')):continue
                    indices.append(i)
                sound['parameter_indices']=indices
        entry["name"]={"Elixir Kit":"Elixir","Hortator Kit":"Hortator","K-WASUB Kit":"K-WASUB Drums"}.get(entry["name"],entry["name"])
        entry["kit_only"]=entry["folder"] in json.loads((ROOT/'config/kit-only-engines.json').read_text())["folders"]
        if port:enrich(entry,port,contract)
        presentation.enrich(entry,port,params)
        quick_metadata.enrich(entry)
        source_names=json.loads((ROOT/'config/original-engine-names.json').read_text())['engines']
        original=next((n['original_name'] for n in source_names if n['port']==(port.name if port else 'sophie' if entry['library']=='sophie.so' else '')),entry['name'])
        if port and port.name=='fm1-kwasub-kit':entry['variant']='Drum mode'
        entry['name']=original
        if entry['name']=='TR-MPC':
            for parameter in entry['parameters']:
                if parameter['key'].startswith(('fx_','int_')):parameter['category']='Source FX'
        # Type is only needed while filtering source-only canvas controls.
        # Runtime values continue to come from the original plugin itself.
        for parameter in entry["parameters"]:
            parameter.pop("type",None)
            if not parameter.get("unit"):parameter.pop("unit",None)
        if port and port.name=='fm1-hortator':
            models=[['DM_KTRX','DM_SDTRX','DM_CPTRX','DM_CHTRX','DM_OHTRX','DM_XTTRX','DM_RSTRX','DM_CYTRX'],['DM_K808','DM_S808','DM_C808','DM_HATC','DM_HATO','DM_TOM','DM_RIM','DM_CYMB'],['DM_K909','DM_S909','DM_C909','DM_HATC','DM_HATO','DM_TOM','DM_RIM','DM_CYMB'],['DM_KBOOM','DM_SSNAP','DM_C909','DM_HMETL','DM_HNOIS','DM_MEMB','DM_CLAVE','DM_CYMB'],['DM_BDEFM','DM_SDEFM','DM_CPEFM','DM_HHEFM','DM_OHTRX','DM_XTEFM','DM_RSEFM','DM_CYEFM'],['DM_KPUNC','DM_SCRAK','DM_CPTRX','DM_HMETL','DM_HNOIS','DM_XTEFM','DM_CBEFM','DM_CYEFM']]
            entry['kit_sound_indices']=[[next(i for i,x in enumerate(originals) if x['model']==m) for m in kit] for kit in models]
        if port and port.name=='fm1-elixir':
            # Retain only the engine's GPL Initkit, with no external patch data.
            bank=own_programs('elixir',params);chosen=list(range(len(bank)))
            entry['kit_names']=[bank[i]['name'] for i in chosen]
            entry['kit_sound_indices']=[list(range(i*len(drum),(i+1)*len(drum))) for i in chosen]
        registry.append(entry)
    presets = []
    sophie=next(i for i,e in enumerate(registry) if e['library']=='sophie.so')
    extra=[i for i,v in enumerate(registry[sophie]['voices']) if role(v)>=5]
    for i,entry in enumerate(registry):
        if not entry['drums']: continue
        engine_kits=[dict(name=n) for n in entry['kit_names']]
        for k,kit in enumerate(engine_kits or [{'name':entry['name']} ]):
            routes=[];used=set()
            source_indices=entry.get('kit_sound_indices',[list(range(k*len(entry['voices']),(k+1)*len(entry['voices'])))])[k if 'kit_sound_indices' in entry else 0]
            available=[]
            for sound in source_indices:
                item=entry['sounds'][sound];v=next(v for v,x in enumerate(entry['voices']) if x['note']==item['note']);available.append((v,sound))
            for lane in range(8):
                voice=next((v for v,sound in available if role(entry['voices'][v])==lane),None)
                if voice is None:
                    voice=next(v for v,x in enumerate(registry[sophie]['voices']) if role(x)==lane)
                    routes.append(dict(engine=sophie,sound=voice))
                else:
                    used.add(voice);routes.append(dict(engine=i,sound=next(sound for v,sound in available if v==voice)))
            routes += [dict(engine=i,sound=sound) for v,sound in available if v not in used]
            while len(routes)<16:
                routes.append(dict(engine=sophie,sound=extra[len(routes)%len(extra)]))
            presets.append(dict(name=entry['name']+' / '+kit['name'] if engine_kits and entry['name']!=kit['name'] else kit['name'], routes=routes))
    # Reuse one ownership list per native voice instead of repeating hundreds
    # of identical integer arrays for every kit preset (small-device memory).
    for entry in registry:
        shared={}
        for sound in entry['sounds']:
            if 'parameter_indices' in sound:shared.setdefault(str(sound['note']),sound.pop('parameter_indices'))
        if shared:entry['voice_parameters']=shared
        for sound in entry['sounds']:sound['name']=sound['name'].strip()
        if any(s.get('requires_audio_input') for s in entry['sounds']):entry['selection']=[i for i,s in enumerate(entry['sounds']) if not s.get('requires_audio_input')]
    import copy
    hortator=next(e for e in registry if 'hortator' in e['folder'])
    acid=copy.deepcopy(hortator);acid.update(folder='RHYTHMER - Acid Engine',source_folder=hortator['folder'],name='Acid Engine',drums=False,voices=[],kit_names=[])
    acid['sounds']=[copy.deepcopy(s) for s in hortator['sounds'] if s.get('source_model')=='DM_ACID']
    assert len(acid['sounds'])==4
    acid['initial_values']={'89':1};acid['preset_parameters'].extend([0,1,89])
    acid['voice_parameters']=hortator.get('voice_parameters',{})
    acid['strip_voice_prefix']='Kick '
    for sound in acid['sounds']:sound['note']=60;sound['parameter_indices']=hortator['voice_parameters']['36']
    aphex=next(e for e in registry if e['name']=='Aphex')
    for name in json.loads((ROOT/'config/acid-aphex-presets.json').read_text())['presets']:
        source_index=next(i for i,s in enumerate(aphex['sounds']) if s['name']==name)
        sound=copy.deepcopy(aphex['sounds'][source_index])
        sound.update(source_engine=aphex['folder'],source_sound=source_index,origin='Original Aphex factory preset, unmodified native selector')
        acid['sounds'].append(sound)
    registry.append(acid)
    h_index=next(i for i,e in enumerate(registry) if e['name']=='Hortator')
    by_name={s['name']:i for i,s in enumerate(registry[h_index]['sounds'])}
    for kit in json.loads((ROOT/'config/hortator-md-kits.json').read_text())['kits']:
        assert len(kit['sounds'])==16
        presets.append(dict(name=kit['name'],source=kit['source'],routes=[dict(engine=h_index,sound=by_name[name]) for name in kit['sounds']]))
    selected=json.loads((ROOT/'config/first-release-candidates.json').read_text())
    elixir_names={e['name']+' / '+n for e in registry if e['name']=='Elixir' for n in e['kit_names']}
    presets=[k for k in presets if k['name'] in selected['kit_presets'] or k['name'] in elixir_names]
    assert len(registry)==len(selected['engine_folders']) and len(presets)==len(selected['kit_presets'])
    # Append new sources without changing numeric identities in saved kit routes.
    previous={i:e['folder'] for i,e in enumerate(registry)}
    if selected.get('source_order'):
        byfolder={e['folder']:e for e in registry}
        assert set(selected['source_order'])==set(byfolder)
        registry=[byfolder[folder] for folder in selected['source_order']]
        current={e['folder']:i for i,e in enumerate(registry)}
        for kit in presets:
            for route in kit['routes']:route['engine']=current[previous[route['engine']]]

    result = dict(schema=2,engines=registry,kits=presets)
    for entry in registry:
        source_synth_metadata.enrich(entry)
        quick_metadata.enrich(entry)
        design_metadata.enrich(entry)
        design_metadata.original_panel_order(entry)
        kit_mix_metadata.enrich(entry)
        semantic_parameter_ux.enrich(entry)
    target=ROOT/'config/sound-catalog.json'
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(len(registry),'engines;',len(presets),'kit presets')
    return result

if __name__ == '__main__': generate()
