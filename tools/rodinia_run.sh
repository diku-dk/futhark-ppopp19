
#!/bin/sh
#
# Wrapper script for running Rodinia benchmarks.

set -e

if [ $# -lt 3 ]; then
    echo "Usage: $0 <benchmark> <dataset> <runs>"
    exit 1
fi

benchmark=$1
dataset=$2
runs=$3

export OPENCL_DEVICE_ID=$(bin/gpuid "$FUTHARK_OPENCL_DEVICE")
export RODINIA_RUNS=$runs

cd rodinia_3.1-patched/opencl/$benchmark
make clean >&2
make >&2
./run "$dataset" >&2

# Skip the first measurement; we treat it as a warmup run.
tail -n +2 runtimes
