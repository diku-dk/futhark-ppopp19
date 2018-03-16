#!/bin/sh
#
# Create FFT data sets that try to keep the amount of work constant.

if [ $# -ne 3 ]; then
    echo "$1: needs three options <n> <m> <k>"
    exit 1
fi

x=$1
y=$2
k=$3 # magical workload parameter.

for n in $(seq $x 1 $y); do
    m=$(echo "(2^$k)/((2^(2*$n))*$n)"|bc)
    inf=benchmarks/fft-data/edge_2pow${n}
    outf=$inf.out
    echo "Generating $inf ($m matrices):"
    futhark-dataset -b \
        -g [$m][$(echo 2^$n|bc)][$(echo "2^$n"|bc)]f32 \
        > $inf
    echo "Generating $outf"
    benchmarks/fft -b < $inf > $outf;
done
