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

def dataset_filename(x, k):
    return "matmul-data/2pow{}_work_2pow{}_outer".format(k, x)

def dataset_prettyname(x, k):
    return str(x)

def datasets(n, m, k):
    return [ (dataset_filename(x, k), dataset_prettyname(x, k))
             for x in range(n, m+1, 1) ]

def plot_datasets(handwritten, n, m, k):
    s = [r'\begin{tabular}{lrrrr}',
         r'\textbf{$n$}&\textbf{Moderate}&\textbf{Incr.}&\textbf{Tuned}&\textbf{%s}\\\hline' % handwritten]
    _, ax = plt.subplots()
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: "${}\mu{{}}s$".format(int(x))))

    data_files, data_names = zip(*datasets(n, m, k))
    plt.xticks(range(len(data_files)), data_names)
    plt.gca().grid(True, axis='y', linestyle='-', linewidth='2')

    def table_it(variants):
        runtimes = {}

        for v in variants:
            f = 'benchmarks/{}.fut'.format(v)
            j = json.load(open('results/{}.json'.format(v)))
            runtimes[v] = j['benchmarks/matmul.fut']['datasets']

        for (df, i) in zip(data_files, range(len(data_files))):
            l = '{} '.format(i)
            for v in variants:
                ms = np.mean(runtimes[v][df]['runtimes'])
                l += '& %.0fms ' % ms
            l += r'\\'
            s.append(l)

    table_it(['matmul-moderate', 'matmul-incremental', 'matmul-incremental-tuned', 'matmul-reference'])
    s.append(r'\end{tabular}')

    def plot_it(fname, **kwargs):
        j = json.load(open(fname))
        all_runtimes = j['benchmarks/matmul.fut']['datasets']
        xs = []
        ys = []
        for (df, i) in zip(data_files, range(len(data_files))):
            ms = np.mean(all_runtimes[df]['runtimes'])
            ys += [ms]
        return plt.plot(range(len(ys)), ys, linewidth=3, markersize=10, **kwargs)[0]

    plot_it('results/matmul-moderate.json', label='moderate',
            linestyle='-.', color='green')
    line = plot_it('results/matmul-incremental.json', label='incremental',
                   linestyle='--', marker='v', color='black',
                   )
    plot_it('results/matmul-incremental-tuned.json', label='incremental (auto-tuned)',
            marker='o', fillstyle='none', color='red')
    plot_it('results/matmul-reference.json', label=handwritten,
            linestyle='dashed', color='grey')

    slowest = max(line.get_ydata())
    if slowest < 500:
        ylim = 500
    elif slowest < 3000:
        ylim = 3000
    else:
        ylim = 12000

    plt.ylim(ymax=ylim,ymin=0)
    plt.xlabel("$n$", size=20)
    plt.legend(loc='upper left', ncol=2, framealpha=1)
    return '\n'.join(s)

handwritten=sys.argv[1]
outfile=sys.argv[2]
tablefile=sys.argv[3]
n=int(sys.argv[4])
m=int(sys.argv[5])
k=int(sys.argv[6])

table = plot_datasets(handwritten, n, m, k)
plt.gcf().set_size_inches(6, 3)
plt.savefig(outfile, bbox_inches='tight')
with open(tablefile, "w") as f:
    f.write(table)
    f.write('\n')
