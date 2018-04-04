#!/usr/bin/env python

from mpi4py import MPI
import random
import sys

points_in_circle = 0
comm = MPI.COMM_WORLD

random.seed()
rank = comm.Get_rank()
size = comm.Get_size()

def in_circle((x, y)):
    return x*x + y*y < 1

def get_rand():
    return (random.uniform(0,1), random.uniform(0,1))

time1 = 0

if len(sys.argv) < 2:
    exit(1)

RUNS = pow(10,int(sys.argv[1]))
SCALED = sys.argv[2]

if SCALED == "false":
    RUNS=RUNS/size
elif SCALED == "true":
    pass
else:
    exit(1)

comm.Barrier()

if rank == 0:
    time1 = MPI.Wtime()


for i in xrange(1, RUNS):
    if in_circle(get_rand()):
        points_in_circle+=1


data = comm.reduce(points_in_circle, root=0)

if rank == 0:
    pi = 4*data/float(size*RUNS)
    time = MPI.Wtime() - time1
    print ",".join(["scaled", "threads", "runs per thread", "time", "pi"])
    print ",".join(map(str, [SCALED, size, RUNS, time, pi]))

MPI.Finalize()
