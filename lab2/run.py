#!/usr/bin/env python
import subprocess
import sys

CMD_TEMPLATE="mpiexec -np {} ./get_pi.py {} {}"

cores = xrange(1,12+1)
problem_sizes = [6, 7, 8, 9]
scaled = ["true", "false"]

if len(sys.argv) < 2:
  print "Usage: {} <output_file>".format(sys.argv[0])
  exit(1)

outfile = sys.argv[1]

with open(outfile, "w", 0) as f:
  f.write(",".join(["scaled", "threads", "runs per thread", "time", "pi"]) + "\n")
  for size in problem_sizes:
    for scale in scaled:
      for core in cores:
        cmd = CMD_TEMPLATE.format(core, size, scale).split(" ")
        result = subprocess.check_output(cmd).split("\n")[1]
        f.write(result + "\n")
  f.close()
