cdef extern from "Python.h":
    ctypedef int Py_intptr_t

    void Py_INCREF(object)
    void Py_XINCREF(object)

    void Py_DECREF(object)
    void Py_XDECREF(object)

    void Py_CLEAR(object)
    

    void* PyMem_Malloc(size_t n)
    void* PyMem_Realloc(void *p, size_t n)
    void PyMem_Free(void *p)
    
    int PyCObject_Check(object p)
    void* PyCObject_AsVoidPtr(object self)
    void* PyCObject_GetDesc(object self)
    object PyCObject_FromVoidPtrAndDesc(void* cobj, void* desc, void (*destr)(void *, void *))

    int PyString_Check(object o)
    char* PyString_AS_STRING(object s)
    char* PyString_AsString(object s) except NULL

    int PyBuffer_Check(object obj)
    int PyObject_AsReadBuffer(object obj, void **buffer, Py_ssize_t *buffer_len) except - 1
    int PyObject_AsWriteBuffer(object obj, void **buffer, Py_ssize_t *buffer_len) except -1

    object PyErr_Occurred()
    void PyErr_Print()
    void PyErr_Clear()
