"""Three additional fresh-process acceptance passes after baseline fixes.

This only validates local files. It never uploads, publishes, installs on a
device, changes repository visibility, or opens public downloads.
"""
from pathlib import Path
import hashlib,json,os,shlex,shutil,subprocess as sp,sys,time
import build

ROOT=Path(__file__).resolve().parents[1]
WORK=build.WORK
HELPER=Path.home()/'.local/share/ssd-development/bin/ssd-qa-output'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def inputs():
    files={}
    for folder in ('config','extensions','tools','tests','ports/common'):
        for p in sorted((ROOT/folder).rglob('*')):
            if not p.is_file() or any(x in p.parts for x in ('build','__pycache__')):continue
            if p.name in ('sound-host.lock.json','final-validation.lock.json'):continue
            files[str(p.relative_to(ROOT))]=digest(p)
    for p in sorted((ROOT/'ports').glob('*/*')):
        if p.name in ('contract.json','params.lock','source-panels.json','model-controls.json','SOURCE.json'):files[str(p.relative_to(ROOT))]=digest(p)
    for name in ('VERSION','docs/USER_MANUAL_KO_DRAFT.md'):files[name]=digest(ROOT/name)
    files['runtime_binary']=digest(WORK/'runtime/build/rhythmer')
    return files

def run(command,log,cwd=ROOT,env=None):
    with log.open('w') as out:
        sp.run(command,cwd=cwd,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',**(env or {})),
               stdout=out,stderr=sp.STDOUT,check=True,timeout=2400)

def container(command,log,pass_number=0):
    mount=['-v',str(WORK)+':'+str(WORK),'-v',str(WORK)+':/Volumes/SSD/Development/BuildCache/groove-os']
    run([build.DOCKER,'run','--rm','--platform','linux/arm64',*mount,
         '-w',str(WORK/'plugins'),'-e','PYTHONDONTWRITEBYTECODE=1',
         '-e','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','-e','UBSAN_OPTIONS=halt_on_error=1',
         '-e','TMPDIR='+str(WORK/'tmp'),'-e','RHYTHMER_GEN_CARD='+str(WORK/'sd-stage'),
         '-e','RHYTHMER_QA_PASS='+str(pass_number),
         'rhythmer-builder','sh','-ec',command],log)

def main():
    build.check()
    from engine_inventory import validate
    from stage_test_catalog import stage
    validate();stage()
    frozen=inputs();identity=hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest()
    parent=WORK/'ui-native-rework/final-passes'/identity[:16]
    sp.run([str(HELPER),str(parent)],check=True,capture_output=True)
    q=shlex.quote
    binary=q(str(WORK/'sound_rack_asan'));catalog=q(str(WORK/'sound-catalog.json'));plugins=q(str(WORK/'sd-stage/Rhythmer/Plugins'))
    shutil.copy2(ROOT/'config/sound-catalog.json',WORK/'sound-catalog.json')
    results=[]
    for n in range(1,4):
        target=parent/('pass-'+str(n));sp.run([str(HELPER),str(target)],check=True,capture_output=True)
        start=time.time();print('Additional acceptance pass',n,'/3: source, UI/presets/kits and upstream 0.2.0',flush=True)
        for name in ('check_release_selection','check_preset_coverage','check_public_banks','check_control_coverage','audit_upstream_020','audit_attribution'):
            run([sys.executable,str(ROOT/'tools'/(name+'.py'))],target/(name+'.log'))
        container('python3 tools/check_wrapper_enums.py',target/'enum-parser.log')
        container('python3 tools/check_plaits_quantizer.py',target/'original-plaits-quantizer.log')
        modes=['transport','userdefaults','labels','plaitscontrols','presetcontrols','controlroundtrip','inspect','singles','kits','kitfilter','enginefilter','kitownership','audit','authored']
        for mode in modes:
            assert inputs()==frozen,'Acceptance inputs changed; restart after the fix'
            print('Pass',n,mode,flush=True)
            container(f'{binary} {catalog} {plugins} {q(mode)}',target/('host-'+mode+'.log'),pass_number=n)
            if mode=='audit':
                audit=json.loads((WORK/'preset-audit.json').read_text())
                assert len(audit)==25 and not any(e['silent'] for e in audit),'Silent native source selection'
                shutil.copy2(WORK/'preset-audit.json',target/'preset-audit.json')
        # A full chromatic replay on the last pass supplements all-source
        # native-note audits in every pass and the prior baseline replay.
        if n==3:container(f'{binary} {catalog} {plugins} playback',target/'host-playback.log')
        container('python3 tools/audit_control_api.py',target/'control-api.log')
        assert inputs()==frozen,'Acceptance inputs changed; restart after the fix'
        run([sys.executable,str(ROOT/'tools/render_ui_audit.py')],target/'ui.log',env={'RHYTHMER_AUDIT_FORCE':'1'})
        summary=json.loads((ROOT/'artifacts'/('ui-'+(ROOT/'VERSION').read_text().strip())/'render-summary.json').read_text())
        assert len(summary)==11 and all('text_issues=0' in g['result'] for g in summary)
        shutil.copy2(ROOT/'artifacts'/('ui-'+(ROOT/'VERSION').read_text().strip())/'render-summary.json',target/'ui-summary.json')
        sp.run([str(HELPER),str(target/'standard-preview')],check=True,capture_output=True)
        runtime=q(str(WORK/'runtime'))
        container(f'cd {runtime} && build/rhythmer --rhythmer-preview {q(str(target/"standard-preview"))}',target/'standard-ui.log')
        container(f'cd {runtime} && build/rhythmer --rhythmer-monkey {1+(n-1)*12} 12 3000',target/'standard-monkey.log')
        container(f'cd {runtime} && python3 -m unittest discover -s tests -v',target/'runtime-020.log')
        container(f'cd {runtime}/base && python3 -m unittest discover -s tests -v',target/'base-020.log')
        container(f'cd {runtime} && build/rhythmer --rhythmer-gen8-check',target/'card-gen-acid-break.log')
        assert 'RHYTHMER_DESIGN' in (target/'card-gen-acid-break.log').read_text(),'GEN card fixture was not connected'
        assert inputs()==frozen,'Acceptance inputs changed; restart final passes after the fix'
        result=dict(pass_number=n,passed=True,elapsed_seconds=round(time.time()-start,1),
                    ui_states=sum(int(g['result'].split('pages=')[1].split()[0]) for g in summary),
                    ui_text_issues=0,host_modes=modes+(['playback'] if n==3 else []),
                    upstream_release_features=16,hardware_validated=False)
        (target/'result.json').write_text(json.dumps(result,indent=2)+'\n');results.append(result)
        print('Additional acceptance pass',n,'/3 PASS',flush=True)
    receipt=dict(version=(ROOT/'VERSION').read_text().strip(),additional_passes=results,
                 runtime_sha256=frozen['runtime_binary'],input_set_sha256=identity,files=frozen,
                 publication='ON_HOLD_NOTIFY_USER_FIRST',hardware_validated=False)
    (ROOT/'config/final-validation.lock.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Three additional passes complete. Local packaging only; publication remains on hold.',flush=True)

if __name__=='__main__':main()
