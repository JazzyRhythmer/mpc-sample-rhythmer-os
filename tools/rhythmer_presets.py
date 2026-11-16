"""Authored Rhythmer patches, distinct from unmodified upstream factory data."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def bank():return json.loads((ROOT/'config/rhythmer-factory-presets.json').read_text())
def normalized(row,params):
    bykey={p.get('key'):p for p in params};values={'0':0.0}
    for key,raw in row['values'].items():
        p=bykey[key];index=next(i for i,q in enumerate(params) if q.get('key')==key)
        lo,hi=p.get('min',p.get('minimum',0)),p.get('max',p.get('maximum',127))
        assert lo<=raw<=hi,(row['name'],key,raw,lo,hi)
        values[str(index)]=(raw-lo)/(hi-lo) if hi!=lo else 0.0
    return values
def programs(ident,params):
    title='INIT PROPHET' if ident=='prophet' else 'Initkit'
    rows=[dict(name=title,values={'0':0.0},origin='Original GPL engine initialization')]
    data=bank();expected=15 if ident=='prophet' else 4
    assert len(data[ident])==expected and len({x['name'] for x in data[ident]})==expected
    for row in data[ident]:rows.append(dict(name=row['name'],values=normalized(row,params),origin='Rhythmer original preset by jazzy rhythmer; GPL-3.0-only',description=row['description']))
    return rows
