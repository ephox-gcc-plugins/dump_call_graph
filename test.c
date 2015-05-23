#define __noinline __attribute__ ((noinline))

extern int fn_5(int argc);

static int __noinline fn_2(int argc)
{
	return argc * 10;
}

static int __noinline fn_3(int argc)
{
	return argc + 4;
}

static int __noinline fn_4(int argc)
{
	int a = fn_5(argc);

	return a % 2;
}

static int __noinline fn_1(int argc)
{
	int a, b, c;

	a = fn_2(argc);
	b = fn_3(argc);
	c = fn_4(argc);
	return a + b + c;
}

int main(int argc, char *argv[])
{
	return fn_1(argc);
}
