#!/usr/bin/env python3
"""Export reviewed source without local history, planning material or build outputs."""
from pathlib import Path
import hashlib
import os
import subprocess
import zipfile
from privacy import verify, BLOCKED_PARTS, PATTERNS
import json

ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
OUTPUT=Path('/Volumes/SSD/Development/Archives/rhythmer-os')
VERSION=(ROOT/'VERSION').read_text().strip()
EXPORT_CHANGES={}
EXCLUDE=BLOCKED_PARTS|{'build','dist','out','artifacts','AGENTS.md','CLAUDE.md','.claude','.codex','.env'}


def collect_tree(root,prefix,files):
    for folder,dirs,names in os.walk(root,followlinks=False):
        dirs[:]=[n for n in dirs if n not in EXCLUDE and not (Path(folder)/n).is_symlink()
                 and not (prefix.startswith('vendor/') and n=='desktop')]
        for name in names:
            p=Path(folder)/name
            if name in EXCLUDE or p.is_symlink() or name.endswith(('.pyc','.pem','.key','.p12')) or name.startswith('.env'):continue
            data=p.read_bytes()
            if prefix.startswith(('third_party/mpc-original/','third_party/runtime/JUCE/','third_party/runtime/openblas/')) and PATTERNS['personal-home'].search(data):
                data.decode('utf-8')
                EXPORT_CHANGES[prefix+p.relative_to(root).as_posix()]={'original_sha256':hashlib.sha256(data).hexdigest(),'change':'Generic upstream machine-specific build/example home path normalized; DSP algorithms and copyright retained'}
                data=PATTERNS['personal-home'].sub(b'/upstream-home/',data)
            # Source exports omit compiled executables/libraries and their embedded build-machine paths.
            if data[:4] in (b'\x7fELF',b'\xcf\xfa\xed\xfe',b'\xce\xfa\xed\xfe',b'\xca\xfe\xba\xbe') or data[:2]==b'MZ':continue
            files[prefix+p.relative_to(root).as_posix()]=data


def main():
    if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD is not mounted')
    files={}
    for name in ('README.md','LICENSE','THIRD_PARTY_NOTICES.md','VERSION'):
        files[name]=(ROOT/name).read_bytes()
    for folder in ('docs','extensions','assets','ports','tests','tools','config','LICENSES','third_party'):
        collect_tree(ROOT/folder,folder+'/',files)
    collect_tree(ROOT/'vendor/mpc-vst-plugins','vendor/mpc-vst-plugins/',files)
    baseline_index=[];seen={}
    for item in json.loads((ROOT/'config/baseline-source.lock.json').read_text()):
        key=(item['repo'],item['commit'])
        if key not in seen:
            seen[key]='third_party/mpc-original/'+item['id']+'/'
            collect_tree(WORK/'baseline-source-depot'/item['folder'],seen[key],files)
        baseline_index.append(dict(repo=item['repo'],tag=item['tag'],commit=item['commit'],source_folder=seen[key]))
    files['BASELINE_SOURCE_INDEX.json']=(json.dumps(baseline_index,indent=2)+'\n').encode()
    # Export the real, branded runtime with populated base sources. Original reserved boot art is absent.
    collect_tree(WORK/'runtime','runtime/',files)
    # Ship the actual framework/font source and its transitive notices too,
    # rather than relying solely on a later network fetch.
    collect_tree(WORK/'runtime/build/deps/JUCE','third_party/runtime/JUCE/',files)
    collect_tree(WORK/'runtime/build/deps/clap','third_party/runtime/clap/',files)
    collect_tree(WORK/'runtime/build/deps/rubik','third_party/runtime/rubik/',files)
    for component in ('fonts','spleeterrt','openblas'):
        dependency=WORK/'runtime/build/deps'/component
        if dependency.is_dir():collect_tree(dependency,'third_party/runtime/'+component+'/',files)
    # Include the reviewed manual inputs needed to rebuild the embedded web bundle.
    public_runtime_docs={'runtime/docs/'+n for n in ('QUICKSTART.md','GUIDE.md','guide/rhythmer.md','guide/gen.md','guide/break-acid.md','guide/install.md')}
    # Other upstream development/planning docs are outside the public surface.
    for name in list(files):
        if (name.startswith('runtime/docs/') and name not in public_runtime_docs and not name.startswith('runtime/docs/guide/') and not name.startswith('runtime/docs/images/')) or name.startswith('runtime/tools/') and name.endswith('.md'):
            del files[name]
    files['RHYTHMER_SOURCE.json']=(json.dumps(dict(product='Rhythmer OS',version=VERSION,source_commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),hardware_validated=False),indent=2)+'\n').encode()
    files['SOURCE_EXPORT_ADJUSTMENTS.json']=(json.dumps(EXPORT_CHANGES,indent=2)+'\n').encode()
    count=verify(files)
    files['SHA256SUMS']=''.join(hashlib.sha256(b).hexdigest()+'  '+n+'\n' for n,b in sorted(files.items())).encode()
    OUTPUT.mkdir(parents=True,exist_ok=True)
    target=OUTPUT/('RHYTHMER-OS-'+VERSION+'-SOURCE.zip')
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            item=zipfile.ZipInfo(name,(2026,1,1,0,0,0));item.external_attr=(0o100755 if name.endswith(('.sh','.py','.command')) else 0o100644)<<16
            item.compress_type=zipfile.ZIP_DEFLATED;z.writestr(item,data)
    with zipfile.ZipFile(target) as z:
        if z.testzip():raise RuntimeError('Source archive corruption')
        verify({name:z.read(name) for name in z.namelist()})
    target.with_suffix('.zip.sha256').write_text(hashlib.sha256(target.read_bytes()).hexdigest()+'  '+target.name+'\n')
    print(str(target));print(str(count)+' source files; privacy checks passed; no Git history')


if __name__=='__main__':main()
