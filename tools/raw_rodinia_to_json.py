#!/usr/bin/env python

import sys
import json

program = sys.argv[1]
datasets = sys.argv[2:]

fut_program = 'benchmarks/{}.fut'.format(program)
d = {fut_program : { 'datasets': {}}}

for dataset in datasets:
    runtimes = []
    fut_dataset = "{}-data/{}.in".format(program, dataset)
    d[fut_program]['datasets'][fut_dataset] = {}
    with open('results/{}-rodinia-{}.runtimes'.format(program, dataset)) as results:
        for line in results:
            runtimes.append(int(line))
    d[fut_program]['datasets'][fut_dataset]['runtimes'] = runtimes

print(json.dumps(d))
