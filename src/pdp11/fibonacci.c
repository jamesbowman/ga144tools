#define PUTCHAR(X) __asm__("mfpi %0" : : "" (X))
#define main  pdpmain

int main()
{
  int i = 1, j = 1;
  for (;;) {
    PUTCHAR(i);
    int tmp = j;
    j = j + i;
    i = tmp;
  }
}
