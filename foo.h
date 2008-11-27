#ifndef FOO_H
#define FOO_H

typedef int foo_int32_t;

double foo(double a);
float foof(float a);
long double fool(long double a);

void mega_foo1(foo_int32_t a);
void mega_foo2(const int a);
void mega_foo3(const int *a);

enum FOO1 {
        FOO1_ENUM1,
        FOO1_ENUM2
} foo1;

enum FOO2 {
        FOO2_ENUM1 = 2,
        FOO2_ENUM2
} foo2;

/* try full structure (public members) */
struct yoyo {
        int a;
        double b;
};

/* try opaque structure */
struct yoyo2;

void mega_struct_foo(struct yoyo*);
void mega_struct_foo2(struct yoyo2*);

#endif
