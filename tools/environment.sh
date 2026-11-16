#!/bin/sh
# Source this file from the repository root on macOS.
mount | /usr/bin/grep -q ' on /Volumes/SSD (' || {
    echo 'RHYTHMER OS: /Volumes/SSD is not mounted; stopping.' >&2
    return 1 2>/dev/null || exit 1
}
export RHYTHMER_WORK=/Volumes/SSD/Development/BuildCache/rhythmer-os
export RHYTHMER_VM_NAME=${RHYTHMER_VM_NAME:-rhythmer-os}
export RHYTHMER_VM_HOME=/Volumes/SSD/Development/VirtualMachines/Lima/rhythmer-os
export TMPDIR="$RHYTHMER_WORK/tmp"
export CLANG_MODULE_CACHE_PATH=/Volumes/SSD/Development/Caches/rhythmer-os/clang
export PYTHONDONTWRITEBYTECODE=1
export PATH="/Volumes/SSD/Development/Toolchains/rhythmer-os/bin:$PATH"
mkdir -p "$TMPDIR" "$CLANG_MODULE_CACHE_PATH"
