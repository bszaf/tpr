#!/usr/bin/env python
import csv

MAX_PROCS=12

def parse_bool(string):
    if string in ['true', 'True', 't']:
        return True
    elif string in ['false', 'False', 'f']:
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

def get_measurements(*args):
    speedup = get_speedup(*args)
    eff = get_efficiency(speedup, *args)
    serial_fraction = get_serial_fraction(speedup, *args)
    return (speedup, eff, serial_fraction)

with open("data/result_raw.csv") as file:
    data_reader = csv.reader(file, delimiter=',')
    headers = data_reader.next()

    for row in data_reader:
        scaled = parse_bool(row[0])
        procs = int(row[1])
        time = float(row[3])
        if procs == 1:
            problem_size = int(row[2])
            one_proc_time = time
            filename = "data/{}".format(get_filename(scaled, problem_size))
            out_file = open(filename, 'wb')
            out_csv = csv.writer(out_file, delimiter=',')

        (speedup, eff, serial_fraction) = get_measurements(scaled, one_proc_time, time, procs)
        row = [procs, time, speedup, eff, serial_fraction]
        out_csv.writerow(row)
        if procs == MAX_PROCS:
            out_file.close()
