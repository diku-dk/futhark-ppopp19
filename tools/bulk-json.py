#!/usr/bin/env python

import sys
import json

rodinia_benchmarks = [('backprop', 'data/medium.in'),
                      ('hotspot', 'data/1024.in'),
                      ('cfd', 'data/fvcorr.domn.193K.toa'),
                      ('kmeans', 'data/kdd_cup.in'),
                      ('lavaMD', 'data/10_boxes.in'),
                      ("nn", 'data/medium.in'),
                      ('pathfinder', 'data/medium.in'),
                      ('srad', 'data/image.in')]

parboil_benchmarks = [('mri-q', 'data/large.in'),
                      ('stencil', 'data/default.in'),
                      ('tpacf', 'data/large.in')]

def get(benchmark):
    return map(int, open('results/{}'.format(benchmark)).read().strip().split('\n'))

results = {}

for (name, dataset) in rodinia_benchmarks:
    data = {'datasets': {dataset: {'runtimes': get('{}-rodinia.runtimes'.format(name))}}}
    results['futhark-benchmarks/rodinia/{}/{}.fut'.format(name, name)] = data

for (name, dataset) in parboil_benchmarks:
    data = {'datasets': {dataset: {'runtimes': get('{}-parboil.runtimes'.format(name))}}}
    results['futhark-benchmarks/parboil/{}/{}.fut'.format(name, name)] = data

results.update(json.load(open('results/OptionPricing-finpar.json')))

print(json.dumps(results))
