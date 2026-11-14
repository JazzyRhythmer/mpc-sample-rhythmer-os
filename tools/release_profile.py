"""Authoritative engine selection for this release."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def profile():
    return json.loads((ROOT/'config/first-release-candidates.json').read_text())
def require_port(name):
    if name not in profile()['active_ports']:
        raise ValueError('Engine is not included in this release: '+name)
