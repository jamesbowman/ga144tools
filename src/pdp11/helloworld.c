#include "pdp11.h"

int main()
{
  static const int s[] = {
    'H', 'E', 'L', 'L', 'O', ' ', 'W', 'O', 'R', 'L', 'D', '!'
  };

  for (int i = 0; i != 12; i++)
      PUTCHAR(s[i]);

  for (;;);
}
