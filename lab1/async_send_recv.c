#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stddef.h>

#ifndef MSG_SIZE
#define MSG_SIZE 1024
#endif

#define DATA_TO_TRANSFER 1024*1024*1024 // 1GB

struct message_s {
  long timestamp;
  char data[MSG_SIZE-sizeof(long)];
};

void fill_message(struct message_s *m) {
  int fill_with = 1234567;
  memset(m->data, fill_with, MSG_SIZE-sizeof(long));
  m->data[MSG_SIZE-sizeof(long)-1] = 0;
}

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

  /* create a type for struct message_s */
  const int nitems = 3;
  MPI_Datatype mpi_message_type;

  int blocklengths[3];
  MPI_Datatype types[3];
  MPI_Aint disps[3];

  blocklengths[0] = 1;
  types[0] = MPI_LONG;
  disps[0] = offsetof(struct message_s, timestamp);

  blocklengths[1] = MSG_SIZE;
  types[1] = MPI_CHAR;
  disps[1] = offsetof(struct message_s, data);

  blocklengths[2] = 1;
  types[2] = MPI_UB;
  disps[2] = sizeof(struct message_s);

  //int MPI_Type_create_struct(int count,
  //    const int array_of_blocklengths[],
  //    const MPI_Aint array_of_displacements[],
  //    const MPI_Datatype array_of_types[],
  //    MPI_Datatype *newtype)
  MPI_Type_create_struct(nitems, blocklengths, disps, types, &mpi_message_type);
  MPI_Type_commit(&mpi_message_type);

  // compute how many transfers need to be done before 1GB is transfered
  int parts = (int)DATA_TO_TRANSFER/MSG_SIZE;

  if (world_rank == 0) {
    struct message_s send_msg;
    struct message_s recv_msg;
    MPI_Request requests[2];

    fill_message(&send_msg);

    // wait for all processes
    MPI_Barrier(MPI_COMM_WORLD);
    send_msg.timestamp = get_current_timestamp();
    for (int i = 0; i < parts; i++) {
      // int MPI_Isend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm, MPI_Request *request)
      MPI_Isend(&send_msg, 1, mpi_message_type, 1, tag, MPI_COMM_WORLD, &requests[0]);
      MPI_Irecv(&recv_msg, 1, mpi_message_type, 1, tag, MPI_COMM_WORLD, &requests[1]);
      MPI_Waitall(2, requests, MPI_STATUSES_IGNORE);
    }

  } else if (world_rank == 1) {
    struct message_s send_msg;
    struct message_s recv_msg;
    MPI_Request requests[2];

    // wait for all processes
    MPI_Barrier(MPI_COMM_WORLD);
    for (int i = 0; i < parts; i++) {
      MPI_Irecv(&recv_msg, 1, mpi_message_type, 0, tag, MPI_COMM_WORLD, &requests[0]);
      MPI_Isend(&send_msg, 1, mpi_message_type, 0, tag, MPI_COMM_WORLD, &requests[1]);
      MPI_Waitall(2, requests, MPI_STATUSES_IGNORE);
    }

    long diff = get_current_timestamp() - recv_msg.timestamp;
    printf("async,%d,%lu,%lu\n", MSG_SIZE, sizeof(struct message_s)*parts*2, diff);
  }
  MPI_Finalize();
}
