#define PUTCHAR(X) __asm__("mfpi %0" : : "rm" (X))
#define emit(X) __asm__("mfpi %0" : : "rm" (X))
#define main  pdpmain
