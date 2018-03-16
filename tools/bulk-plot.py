#!/usr/bin/env python

import numpy as np
import sys
import json

import matplotlib

matplotlib.use('Agg') # For headless use

import matplotlib.pyplot as plt
import os

outputfile = sys.argv[1]

rodinia_programs = [("Backprop", "rodinia/backprop/backprop.fut", 'data/medium.in'),
                    ("CFD", "rodinia/cfd/cfd.fut", 'data/fvcorr.domn.193K.toa'),
                    ("HotSpot", "rodinia/hotspot/hotspot.fut", 'data/1024.in'),
                    ("K-means", "rodinia/kmeans/kmeans.fut", 'data/kdd_cup.in'),
                    ("LavaMD", "rodinia/lavaMD/lavaMD.fut", 'data/10_boxes.in'),
                    ("Pathfinder", "rodinia/pathfinder/pathfinder.fut", 'data/medium.in'),
                    ("SRAD", "rodinia/srad/srad.fut", 'data/image.in')]

parboil_programs = [("MRI-Q", "parboil/mri-q/mri-q.fut", "data/large.in"),
                    ("Stencil", "parboil/stencil/stencil.fut", "data/default.in"),
                    ("TPACF", "parboil/tpacf/tpacf.fut", "data/large.in")]

reference_results = json.load(open('results/bulk-reference.json'))
moderate_results = json.load(open('results/bulk-moderate.json'))
incremental_results = json.load(open('results/bulk-incremental.json'))

def plotting_info(x):
    name, filename, dataset = x
    filename_with_dir = 'futhark-benchmarks/{}'.format(filename)
    ref_runtime = np.mean(reference_results[filename_with_dir]['datasets'][dataset]['runtimes'])
    moderate_runtime = np.mean(moderate_results[filename_with_dir]['datasets'][dataset]['runtimes'])
    incremental_runtime = np.mean(incremental_results[filename_with_dir]['datasets'][dataset]['runtimes'])

    moderate_speedup = ref_runtime / moderate_runtime
    incremental_speedup = ref_runtime / incremental_runtime
    return (name, ref_runtime, moderate_speedup, incremental_speedup)

to_plot = list(filter(lambda x: x is not None,
                      map(plotting_info,
                          rodinia_programs + parboil_programs)))

(program_names, ref_runtimes, program_speedups, program_aux_speedups) = zip(*to_plot)

N = len(to_plot)

# the widths of the bar
width = 0.5
def compute_space(x):
    if x[2] == 0.0:
        return width*2
    else:
        return width*3
spaces = np.array(list(map(compute_space, to_plot)))

# the x locations for the bars
ind = width+np.concatenate(([0], np.cumsum(spaces)[:-1]))

fig, ax = plt.subplots()

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
font = {'family': 'normal',
        'size' : 9}
plt.rc('font', **font)
grey='#aaaaaa'

ymax=8
ax.set_ylim([0.0,ymax])
ax.set_xlim([0.0,ind[-1]+1])
ax.set_ylabel('Speedup')
ax.set_xticks(ind+width)
ax.set_xticklabels(program_names)
ax.xaxis.set_ticks_position('none')
ax.yaxis.set_ticks_position('none')
ax.yaxis.grid(color=grey,zorder=0)
ax.spines['bottom'].set_color(grey)
ax.spines['top'].set_color('none')
ax.spines['left'].set_color(grey)
ax.spines['right'].set_color('none')

gridlines = ax.get_xgridlines() + ax.get_ygridlines()
for line in gridlines:
    line.set_linestyle('-')

rects = ax.bar(ind, program_speedups, width,
               color='#abedaf', hatch='/', zorder=3, label='Moderate')
aux_rects = ax.bar(ind+width, program_aux_speedups, width,
                   color='#ffcebf', hatch='\\', zorder=3, label='Incremental')

def label_rect(rect):
    height = rect.get_height()

    if height == 0.0:
        return

    font = {'family': 'sans-serif',
            'size': 9,
    }
    bounded_height = min(ymax, height)
    ax.text(rect.get_x() + rect.get_width(), 1.05*bounded_height,
            '%.2f' % height,
            ha='center', va='bottom', fontdict=font, rotation=45)

def add_ref(x):
    rect, runtime = x
    ax.text(rect.get_x() + rect.get_width(), -2,
            '%.2fms' % (runtime/1000),
            ha='center', va='baseline', fontdict=font)

map(label_rect, rects)
map(label_rect, aux_rects)
map(add_ref, zip(rects, ref_runtimes))

ax.legend(bbox_to_anchor=(0., 1.15, 1., .115), loc=3, ncol=2, borderaxespad=0.)

fig.set_size_inches(10.5, 1.5)
plt.rc('text')
plt.savefig(outputfile, bbox_inches='tight')
