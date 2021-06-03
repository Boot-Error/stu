#!/bin/bash

set -e

INPUT_DIR=$1
OUTPUT_DIR=$2

function convertToLandspaceWithBlur() {
  input_file=$1
  output_file=$OUTPUT_DIR/$(basename $input_file)
  ffmpeg -i {} -vf 'split[original][copy];[copy]scale=ih*16/9:-1,crop=h=iw*9/16,gblur=sigma=20[blurred];[blurred][original]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2' $output_file 

}

export -f convertToLandspaceWithBlur

ls $INPUT_DIR/*.mp4 | xargs -I {} convertToLandspaceWithBlur {}