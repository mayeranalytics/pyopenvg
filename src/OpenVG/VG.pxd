cdef extern from "stdlib.h":
    ctypedef long size_t

cdef extern from "VG/openvg.h":
    ctypedef void* VGHandle
    ctypedef VGHandle VGPath
    ctypedef VGHandle VGPaint
    ctypedef VGHandle VGImage


cdef class Path:
    cdef VGPath handle
    cdef public object style
    cdef readonly size_t datasize
    cdef int (*datafunc)(object, int, void*) except -1
    cdef object __weakref__

cdef class Paint:
    cdef VGPaint handle
    cdef object __weakref__
cdef class ColorPaint(Paint)
cdef class GradientPaint(Paint)
cdef class PatternPaint(Paint):
    cdef object _pattern

cdef class Image:
    cdef VGImage handle
    cdef readonly int width, height
    cdef object format
    cdef object __weakref__
