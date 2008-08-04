cdef extern from "stdlib.h":
    ctypedef long size_t
    void* malloc(size_t size)
    void* calloc(size_t nobj, size_t size)
    void* realloc(void* p, size_t size)
    void free(void* p)

    void srand(unsigned int seed)
    int rand()

    int abs(int n)
    long labs(long n)