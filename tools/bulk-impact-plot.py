#!/usr/bin/env python

import numpy as np
import sys
import json

import matplotlib

matplotlib.use('Agg') # For headless use

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import os

outputfile = sys.argv[1]

programs = [("OptionPricing",
             "OptionPricing",
             [("small", "OptionPricing-data/small.in"),
              ("medium", "OptionPricing-data/medium.in"),
              ("skewed", "OptionPricing-data/skewed.in")]),
            ("NN",
             "nn",
             [("n=256", "nn-data/n256_m2048"),
              ("n=1024", "nn-data/n1024_m512"),
              ("n=4096", "nn-data/n4096_m128")])]

def plotting_info(x):
    name, filename, datasets = x

    moderate_results = json.load(open('results/{}-moderate.json'.format(filename)))
    incremental_results = json.load(open('results/{}-incremental.json'.format(filename)))
    incremental_tuned_results = json.load(open('results/{}-incremental-tuned.json'.format(filename)))
    fut_name = 'benchmarks/{}.fut'.format(filename)

    bars = []
    for (dataset_name, dataset_file) in datasets:
        moderate_runtime = np.mean(moderate_results[fut_name]['datasets'][dataset_file]['runtimes'])
        incremental_runtime = np.mean(incremental_results[fut_name]['datasets'][dataset_file]['runtimes'])
        incremental_tuned_runtime = np.mean(incremental_tuned_results[fut_name]['datasets'][dataset_file]['runtimes'])
        bars += [(dataset_name, moderate_runtime, incremental_runtime, incremental_tuned_runtime)]
    return (name, bars)

program_plots = map(plotting_info, programs)

bars_per_program = map(lambda x: len(x[1]), program_plots)
num_bars = sum(bars_per_program)
num_programs = len(program_plots)
width = 0.33

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
font = {'family': 'sans-serif',
        'size' : 9}
plt.rc('font', **font)
plt.rc('text', usetex=True)
grey='#aaaaaa'

i = 0
plt.figure(figsize=(5, 1))

for (program_name, info) in program_plots:
    plt.subplot(1, num_programs, num_programs-i)

    dataset_names, ref_runtimes, untuned_runtimes, tuned_runtimes = zip(*info)
    untuned_speedups = np.array(ref_runtimes)/np.array(untuned_runtimes)
    tuned_speedups = np.array(ref_runtimes)/np.array(tuned_runtimes)

    ind = np.arange(len(ref_runtimes))
    plt.gca().grid(True, axis='y', linestyle='-', linewidth='2', color='grey')
    plt.gca().set_title(program_name)
    plt.gca().set_xticks(ind + width / 2)
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off

    notuned_rects = plt.bar(ind,
                            untuned_speedups, width,
                            color='#ffcebf', hatch='\\', zorder=3, label="Not autotuned")
    tuned_rects = plt.bar(ind + width,
                          tuned_speedups, width,
                          color='#ff7c4c', hatch='*', zorder=3, label="Autotuned")
    ymax = plt.ylim()[1]

    if ymax > 3:
        plt.gca().set_yticks(np.arange(np.ceil(plt.ylim()[1])))
    else:
        plt.gca().set_yticks(np.arange(np.ceil(plt.ylim()[1]/0.5))*0.5)
    notch = ymax/30

    for (dataset_name, r, ref) in zip(dataset_names, notuned_rects, ref_runtimes):
        plt.text(r.get_x()+r.get_width(), r.get_y()-notch,
                 "{}\n${}ms$".format(dataset_name, int(ref/1000)),
                 ha='center', va='top')

    i += 1

plt.legend(bbox_to_anchor=(1,-0.7), loc='lower center', ncol=2, borderaxespad=0.)
plt.rc('text')
plt.savefig(outputfile, bbox_inches='tight')
