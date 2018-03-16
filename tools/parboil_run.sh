#!/bin/sh
#
# Wrapper script for running Parboil benchmark.

set -e

export OPENCL_DEVICE_ID=$(bin/gpuid "$FUTHARK_OPENCL_DEVICE")

benchmark=$1
variation=$2
dataset=$3
runs=$4

cd parboil-patched/

for i in $(seq $runs); do
    ./parboil run $benchmark $variation $dataset | grep Kernel|awk '{print int($3*1000000)}'
done
