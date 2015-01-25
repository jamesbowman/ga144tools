/*
 * Filename:
 *
 *   ackermann.c
 *
 * Description:
 *
 *   Ackermann's function "is an example of a recursive function which 
 *   is not primitive recursive". It is interesting from the point of 
 *   view of benchmarking because it "grows faster than any primitive 
 *   recursive function" and gives us a lot of nested function calls
 *   for little effort.
 * 
 *   It is defined as follows:
 *   A(0, n) = n+1 
 *   A(m, 0) = A(m-1, 1) 
 *   A(m, n) = A(m-1, A(m, n-1)) 
 *
 *   We use A(3,6) as the benchmark. This used to take long enough to 
 *   confirm the execution time with a stopwatch. Nowadays that's out
 *   of the question. BTW, the value of A(4,2) has 19729 digits!
 *
 *   A (3,6) gives us 172233 calls, with a nesting depth of 511.
 *
 * Credits:
 *
 *   Ackermann's function is named for Wilhelm Ackermann, a 
 *   mathematical logician who worked Germany during the first half
 *   if the 20th century.
 *
 */

#define OUTPUT(X) __asm__("output %0" : : "" (X))

static int 
A (int m, int n)
{
  if (m == 0)
    return n + 1;
  else if (n == 0)
    return A (m - 1, 1);
  else
    return A (m - 1, A (m, n - 1));
}

Main ()
{
  for (;;)
    OUTPUT(A (3,6));
}
