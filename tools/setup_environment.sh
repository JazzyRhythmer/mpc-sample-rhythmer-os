#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
. ./tools/environment.sh
LIMA_BIN=/Volumes/SSD/Development/Toolchains/fm1-six-tooling/lima/bin/limactl
[ -x "$LIMA_BIN" ] || { echo "Configured shared Lima tool is missing: $LIMA_BIN" >&2; exit 1; }
mkdir -p /Volumes/SSD/Development/Toolchains/rhythmer-os/bin "$RHYTHMER_VM_HOME"
cp tools/docker.sh /Volumes/SSD/Development/Toolchains/rhythmer-os/bin/docker
chmod +x /Volumes/SSD/Development/Toolchains/rhythmer-os/bin/docker
env LIMA_HOME="$RHYTHMER_VM_HOME" "$LIMA_BIN" start -y --name="$RHYTHMER_VM_NAME" config/lima.yaml
python3 tools/build.py prepare
cd "$RHYTHMER_WORK/runtime"
python3 tools/dependencies.py
docker build --platform linux/arm64 -t sample-base-builder base/tools
docker build --platform linux/arm64 -t rhythmer-upstream-builder tools/plugin_support
docker build --platform linux/arm64 -t rhythmer-builder "$RHYTHMER_WORK/plugins/tools/qa-image"
