#!/usr/bin/env python3
"""Gate excluded external banks in source, rebuilt modules and release archives."""
from pathlib import Path
import hashlib,json,re,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
def check(archives=()):
    omitted={}
    for ident,macro,header in [('prophet','P5_FACTORY_N','melodee_prophet_factory.h'),('elixir','FACTORY_NKITS','factory_kits.h')]:
        port=ROOT/'ports'/('fm1-'+ident);pin=json.loads((port/'SOURCE.json').read_text())
        excluded=pin['omitted_vendor_presets'];assert len(excluded)==(1 if ident=='prophet' else 117)
        assert not set(excluded)&set(pin['files'])
        for rel,sha in excluded.items():
            assert not (port/'original'/rel).exists(),('Excluded bank returned',ident,rel)
            omitted[sha]=(ident,rel)
        generated=WORK/'plugins/ports'/port.name/'build'/header
        assert re.search(r'#define '+macro+r'\s+0u?\b',generated.read_text()),('Bank still compiled',ident)
    c=json.loads((ROOT/'config/sound-catalog.json').read_text());byname={e['name']:e for e in c['engines']}
    assert [s['name'] for s in byname['Prophet']['sounds']]==['INIT PROPHET']+[p['name'] for p in json.loads((ROOT/'config/rhythmer-factory-presets.json').read_text())['prophet']]
    assert len(byname['Elixir']['sounds'])==35 and sum(s['name'].startswith('Initkit / ') for s in byname['Elixir']['sounds'])==7
    assert byname['Elixir']['kit_names']==['Initkit']+[p['name'] for p in json.loads((ROOT/'config/rhythmer-factory-presets.json').read_text())['elixir']]
    assert sum(len(e.get('selection',e['sounds'])) for e in c['engines'])==2659
    assert len(c['kits'])==36
    assert [k['name'] for k in c['kits'] if k['name'].startswith('Elixir / ')]==['Elixir / '+n for n in byname['Elixir']['kit_names']]
    byfolder={e['folder']:e for e in c['engines']}
    # All automatic GEN selections must refer to the same reduced catalogue.
    for e in json.loads((ROOT/'config/gen-engine-map.json').read_text())['engines']:
        choices=byfolder[e['folder']].get('selection',byfolder[e['folder']]['sounds'])
        assert all(n==-1 or 0<=n<len(choices) for n in e['programs'])
        assert all(n==-1 or 0<=n<len(choices) for n in e['recipes'])
    for path in archives:
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            for name in z.namelist():
                data=z.read(name)
                assert hashlib.sha256(data).hexdigest() not in omitted,('Excluded bank in archive',path,name)
                if re.search(r'(?:fm1-prophet|fm1-elixir)/original/assets/',name):
                    assert not name.lower().endswith(('.syx','.snd')),('Excluded asset path',name)
    print('Public bank gate: 118 external assets absent; zero compiled factory banks; 2659 selections (2616 original + 43 newly authored) / 36 kits; GEN indices valid;',len(archives),'archives checked')
if __name__=='__main__':check(sys.argv[1:])
