#!/usr/bin/env python3
"""Keep the device's offline custom guides and their local links complete."""
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ('GETTING_STARTED_KO.md', 'TRACK_WORKFLOW.md', 'GEN_WORKFLOW.md',
         'BREAK_ACID_GUIDE_KO.md', 'SD_CARD_GUIDE.md', 'RHYTHMER_PRESETS.md',
         'USER_MANUAL_KO_DRAFT.md', 'VERIFICATION.md', 'MANUAL_020_EN.md',
         'FIRST_GROOVE_020_EN.md', 'FIRST_GROOVE_020_KO.md',
         'QUICK_REFERENCE_020_EN.md', 'SYSTEM_MAP_020_EN.md')
LINK = re.compile(r'(!?\[[^\]]*\]\()([^)\s]+)(\))')

def sync(runtime):
    docs = ROOT/'docs'
    target = runtime/'docs/guide'
    target.mkdir(parents=True, exist_ok=True)
    pending = [docs/name for name in SEEDS]
    done = set()
    while pending:
        original = pending.pop()
        if original in done:
            continue
        done.add(original)
        def link(match):
            value = match[2]
            if ':' in value or value.startswith('#'):
                return match[0]
            path, mark, anchor = value.partition('#')
            source = (original.parent/path).resolve()
            if source.suffix.lower() == '.md' and source.is_relative_to(docs):
                if not source.is_file():
                    raise RuntimeError('Missing guide link: '+original.name+' -> '+path)
                pending.append(source)
                return match[1]+source.name+(mark+anchor if mark else '')+match[3]
            if match[1].startswith('!['):
                if not source.is_file() or not source.is_relative_to(ROOT):
                    raise RuntimeError('Missing guide image: '+path)
                image = runtime/'docs/images/rhythmer'/source.name
                image.parent.mkdir(parents=True, exist_ok=True)
                if not image.exists() or image.read_bytes()!=source.read_bytes():
                    shutil.copy2(source,image)
                return match[1]+'../images/rhythmer/'+source.name+match[3]
            return match[0]
        rendered = LINK.sub(link, original.read_text())
        output = target/original.name
        if not output.exists() or output.read_text()!=rendered:
            output.write_text(rendered)
    print(f'Offline custom guides: {len(done)} pages with local guide/image dependencies')

if __name__ == '__main__':
    sync(Path(sys.argv[1]).resolve())
