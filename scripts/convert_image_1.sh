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
if [ "$3" == "" ]; then
    exit 1
fi

OUTDIR="$2/$(basename "$(dirname "$1")")"
mkdir -p "${OUTDIR}"
OUTNAME="${OUTDIR}/$(basename $1)"

convert \
    -background white \
    -alpha remove \
    -alpha off \
    -fuzz 5% \
    -trim \
    -resize "$3x$3" \
    -gravity center \
    "$1" "${OUTNAME}"

identify -format '%F@%w@%h' "${OUTNAME}" | awk -F'@' '{ if($2<'"$4"'){print "mogrify -extent '"$4"'x"$3 " -gravity center "  $1 } }' | bash -x
