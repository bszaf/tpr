all: mp

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S), Darwin)
	CC = gcc-7
endif
ifeq ($(UNAME_S), Linux)
	CC = gcc
endif

mp:
	$(CC) -std=c99 -lm -fopenmp bucket.c -o bucket

debug:
	$(CC) -std=c99 -g -lm -fopenmp -D debug bucket.c -o bucket_debug

clean:
	rm -rf bucket bucket_debug
