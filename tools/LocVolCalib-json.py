#!/usr/bin/env python
#
# Transform the files produced by run-finpar-bench.sh into a JSON file
# that can be processed by LocVolCalib-plot.py (which accepts the same
# format as produced by futhark-bench).

import sys
import json

benchmark = sys.argv[1]

def get(dataset):
    return map(int, open('results/LocVolCalib-{}-{}.raw'.format(benchmark, dataset)).read().strip().split('\n'))

small = get('small')
medium = get('medium')
large = get('large')

print(json.dumps({'benchmarks/LocVolCalib.fut':
                  {'datasets': {'LocVolCalib-data/small.in':{'runtimes': small},
                                'LocVolCalib-data/medium.in':{'runtimes': medium},
                                'LocVolCalib-data/large.in':{'runtimes': large}}}}))
