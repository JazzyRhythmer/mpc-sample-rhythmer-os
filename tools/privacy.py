#!/usr/bin/env python3
"""Check export/package bytes without printing potentially sensitive values."""
import re
import hashlib

BLOCKED_PARTS = {'.git','.codex-private','.githooks','__pycache__','.DS_Store'}
PATTERNS = {
    'personal-home': re.compile(rb'/(?:Users|home)/[A-Za-z0-9._-]+/'),
    'private-key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'service-token': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-proj-[A-Za-z0-9_-]{25,}|AKIA[A-Z0-9]{16})\b'),
    'bearer-token': re.compile(rb'(?i)\b(?:Bearer\s+[a-z0-9._~+/-]{24,}=*|xox[baprs]-[a-z0-9-]{20,}|ya29\.[a-z0-9_-]{30,})'),
    'secret-assignment': re.compile(rb'''(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|password)\s*[:=]\s*["'](?!YOUR|EXAMPLE|CHANGE|test|dummy|placeholder|\$|<)[A-Za-z0-9_+/-]{20,}'''),
}
DISCUSSION = re.compile(r'CONVERSATION_' + r'RAW|Turn\s+\d|대화\s*(?:원본|근거|맥락|기록)|사용자\s*(?:발언|요청|지시)|Chat' + r'GPT|Assistant 응답')


def findings(name, data, own_document=True):
    result=[]
    parts=name.replace('\\','/').split('/')
    if (any(p in BLOCKED_PARTS for p in parts) or parts[-1] == 'AGENTS.md'
            or parts[-1].startswith('.env') or parts[-1].endswith(('.pem','.key','.p12'))):
        result.append('private-file')
    for kind,pattern in PATTERNS.items():
        if pattern.search(data):
            # Pinned, public upstream unit-test fixture uses a fictional home.
            # Keep corresponding source byte-identical; this is not a developer path.
            public_fixture=(kind=='personal-home' and name.endswith('ports/fm1-frodhes/original/plugin/tests/test_paths.c') and hashlib.sha256(data).hexdigest()=='d3288d2394d66284c83cece3b57f5f89da82f7794d1566c577536041cf7a3b1b')
            if not public_fixture:result.append(kind)
    if own_document and name.lower().endswith(('.md','.txt','.json')):
        if DISCUSSION.search(data.decode('utf-8',errors='ignore')):result.append('discussion-record')
    return result


def verify(files):
    issues=[]
    for name,data in files.items():
        # Third-party author/source notices may describe their own tools/history.
        own=not any(x in name.split('/') for x in ('vendor','base','third_party','ports'))
        for kind in findings(name,data,own):issues.append((name,kind))
    if issues:
        raise RuntimeError('Privacy scan failed (values suppressed):\n'+'\n'.join(n+': '+k for n,k in issues))
    return len(files)
