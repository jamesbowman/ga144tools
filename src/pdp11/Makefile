CC=pdp11-aout-gcc
CFLAGS=-Os -fomit-frame-pointer -std=c99
AS=pdp11-aout-as
LD=pdp11-aout-ld

all: crt0.o triangle.bin benchmark.bin

%.bin: %.o
	$(LD) --oformat binary -o $@ crt0.o $^

main.o: main.c Makefile

crt0.o: crt0.s
