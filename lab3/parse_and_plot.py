#!/usr/bin/env python
import csv
from collections import defaultdict
import matplotlib.pyplot as plt


result_dict = defaultdict(lambda: defaultdict(lambda : defaultdict(dict)))
available_threads = set()
available_sizes = set()
available_buckets = set()

def parse_scaled(string):
    if string == 'scaled':
        return True
    elif string == 'unscaled':
        return False
    else:
        raise "error"

def get_filename(scaled, problem_size):
    if scaled:
        return "scaling_{}.csv".format(problem_size)
    else:
        return "non_scaling_{}.csv".format(problem_size)

def get_speedup(scaled, one_cpu_time, n_proc_time, n_proc):
    if scaled:
        return one_cpu_time/n_proc_time*n_proc
    else:
        return one_cpu_time/n_proc_time

def get_efficiency(speedup, scaled, one_cpu_time, n_proc_time, n_proc):
    return speedup/float(n_proc)

def get_serial_fraction(speedup, scaled, one_cpu_time, n_proc_time, n_proc):
    if n_proc != 1:
        a = 1/speedup-1/float(n_proc)
        b = 1-1/float(n_proc)
        return a/b
    else:
        return 1.0

def calc_measurements(*args):
    speedup = get_speedup(*args)
    eff = get_efficiency(speedup, *args)
    serial_fraction = get_serial_fraction(speedup, *args)
    return (speedup, eff, serial_fraction)

def get_results_by_threads(scaled, buckets, size):
        for thread in available_threads:
            yield result_dict[scaled][thread][size][buckets]

def get_results_by_buckets(scaled, thread, size):
        for buckets in available_buckets:
            yield result_dict[scaled][thread][size][buckets]

###
## Read part
###

with open("data/result.csv") as file:
    data_reader = csv.reader(file, delimiter=',')
    headers = data_reader.next()

    for row in data_reader:
        scaled = parse_scaled(row[0])
        threads = int(row[1])
        problem_size = int(row[2])
        buckets = int(row[3])
        time = float(row[4])
        if threads == 1:
            one_proc_problem_size = problem_size
            one_proc_time = time
        else:
            (one_proc_time, _, _, _) = result_dict[scaled][1][one_proc_problem_size][buckets]
        available_threads.add(threads)
        available_sizes.add(one_proc_problem_size)
        available_buckets.add(buckets)
        (speedup, eff, serial_fraction) = calc_measurements(scaled, one_proc_time, time, threads)
        result = (time, speedup, eff, serial_fraction)
        result_dict[scaled][threads][one_proc_problem_size][buckets] = result
###
## plot part
###
procs = sorted(list(available_threads))
figure = 1
for size in available_sizes:
    for scaled in [True, False]:
        for bucket in sorted(list(available_buckets)):
            [times, speedups, effs, serial_fr] =  zip(*get_results_by_threads(scaled, bucket, size))
            plt.figure(figure)
            label = "bucket_size = {:,}".format(size/bucket)
            plt.scatter(procs, times, label=label)
            plt.figure(figure+1)
            plt.scatter(procs, speedups, label=label)
            plt.figure(figure+2)
            plt.scatter(procs, effs, label=label)
            plt.figure(figure+3)
            plt.scatter(procs, serial_fr, label=label)
        scaled_str = "Scaled" if scaled else "Not scaled"
        figures = [
            {
                "id"       : figure,
                "title"    : "Time\n {}, Size = {:,}".format(scaled_str, size),
                "ylabel"   : "Metric Value",
                "xlabel"   : "Number of CPUs",
                "filename" : "size_{}_scaled_{}_time.png".format(size, scaled)
             },
            {
                "id"       : figure+1,
                "title"    : "Speedup\n {}, Size = {:,}".format(scaled_str, size),
                "ylabel"   : "Metric Value",
                "xlabel"   : "Number of CPUs",
                "filename" : "size_{}_scaled_{}_speedup.png".format(size, scaled)
            },
            {
                "id"       : figure+2,
                "title"    : "Efficiency\n {}, Size = {:,}".format(scaled_str, size),
                "ylabel"   : "Metric Value",
                "xlabel"   : "Number of CPUs",
                "filename" : "size_{}_scaled_{}_efficiency.png".format(size, scaled)
            },
            {
                "id"       : figure+3,
                "title"    : "Karp-Flatt metric - serial fraction\n {}, Size = {:,}".format(scaled_str, size),
                "ylabel"   : "Metric Value",
                "xlabel"   : "Number of CPUs",
                "filename" : "size_{}_scaled_{}_serial_fraction.png".format(size, scaled)
            }
        ]
        for current_figure in figures:
            plt.figure(current_figure['id'])
            plt.legend()
            plt.grid(True, linestyle=":")
            plt.title(current_figure['title'])
            plt.ylabel(current_figure['ylabel'])
            plt.xlabel(current_figure['xlabel'])
            plt.savefig("imgs/{}".format(current_figure['filename']))
            plt.close(current_figure['id'])

        figure = figure + 4
