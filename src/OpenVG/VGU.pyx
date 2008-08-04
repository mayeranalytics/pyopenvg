include "VG/vgu.pxi"
from VG cimport class Path
from VG import VGError
 
class VGUError(VGError):
    error_code_table = {VGU_NO_ERROR:"VGU_NO_ERROR",
                        VGU_BAD_HANDLE_ERROR:"VGU_BAD_HANDLE_ERROR",
                        VGU_ILLEGAL_ARGUMENT_ERROR:"VGU_ILLEGAL_ARGUMENT_ERROR",
                        VGU_OUT_OF_MEMORY_ERROR:"VGU_OUT_OF_MEMORY_ERROR",
                        VGU_PATH_CAPABILITY_ERROR:"VGU_PATH_CAPABILITY_ERROR",
                        VGU_BAD_WARP_ERROR:"VGU_BAD_WARP_ERROR"}


#VGU functions
def line(Path path not None, p1, p2):
    error_code = vguLine(path.handle, p1[0], p1[1], p2[0], p2[1])
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)

def rect(Path path not None, corner, dimensions):
    error_code = vguRect(path.handle, corner[0], corner[1],
                         dimensions[0], dimensions[1])
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)

def round_rect(Path path not None, corner, dimensions, arc_width, arc_height):
    error_code = vguRoundRect(path.handle, corner[0], corner[1],
                              dimensions[0], dimensions[1],
                              arc_width, arc_height)
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)

def ellipse(Path path not None, center, dimensions):
    error_code = vguEllipse(path.handle, center[0], center[1],
                            dimensions[0], dimensions[1])
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)

def arc(Path path not None, corner, dimensions, start_angle, angle_extent, arc_type):
    if arc_type not in (VGU_ARC_OPEN, VGU_ARC_CHORD, VGU_ARC_PIE):
        raise ValueError("Invalid arc type %r" % arc_type)
    error_code = vguArc(path.handle, corner[0], corner[1],
                        dimensions[0], dimensions[1],
                        start_angle, angle_extent, arc_type)
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)


__all__ = ["VGUError", "line", "rect", "round_rect", "ellipse", "arc"]
