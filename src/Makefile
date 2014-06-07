CC=pdp11-aout-gcc
CFLAGS=-Os -fomit-frame-pointer
AS=pdp11-aout-as
LD=pdp11-aout-ld

all: main.o binary
	pdp11-aout-objdump -d main.o

binary: a.out Makefile
	pdp11-aout-ld --oformat binary -o binary a.out

a.out: crt0.o Makefile
	$(LD) -o a.out crt0.o

main.o: main.c Makefile

crt0.o: crt0.s
