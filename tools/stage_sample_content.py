#!/usr/bin/env python3
"""Stage the original Hortator CC0 percussion material for Rhythmer's sampler."""
import hashlib
import json
import os
from pathlib import Path
import wave
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
ROOT=Path(__file__).resolve().parents[1]
def main():
    if not os.path.ismount('/Volumes/SSD'):raise SystemExit('SSD not mounted')
    source=WORK/'source-depot/hortator/assets/samples-cc0'
    dest=WORK/'sample-stage/Samples/Rhythmer/Hortator CC0 Percussion';dest.mkdir(parents=True,exist_ok=True)
    entries=[]
    names=['Tambourine','Shaker','Conga','Claves','Woodblock']
    for i,p in enumerate(sorted((source/'KIT').glob('*.wav'))):
        with wave.open(str(p),'rb') as f:
            params=f.getparams();data=f.readframes(f.getnframes());frame_bytes=f.getnchannels()*f.getsampwidth()
        assert data and len(data)%frame_bytes==0 and any(data)
        # The source depot deliberately retains prefixes of longer CC0 files.
        # Write the actual available PCM length into the generated WAV header.
        target=dest/(str(i+1).zfill(2)+' '+names[i]+'.wav')
        with wave.open(str(target),'wb') as out:out.setparams(params);out.writeframes(data)
        with wave.open(str(target),'rb') as check:assert len(check.readframes(check.getnframes()))==len(data)
        entries.append(dict(file=target.name,original=p.name,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            sha256=hashlib.sha256(target.read_bytes()).hexdigest(),frames=len(data)//frame_bytes,rate=params.framerate))
    for name in ('ATTRIBUTION.txt','CREDITS.txt'):(dest/name).write_bytes((source/name).read_bytes())
    pin=json.loads((ROOT/'ports/fm1-hortator/SOURCE.json').read_text())
    (dest/'SOURCE.json').write_text(json.dumps(dict(repo=pin['repo'],
        commit=pin['commit'],license='CC0-1.0',material='VCSL / Versilian Studios / Sam Gossner',
        adaptation='Available source PCM retained; generated WAV length headers corrected',files=entries),indent=2)+'\n')
    print('CC0 percussion: five decoded WAV files staged, headers and payload lengths verified')
if __name__=='__main__':main()
