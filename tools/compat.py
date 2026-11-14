#!/usr/bin/env python3
"""One optional metadata fallback; keep third-party plugin binaries unchanged."""
from pathlib import Path
import sys


def apply(root):
    file = root / 'src/melodee/plugin/plugin_files.cpp'
    text = file.read_text()
    if 'folder / "drum-map.json"' in text:
        return
    old = '    read_drums(f, (folder / so).string());\n    return true;'
    if text.count(old) != 1:
        raise RuntimeError('Pinned Open MPC scanner changed; review metadata fallback')
    text = text.replace(old, '''    read_drums(f, (folder / so).string());
    // Rhythmer OS: optional companion metadata for unchanged prebuilt drum plug-ins.
    // Scanned on the rack thread; embedded maps still take precedence.
    const auto map = folder / "drum-map.json";
    std::error_code map_error;
    if (f.drums.empty() && !fs::is_symlink(map, map_error) && fs::is_regular_file(map, map_error)
        && fs::file_size(map, map_error) <= 65536 && !map_error)
        read_drums(f, map.string());
    return true;''')
    file.write_text(text)


if __name__ == '__main__':
    apply(Path(sys.argv[1]))
