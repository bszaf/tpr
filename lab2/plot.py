#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import time
import csv

def create_seria((proc, time, speedup, eff, serial_fraction), row):
    return (
        proc + [int(row[0])],
        time + [float(row[1])],
        speedup + [float(row[2])],
        eff + [float(row[3])],
        serial_fraction + [float(row[4])]
    )

def get_masurements_from_file(filename):
    filename = "data/{}".format(filename)
    with open(filename) as file:
        csv_reader = csv.reader(file, delimiter=',')
        acc = ([], [], [], [], [])
        return reduce(create_seria, csv_reader, acc)
        close(filename)


non_scaling_files = [('10^6 points', 'non_scaling_1000000.csv'),
                     ('10^7 points', 'non_scaling_10000000.csv'),
                     ('10^8 points', 'non_scaling_100000000.csv'),
                     ('10^9 points', 'non_scaling_1000000000.csv')]

scaling_files = [('10^6 points', 'non_scaling_1000000.csv'),
                 ('10^7 points', 'non_scaling_10000000.csv'),
                 ('10^8 points', 'non_scaling_100000000.csv'),
                 ('10^9 points', 'non_scaling_1000000000.csv')]

for label, file in non_scaling_files:
    (procs, times, speedups, eff, s) = get_masurements_from_file(file)
    procs = procs[1:]
    times = times[1:]
    speedups = speedups[1:]
    eff = eff[1:]
    s = s[1:]
    plt.figure(1)
    plt.scatter(procs, speedups, label=label)
    plt.figure(2)
    plt.scatter(procs, eff, label=label)
    plt.figure(3)
    plt.scatter(procs, s, label=label)

for label, file in scaling_files:
    (procs, times, speedups, eff, s) = get_masurements_from_file(file)
    procs = procs[1:]
    times = times[1:]
    speedups = speedups[1:]
    eff = eff[1:]
    s = s[1:]
    plt.figure(4)
    plt.scatter(procs, speedups, label=label)
    plt.figure(5)
    plt.scatter(procs, eff, label=label)
    plt.figure(6)
    plt.scatter(procs, s, label=label)

to_save = [
    (1, "Speedup", "Metric Value", "Number of CPUs", "non_scaling_speedup.png"),
    (2, "Efficiency", "Metric Value", "Number of CPUs", "non_scaling_efficiency.png"),
    (3, "Karp-Flatt metric - serial fraction", "Metric Value", "Number of CPUs", "non_scaling_serial_fraction.png"),
    (4, "Speedup", "Metric Value", "Number of CPUs", "scaling_speedup.png"),
    (5, "Efficiency", "Metric Value", "Number of CPUs", "scaling_efficiency.png"),
    (6, "Karp-Flatt metric - serial fraction", "Metric Value", "Number of CPUs", "scaling_serial_fraction.png")
]

for figure, title, ylabel, xlabel, outfile in to_save:
    plt.figure(figure)
    plt.legend()
    plt.grid(True, linestyle=":")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.savefig("imgs/{}".format(outfile))
