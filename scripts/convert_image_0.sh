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
MAGICK_CONFIGURE_PATH=~/.config/ImageMagick.xml \
    convert \
    -limit disk 0 \
    -fuzz 5% \
    -trim \
    -resize "${MAX_SIZE}x${MAX_SIZE}^" \
    -gravity center \
    "$1" \
    "${OUTNAME}" \
