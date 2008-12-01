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

/* try typedef'd opaque structure */
typedef struct yoyo4_tag yoyo4;
typedef struct yoyo5_tag yoyo5;

/* try 'inner' structure */
struct yoyo3 {
        struct yoyo a;
        int b;
        double c;
};

struct yoyo5_tag {
        int a;
};

/* try recursive structure */
struct yoyo6 {
        struct yoyo6* head;
};

/* structures with function pointers variables */
struct yoyo7 {
        void (*init)();
        void (*destroy)(int);
};

struct yoyo9 {
        foo2_int32_t a;
};

/*
 * Union
 */
union yuyu1 {
        int a;
};

union yuyu2 {
        union yuyu1 a;
};

/*
 * Function declarations
 */
double foo(double a);
float foof(float a);
long double fool(long double a);

void mega_foo1(foo_int32_t a);
void mega_foo1_1(foo3_int32_t a);
void mega_foo2(const int a);
void mega_foo3(const int *a);

/* function pointer */
void (*foo_fptr1)();
void (*foo_fptr2)(int, int);

typedef void(*foo_func2_t)();

void mega_foo4(foo_func2_t a);
void mega_foo5(void (*a)());

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

enum {
	FOO_ENUM
};

/* structures with function pointers variables */
struct yoyo8 {
        int a;
        enum FOO1 foo;
};

void mega_enum_foo(enum FOO1);

void mega_struct_foo(struct yoyo*);
void mega_struct_foo2(struct yoyo2*);
void mega_struct_foo3(yoyo3*);
void mega_struct_foo4(yoyo4*);
void mega_struct_foo5(yoyo5*);
void mega_struct_foo6(yoyo6*);
void mega_struct_foo7(struct yoyo7*);
void mega_struct_foo8(struct yoyo8*);
void mega_struct_foo9(struct yoyo9*);

void mega_union_foo(union yuyu1*);
void mega_union_foo2(union yuyu2*);
#endif
