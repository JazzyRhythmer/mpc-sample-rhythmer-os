"""Read original bank identities from pinned data, never substitute recipes."""
import hashlib,importlib.util,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(path):
 spec=importlib.util.spec_from_file_location('original_bank_'+path.stem,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def elixir_kits():
 port=ROOT/'ports/fm1-elixir/original';m=module(port/'tools/gen_factory_kits.py');seen=set();rows=[]
 for name,data,path in (row for bank in ('factory','hrtl-dlc','hrtl-untz') for row in m.kits_in(port/'assets/kits'/bank)):
  if data in seen:continue
  seen.add(data);rows.append(dict(name=name.strip(),sha256=hashlib.sha256(data).hexdigest(),source=path.relative_to(port).as_posix()))
 return rows+[dict(name='Initkit',source='firmware/src/kit.c:kit_init_values')]
def hortator_presets():
 s=(ROOT/'ports/fm1-hortator/original/preset_bank.h').read_text().split('static const preset_t PRE_FACTORY[]',1)[1].split('};',1)[0]
 groups=[{'DM_S808','DM_S909','DM_SSNAP','DM_SCRAK','DM_SDTRX','DM_SDEFM'}, {'DM_C808','DM_C909','DM_CPTRX','DM_CPEFM'}, {'DM_HATC','DM_HMETL','DM_HNOIS','DM_CHTRX','DM_MATRX','DM_HHEFM'}, {'DM_HATO','DM_OHTRX'}, {'DM_TOM','DM_CONGA','DM_MEMB','DM_XTTRX','DM_XCTRX','DM_XTEFM'}, {'DM_RIM','DM_CLAVE','DM_RSTRX','DM_CLTRX','DM_RSEFM','DM_COWB','DM_CBTRX','DM_CBEFM','DM_FM'}, {'DM_CYMB','DM_CYTRX','DM_CYEFM'}]
 rows=[]
 for model,knobs,name in re.findall(r'\{(DM_\w+),\s*\{([^}]+)\},\s*"([^"]+)"\s*\}',s):
  lane=next((i+1 for i,g in enumerate(groups) if model in g),0);values=[int(v.strip()) for v in knobs.split(',')];assert len(values)==8
  rows.append(dict(name=name,model=model,knobs=values,note=60 if model=='DM_ACID' else [36,38,39,42,46,45,37,49][lane],lane=lane))
 assert len(rows)==151
 return rows

def mono2k_models():
 port=ROOT/'ports/fm1-mono2k/original'
 enum=re.search(r'enum \{ M_GSIN,(.*?)M_COUNT', (port/'m2k.h').read_text(),re.S)[1]
 codes=['M_GSIN']+re.findall(r'\bM_[A-Z]+\b',re.sub(r'/\*.*?\*/','',enum,flags=re.S))
 text=(port/'m2k_ui.c').read_text().split('static const mi_t MI[M_COUNT]',1)[1]
 names=re.findall(r'^    \{"([^"\n]+)", "[^"\n]+", "[^"\n]+", "[^"\n]+", \{',text,re.M)[:len(codes)]
 assert len(names)==len(codes)==19
 selected=re.search(r'machines\[\]\s*=\s*\{([^}]+)',(ROOT/'ports/common/mono2k_native.c').read_text())[1].split(',')
 assert set(selected)==set(codes)-{'M_FXC','M_FXR','M_FXD'}
 return [names[codes.index(code)] for code in selected]
def mono2k_library():
 text=(ROOT/'ports/fm1-mono2k/original/m2k_lib.c').read_text()
 rows=[dict(name=n,category=c,model=m,root=int(root)) for n,c,m,root in re.findall(r'S\("([^"\n]+)",\s*(CAT_\w+),\s*(M_\w+),\s*(\d+),',text)]
 assert len(rows)==96
 return rows
