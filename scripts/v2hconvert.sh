#!/bin/bash

set -e

INPUT_FILE=$1
OUTPUT_DIR=$2

ffmpeg -i $INPUT_FILE -vf 'split[original][copy];[copy]scale=ih*16/9:-1,crop=h=iw*9/16,gblur=sigma=20[blurred];[blurred][original]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2' $OUTPUT_DIR/$(basename $INPUT_FILE)
