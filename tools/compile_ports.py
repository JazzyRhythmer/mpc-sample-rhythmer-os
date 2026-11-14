#!/usr/bin/env python3
"""Run inside the existing Melodee builder. Reuse Open MPC's wrapper/adapter."""
from release_profile import require_port
import json
import os
from pathlib import Path
import subprocess as sp
import sys

ROOT = Path(__file__).resolve().parents[1]
MV = ROOT / "vendor/mpc-vst-plugins"


def run(args, cwd):
    env = dict(os.environ, UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    sp.run([str(a) for a in args], cwd=cwd, env=env, check=True)


def build(name):
    require_port(name)
    port = ROOT / "ports" / name
    cfg = json.loads((port / "vst.json").read_text())
    run([sys.executable, MV / "tools/gen_vst.py", port / "vst.json"], ROOT)
    # The upstream host test covers independent instances, parameters, MIDI,
    # odd blocks, and state round-trips under ASan/UBSan on this native ARM VM.
    run(["bash", MV / "tools/test_port.sh", port / "vst.json"], ROOT)
    out = port / "build"
    objects = []
    sources = [port / s for s in cfg["build"]["sources"]] + [
        MV / "adapters/schwung/schwung_engine.c", MV / "wrapper/vst2_wrap.c"
    ]
    for i, source in enumerate(sources):
        cpp = source.suffix in (".cpp", ".cc", ".cxx")
        obj = out / (str(i) + ".o")
        # Do not apply a C++ language switch to the C wrapper.
        flags = [f for f in cfg["build"].get("cflags", []) if not f.startswith("-std=")]
        run(["g++" if cpp else "gcc", "-O2", "-fPIC", "-fvisibility=hidden",
             "-std=gnu++17" if cpp else "-std=gnu11", *flags,
             "-I" + str(out), "-I" + str(MV / "wrapper"),
             "-c", source, "-o", obj], port)
        objects.append(obj)
    run(["g++", "-shared", *objects, "-lm", "-lpthread", "-ldl",
         "-Wl,--no-undefined", "-o", out / cfg["so"]], port)
    run(["strip", out / cfg["so"]], port)
    run(["readelf", "-h", out / cfg["so"]], port)


if __name__ == "__main__":
    for name in sys.argv[1:] or ["sophie"]:
        build(name)
