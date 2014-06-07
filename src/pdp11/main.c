#define SNAP(X) __asm__("mfpi %0" : : "r" (i))
#define main  pdpmain

int main()
{
  for (int j = 3; ; j++)
    for (int i = 0; i != j; i += 1)
        SNAP(i);
}
