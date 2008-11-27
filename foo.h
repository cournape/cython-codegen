#ifndef FOO_H
#define FOO_H

/*
 * Typedefs
 */
typedef int foo_int32_t;

/* To test 'recursive' typdefs */
typedef foo_int32_t foo2_int32_t;
typedef foo2_int32_t foo3_int32_t;

/*
 * structures
 */
struct yoyo {
        int a;
        double b;
};

/* try opaque structure */
struct yoyo2;

/* try 'inner' structure */
struct yoyo3 {
        struct yoyo a;
        int b;
        double c;
};

/*
 * Function declarations
 */
double foo(double a);
float foof(float a);
long double fool(long double a);

void mega_foo1(foo_int32_t a);
void mega_foo2(const int a);
void mega_foo3(const int *a);

/* function pointer */
void (*foo_fptr1)();
void (*foo_fptr2)(int, int);

typedef void(*foo_func2_t)();

/*
 * Enum definitions
 */
enum FOO1 {
        FOO1_ENUM1,
        FOO1_ENUM2
} foo1;

enum FOO2 {
        FOO2_ENUM1 = 2,
        FOO2_ENUM2
} foo2;

void mega_struct_foo(struct yoyo*);
void mega_struct_foo2(struct yoyo2*);

#endif
