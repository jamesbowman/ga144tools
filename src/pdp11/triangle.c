#define PUTCHAR(X) __asm__("mfpi %0" : : "" (X))
#define main  pdpmain

int main()
{
  for (int j = 1; ; j++) {
    for (int i = 0; i != j; i += 1)
        PUTCHAR(i);
    PUTCHAR(9999);
  }
}
