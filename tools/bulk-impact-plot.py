#!/usr/bin/env python

import numpy as np
import sys
import json

import matplotlib

matplotlib.use('Agg') # For headless use

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import os

if int(matplotlib.__version__.split('.')[0]) < 3:
    raise Exception('Plotting requires Matplotlib version 3.  Installed version is %s.' %
                    matplotlib.__version__)

outputfile = sys.argv[1]

programs = [
    # Novel ones
    ("Heston",
     "heston32",
     ("1062", "heston32-data/1062_quotes.in"),
     ("10000", "heston32-data/10000_quotes.in")),
    ("OptionPricing",
     "OptionPricing",
     ("D1", "OptionPricing-data/D1.in"),
     ("D2", "OptionPricing-data/D2.in")),

    # Pure ones
    ("Backprop",
     "backprop",
     ("D1", "backprop-data/D1.in"),
     ("D2", "backprop-data/D2.in")),
    ("LavaMD",
     "lavaMD",
     ("D1", "lavaMD-data/D1.in"),
     ("D2", "lavaMD-data/D2.in")),
    ("NW",
     "nw",
     ("D1", "nw-data/D1.in"),
     ("D2", "nw-data/D2.in")),

    # Modified ones
    ("NN",
     "nn",
     ("D1", "nn-data/D1.in"),
     ("D2", "nn-data/D2.in")),
    ("SRAD",
     "srad",
     ("D1", "srad-data/D1.in"),
     ("D2", "srad-data/D2.in")),
    ("Pathfinder",
     "pathfinder",
     ("D1", "pathfinder-data/D1.in"),
     ("D2", "pathfinder-data/D2.in"))
]

