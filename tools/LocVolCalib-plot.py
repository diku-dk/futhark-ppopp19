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
    plt.gca().grid(True, axis='y', linestyle='-', linewidth='2', color='grey')

    def plot_it(progname, fname, offset, **kwargs):
        j = json.load(open(fname))
        all_runtimes = j['benchmarks/{}.fut'.format(progname)]['datasets']
        xs = []
        df = dataset_filename(dataset)
        ys = [np.mean(all_runtimes[df]['runtimes'])/1000]
        return plt.bar(offset + np.arange(len(ys)) * 8 + 10, ys, **kwargs)[0]

    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off') # labels along the bottom edge are off

    rects = [plot_it('LocVolCalib', 'results/LocVolCalib-moderate.json', 0,
                     label="moderate flattening",
                     color='#abedaf', hatch='/'),
             plot_it('LocVolCalib-partridag', 'results/LocVolCalib-partridag-moderate.json', 1,
                     label="moderate flattening (only parallel tridag)",
                     color='#adc3ff', hatch='+'),
             plot_it('LocVolCalib', 'results/LocVolCalib-incremental.json', 2,
                     label="incremental flattening",
                     color='#ffcebf', hatch='\\'),
             plot_it('LocVolCalib-partridag', 'results/LocVolCalib-partridag-incremental.json', 3,
                     label="incremental flattening (only parallel tridag)",
                     color='#e2f442', hatch='X'),
             plot_it('LocVolCalib-partridag', 'results/LocVolCalib-partridag-incremental-tuned.json', 4,
                     label="incremental flattening (only parallel tridag; auto-tuned)",
                     color='#ff7c4c', hatch='*'),
             plot_it('LocVolCalib', 'results/LocVolCalib-finpar-OutParOpenCLMP.json', 5,
                     label="FinPar (only outer parallelism)",
                     color='#54c3f2', hatch='o'),
             plot_it('LocVolCalib', 'results/LocVolCalib-finpar-AllParOpenCLMP.json', 6,
                     label="FinPar (all parallelism)",
                     color='#8cffd4', hatch='.')]
    reference = rects[-1].get_height()
    slowest = max(map(lambda r: r.get_height(), rects))

    if slowest < 300:
        ylim = 300
    elif slowest < 600:
        ylim = 600
    elif slowest < 3000:
        ylim = 3000
    else:
        ylim = 6000

    for r in rects:
        plt.text(r.get_x()-0.1, r.get_height()+ylim/60, "$\\times$%.1f" % (r.get_height()/reference))
    plt.margins(0.1, 0)
    plt.xlabel(dataset)
    plt.ylim(ymax=ylim)

plt.figure(figsize=(12,3))
plt.subplot(1,3,1)
plot_results('small')
plt.subplot(1,3,2)
plot_results('medium')
plt.subplot(1,3,3)
plot_results('large')
plt.legend(bbox_to_anchor=(-0.8,-0.2), loc='upper center', ncol=2, borderaxespad=0.)
plt.tight_layout()

plt.savefig("LocVolCalib-runtimes.pdf", bbox_inches='tight')
