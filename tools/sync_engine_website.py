#!/usr/bin/env python3
"""Sync public engine facts and production-render previews; never publish."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];WEB=ROOT.parent/'jr-web/public/mpc-sample';WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os');QA=WORK/'upstream-030-20261117/final/engine-previews'
def load(p):return json.loads(p.read_text())
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
engines=load(WEB/'engines.json');views={e['engine']:e for e in load(WORK/'edit-inspect.json')};catalog=load(ROOT/'config/sound-catalog.json');coverage=load(ROOT/'config/preset-coverage.json')
new=[dict(name='Frodhes',category='Synths',hook='Tines, bells and warm keys.',description='Electric-piano, vibraphone and marimba voices with 57 original programs. Shape the tone with source-native filters, envelopes, modulation and effects.'),dict(name='Tenebrae',category='Synths',hook='Eight ways to shape a voice.',description='Eight oscillator models cover basses, leads, pads, keys and textured sounds. Explore 164 original programs including Init, with oscillator shaping, resonant filtering, envelopes and modulation.')]
for e in new:
 if not any(x['name']==e['name'] for x in engines):engines.append(e)
for e in engines:
 view=views.get(e['name'])
 if view:
  byid={p['index']:p for p in view['parameters']}
  e['parameters']=[{'name':byid[n]['name'],'text':byid[n]['text']} for n in [i for i in view['edit_order'] if i >= 6][:12]]
  e['programs']=view['programs'];e['program_count']=len(view['programs'])
 elif e['name']=='Rhythmer Kit':
  e['programs']=[k['name'] for k in catalog['kits']];e['program_count']=len(catalog['kits']);e['parameters']=[{'name':'Pad Volume','text':'Selected pad'},{'name':'Cutoff / Resonance','text':'ALL PADS'},{'name':'PAD SOURCE','text':'Engine and sound per pad'}]
 e['capture']='motion/'+e['name'].lower().replace(' ','-')+'-still.png'
 if e['name']=='FMini-1':e['description']='Minimoog Model D-style synthesis from the original FMini-1 2.6.0 engine, with 200 original factory presets. Three oscillators, revised filter response, contour shaping, LFO, modulation and source effects.'
 if e['name']=='Break Engine':e['description']='Browse your own one-to-four-bar loops, audition dry or tempo-synchronised, then divide into 16 equal slices. BREAK GEN creates patterns; six-page BRK PERF adds held rolls, pitch, A/B switching and recorded performance commands. No break samples are bundled.'
assert len(engines)==coverage['track_picker_entries']==22
save(WEB/'engines.json',engines)
motion={}
for e in load(QA/'frames-index.json'):
 slug=e['slug'];src=WEB/'assets/motion'/(slug+'.png');assert src.is_file(),src
 motion[e['name']]=dict(src='assets/motion/'+src.name,still='assets/motion/'+slug+'-still.png',frames=30,fps=10,columns=10,width=320,height=240,preset=e['preset'],sha256=sha(src),ui_version='0.2.0',capture='Production runtime renderer; simulated note and sustain input',runtime_sha256=sha(WORK/'runtime/build/rhythmer'))
 shutil.copy2(WEB/'assets/motion'/(slug+'-still.png'),ROOT/'assets/engines'/(slug+'-still.png'))
shutil.copy2(QA/'break-perf-0.png',WEB/'assets/motion/break-engine-still.png');shutil.copy2(QA/'break-perf-0.png',ROOT/'assets/engines/break-engine-still.png')
motion['Break Engine']=dict(src='assets/motion/break-engine-still.png',still='assets/motion/break-engine-still.png',frames=1,fps=1,columns=1,width=320,height=240,preset='BRK PERF',sha256=sha(QA/'break-perf-0.png'),ui_version='0.2.0',capture='Production native BRK PERF page; static reference')
assert set(motion)=={e['name'] for e in engines};save(WEB/'motion.json',motion)
s=WEB/'index.html';t=s.read_text();t=t.replace('01 / 20','01 / 22').replace('20 ENGINE SCREENS','22 ENGINE SCREENS').replace('<b>20</b>','<b>22</b>').replace('ALL / 20','ALL / 22');t=t.replace('<b>∞</b><span>REASONS TO KEEP PLAYING</span>','<b>2,888</b><span>FACTORY SOUND SELECTIONS</span>');t=t.replace('Current development selection. Final public build contents may change.','22 picker entries include Rhythmer Kit, Acid and Break. 2,888 sound selections span 27 source views, including kit voices and shared Acid selections; they are not 2,888 unique synth patches.');
# Preserve historical video asset links; only the current installer/version references change.
t=t.replace('v0.4.0-beta.3-hotfix.3','v0.2.0').replace('RHYTHMER-OS-0.4.0-beta.3-','RHYTHMER-OS-0.2.0-').replace('0.4.0-BETA.3','0.2.0').replace('Install 0.4.0-beta.3.','Install 0.2.0.').replace('version is 0.4.0-beta.3','version is 0.2.0')
t=t.replace('Watch the groove come together, then follow the illustrated guide to shape the sounds, balance the tracks and perform a mute jam.','The video demonstrates the musical idea using earlier screens. Follow the updated 0.2.0 written guide for current buttons, track setup, sound editing and Break controls.')
summary='''<article class="install-guide" id="release-notes"><p class="eyebrow">RHYTHMER OS 0.2.0</p><h3>New sounds. Better flow.</h3><p>Frodhes and Tenebrae join the collection; FMini-1 moves to its original 2.6.0 engine. Explore 22 engine entries and 36 complete Rhythmer Kits.</p><ul><li>Clearer track setup, instrument changes and empty-pad sample loading.</li><li>Break audition, source replacement and performance controls with clearer navigation.</li><li>Pad-volume-first kit editing, refined sound controls and User Sound / User Kit saving.</li><li>Two-page Acid GEN, eight Aphex Acid choices and a steadier MIDI tempo display.</li><li>Fixes to presets, parameter mapping, pad labels, saving, cancellation and Back.</li></ul><p>Practical 0.2.0 manual and first-groove instructions match the current controls.</p><a class="textlink" href="https://github.com/jazzyrhythmer/mpc-sample-rhythmer-os/releases/tag/v0.2.0">READ THE FULL 0.2.0 RELEASE NOTES ↗</a></article>'''
t=t.replace('Current development selection. Final public build contents may change; physical-device validation is still in progress.','22 picker entries include Rhythmer Kit, Acid and Break. The 2,888 sound selections span 27 source views, including kit voices and shared Acid choices; they are not 2,888 unique synth patches. Physical-device validation remains pending.').replace('The guide follows the film, step by step.','The written guide uses the current 0.2.0 controls.').replace('Twenty engines. Hear them play.','Hear the engine collection.').replace('One loop from each engine, with its own screen and sound. Ported and integrated for MPC Sample, and shared for the open-source community.','This earlier film features 20 engines. The interactive previews above cover all 22 current entries, including Frodhes and Tenebrae. Original sources and credits are shared with the community.')
if 'id="release-notes"' not in t:t=t.replace('</div></section><section id="support"','</div>'+summary+'</section><section id="support"')
s.write_text(t)
for n in ['app.js','showcase.js','screen-response.js','index.html']:
 p=WEB/n;t=p.read_text().replace('engines-5e9a010a0f','020-production-22').replace('kit-final-v6','020-production-22').replace('beta3-native1','020-production-22').replace('geometry2','020-production-22');
 if n=='showcase.js':t=t.replace("+' / 20'","+' / '+scenes.length")
 p.write_text(t)
p=ROOT/'README.md';t=p.read_text().replace('Twenty instrument entries','Twenty-two instrument entries').replace('**Watch the latest guided session. Then make it yours.**','**Watch the groove, then follow the current written guide.**').replace('*4 bars · 140 BPM · C minor · Follow at your own pace. Click the thumbnail to open the video.*','*4 bars · 140 BPM · C minor. The video uses earlier screens; follow the updated 0.2.0 guide for current menu names and controls.*');t=t.replace('Twenty-two instrument entries, with different ways to start a sound.','Twenty-two instrument entries, 36 complete Rhythmer Kits and 2,888 factory sound selections across 27 source views (including kit voices and shared Acid selections).')
for e in new:
 marker='### '+e['name']+'\n';assert marker in t
 if 'assets/engines/'+e['name'].lower()+'-still.png' not in t:t=t.replace(marker,marker+'\n<img src="assets/engines/'+e['name'].lower()+'-still.png" width="400" alt="'+e['name']+' — RHYTHMER OS 0.2.0 screen">\n')
p.write_text(t)
print('Updated 22 entries, 36 kits, 2888 selections and 22 production screen references')