def plotting_info(x):
    name, filename, d1, d2 = x

    moderate_results = json.load(open('results/{}-moderate.json'.format(filename)))
    incremental_results = json.load(open('results/{}-incremental.json'.format(filename)))
    incremental_tuned_results = json.load(open('results/{}-incremental-tuned.json'.format(filename)))
    baseline_results = {}
    handwritten_results = {}

    try:
        baseline_results = json.load(open('results/{}-baseline.json'.format(filename)))
    except:
        pass

    try:
        handwritten_results = json.load(open('results/{}-rodinia.json'.format(filename)))
    except:
        pass

    try:
        handwritten_results = json.load(open('results/{}-finpar.json'.format(filename)))
    except:
        pass

    fut_name = 'benchmarks/{}.fut'.format(filename)
    baseline_fut_name = 'benchmarks/{}-baseline.fut'.format(filename)

    def for_dataset(d):
        moderate_runtime = np.mean(moderate_results[fut_name]['datasets'][d]['runtimes'])
        incremental_runtime = np.mean(incremental_results[fut_name]['datasets'][d]['runtimes'])
        incremental_tuned_runtime = np.mean(incremental_tuned_results[fut_name]['datasets'][d]['runtimes'])

        try:
            moderate_runtime = np.mean(baseline_results[baseline_fut_name]['datasets'][d]['runtimes'])
        except KeyError:
            pass

        try:
            handwritten_runtime = np.mean(handwritten_results[fut_name]['datasets'][d]['runtimes'])
        except KeyError:
            handwritten_runtime = None
        return (moderate_runtime, incremental_runtime, incremental_tuned_runtime, handwritten_runtime)

    return (name, (for_dataset(d1[1]), for_dataset(d2[1])))

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
    (d1, d2) = info
    plt.subplot(1, num_programs, i+1)
    d1_moderate_runtime, d1_untuned_runtime, d1_tuned_runtime, d1_handwritten_runtime = d1
    d2_moderate_runtime, d2_untuned_runtime, d2_tuned_runtime, d2_handwritten_runtime = d2

    d1_untuned_speedup = d1_moderate_runtime/d1_untuned_runtime
    d1_tuned_speedup = d1_moderate_runtime/d1_tuned_runtime
    d1_handwritten_speedup = d1_moderate_runtime/d1_handwritten_runtime if d1_handwritten_runtime else None

    d2_untuned_speedup = d2_moderate_runtime/d2_untuned_runtime
    d2_tuned_speedup = d2_moderate_runtime/d2_tuned_runtime
    d2_handwritten_speedup = d2_moderate_runtime/d2_handwritten_runtime if d2_handwritten_runtime else None

    plt.gca().get_yaxis().set_visible(False)

    offset = width if d1_handwritten_runtime else 0

    plt.gca().grid(True, axis='y', linestyle='-', linewidth='2', color='grey')
    plt.gca().set_title(program_name)
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off

    d1_untuned_rect, d2_untuned_rect = plt.bar([0, 1+offset],
                                               [d1_untuned_speedup, d2_untuned_speedup], width,
                                               color='#ffcebf', zorder=3, label="Not autotuned")
    d1_tuned_rect, d2_tuned_rect = plt.bar([width, 1 + width + offset],
                                           [d1_tuned_speedup, d2_tuned_speedup], width,
                                           color='#ff7c4c', zorder=3, label="Autotuned")

    if d1_handwritten_speedup and d2_handwritten_speedup:
        handwritten_ind = [width*2, 1 + width*2 + offset]
        handwritten_speedups = [d1_handwritten_speedup, d2_handwritten_speedup]
    elif d1_handwritten_speedup:
        handwritten_ind = [width*2]
        handwritten_speedups = [d1_handwritten_speedup]
    elif d2_handwritten_speedup:
        handwritten_ind = [1 + width*2 + offset]
        handwritten_speedups = [d2_handwritten_speedup]
    else:
        handwritten_ind = []
        handwritten_speedups = []

    d1_handwritten_rect = None
    d2_handwritten_rect = None
    if len(handwritten_ind) > 0:
        handwritten_rects = plt.bar(handwritten_ind,
                                handwritten_speedups, width,
                                color='#ffac4c', zorder=3, label="Handwritten")
        if d1_handwritten_speedup:
            d1_handwritten_rect = handwritten_rects[0]
            if d2_handwritten_speedup:
                d2_handwritten_rect = handwritten_rects[1]
        elif d2_handwritten_speedup:
            d2_handwritten_rect = handwritten_rects[0]
    else:
        # Hack to make the legend work.
        plt.bar([0], [0], 0, color='#ffac4c', zorder=3, label="Handwritten")

    ymin, ymax = plt.ylim()
    notch = ymax/30
    plt.ylim(ymin, ymax+4*notch)

    def rect_it(d, r, ms):
        if r:
            r_ypos = max(3*notch, r.get_y()+r.get_height()+3*notch)
            if r.get_height() < 0.1:
                label = "%.2f" % (round(r.get_height()*100)/100)
            else:
                label = "%.1f" % (round(r.get_height()*10)/10)
            plt.text(r.get_x(), r_ypos,
                     label,
                     ha='left', va='baseline', size='smaller', rotation=45)

    rect_it(d1_untuned_speedup, d1_untuned_rect, d1_untuned_runtime)
    rect_it(d2_untuned_speedup, d2_untuned_rect, d2_untuned_runtime)
    rect_it(d1_tuned_speedup, d1_tuned_rect, d1_tuned_runtime)
    rect_it(d2_tuned_speedup, d2_tuned_rect, d2_tuned_runtime)
    rect_it(d1_handwritten_speedup, d1_handwritten_rect, d1_handwritten_runtime)
    rect_it(d2_handwritten_speedup, d2_handwritten_rect, d2_handwritten_runtime)

    def time(ref):
        if ref > 1000000:
            return "$%.1fs$" % (ref/1000000)
        elif ref < 5000:
            return "$%.1fms$" % (ref/1000)
        else:
            return "${}ms$".format(int(ref/1000))


    plt.text(d1_untuned_rect.get_x() + width + offset/2, -6*notch, time(d1_moderate_runtime),
             ha='center', va='baseline', weight='bold')
    plt.text(d1_untuned_rect.get_x() + width + offset/2, -12*notch, 'D1',
             ha='center', va='baseline', weight='bold', size='larger')
    plt.text(d2_untuned_rect.get_x() + width + offset/2, -6*notch, time(d2_moderate_runtime),
             ha='center', va='baseline', weight='bold')
    plt.text(d2_untuned_rect.get_x() + width + offset/2, -12*notch, 'D2',
             ha='center', va='baseline', weight='bold', size='larger')

    i += 1

plt.legend(bbox_to_anchor=(0,-0.7), loc='lower right', ncol=3, borderaxespad=0.)
plt.rc('text')
print('Rendering {}...'.format(outputfile))
plt.savefig(outputfile, bbox_inches='tight')
