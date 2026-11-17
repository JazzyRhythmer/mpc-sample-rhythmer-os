"""Read original source banks for source-built instruments; never invent patches."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def bank(port):
    if port.name=='fm1-frodhes':
        text=(port/'original/plugin/gen/params_map.h').read_text()
        strings=[json.loads('"'+x+'"') for x in re.findall(r'"((?:\\.|[^"\\])*)"',text.split('static const char *const FRP_TEXT',1)[1].split('};',1)[0])]
        row=next(l for l in text.splitlines() if '{0x10002u,' in l)
        values=re.findall(r'(?:0x[0-9a-fA-F]+|\d+)u',row)
        count=int(values[1][:-1])+1;offset=int(values[-1][:-1])
        names=strings[offset:offset+count];assert len(names)==57
        return [dict(name=n,program=i,note=60) for i,n in enumerate(names)]
    if port.name=='move-tenebrae':
        text=(port/'original/src/dsp/tenebrae_presets.h').read_text().split('static const tb_preset_t TB_PRESETS[] = {',1)[1]
        rows=re.findall(r'^\{\s*"([^"]+)",\s*"([^"]+)",\s*(\d+),\s*\{',text,re.M)
        assert len(rows)==164 and len({int(r[2]) for r in rows})==164
        return [dict(name=n,native_key='preset',native_value=str(i),note=60,source_category=cat,source_uid=int(uid)) for i,(n,cat,uid) in enumerate(rows)]
    return []
def enrich(engine):
    if engine['name']=='Frodhes':
        engine['gen_roles']=['chords','melody']
        for i,s in enumerate(engine['sounds']):
            n=s['name'].upper();s['gen_tags']=['bell','keys'] if 'VIB' in n else ['mallet','pluck'] if 'MARIMBA' in n or 'WOOD' in n else ['electric piano']+(['keys','chords'] if i else [])
    if engine['name']=='Tenebrae':
        for s in engine['sounds']:
            c=s['source_category'];s['gen_tags']=[c]+(['chords'] if c in ('pad','brass') else [])
