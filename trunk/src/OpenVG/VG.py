try:
    from amanithvg import *
except ImportError:
    try:
        from shivavg import *
    except:
        raise RuntimeError("Unable to locate AmanithVG or ShivaVG")

__all__ = ["Path", "Paint", "ColorPaint", "GradientPaint", "PatternPaint",
           "Image", "Context", "Style" "VGError", "check_error", "interpolate",
           "write_image", "write_buffer", "write_to_buffer", "write_to_image",
           "copy_pixels"]
