include "stdlib.pxi"
include "VG/vgu.pxi"
from amanithvg cimport class Path
from amanithvg import VGError
 
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

def polygon(Path path not None, points, closed=True):
    cdef VGfloat *p
    cdef VGint count

    count = len(points)
    p = <VGfloat*>malloc(sizeof(VGfloat) * count * 2)
    for i from 0 <= i < count:
        p[2*i] = points[i][0]
        p[2*i+1] = points[i][1]
    
    error_code = vguPolygon(path.handle, p, count, closed)
    free(<void*>p)

    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)
    
def rect(Path path not None, pos, dimensions):
    error_code = vguRect(path.handle, pos[0], pos[1],
                         dimensions[0], dimensions[1])
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)

def round_rect(Path path not None, pos, dimensions, arc_width, arc_height):
    error_code = vguRoundRect(path.handle, pos[0], pos[1],
                              dimensions[0], dimensions[1],
                              arc_width, arc_height)
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)

def ellipse(Path path not None, center, dimensions):
    error_code = vguEllipse(path.handle, center[0], center[1],
                            dimensions[0], dimensions[1])
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)

def arc(Path path not None, pos, dimensions, start_angle, angle_extent, arc_type):
    if arc_type not in (VGU_ARC_OPEN, VGU_ARC_CHORD, VGU_ARC_PIE):
        raise ValueError("Invalid arc type %r" % arc_type)
    error_code = vguArc(path.handle, pos[0], pos[1],
                        dimensions[0], dimensions[1],
                        start_angle, angle_extent, arc_type)
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)

def compute_warp_quad_to_square(p1, p2, p3, p4):
    #   p2 _______ p3      0,1 ______ 1,1
    #     /      /            |      |
    #    /      /     -->     |      |
    # p1/______/ p4        0,0|______|1,0
    cdef VGfloat m[9]
    error_code = vguComputeWarpQuadToSquare(p1[0], p1[1], p2[0], p2[1],
                                            p3[0], p3[1], p4[0], p4[1], m)
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)

    return [m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8]]

def compute_warp_square_to_quad(p1, p2, p3, p4):
    #0,1 ______ 1,1         p2 _______ p3
    #   |      |              /      /
    #   |      |   -->       /      /
    #0,0|______|1,0       p1/______/ p4
    cdef VGfloat m[9]
    error_code = vguComputeWarpSquareToQuad(p1[0], p1[1], p2[0], p2[1],
                                            p3[0], p3[1], p4[0], p4[1], m)
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)

    return [m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8]]

def compute_warp_quad_to_quad(quad1, quad2):
    #   p2 _______ p3      q2 _______ q3
    #     /      /            \      \
    #    /      /     -->      \      \
    # p1/______/ p4          q1 \______\ q4
    cdef VGfloat m[9]
    p1, p2, p3, p4 = quad1
    q1, q2, q3, q4 = quad2
    error_code = vguComputeWarpQuadToQuad(q1[0], q1[1], q2[0], q2[1],
                                          q3[0], q3[1], q4[0], q4[1],
                                          p1[0], p1[1], p2[0], p2[1],
                                          p3[0], p3[1], p4[0], p4[1], m)
    if error_code != VGU_NO_ERROR:
        raise VGUError(error_code)

    return [m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8]]

