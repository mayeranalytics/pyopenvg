cdef extern from "VG/openvg.h":
    ctypedef void* VGHandle


cdef class Path:
    cdef VGHandle handle
    cdef object __weakref__

cdef class Paint:
    cdef VGHandle handle
    cdef object __weakref__
cdef class ColorPaint(Paint)
cdef class GradientPaint(Paint)
cdef class PatternPaint(Paint):
    cdef object _pattern

cdef class Image:
    cdef VGHandle handle
    cdef object __weakref__
