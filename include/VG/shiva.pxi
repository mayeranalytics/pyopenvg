cdef extern from "VG/openvg.h":
    VGboolean vgCreateContextSH(VGint width, VGint height)
    void vgResizeSurfaceSH(VGint width, VGint height)
    void vgDestroyContextSH()
