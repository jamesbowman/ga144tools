#include "pdp11.h"

int factorial(int x)
{
  if (x == 1)
    return 1;
  else
    return x * factorial(x - 1);
}

int main()
{
  for (int i = 1; i < 9; i++)
    emit(factorial(i));

  for (;;);
}
