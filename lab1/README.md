Content
---
This repository contains MPI benchmarks. It included two benchmarks:
 - one2one for sending 2GB data between two ranks.
   It is intended to measure throughput between ranks.
 - one2one for sending tiny message betwwen two ranks.
   It sends a lot of tiny messages between two ranks.
   Total time is divided by number of messages, which should give approximate time needed to transfer one tiny message.

Also there are two types of messaging used for each benchmark:
 - using `MPI_Isend` and `MPI_Irecv`
 - using `MPI_Send` and `MPI_Recv`

Requirements
---
It requires MPI library.
It was tested with [MPICH](https://www.mpich.org/downloads/) in `3.2.1` version.

Compiling & running
---

In order to compile files `mpicc` should be used:
```
mpicc -std=c11 async_send_recv.c -o async_send_recv
mpicc -std=c11 sync_send_recv.c -o sync_send_recv
mpicc -std=c11 async_short_msg.c -o async_short_msg 
mpicc -std=c11 sync_short_msg.c -o sync_short_msg 
```

`*_send_recv` also allows to customise message size to be used, via defining macro:
```
mpicc -DMSG_SIZE=$$((1024*1024)) -std=c11 async_send_recv.c -o async_send_recv
```

To run compiled programs with MPI, it is essential to supply machines, on which it will started:

```
nodes.txt:
    host1:4
    host1:4
```
Then it is possible to start programs:
```
mpiexec -machinefile ./nodes.txt -np 2 [program]
```
