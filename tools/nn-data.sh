#!/bin/sh

set -e

FUTHARK_DATASET=$1
N=$2
M=$3
neighbors=100

echo $neighbors

$FUTHARK_DATASET -b --f32-bounds=30:30 -g [$N]f32
$FUTHARK_DATASET -b --f32-bounds=90:90 -g [$N]f32
$FUTHARK_DATASET -b --f32-bounds=0:360 -g [$N][$M]f32 -g [$N][$M]f32
