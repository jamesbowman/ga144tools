extern void out(int);

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

int Main(void)
{
  return fib(65535);
}
