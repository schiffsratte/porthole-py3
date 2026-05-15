#!/bin/sh
set -eu

PN=porthole
PV=20260515
DISTDIR=${DISTDIR:-/var/cache/distfiles}
OUT="${DISTDIR}/${PN}-${PV}.tar.gz"
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)

if [ ! -w "${DISTDIR}" ]; then
    DISTDIR=/tmp/porthole-distfiles
    OUT="${DISTDIR}/${PN}-${PV}.tar.gz"
    mkdir -p "${DISTDIR}"
fi

tmpdir=$(mktemp -d)
trap 'rm -rf "${tmpdir}"' EXIT INT TERM

mkdir -p "${tmpdir}/${PN}-${PV}"

tar \
    --exclude='.git' \
    --exclude='.agents' \
    --exclude='.codex' \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='pyvenv.cfg' \
    --exclude='notes' \
    --exclude='packaging/portage' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='build' \
    --exclude='dist' \
    --exclude='porthole.egg-info' \
    -C "${ROOT_DIR}" \
    -cf - . | tar -C "${tmpdir}/${PN}-${PV}" -xf -

tar \
    --sort=name \
    --mtime='UTC 2026-05-15' \
    --owner=0 \
    --group=0 \
    --numeric-owner \
    -C "${tmpdir}" \
    -cf - "${PN}-${PV}" | gzip -n > "${OUT}"

echo "Created ${OUT}"
if [ "${DISTDIR}" != "/var/cache/distfiles" ]; then
    echo "Install it with:"
    echo "  sudo install -Dm0644 '${OUT}' '/var/cache/distfiles/${PN}-${PV}.tar.gz'"
fi
