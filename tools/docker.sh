#!/bin/sh
# A Docker-compatible CLI over the dedicated SSD-backed Lima/nerdctl instance.
set -eu
mount | /usr/bin/grep -q ' on /Volumes/SSD (' || {
    echo 'SSD is not mounted; stopping.' >&2
    exit 1
}
exec env LIMA_HOME=/Volumes/SSD/Development/VirtualMachines/Lima/rhythmer-os \
    /Volumes/SSD/Development/Toolchains/fm1-six-tooling/lima/bin/limactl shell "${RHYTHMER_VM_NAME:-rhythmer-os}" nerdctl "$@"
