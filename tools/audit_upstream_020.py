"""Compare all sixteen release feature paths with the pinned upstream.
Source equality is not hardware/network/USB verification.
"""
from pathlib import Path
import sys,json,hashlib,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'));from rename_runtime import rename_text
A=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os/runtime');V=ROOT/'vendor/rhythmer';O=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os/ui-native-rework')
features=[
 ('audio_formats','WAV/MP3/FLAC/Ogg/AIFF and preview',['shell/sample_decode.cpp','shell/sample_files.cpp','shell/sample_library.cpp','pages/samples_page.cpp']),
 ('chop','Beats tempo detection and encoder/SHIFT zoom',['model/chop_slices.h','shell/chop_mode.cpp','pages/chop_page.cpp']),
 ('empty_track','New track entry',['shell/new_track.h','shell/new_track.cpp','pages/stage_page.cpp']),
 ('load_kit','MPC projects/internal factory kits/XPM/XTY/colour',['shell/mpc_project.cpp','shell/mpc_program.cpp','model/pad_params.h']),
 ('pad_sends','Per-pad A-D sends',['model/pad_params.h','shell/bindings.cpp','pages/sends_page.cpp']),
 ('freeze','Freeze and Deep Freeze',['model/print.cpp','engine/print_render.cpp','engine/print_player.cpp','shell/print_jobs.cpp']),
 ('plugin_formats','CLAP/LV2/VST2/VST3 with folders',['plugin/plugin_files.cpp','plugin/clap_instance.cpp','plugin/plugin_rack.cpp','plugin/preset_rows.h']),
 ('preset_macros','Stage PRESETS FILTER/ECHO/SPACE',['engine/macros.cpp','shell/bindings.cpp','pages/stage_page.cpp']),
 ('patterns128','128 patterns A-H and scene encoder',['model/limits.h','model/pattern.cpp','pages/patterns_page.cpp']),
 ('roll_marks','SHIFT encoder note selection, collective editing',['shell/roll.cpp','shell/roll_edit.cpp','pages/roll_page.cpp']),
 ('levels_zones','16 Levels Zones',['model/scales.h','pages/keys_page.cpp']),
 ('midi','All-page note input, per-track port/channel, remote CC',['shell/midi_io.cpp','shell/midi_route.cpp','model/midi_config.h']),
 ('gestures','Hold SAMPLE / mixer / ERASE / copy',['shell/sample_mode.cpp','shell/erase_copy.cpp','shell/shell.cpp']),
 ('usb_web','USB web uploads/Files/docs',['web/web_app.cpp','web/card_files.cpp','web/web_server.cpp','web/static/files.html']),
 ('mirror','USB UVC 320x240..1280x960 and rates',['@base/drivers/mirror_frame.cpp','@base/drivers/screen_mirror.cpp','pages/settings_page.cpp']),
 ('updates','Signed SD ZIP updates',['shell/update.cpp','shell/update.h'])]
rows=[]
for ident,title,files in features:
 evidence=[]
 for f in files:
  if f.startswith('@base/'):
   rel=f[6:];a=A/'base/src'/rel;v=V/'base/src'/rel;isbase=True
  else:
   a=A/'src/rhythmer'/f;v=V/'src/melodee'/f;isbase=False
  if not v.exists() or not a.exists():
   evidence.append(dict(file=f,exists=False));continue
  expected=v.read_text() if isbase else rename_text(v.read_text())
  actual=a.read_text();evidence.append(dict(file=f,exists=True,renamed_upstream_equal=expected==actual,sha256=hashlib.sha256(a.read_bytes()).hexdigest()))
 rows.append(dict(id=ident,feature=title,evidence=evidence,status='SOURCE_REVIEW',hardware_verified=False))
assert all(e['exists'] for r in rows for e in r['evidence']), 'Missing upstream feature evidence'
(O/'upstream-020-source-matrix.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:print(r['id'],[(e['file'],e.get('renamed_upstream_equal','MISSING')) for e in r['evidence']])
