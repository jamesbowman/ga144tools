#define SNAP(X) __asm__("mfpi %0" : : "" (X))
#define main  pdpmain

int main()
{
  for (int j = 3; ; j++) {
    SNAP(9999);
    for (int i = 0; i != j; i += 1)
        SNAP(i);
  }
}
