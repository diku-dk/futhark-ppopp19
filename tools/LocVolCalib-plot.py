#!/usr/bin/env python

import matplotlib
matplotlib.use('Agg') # for headless use.

from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import sys
import json

rc('text', usetex=True)

def dataset_filename(x):
    return "LocVolCalib-data/{}.in".format(x)

def dataset_prettyname(x):
    return x

def datasets():
    return [ (dataset_filename(x), dataset_prettyname(x))
             for x in ["small", "medium", "large"] ]

def plot_results(dataset):
    data_files, data_names = zip(*datasets())
    plt.gca().grid(True, axis=True, linestyle='-', linewidth='2', color='grey')

    reference = np.mean((json.load(open('results/LocVolCalib-moderate.json')))['benchmarks/LocVolCalib.fut']['datasets'][dataset_filename(dataset)]['runtimes'])/1000
    def plot_it(progname, fname, offset, **kwargs):
        j = json.load(open(fname))
        all_runtimes = j['benchmarks/{}.fut'.format(progname)]['datasets']
        xs = []
        df = dataset_filename(dataset)
        ys = [reference/(np.mean(all_runtimes[df]['runtimes'])/1000)]
        return plt.bar(offset + np.arange(len(ys)) * 4 + 10, ys, **kwargs)[0]

    plt.yticks([], [])
    plt.xticks([], [])

    rects = [plot_it('LocVolCalib', 'results/LocVolCalib-moderate.json', 0,
                     label="moderate flattening",
                     color='#abedaf'),
             plot_it('LocVolCalib', 'results/LocVolCalib-incremental.json', 1,
                     label="incremental flattening",
                     color='#e2f442'),
             plot_it('LocVolCalib', 'results/LocVolCalib-incremental-tuned.json', 2,
                     label="incremental flattening (auto-tuned)",
                     color='#ff7c4c'),
             plot_it('LocVolCalib', 'results/LocVolCalib-finpar-OutParOpenCLMP.json', 3,
                     label="FinPar (outer parallelism)",
                     color='#54c3f2'),
             plot_it('LocVolCalib', 'results/LocVolCalib-finpar-AllParOpenCLMP.json', 4,
                     label="FinPar (all parallelism)",
                     color='#8cffd4')]

    slowest = max(map(lambda r: r.get_height(), rects))

    for r in rects:
        plt.text(r.get_x(), r.get_height(), "$%.1f$" % r.get_height(),
                 verticalalignment='bottom',
                 family='sans serif',
                 size='smaller')
    plt.margins(0.1, 0)

    plt.xlabel("%s (baseline: %dms)" % (dataset, reference))

plt.figure(figsize=(6,1.5))
plt.subplot(1,3,1)
plot_results('small')
plt.subplot(1,3,2)
plot_results('medium')
plt.subplot(1,3,3)
plot_results('large')
plt.legend(bbox_to_anchor=(-0.7,-0.2), loc='upper center', ncol=2, borderaxespad=0.)

plt.savefig("LocVolCalib-runtimes.pdf", bbox_inches='tight')
