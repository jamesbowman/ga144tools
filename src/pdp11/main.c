#define SNAP(X) asm("mfpi %0" : : "r" (i))
#define main  pdpmain

main()
{
  int i;
  for (;;)
    for (i = 0; i != 10; i++)
        SNAP(i);
}
