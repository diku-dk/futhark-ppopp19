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
    return "fft-data/edge_2pow{}".format(x)

def dataset_prettyname(x):
    return "${}$".format(x)

def datasets(x, y, k):
    return [ (dataset_filename(x), dataset_prettyname(x))
             for x in range(x, y+1, 1) ]

def plot_datasets(n, ymax=None):
    _, ax = plt.subplots()
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: "${}\mu{{}}s$".format(int(x))))

    data_files, data_names = zip(*datasets(2, 10, 24))
    plt.xticks(range(len(data_files)), data_names, size=20)
    plt.gca().grid(True, axis='y', linestyle='-', linewidth='2')

    def plot_it(fname, **kwargs):
        j = json.load(open(fname))
        all_runtimes = j['benchmarks/fft.fut']['datasets']
        xs = []
        ys = []
        for df in data_files:
            ys += [np.mean(all_runtimes[df]['runtimes'])]
        plt.plot(range(len(ys)), ys, linewidth=3, markersize=10, **kwargs)

    plot_it('results/fft-moderate.json', label='moderate',
            linestyle='-.', color='green')
    plot_it('results/fft-incremental.json', label='incremental',
            linestyle='--', marker='v', color='black')
    plot_it('results/fft-incremental-tuned.json', label='incremental (auto-tuned)',
            marker='o', fillstyle='none', color='red')
    plt.ylim(ymin=0, ymax=ymax)
    plt.xlabel("$n$", size=20)
    plt.legend(loc='upper right')

plot_datasets(10, ymax=8000)
plt.gcf().set_size_inches(8, 4)
plt.savefig("fft-runtimes.pdf", bbox_inches='tight')
