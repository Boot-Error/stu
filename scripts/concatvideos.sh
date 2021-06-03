#!/bin/bash

set -e

INPUT_DIR=$1

echo Cleaning temporary files
rm -rvf $INPUT_DIR/*.ts

function convertToTs() {
  INDIR=$(dirname $1)
  OUTFILE=$INDIR/$(basename $1 .mp4).ts
  # from https://stackoverflow.com/a/37216101
  ffmpeg -i $1 -c copy -bsf:v h264_mp4toannexb -f mpegts $OUTFILE
}

export -f convertToTs

echo Create Temp files
ls $INPUT_DIR/*.mp4 | xargs -I {} convertToTs {}


# Concat to final output
ffmpeg -i "concat:$(ls $INPUT_DIR/*.ts | tr '\n' '|')" -c copy -bsf:a aac_adtstoasc output.mp4
