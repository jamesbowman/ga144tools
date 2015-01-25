/*
 * Filename:
 *
 *   sieve.c
 *
 * Description:
 *
 *   The Sieve of Eratosthenes benchmark, from Byte Magazine
 *   early 1980s, when a PC would do well to run this in 10 
 *   seconds. This version really does count prime numbers
 *   but omits the numbers 1, 3 and all even numbers. The
 *   expected count is 1899.
 *
 */

#define OUTPUT(X) __asm__("mfpi %0" : : "" (X))


#define SIZE 8190

int
sieve ()
{
  unsigned int flags [SIZE + 1];
  int iter; 
  int count;

  for (iter = 1; iter <= 10; iter++) 
    {
      int i, prime, k;

      count = 0;

      for (i = 0; i <= SIZE; i++)
        flags [i] = 1;

      for (i = 0; i <= SIZE; i++) 
        {
          if (flags [i]) 
            {
              prime = i + i + 3;
              k = i + prime;

              while (k <= SIZE)
                {
                  flags [k] = 0;
                  k += prime;
                }

              count++;
            }
        }
    }

  return count;
}

int Main ()
{
  return(sieve());
}
