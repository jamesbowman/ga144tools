#define EMIT(X) __asm__("mfpi %0" : : "" (X))
#define main  pdpmain

int main()
{
  static const int s[] = {'H', 'E', 'L', 'L', 'O', ' ', 'W', 'O', 'R', 'L', 'D'};
  for (int i = 0; i != sizeof(s)/2; i += 1)
      EMIT(s[i]);
  for (;;);
}
