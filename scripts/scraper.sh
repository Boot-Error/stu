#!/bin/bash

set -e

week=$(date +week%U)
dataDir=data/$week

mkdir -pv $dataDir

pushd $dataDir || exit 1
tiktok-scraper trend -d -n 10 -t csv
popd

echo Done
