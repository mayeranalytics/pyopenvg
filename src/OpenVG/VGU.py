try:
    from amanithvgu import *
except ImportError:
    try:
        from shivavgu import *
    except:
        raise RuntimeError("Unable to locate AmanithVG or ShivaVG")

__all__ = ["VGUError", "line", "rect", "round_rect", "ellipse", "arc",
           "polygon",
           "compute_warp_quad_to_square", "compute_warp_square_to_quad",
           "compute_warp_quad_to_quad"]
