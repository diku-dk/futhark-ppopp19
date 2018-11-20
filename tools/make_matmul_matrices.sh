#!/bin/sh
#
# Generate matrices for the matrix multiplication benchmark.

root="$(dirname "$0")/.."
. $root/binaries.mk

if [ $# -ne 3 ]; then
    echo "$1: needs three options <n> <m> <k>"
    exit 1
fi

n=$1
m=$2
k=$3

for x in $(seq $n 1 $m); do
    y=$(echo $k-$x-$x|bc)
    inf=benchmarks/matmul-data/2pow${k}_work_2pow${x}_outer
    outf=$inf.out
    echo "Generating $inf"
    $root/$FUTHARK_DATASET -b \
        -g [$(echo "2^$x"|bc)][$(echo "2^$y"|bc)]f32 \
        -g [$(echo "2^$y"|bc)][$(echo "2^$x"|bc)]f32 \
        > $inf
done
