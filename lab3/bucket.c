#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>
#include <pthread.h>

#define MAX_VALUE 10000000

#ifdef debug
    #define DO_IF_DEBUG(...) __VA_ARGS__
    #define DEBUG(...) fprintf(stderr, __VA_ARGS__)
#else
    #define DO_IF_DEBUG(...)
    #define DEBUG(...)
#endif

int num_threads;

void fill_table(int *table, int size) {
    unsigned int a = -1;
    #pragma omp parallel for
    for (int i = 0; i < size; i++) {
        table[i] = ((int) rand_r(&a)) % MAX_VALUE;
    }
}

void print_table(int *table, int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", table[i]);
    }
}

void prepare_buckets(int *table, int size, int max_value, int *occurences, int *starts, int buckets_no) {
    // calculate how many elements should be assigned by each thread
    int range = size / num_threads;

    #pragma omp parallel for //reduction(+:occurences[:buckets_no])
    for (int i = 0; i < num_threads; i++) {
        // calculate the pointer to place where each thread should start
        int *start = table + (i*range);
        int work_size = range - 1;
        if (i+1 == num_threads)
            work_size = size - (range * i) - 1; // special case - last element may be not in range
        DEBUG("[assigning_to_bucket] Thread num: %d, start: %d, end: %d "
                "my first elem: %d, my last elem: %d \n",
                omp_get_thread_num(),
                (i*range),
                (i*range)+work_size,
                start[0],
                start[work_size]);
        for(int j = 0; j <= work_size; j++) {
            // calculate bucket numer
            int bucket_no = floor(start[j] / (float) max_value * buckets_no);
            // if value == max_value bucket number may over flow
            if (bucket_no == buckets_no) bucket_no--; // do not go above buckets_no
            #pragma omp atomic
            occurences[bucket_no]++; // count how many elements there is in each bucket
        }

    }
    // calculate where is start place for each bucket
    starts[0] = 0;
    for(int i = 1; i < buckets_no; i++) {
        starts[i] = occurences[i-1] + starts[i-1];
    }

    DO_IF_DEBUG(
            for(int i = 0; i < buckets_no; i++)
                printf("bucket %d: start: %d items: %d \n", i, occurences[i], starts[i]);
            )
};


void put_to_buckets(int *from, int *to, int table_size, int *starts, int buckets_no, int max_value) {
    // make copy of it. It should not be modified
    int *starts_copy = malloc(sizeof(int) * buckets_no);
    memcpy(starts_copy, starts, sizeof(int) * buckets_no);

    // Each threads gets assigned buckets if bucket_number % num_threads = thread_num
    // All of therds goes through table, but each bucket has assigned
    // only one thread, so there is no need of synchronization.
    #pragma omp parallel for //reduction(+:occurences[:buckets_no])
    for (int i = 0; i < num_threads; i++) {
        // calculate the pointer to place where each thread should start
        for(int j = 0; j < table_size; j++) {
            // calculate bucket numer
            int bucket_no = floor(from[j] / (float) max_value * buckets_no);
            // if value == max_value bucket number may over flow
            if (bucket_no % num_threads == i) {
                int target_position = starts_copy[bucket_no]++;
                to[target_position] = from[j];
            }
        }
    }
    free(starts_copy);
}

int compare_function(const void *a, const void *b) {
    int *x = (int *) a;
    int *y = (int *) b;
    return *x - *y;
}

void sort_buckets(int *table, int *starts, int *occurences, int buckets_no) {
    #pragma omp parallel for
    for (int i = 0; i < buckets_no; i++) {
        qsort(table + starts[i], occurences[i], sizeof(int), compare_function);
    }
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: %s <num_threads> <table_size> <buckets>\n", argv[0]);
        return 1;
    }
    num_threads = atoi(argv[1]);
    int table_size = atoi(argv[2]);
    int buckets_no = atoi(argv[3]);
    omp_set_num_threads(num_threads);
    int max_value = MAX_VALUE;
    double start_time;
    double end_time;

    DEBUG("Table size: %d \n buckets: %d \n max_value: %d \n threads: %d \n",
            table_size,
            buckets_no,
            max_value,
            omp_get_thread_num());
    DEBUG("Filling table\n");

    int *source_table = malloc(sizeof(int) * table_size);
    int *target_table = malloc(sizeof(int) * table_size);
    fill_table(source_table, table_size);

    DO_IF_DEBUG(printf("Initial table: ");
          print_table(source_table, table_size);
          printf("\n");)

    start_time = omp_get_wtime();

    int *occurences = calloc(sizeof(int), buckets_no);
    int *starts = malloc(sizeof(int) * buckets_no);

    DEBUG("Assigning to buckets\n");
    prepare_buckets(source_table, table_size, max_value, occurences, starts, buckets_no);
    put_to_buckets(source_table, target_table, table_size, starts, buckets_no, max_value);
    DEBUG("Sorting each bucket\n");
    sort_buckets(target_table, starts, occurences, buckets_no);

    free(occurences);
    free(starts);

    end_time = omp_get_wtime();
    DO_IF_DEBUG(print_table(target_table, table_size));
    printf("Work took %f sec. time.\n", end_time-start_time);

    return 0;
}
