#define OUTPUT(X) __asm__("output %0" : : "" (X))

int fib(unsigned int n)
{
  int a = 0;
  int b = 1;
  while (n--){
    int tmp = b;
    b = b + a;
    a = tmp;
  } ;
  return a;
}

void Main(void)
{
  OUTPUT(fib(65535));
  OUTPUT(0x947);
}
