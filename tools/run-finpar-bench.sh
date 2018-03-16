#!/bin/sh
#
# FinPar is relatively unstructured:
#
#  * It is configured by directly editing files.
#  * The runtime results are not produced in a machine-readable form.
#
# Hence this script serves as a wrapper, and in particular edits the
# bundled configuration file directory to respect
# $FUTHARK_OPENCL_DEVICE.  Ugh.

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 <benchmark> <dataset>"
    exit 1
fi

benchmark=$1
dataset=$2

gpuid=$(bin/gpuid "$FUTHARK_OPENCL_DEVICE")

sed 's/^GPU_DEVICE_ID=.*$/GPU_DEVICE_ID='$gpuid'/' -i finpar/platform.mk

echo "Putting debug output for $benchmark ($dataset) in finpar.log" >&2
(cd finpar/$benchmark && make 2>&1) >> finpar.log

avg() {
    awk ' /Runtime in micro/ { print $1 }'
}

for i in $(seq 10); do
    (cd finpar/$benchmark && make run_$dataset) | tee -a finpar.log
done | avg
