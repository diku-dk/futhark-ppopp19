#!/usr/bin/env python
#
# Transform the files produced by run-finpar-bench.sh into a JSON file.

import sys
import json

def get(dataset):
    return map(int, open('results/OptionPricing-finpar-{}.raw'.format(dataset)).read().strip().split('\n'))

d1 = get('D1')
d2 = get('D2')

print(json.dumps({'benchmarks/OptionPricing.fut':
                  {'datasets': {'OptionPricing-data/D1.in':{'runtimes': d1},
                                'OptionPricing-data/D2.in':{'runtimes': d2}}}}))
