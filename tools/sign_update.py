#!/usr/bin/env python3
"""Sign an autorun-only update with the private release key outside the checkout.

OpenSSL runs in the SSD-backed build VM; the key is passed over stdin and is
never written into the shared work directory or included in any archive.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
WORK=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os')
DOCKER='/Volumes/SSD/Development/Toolchains/rhythmer-os/bin/docker'
KEY=Path(os.environ.get('RHYTHMER_SIGNING_KEY','/Volumes/SSD/Development/Toolchains/rhythmer-os/signing/release-signing.pem'))
LIST='autorun/rhythmer/RELEASE.sha256'


def sign(files):
    if not os.path.ismount('/Volumes/SSD'):raise RuntimeError('SSD is not mounted')
    if not KEY.is_file():raise RuntimeError('Rhythmer release signing key is unavailable; do not substitute an upstream key')
    subset={n:b for n,b in files.items() if n.startswith('autorun/') and n not in (LIST,LIST+'.sig')}
    listing=''.join(hashlib.sha256(b).hexdigest()+'  '+n+'\n' for n,b in sorted(subset.items())).encode()
    with tempfile.TemporaryDirectory(prefix='sign-',dir=WORK) as directory:
        p=Path(directory);(p/'list').write_bytes(listing)
        (p/'public.txt').write_bytes((ROOT/'config/update-public-key.txt').read_bytes())
        command=[DOCKER,'run','--rm','-i','--platform','linux/arm64','-v',str(p)+':/sign','rhythmer-builder','sh','-ec',
                 'openssl pkeyutl -sign -inkey /dev/stdin -rawin -in /sign/list -out /sign/list.sig && '
                 'openssl pkeyutl -verify -pubin -inkey /sign/public.txt -rawin -in /sign/list -sigfile /sign/list.sig >/dev/null']
        result=subprocess.run(command,input=KEY.read_bytes(),capture_output=True)
        if result.returncode:raise RuntimeError('Rhythmer update signature verification failed: '+result.stderr.decode())
        files[LIST]=listing;files[LIST+'.sig']=(p/'list.sig').read_bytes()
    return files
