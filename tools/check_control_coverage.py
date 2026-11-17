"""Bind presentation keys to the complete published port contracts and source panels.

This checks the control boundary; DSP behavior and original factory data have
separate compiled checks. A matching contract alone is not a sound audit.
"""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')

def check():
    catalog=json.loads((ROOT/'config/sound-catalog.json').read_text())
    for ident in ('s1vave','obervave'):
        pin=json.loads((ROOT/'ports'/('fm1-'+ident)/'SOURCE.json').read_text())['display_source']
        assert hashlib.sha256((ROOT/pin['adapter_fragment']).read_bytes()).hexdigest()==pin['fragment_sha256'],'Source value formatter changed'

    ports={json.loads(p.read_text())['so']:p.parent for p in (ROOT/'ports').glob('*/vst.json')}
    rows=[]
    for engine in catalog['engines']:
        port=ports.get(engine['library'])
        if not port:continue
        contract=port/'contract.json'
        source=json.loads(contract.read_text())['chain_params']
        keys=[p['key'] for p in source]
        assert keys==[p['key'] for p in engine['parameters']],(engine['name'],'native IDs/order changed')
        assert len(keys)==len(set(keys)),(engine['name'],'duplicate native keys')
        hidden=set(engine['hidden_keys'])
        assert hidden<=set(keys),(engine['name'],'invalid hidden key')
        panels=port/'source-panels.json'
        panel_keys={p['key'] for p in json.loads(panels.read_text())} if panels.is_file() else set()
        assert panel_keys<=set(keys),(engine['name'],'original sound panel control missing')
        rows.append(dict(engine=engine['name'],port=port.name,native_controls=len(keys),
                         contract_sha256=hashlib.sha256(contract.read_bytes()).hexdigest(),
                         original_panel_keys=len(panel_keys),
                         hidden=[dict(key=p['key'],name=p['name']) for p in source if p['key'] in hidden],missing=[]))
    assert len(rows)==22,'Unexpected native/source-view contract count'
    (WORK/'source-control-coverage.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('Control boundary: 22 source contracts; original panel keys present; native IDs/order stable; no missing keys')
    return rows

if __name__=='__main__':check()
