#!/usr/bin/env bash

if [ "$1" == "" ]; then
    exit 1
fi
if [ "$2" == "" ]; then
    exit 1
fi

# Max pixels
if [ "$3" == "" ]; then
    exit 1
fi

# Min pixels
if [ "$4" == "" ]; then
    exit 1
fi

OUTDIR="$2/$(basename "$(dirname "$1")")"
mkdir -p "${OUTDIR}"
OUTNAME="${OUTDIR}/$(basename $1)"

poetry run python ./scripts/resize.py --remove_alpha -i "$1" -o "${OUTNAME}" --size "$3" --min_size "$4"
