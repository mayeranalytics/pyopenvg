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
        set(constants.VG_MATRIX_MODE, mode)
    old_matrix = get_matrix()
    load_matrix(matrix)

    yield

    if old_mode is not None:
        set(constants.VG_MATRIX_MODE, old_mode)
    load_matrix(old_matrix)

del contextlib

class Style(object):
    def __init__(self, stroke_paint=None, fill_paint=None, **params):
        self.params = {}
        self.old_params = {}

        self.stroke_paint = None
        self.fill_paint = None
        
        self.old_stroke_paint = None
        self.old_fill_paint = None

        self.stroke_paint = stroke_paint 
        self.fill_paint = fill_paint
        
        for name, value in params.items():
            param_type = constants.param_table[name]
            
            self.params[param_type] = value
    
    def enable(self):
        if self.stroke_paint:
            self.old_stroke_paint = get_paint(constants.VG_STROKE_PATH)
            set_paint(self.stroke_paint, constants.VG_STROKE_PATH)

            if self.stroke_paint.transform:
                old_mode = get(constants.VG_MATRIX_MODE)
                set(constants.VG_MATRIX_MODE, constants.VG_MATRIX_STROKE_PAINT_TO_USER)
                load_matrix(self.stroke_paint.transform)
                set(constants.VG_MATRIX_MODE, old_mode)

        if self.fill_paint:
            self.old_fill_paint = get_paint(constants.VG_FILL_PATH)
            set_paint(self.fill_paint, constants.VG_FILL_PATH)
            
            if self.fill_paint.transform:
                old_mode = get(constants.VG_MATRIX_MODE)
                set(constants.VG_MATRIX_MODE, constants.VG_MATRIX_FILL_PAINT_TO_USER)
                load_matrix(self.fill_paint.transform)
                set(constants.VG_MATRIX_MODE, old_mode)
            
        for param_type, value in self.params.items():
            self.old_params[param_type] = get(param_type)
            set(param_type, value)

    def disable(self):
        if self.stroke_paint:
            if (self.old_stroke_paint and self.old_stroke_paint.transform) or \
               self.stroke_paint.transform:
                old_mode = get(constants.VG_MATRIX_MODE)
                set(constants.VG_MATRIX_MODE,constants.VG_MATRIX_STROKE_PAINT_TO_USER)
                if self.old_stroke_paint and self.old_stroke_paint.transform:
                    load_matrix(self.old_stroke_paint.transform)
                else:
                    load_identity()
                set(constants.VG_MATRIX_MODE, old_mode)
            
            set_paint(self.old_stroke_paint, constants.VG_STROKE_PATH)
            self.old_stroke_paint = None
            
        if self.fill_paint:
            if (self.old_fill_paint and self.old_fill_paint.transform) or \
               self.fill_paint.transform:
                old_mode = get(constants.VG_MATRIX_MODE)
                set(constants.VG_MATRIX_MODE, constants.VG_MATRIX_FILL_PAINT_TO_USER)
                if self.old_fill_paint and self.old_fill_paint.transform:
                    load_matrix(self.old_fill_paint.transform)
                else:
                    load_identity()
                set(constants.VG_MATRIX_MODE, old_mode)
            
            set_paint(self.old_fill_paint, constants.VG_FILL_PATH)
            self.old_fill_paint = None
        
        for param_type, val in self.old_params.items():
            set(param_type, val)
        self.old_params.clear()

    def __enter__(self):
        self.enable()
        
    def __exit__(self, exc_type, value, traceback):
        self.disable()

    def __contains__(self, key):
        return key in self.params

    def __getitem__(self, name):
        return self.params[name]

    def __setitem__(self, name, value):
        if name not in constants.param_table.values():
            raise KeyError("Invalid parameter type %r" % name)
        self.params[name] = value

    def __delitem__(self, name):
        del self.params[name]

    def __iter__(self):
        return iter(self.params)

    def __add__(self, other):       
        style = object.__new__(Style)

        style.stroke_paint = None
        if self.stroke_paint:
            style.stroke_paint = self.stroke_paint
        if other.stroke_paint:
            style.stroke_paint = other.stroke_paint

        style.fill_paint = None
        if self.fill_paint:
            style.fill_paint = self.fill_paint
        if other.fill_paint:
            style.fill_paint = other.fill_paint

        style.old_stroke_paint = None
        style.old_fill_paint = None
        
        style.params = self.params.copy()
        style.params.update(other.params)
        style.old_params = {}

        return style


__all__ = ["Path", "Paint", "ColorPaint", "GradientPaint", "PatternPaint",
           "Image", "Context", "Style" "VGError", "check_error", "interpolate",
           "write_image", "write_buffer", "write_to_buffer", "write_to_image",
           "copy_pixels"]
