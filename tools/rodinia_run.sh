#!/bin/sh
#
# Wrapper script for running Rodinia benchmarks.

set -e

export OPENCL_DEVICE_ID=$(bin/gpuid "$FUTHARK_OPENCL_DEVICE")
export RODINIA_RUNS=$2

cd rodinia_3.1-patched/$1
make clean
make
./run
