#!/usr/bin/env python3
"""Read a Schwung v2 module's own parameter contract; no DSP translation."""
import ctypes as C
import json
import sys


class API(C.Structure):
    _fields_ = [("version", C.c_uint32)] + [
        (name, C.c_void_p) for name in
        ("create", "destroy", "midi", "set", "get", "error", "render")
    ]


def read(path):
    library = C.CDLL(str(path))
    entry = library.move_plugin_init_v2
    entry.argtypes = [C.c_void_p]
    entry.restype = C.POINTER(API)
    api = entry(None).contents
    if api.version != 2:
        raise RuntimeError("Expected Schwung API v2")
    create = C.CFUNCTYPE(C.c_void_p, C.c_char_p, C.c_char_p)(api.create)
    destroy = C.CFUNCTYPE(None, C.c_void_p)(api.destroy)
    get = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_char_p, C.c_void_p, C.c_int)(api.get)
    instance = create(b"", None)
    if not instance:
        raise RuntimeError("DSP creation failed")
    try:
        result = {}
        for key in ("chain_params", "ui_hierarchy", "state"):
            buffer = C.create_string_buffer(1024 * 1024)
            size = get(instance, key.encode(), buffer, len(buffer))
            if size > 0:
                result[key] = json.loads(buffer.value)
        if not result.get("chain_params"):
            raise RuntimeError("No runtime parameter metadata")
        return result
    finally:
        destroy(instance)


if __name__ == "__main__":
    print(json.dumps(read(sys.argv[1]), indent=2))
