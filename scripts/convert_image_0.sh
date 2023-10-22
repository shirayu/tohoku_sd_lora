#!/usr/bin/env bash

if [ "$1" == "" ]; then
    exit 1
fi
if [ "$2" == "" ]; then
    exit 1
fi

OUTDIR="$2/$(basename "$(dirname "$1")")"
mkdir -p "${OUTDIR}"
OUTNAME="${OUTDIR}/$(basename $1)"

if [[ -f ${OUTNAME} ]]; then
    exit 1
fi

MAX_SIZE="${MAX_SIZE:-2048}"

# Only minimize (not enlarge)
poetry run python ./scripts/resize.py -i "$1" -o "${OUTNAME}"
