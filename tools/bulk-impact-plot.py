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

programs = [ # Novel ones
            ("OptionPricing",
             "OptionPricing",
             [("medium", "OptionPricing-data/medium.in"),
              ("skewed", "OptionPricing-data/skewed.in")]),
            ("Heston",
             "heston32",
             [("1062", "heston32-data/1062_quotes.in"),
              ("10000", "heston32-data/10000_quotes.in")]),

            # Pure ones
            ("Backprop",
             "backprop",
             [("small", "backprop-data/small.in"),
              ("medium", "backprop-data/medium.in")]),
            ("LavaMD",
             "lavaMD",
             [("27x64x30", "lavaMD-data/27_64_30.in"),
              ("10x100x27", "lavaMD-data/10_100_27.in")]),
            ("NW",
             "nw",
             [("large", "nw-data/large.in"),
              ("medium", "nw-data/medium.in")]),

            # Modified ones
            ("NN",
             "nn",
             [("n=256", "nn-data/n256_m2048"),
              ("n=4096", "nn-data/n4096_m128")]),
            ("SRAD",
             "srad",
             [("1024 small", "srad-data/1024-small-images.in"),
              ("1 large", "srad-data/one-big-image.in")]),
            ("Pathfinder",
             "pathfinder",
             [("391x100x256", "pathfinder-data/391_100_256.in"),
              ("1x100x100096", "pathfinder-data/1_100_100096.in")])]

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
plt.figure(figsize=(10, 1))

for (program_name, info) in program_plots:
    print('Plotting {}...'.format(program_name))
    plt.subplot(1, num_programs, num_programs-i)

    dataset_names, ref_runtimes, untuned_runtimes, tuned_runtimes = zip(*info)
    untuned_speedups = np.array(ref_runtimes)/np.array(untuned_runtimes)
    tuned_speedups = np.array(ref_runtimes)/np.array(tuned_runtimes)

    plt.gca().get_yaxis().set_visible(False)

    ind = np.arange(len(ref_runtimes))
    plt.gca().grid(True, axis='y', linestyle='-', linewidth='2', color='grey')
    plt.gca().set_title(program_name)
    plt.gca().set_xticks(ind + width)
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

    notch = ymax/30

    for (dataset_name, r1, r2, ref) in zip(dataset_names, notuned_rects,
                                           tuned_rects, ref_runtimes):
        if ref > 1000000:
            time = "$%.2fs$" % (ref/1000000)
        elif ref < 5000:
            time = "$%.2fms$" % (ref/1000)
        else:
            time = "${}ms$".format(int(ref/1000))

        plt.text(r1.get_x()+r1.get_width(), r1.get_y()-6*notch,
                 "{}".format(dataset_name),
                 ha='center', va='top', rotation=360-25)
        plt.text(r1.get_x()+r1.get_width(), r1.get_y()-notch,
                 time, ha='center', va='top')

        r1_ypos = max(4*notch, r1.get_y()+r1.get_height()+3*notch)
        r2_ypos = max(4*notch, r2.get_y()+r2.get_height()+3*notch)

        if np.abs(r2_ypos - r1_ypos) < 4*notch:
            if r1_ypos > 4*notch:
                r1_ypos = r2_ypos - 4*notch
            else:
                r2_ypos = r1_ypos + 4*notch

        if r1.get_height() > r2.get_height() and r1_ypos < r2_ypos:
            (r1_ypos, r2_ypos) = (r2_ypos, r1_ypos)

        plt.text(r1.get_x(), r1_ypos,
                 "%.1f$\\times$" % (round(r1.get_height()*10)/10),
                 ha='left', va='top')
        plt.text(r2.get_x(), r2_ypos,
                 "%.1f$\\times$" % (round(r2.get_height()*10)/10),
                 ha='left', va='top')

    i += 1

plt.legend(bbox_to_anchor=(9.4,-1), loc='lower right', ncol=2, borderaxespad=0.)
plt.rc('text')
print('Saving {}...'.format(outputfile))
plt.savefig(outputfile, bbox_inches='tight')
