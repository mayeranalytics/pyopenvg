try:
    from amanithvg import *
except ImportError:
    try:
        from shivavg import *
    except:
        raise RuntimeError("Unable to locate AmanithVG or ShivaVG")

import constants

import contextlib
@contextlib.contextmanager
def push(matrix, mode=None):
    old_mode = None
    if mode is not None:
        old_mode = get(constants.VG_MATRIX_MODE)
        set(VG_MATRIX_MODE, mode)
    old_matrix = get_matrix()
    load_matrix(matrix)

    yield

    if old_mode is not None:
        set(VG_MATRIX_MODE, old_mode)
    load_matrix(old_matrix)

del contextlib


__all__ = ["Path", "Paint", "ColorPaint", "GradientPaint", "PatternPaint",
           "Image", "Context", "Style" "VGError", "check_error", "interpolate",
           "write_image", "write_buffer", "write_to_buffer", "write_to_image",
           "copy_pixels"]
