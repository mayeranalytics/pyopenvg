cdef extern from "VG/openvg.h":
    VGboolean vgInitContextAM(VGint surfaceWidth,
                              VGint surfaceHeight,
                              VGboolean surfaceLinearColorSpace)
    void vgDestroyContextAM()

    void vgResizeSurfaceAM(VGint surfaceWidth, VGint surfaceHeight)
    VGint vgGetSurfaceWidthAM()
    VGint vgGetSurfaceHeightAM()
    VGImageFormat vgGetSurfaceFormatAM()
    VGubyte* vgGetSurfacePixelsAM() 
