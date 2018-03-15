#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stddef.h>


long get_current_timestamp() {
  struct timespec ts;
  timespec_get(&ts, TIME_UTC);
  return (long)ts.tv_sec * 1000000000L + ts.tv_nsec;
}

int main(int argc, char** argv) {

  MPI_Init(NULL, NULL);

  // tag for message
  const int tag = 44;

  int world_rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
  int world_size;
  MPI_Comm_size(MPI_COMM_WORLD, &world_size);

  if (world_size < 2) {
    fprintf(stderr, "World size must be greater than 1 for %s\n", argv[0]);
    MPI_Abort(MPI_COMM_WORLD, 1);
  }

  int number_of_transfers = 10000;
  if (world_rank == 0) {
    long send_msg;
    long recv_msg;

    MPI_Barrier(MPI_COMM_WORLD);
    send_msg = get_current_timestamp();
    // int MPI_Send(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
    for(int i = 0; i < number_of_transfers; i++) {
      MPI_Send(&send_msg, 1, MPI_LONG, 1, tag, MPI_COMM_WORLD);
      MPI_Recv(&recv_msg, 1, MPI_LONG, 1, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    }
  } else if (world_rank == 1) {
    long send_msg = -1;
    long recv_msg;

    MPI_Barrier(MPI_COMM_WORLD);

    for(int i = 0; i < number_of_transfers; i++) {
      MPI_Recv(&recv_msg, 1, MPI_LONG, 0, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
      MPI_Send(&send_msg, 1, MPI_LONG, 0, tag, MPI_COMM_WORLD);
    }
    long diff = get_current_timestamp() - recv_msg;
    printf("Transfered msgs: %d\n Total time nanoseconds:  %lu\n avg time: %lu\n", number_of_transfers*2, diff, diff/(number_of_transfers*2));
  }
  MPI_Finalize();
}
