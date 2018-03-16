#!/usr/bin/env python
#
# Transform the files produced by run-finpar-bench.sh into a JSON file.

import sys
import json

def get(dataset):
    return map(int, open('results/OptionPricing-finpar-{}.raw'.format(dataset)).read().strip().split('\n'))

small = get('small')
medium = get('medium')
large = get('large')

print(json.dumps({'futhark-benchmarks/finpar/OptionPricing.fut':
                  {'datasets': {'OptionPricing-data/small.in':{'runtimes': small},
                                'OptionPricing-data/medium.in':{'runtimes': medium},
                                'OptionPricing-data/large.in':{'runtimes': large}}}}))
