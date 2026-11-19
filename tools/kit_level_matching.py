"""Measured factory-kit mixing only. Original source presets stay unchanged."""
import json
from pathlib import Path

def apply(catalog):
    path=Path(__file__).resolve().parents[1]/"config/kit-level-matching.json"
    if path.exists():
        data=json.loads(path.read_text())
        catalog["kit_order_legacy"]=data["legacy_order"]
        for kit in catalog["kits"]:
            mix=data["kits"].get(kit["name"])
            if not mix:raise RuntimeError("Unmeasured kit: "+kit["name"])
            if len(kit["routes"])!=len(mix["pads"]):raise RuntimeError("Kit route count changed")
            kit["mix_gain"]=mix["gain"]
            for route,pad in zip(kit["routes"],mix["pads"]):
                source=catalog["engines"][route["engine"]]
                sound=source["sounds"][route["sound"]]
                if source["folder"]!=pad["source_folder"] or sound["name"]!=pad["sound"]:raise RuntimeError("Kit source changed; recalibration required")
                route["mix_values"]=pad["values"]
                route["mix_role"]=pad["role"]
    catalog["kits"].sort(key=lambda k:(0 if k["name"]=="K-WASUB / 909" else 1 if k["name"].startswith("K-WASUB /") else 2))
