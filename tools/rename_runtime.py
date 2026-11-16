#!/usr/bin/env python3
"""Mechanical product-code rename, retaining origin/legal/serialized identity.

Run on the disposable SSD source snapshot, never on the pinned upstream.
"""
from pathlib import Path
import re
import sys

KEEP = (
    'urn:melodee:',                     # LV2 fixture/plugin identifiers must match Turtle metadata
    'MELODEE1',                         # existing .mldp file magic
    'Melodee by Kerem Kilic (Ellic Studio)',
    'Melodee by Kerem Kiliç (Ellic Studio)',
    'Melodee Poly', 'Melodee PD', 'Melodee Chip',
    'Melodee%20Poly', 'Melodee%20PD', 'Melodee%20Chip',
    'melodee-poly', 'melodee-pd', 'melodee-chip',
    'melodee_mods=', 'melodee=',         # legacy plugin state protocol
)


def rename_text(text):
    saved = []
    def keep(value):
        saved.append(value)
        return 'RHYTHMER_KEPT_TOKEN_%06d' % (len(saved) - 1)
    text = re.sub(r'https?://[^\s<>\)"\'`]+', lambda m: keep(m.group()), text)
    text = re.sub(r'^.*(?:Copyright|copyright|SPDX-License-Identifier).*$'
                  , lambda m: keep(m.group()), text, flags=re.M)
    for value in KEEP:
        text = text.replace(value, keep(value))
    text = text.replace('MELODEE', 'RHYTHMER').replace('Melodee', 'Rhythmer').replace('melodee', 'rhythmer')
    for i, value in enumerate(saved):
        text = text.replace('RHYTHMER_KEPT_TOKEN_%06d' % i, value)
    return text


def apply(root):
    if not (root / 'src/melodee').is_dir():
        raise RuntimeError('Expected a fresh pinned source snapshot')
    suffixes = {'.cpp', '.h', '.c', '.py', '.sh', '.md', '.mk', '.txt', '.html', '.css', '.js', '.svg'}
    for p in sorted(root.rglob('*')):
        rel = p.relative_to(root)
        if rel.parts[0] in ('build', 'base', '.git') or not p.is_file():
            continue
        if p.name in ('LICENSE', 'THIRD_PARTY.md', 'AGENTS.md'):
            continue
        if p.suffix not in suffixes and p.name not in ('Makefile', 'AGENTS.md'):
            continue
        try:
            old = p.read_text()
        except UnicodeDecodeError:
            continue
        new = rename_text(old)
        if old != new:
            p.write_text(new)
    # Rename descendants before their containing folder.
    for p in sorted(root.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        rel = p.relative_to(root)
        if rel.parts[0] in ('build', 'base', '.git'):
            continue
        name = p.name.replace('MELODEE', 'RHYTHMER').replace('Melodee', 'Rhythmer').replace('melodee', 'rhythmer')
        if name != p.name:
            p.rename(p.with_name(name))
    # Make the original author's source description explicit after the rename.
    readme = root / 'README.md'
    readme.write_text('# Rhythmer OS\n\nDeveloped by jazzy rhythmer.\n\n'
                      'Based on Melodee by Kerem Kiliç (Ellic Studio), AGPL-3.0-only.\n'
                      'See THIRD_PARTY.md and the Rhythmer OS source/patch inventory.\n')
    print('Renamed source tree to src/rhythmer, namespace rhythmer, RhythmerApp and build/rhythmer')


if __name__ == '__main__':
    apply(Path(sys.argv[1]))
