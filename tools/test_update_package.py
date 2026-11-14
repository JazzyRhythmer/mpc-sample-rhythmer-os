#!/usr/bin/env python3
"""Exercise signed-update identity and tamper rejection, without installing."""
from pathlib import Path
import importlib.util,json,re,subprocess,sys
from sign_update import sign
ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
APP=WORK/'runtime'
DOCKER='/Volumes/SSD/Development/Toolchains/rhythmer-os/bin/docker'

def main():
    spec=importlib.util.spec_from_file_location('release',APP/'tools/make_release.py');release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)
    assert release.public_key()==(ROOT/'config/update-public-key.txt').read_text(),'Runtime and release update keys differ'
    version='v'+(ROOT/'VERSION').read_text().strip()
    files=release.collect(APP/'build/rhythmer',version,'fixture')
    sign(files)
    release.write_zip(files,APP/'build/update-test.zip',1767225600)
    damaged=dict(files);damaged['autorun/rhythmer/VERSION']=b'v99.0.0 changed\n'
    release.write_zip(damaged,APP/'build/update-damaged.zip',1767225600)
    (APP/'build/update-public.txt').write_bytes((ROOT/'config/update-public-key.txt').read_bytes())
    header=(ROOT/'vendor/rhythmer/src/melodee/shell/update.h').read_text()
    lines=re.findall(r'^\s*"([^"\n]*)\\n"',header,re.M)
    (APP/'build/upstream-public.txt').write_text('\n'.join(lines[:3])+'\n')
    cases=[('own', 'update-test.zip','rhythmer','update-public.txt',True),
           ('other-package','update-test.zip','melodee','update-public.txt',False),
           ('upstream-key','update-test.zip','rhythmer','upstream-public.txt',False),
           ('tampered-version','update-damaged.zip','rhythmer','update-public.txt',False)]
    result=[]
    for name,zipname,package,key,okay in cases:
        cmd=[DOCKER,'run','--rm','--platform','linux/arm64','-v',str(WORK)+':'+str(WORK),'-v',str(WORK)+':/Volumes/SSD/Development/BuildCache/groove-os','-v',str(APP)+':/work','-w','/work','rhythmer-builder',
             'sh','base/install/sd-update.sh','check','build/'+zipname,package,'build/'+key]
        done=subprocess.run(cmd,capture_output=True,text=True)
        assert (done.returncode==0)==okay,(name,done.returncode,done.stderr)
        if okay:assert done.stdout.strip()==version,done.stdout
        result.append(dict(case=name,accepted=done.returncode==0,expected=okay))
    target=ROOT/'artifacts/upstream-v020-audit/update-check.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print('Signed update checks passed: own identity accepted; wrong package/key and tampering rejected. No install/restart performed.')
if __name__=='__main__':main()
