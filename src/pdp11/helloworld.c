#define PUTCHAR(X) __asm__("mfpi %0" : : "rm" (X))
#define main  pdpmain

int main()
{
  static const int s[] = {'H', 'E', 'L', 'L', 'O', ' ', 'W', 'O', 'R', 'L', 'D'};
  for (int i = 0; i != 11; i += 1)
      PUTCHAR(s[i]);
  for (;;);
}
