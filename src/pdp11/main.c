#define EMIT(X) __asm__("mfpi %0" : : "" (X))
#define main  pdpmain

extern void tellme()
{
  EMIT(9090);
  EMIT(9090);
  EMIT(9090);
  EMIT(9090);
}

int main()
{
  for (int j = 1; ; j++) {
    for (int i = 0; i != j; i += 1)
        EMIT(i);
    tellme();
  }
}
