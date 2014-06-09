CC=pdp11-aout-gcc
CFLAGS=-Os -fomit-frame-pointer -std=c99
AS=pdp11-aout-as
LD=pdp11-aout-ld

all: crt0.o triangle.bin benchmark.bin smoke.bin helloworld.bin

%.bin: %.o
	$(LD) -o a.out crt0.o $^
	$(LD) --oformat binary -o $@ a.out

crt0.o: crt0.s
