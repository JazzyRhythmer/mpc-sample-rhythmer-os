#!/usr/bin/env python3
"""Three fresh-process regression passes on the frozen 0.3 integration.

No publishing or device installation. The complete native suite is a separate
baseline; these extra passes target navigation, source/control state and render
contracts. Receipts state the actual scope rather than claiming hardware QA.
"""
from pathlib import Path
import hashlib,json,os,shlex,subprocess as sp,time
import build
ROOT=Path(__file__).resolve().parents[1];WORK=build.WORK
PARENT=WORK/'upstream-030-20261117/final';HELPER=Path.home()/'.local/share/ssd-development/bin/ssd-qa-output'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inputs():
 files={}
 for folder in ('config','extensions','tools','tests','ports/common','docs','assets/manual'):
  for p in sorted((ROOT/folder).rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts and 'build' not in p.parts and p.name not in ('sound-host.lock.json','final-validation.lock.json'):
    files[str(p.relative_to(ROOT))]=digest(p)
 for name in ('VERSION','README.md'):files[name]=digest(ROOT/name)
 files['runtime_binary']=digest(WORK/'runtime/build/rhythmer');return files
def run(command,log,cwd=ROOT):
 with log.open('w') as out:sp.run(command,cwd=cwd,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),stdout=out,stderr=sp.STDOUT,check=True,timeout=5400)
def container(command,log,n=0):
 run([build.DOCKER,'run','--rm','-v',str(WORK)+':'+str(WORK),'-v',str(WORK)+':/Volumes/SSD/Development/BuildCache/groove-os','-w',str(WORK/'runtime'),'-e','PYTHONDONTWRITEBYTECODE=1','-e','TMPDIR='+str(PARENT.parent/'test-tmp'),'-e','RHYTHMER_GEN_CARD='+str(WORK/'sd-stage'),'-e','RHYTHMER_BREAK_QA='+str(PARENT.parent/'qa'),'-e','RHYTHMER_GEN_DIAGNOSTICS='+str(PARENT),'-e','RHYTHMER_QA_PASS='+str(n),'-e','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','-e','UBSAN_OPTIONS=halt_on_error=1','rhythmer-builder','sh','-ec',command],log)
def main():
 build.check();frozen=inputs();results=[];q=shlex.quote
 for n in range(1,4):
  folder=PARENT/('acceptance-'+str(n));sp.run([str(HELPER),str(folder)],check=True,capture_output=True);start=time.time();print('Fresh regression pass',n,flush=True)
  for name in ('check_release_selection','check_preset_coverage','check_public_banks','check_control_coverage','audit_upstream_030','audit_attribution'):
   run(['python3',str(ROOT/'tools'/(name+'.py'))]+(['--output',str(folder/'upstream-source.json')] if name=='audit_upstream_030' else []),folder/(name+'.log'))
  for option in ('navigation','track','gen8','break-p1'):
   container('build/rhythmer --rhythmer-'+option+'-check',folder/(option+'.log'),n)
  container('build/rhythmer --rhythmer-monkey '+str(1+12*(n-1))+' 12 3000 && build/rhythmer --self-test '+q(str(folder/'audio.wav')),folder/'monkey-audio.log',n)
  modes=['presetcontrols','kits','controlroundtrip','kitownership','enginefilter','kitfilter','userdefaults','transport']
  for mode in modes:
   container(q(str(PARENT/'sound_rack_test'))+' '+q(str(WORK/'sound-catalog.json'))+' '+q(str(WORK/'sd-stage/Rhythmer/Plugins'))+' '+mode,folder/('host-'+mode+'.log'),n)
  container('python3 -m unittest discover -s tests -p test_layout.py -v && python3 -m unittest discover -s tests -p test_upstream_integration.py -v && python3 -m unittest discover -s tests -p test_tempo_display.py -v',folder/'native-regression.log',n)
  font=n-1
  container('RHYTHMER_FONT='+str(font)+' build/rhythmer --rhythmer-preview '+q(str(folder)),folder/'screens.log',n)
  assert 'text_issues=0' in (folder/'screens.log').read_text()
  assert inputs()==frozen,'Inputs changed during regression; repeat after fixing'
  item=dict(pass_number=n,passed=True,elapsed_seconds=round(time.time()-start,1),host_modes=modes,ui_pages=504,native_suite='Focused layout, integration and tempo regression; full 48-test baseline separately recorded',hardware_validated=False)
  (folder/'result.json').write_text(json.dumps(item,indent=2)+'\n');results.append(item);print('PASS',n,flush=True)
 # Every supported font, after the final width adjustment.
 for font in range(3,8):
  folder=PARENT/'fonts'/str(font)
  container('RHYTHMER_FONT='+str(font)+' build/rhythmer --rhythmer-preview '+q(str(folder)),PARENT/'fonts'/('font-'+str(font)+'.log'))
  assert 'text_issues=0' in (PARENT/'fonts'/('font-'+str(font)+'.log')).read_text()
 assert inputs()==frozen
 receipt=dict(version=(ROOT/'VERSION').read_text().strip(),upstream='Melodee Sample v0.3.0',additional_ui_preset_passes=3,additional_upstream_passes=3,additional_passes=results,runtime_sha256=frozen.pop('runtime_binary'),files=frozen,baseline_evidence={p.name:digest(p) for p in [PARENT/'runtime-suite.log',PARENT/'preset-audit.json',PARENT/'host-audit.log',PARENT/'upstream-source.json']},hardware_validated=False,scope='Automated Linux ARM64 runtime, production host and software-render checks; physical device unverified')
 (ROOT/'config/final-validation.lock.json').write_text(json.dumps(receipt,indent=2)+'\n')
 previous=json.loads((ROOT/'config/sound-host.lock.json').read_text());previous.update({k:receipt[k] for k in ('runtime_sha256','files','additional_ui_preset_passes','additional_upstream_passes','scope')});previous['evidence']=receipt['baseline_evidence'];previous['regression_passes']=results;(ROOT/'config/sound-host.lock.json').write_text(json.dumps(previous,indent=2)+'\n')
 print('Three additional passes and eight-font render coverage passed; publication remains a separate action.',flush=True)
if __name__=='__main__':main()
