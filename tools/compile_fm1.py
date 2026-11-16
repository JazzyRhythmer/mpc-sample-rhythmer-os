#!/usr/bin/env python3
"""Compile original FM-1 synthesis units through the existing native wrapper."""
import json
from public_factory_data import write_empty_bank
from pathlib import Path
import shutil
import subprocess as sp
import sys
import re
import xml.etree.ElementTree as ET
from compile_moves import compile_wrapper,ROOT,WORK,MV
from prepare_drumx import function

def build(ident):
    from release_profile import require_port
    require_port("fm1-"+ident)
    p=ROOT/'ports'/('fm1-'+ident);cfg=json.loads((p/'vst.json').read_text());pin=json.loads((p/'SOURCE.json').read_text())
    out=p/'build';out.mkdir(parents=True,exist_ok=True)
    flags=['-std=gnu11','-O2','-fwrapv','-fPIC','-fvisibility=hidden','-DFM1_S1='+str(int(ident=='s1vave')),
        '-I'+str(p/'original'),'-I'+str(out),'-I'+str(ROOT/'ports/common')]
    for header in {'fm106':['fm106_presets.h'],'s1vave':['obv_patches.h'],'cs1':['cs1_presets.h','cs1_sounds_conv.h']}.get(ident,[]):shutil.copy2(p/'original'/header,out/header)
    if ident=='guru600':
        for header in ('p600_bank.h','p600_sci.h'):shutil.copy2(p/'original/firmware/src'/header,out/header)
    if ident=='kwasub-kit':flags.append('-DFM1_KWASUB_KIT=1')
    if ident=='prophet':
        flags+=['-DMELODEE_DUAL_CORE=0','-DMELODEE_RAM_AUDIO=0','-DMELODEE_USB_HOST=0','-DMELODEE_BLE=0',
            '-DRES_OK()=1','-ffunction-sections','-fdata-sections','-Wl,--gc-sections',
            '-I'+str(p/'original/firmware/src'),'-DFM1_HYDRA='+'0']
        for tool,header in [('gen_tables.py','melodee_tables.h'),('gen_fm6_patches.py','melodee_fm6.h')]:
            sp.run([sys.executable,str(p/'original/tools'/tool),str(out/header)],check=True)
        if (p/'original/tools/gen_909_tables.py').is_file():sp.run([sys.executable,str(p/'original/tools/gen_909_tables.py'),str(out/'x0x_drum_tables.h')],check=True)
        write_empty_bank('prophet',out/'melodee_prophet_factory.h')
        (out/'melodee_cz1.h').write_text('#define CZ_FACTORY_N 1u\nstatic const uint8_t CZ_DICT[144]={0},CZ_LZ[144]={0};\nstatic const uint16_t CZ_LZ_AT[2]={0};\nstatic const struct {uint8_t k;char name[13];} CZ_SHORT[1]={{0,"Init"}};\n')
        (out/'melodee_j106.h').write_text('#define J106_FACTORY_N 0u\nstatic const struct {uint8_t raw[J106_RAW];char name[21];} J106_FACTORY[1]={{{0},"Init"}};\n')
        host=(p/'original/tests/hostsim.c').read_text();end=host.index('#include "../firmware/src/mix.c"')+len('#include "../firmware/src/mix.c"')
        prefix=host[host.index('#define __attribute__(x)'):end].replace('"../firmware/','"firmware/')
        (out/'fm1_core.h').write_text(prefix+'\n#undef __attribute__\n')
        # Only the original sound/preset helper is retained; firmware sequence,
        # USB, key scanning, display and storage code are not in the prefix.
        helpers='\n'.join(function(host,f) for f in ('host_preset_values','host_preset_req','host_preset'))
        seq=(p/'original/firmware/src/seq.c').read_text()
        helpers='\n'.join(function(seq,f) for f in ('scale_mask','scale_count'))+'\n'+helpers
        (out/'preset_helpers.h').write_text(helpers)
    if ident in ('fmini','guru600'):
        flags+=['-DFELUCCA_CPU2=0','-DFELUCCA_FLASH=0','-I'+str(p),
            '-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-I'+str(p/'original'),'-I'+str(p/'original/firmware/src')]
        if ident=='fmini':flags.append('-DFELUCCA_FMINI_ONLY=1')
        else:
            flags+=['-DFELUCCA_P600=1','-DFELUCCA_SLICE=1']
            (out/'felucca_samples.h').write_text('''#define SMP_NSETS 4u
#define SMP_SET_NAMES_INIT "Empty","Empty","Empty","Empty"
static const uint8_t SMP_DATA[1]={0};
static const uint8_t SMP_SET_ORIG[4]={0,1,2,3};
static const smp_zone_t SMP_ZONES[1]={{0}};
static const smp_set_t SMP_SETS[4]={{"Empty",0,1},{"Empty",0,1},{"Empty",0,1},{"Empty",0,1}};
static const preset_t SMP_PRESET_TABLE[1]={{0}};
#define SMP_NPRESETS 1u
#define SLC_BREAK_INIT {0}
#define SLC_PIANO_INIT {0}
''')
        for tool,header in [('gen_tables.py','felucca_tables.h'),('gen_fm6_patches.py','felucca_fm6.h')]:
            sp.run([sys.executable,str(p/'original/tools'/tool),str(out/header)],check=True)
        host=(p/'original/tests/hostsim.c').read_text()
        end=host.index('#include "../firmware/src/fx.c"')+len('#include "../firmware/src/fx.c"')
        prefix=host[host.index('#define __attribute__(x)'):end].replace('"../firmware/','"firmware/')
        (out/'fm1_core.h').write_text(prefix+'\n#undef __attribute__\n')
        helpers='\n'.join(function(host,f) for f in ('host_tracks_init','host_preset_values','host_preset_req','host_preset'))
        (out/'preset_helpers.h').write_text(helpers)
        if ident=='guru600':
            ui=(p/'original/firmware/src/ui.c').read_text()
            (out/'original_preset_params.h').write_text('/* GPL-3.0-only: original Guru-600 preset loading */\n'+function(ui,'param_kept')+function(ui,'preset_params'))
        if ident=='fmini':
            src=re.sub(r'/\*.*?\*/','',(p/'original/firmware/src/eng_fmini.c').read_text(),flags=re.S)
            group=re.search(r'enum\s*\{\s*FG_R1(.*?)FG_NUM',src,re.S)
            names=['FG_R1']+re.findall(r'\bFG_[A-Z0-9]+\b',group.group(1))
            (out/'patch_names.h').write_text('static const char* patch_names[]={'+','.join(json.dumps(n[3:]) for n in names)+'};\n')
    if ident=='hortator':
        data=(p/'original/preset_bank.h').read_text();start=data.index('static const preset_t PRE_FACTORY[]');end=data.index('#define PRE_NFACT');
        (out/'original_presets.h').write_text('/* SPDX-License-Identifier: GPL-3.0-only; 2026 DEADACTIVE. Original factory data. */\n'+ 'typedef struct {uint8_t model;int8_t k[8];char name[9];} preset_t;\n'+re.sub(r'^.*\{DM_SMPL,.*\n','',data[start:end],flags=re.M)+'\n#define PRE_NFACT (sizeof PRE_FACTORY/sizeof PRE_FACTORY[0])\n')
        sp.run([sys.executable,str(p/'original/gen_tables.py'),str(out/'felucca_tables.h')],check=True)
        registry=(p/'original/dmodels.c').read_text().replace('#include "dm_sample.c"','')
        registry=registry.replace(' DM_SMPL,','').replace(' DM_SMPL_DEF,','').replace('"SAMPL", ','')
        (out/'registry.h').write_text(registry)
        (out/'pitch_helper.h').write_text(function((p/'original/eng_sample.c').read_text(),'pow2_q16'))
        # Original descriptor tables and DSP only; no firmware UI or sequencer.
        params=(p/'original/params.c').read_text()
        (out/'hortator_params.h').write_text(params[:params.index('/* (upstream 1.0.2, #48)')].replace('SMP_ALL_NAMES','N_DASH'))
        (out/'hortator_mix.h').write_text(function((p/'original/perform.c').read_text(),'pf_mix')+'\n#define SWING_MAX 100\n'+function((p/'original/drum_core.c').read_text(),'track_swing'))
        fx=(p/'original/fx.c').read_text()
        (out/'hortator_fx.h').write_text(fx[:fx.index('static void events_block')].replace('#include "perform.c"','/* Master performance uses the Rhythmer host. */'))

    if ident=='elixir':
        flags+=['-I'+str(p/'original/firmware/src')]
        sp.run([sys.executable,str(p/'original/tools/gen_tables.py'),str(out/'elixir_tables.h')],check=True)
        write_empty_bank('elixir',out/'factory_kits.h')
    if ident=='cs1':
        flags+=['-I'+str(p)]
        # The complete pinned original tone and sound tables are included directly.
        src=(p/'original/cs1.c').read_text()
        (out/'sounds.h').write_text(src[src.index('static const patch_t INIT_PATCH'):src.index('#define NSOUND')]+
            '\n#define NSOUND (sizeof SOUNDS / sizeof SOUNDS[0])\n'+
            function(src,'tone_load')+'\n#define DEF(v,d) ((v)?(v):(d))\n'+function(src,'sound_load'))
        raw=re.sub(r'/\*.*?\*/','',(p/'original/cs1_voice.h').read_text(),flags=re.S)
        structs=re.findall(r'typedef struct\s*\{(.*?)\}\s*(chan_patch_t|patch_t);',raw,re.S)
        fields={}
        for body,name in structs:
            fields[name]=[word.strip() for decl in re.findall(r'uint8_t\s+([^;]+);',body) for word in decl.split(',')]
        ranges={(kind,field):int(maximum) for kind,field,maximum in re.findall(r'\b(CH|GL)\(\s*(\w+)\s*,\s*"[^"]*"\s*,\s*(\d+)',src)}
        controls=[]
        for ch in range(2):
            for field in fields['chan_patch_t']:controls.append((f'Channel {ch+1} '+field,f'offsetof(patch_t,ch)+{ch}*sizeof(chan_patch_t)+offsetof(chan_patch_t,{field})',ranges.get(('CH',field),127)))
        for field in fields['patch_t']:controls.append((field,f'offsetof(patch_t,{field})',ranges.get(('GL',field),127)))
        (out/'controls.h').write_text('static const struct {const char *name;unsigned offset,max;} controls[]={\n'+
            '\n'.join('{'+json.dumps(n)+','+o+','+str(m)+'},' for n,o,m in controls)+'\n};\n')
    (out/'compile_flags.json').write_text(json.dumps(flags))
    sp.run(['gcc',*flags,'-shared',str(ROOT/'ports/common'/pin['adapter']),'-lm','-Wl,--no-undefined','-o',str(out/'dsp.so')],check=True)
    if ident in ('mono2k','fm106','s1vave','obervave','elixir','hortator','prophet','guru600','cs1'):
        sp.run([sys.executable,str(ROOT/'tools/check_factory_data.py'),ident],check=True)
    probe=WORK/'move-probes/probe'
    result=sp.run([str(probe),str(out/'dsp.so'),str(out)],capture_output=True,text=True,timeout=60,check=True)
    info=json.loads(result.stdout.split('RHYTHMER_PROBE_BEGIN\n',1)[1]);params=json.loads(info['chain_params'])
    for parameter in params:
        if parameter['name']=='FX Routing':parameter.update(type='enum',options=['CHAIN','SPLIT'])
        if parameter['name']=='Reverb Type':
            original=(p/'original/params.c' if (p/'original/params.c').is_file() else p/'original/firmware/src/params.c').read_text()
            candidates=re.findall(r'N_RTYPE\[\]\s*=\s*\{([^}]+)\}',original)
            choices=[re.findall(r'"([^"\n]+)"',x) for x in candidates]
            names=next(x for x in choices if len(x)==parameter['max']-parameter['min']+1)
            parameter.update(type='enum',options=names)

    if ident=='fmini':
        source=(p/'original/firmware/src/params.c').read_text()
        from presentation_metadata import arrays
        tables=arrays(source)
        options={'Drive Type':tables['N_DRVTYPE'],'Chorus Type':tables['N_CHOTYPE'],
                 'Pitch Bend Range':['+/-2 st','+/-12 st','+2 / -12 st','+2 / -24 st']}
        for parameter in params:
            name=parameter['name']
            if name in options:parameter.update(type='enum',options=options[name])
            if name in ('OSC 1 On','OSC 2 On','OSC 3 On','Noise On','Pink Noise','Mod to Osc','Mod to Filter','Glide On','LFO Square','High Pass On','Release Follows Decay'):parameter.update(type='enum',options=['Off','On'])
    if ident in ('fmini','guru600','prophet'):
        import source_panels
        source_panels.export(ident)
    if ident in ('fmini','guru600','prophet','s1vave','obervave'):
        for parameter in params[1:]:parameter['dynamic_display']=True
    (out/'probe.json').write_text(json.dumps(info,indent=2)+'\n')
    hierarchy={}
    if ident=='hortator':
        notes=[36,38,39,42,46,45,37,49];names=['Kick','Snare','Clap','Closed Hat','Open Hat','Tom','Rim','Cymbal']
        hierarchy={'pad_layout':'drums','levels':{str(i):dict(name=name,note=note) for i,(name,note) in enumerate(zip(names,notes))}}
        for parameter in params:parameter['dynamic_display']=True
        params[0].update(type='enum',options=['TRX Classic','808','909','Plaits','FM','Industrial'])
    if ident=='elixir':
        for parameter in params:parameter['dynamic_display']=True
    if ident=='elixir':
        names=['Kick','Low Tom','Percussion','Snare','Cymbal','Closed Hat','Open Hat'];notes=[36,45,47,38,49,42,46]
        hierarchy={'pad_layout':'drums','levels':{str(i):dict(name=n,note=k) for i,(n,k) in enumerate(zip(names,notes))}}
        bank=(out/'factory_kits.h').read_text();factory_names=re.search(r'FACTORY_NAMES\[[^;]+?=\s*\{(.*?)\};',bank,re.S).group(1);nfactory=int(re.search(r'#define FACTORY_NKITS (\d+)',bank).group(1));names=[bytes(int(v) for v in re.findall(r'\d+',row)).decode('ascii').strip() for row in re.findall(r'\{([^{}]+)\}',factory_names)][:nfactory];params[0].update(type='enum',options=names+['Initkit'])
    if ident=='kwasub-kit':
        names=['Kick','Snare','Clap','Closed Hat','Open Hat','Tom','Percussion','Cymbal']
        hierarchy={'pad_layout':'drums','levels':{str(i):dict(name=n,note=36+i) for i,n in enumerate(names)}}
        params[0].update(type='enum',options=['808','909','Dub Techno','Acoustic'])
    if ident=='mono2k':
        from original_banks import mono2k_models
        params[0].update(type='enum',options=mono2k_models())
        for parameter in params[1:-1]:parameter['dynamic_display']=True
    (p/'contract.json').write_text(json.dumps({'chain_params':params,'ui_hierarchy':hierarchy},indent=2)+'\n')
    compile_wrapper(p,cfg,ident)
    dest=WORK/'move-stage/Plugins'/('RHYTHMER - FM1 - '+ident+' - '+cfg['name']);dest.mkdir(parents=True,exist_ok=True)
    (dest/'module').mkdir(exist_ok=True)
    shutil.copy2(out/'dsp.so',dest/'module/dsp.so');shutil.copy2(out/cfg['so'],dest/cfg['so'])
    xml=ET.Element('PLUGIN',dict(name=cfg['name'],descriptiveName=cfg['name'],format='VST',category='Synth',
        manufacturer=cfg['vendor'],version='1.0',file='%payload-path%/'+dest.name+'/'+cfg['so'],
        uid=format(int.from_bytes(cfg['uid'].encode(),'big'),'x'),isInstrument='1',fileTime='0',
        infoUpdateTime='0',numInputs='0',numOutputs='2',isShell='0'))
    ET.ElementTree(xml).write(dest/'plugin-meta.xml',encoding='utf-8')
    if hierarchy:(dest/'drum-map.json').write_text(json.dumps(hierarchy,indent=2)+'\n')
    for f in ('LICENSE','LICENSING.md','NOTICE.md','SOURCE.json','VENDORED.md'):
        if (p/f).is_file():shutil.copy2(p/f,dest/f)
    shutil.copy2(MV/'LICENSE',dest/'Open-MPC-MIT-LICENSE.txt')
    shutil.copy2(ROOT/'ports/common/move-sdk/LICENSE',dest/'Schwung-API-MIT-LICENSE.txt')
    for relative,label in [('assets/kits/README.md','FACTORY_BANK_NOTICE.md'),('assets/prophet5-factory/README.md','FACTORY_BANK_NOTICE.md')]:
        if (p/'original'/relative).is_file():shutil.copy2(p/'original'/relative,dest/label)
    print('BUILT',ident,'controls',len(params),'peak',info['peak'],flush=True)
if __name__=='__main__':
    failed=[]
    for ident in sys.argv[1:]:
        try:build(ident)
        except Exception:
            import traceback
            traceback.print_exc();failed.append(ident)
    if failed:raise SystemExit('Failed: '+', '.join(failed))
