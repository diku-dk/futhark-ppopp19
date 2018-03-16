#!/bin/sh
#
# Generate matrices for the matrix multiplication benchmark.

if [ $# -ne 3 ]; then
    echo "$1: needs three options <n> <m> <k>"
    exit 1
fi

n=$1
m=$2
k=$3

for x in $(seq $n 1 $m); do
    y=$(echo $k-$x|bc)
    inf=matmul-data/2pow${k}_work_2pow${x}_outer
    echo "-- compiled input @ $inf"
done
