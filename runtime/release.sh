#!/bin/sh
# Build, strip and package a Rhythmer release: ./release.sh v0.1.0-alpha.1
# writes dist/Rhythmer-MPC-Sample-<version>.zip and its .sha256.
set -eu
cd "$(dirname "$0")"
[ $# -ge 1 ] || { echo "usage: ./release.sh VERSION [--allow-dirty]" >&2; exit 2; }
RHYTHMER_VERSION=$1 ./build.sh
docker run --rm --platform linux/arm64 -v "$PWD:/work" sample-base-builder \
    sh -c 'strip -o build/rhythmer.release build/rhythmer && build/rhythmer.release --self-test build/release-test.wav'
python3 tools/make_release.py "$@"
