import weakref
_paint_table = weakref.WeakValueDictionary()
_image_table = weakref.WeakValueDictionary()

del weakref

include "stdlib.pxi"
include "Python.pxi"
include "VG/openvg.pxi"

class VGError(BaseException):
    error_code_table = {VG_NO_ERROR:"VG_NO_ERROR",
                        VG_BAD_HANDLE_ERROR:"VG_BAD_HANDLE_ERROR",
                        VG_ILLEGAL_ARGUMENT_ERROR:"VG_ILLEGAL_ARGUMENT_ERROR",
                        VG_OUT_OF_MEMORY_ERROR:"VG_OUT_OF_MEMORY_ERROR",
                        VG_PATH_CAPABILITY_ERROR:"VG_PATH_CAPABILITY_ERROR",
                        VG_UNSUPPORTED_IMAGE_FORMAT_ERROR:"VG_UNSUPPORTED_IMAGE_FORMAT_ERROR",
                        VG_UNSUPPORTED_PATH_FORMAT_ERROR:"VG_UNSUPPORTED_PATH_FORMAT_ERROR",
                        VG_IMAGE_IN_USE_ERROR:"VG_IMAGE_IN_USE_ERROR",
                        VG_NO_CONTEXT_ERROR:"VG_NO_CONTEXT_ERROR"}
    def __init__(self, error_code, msg=None):
        if msg is not None:
            msg = "%s: %s" % (self.error_code_table[error_code], msg)
        else:
            msg = self.error_code_table[error_code]
        BaseException.__init__(self, msg)



include "path.pyx"
include "paint.pyx"
include "image.pyx"



def create_context(dimensions):
    return Context(dimensions)

def resize_context(dimensions):
    if Context.singleton is not None:
        Context.singleton.resize(dimensions)
    else:
        raise RuntimeError("Cannot resize context before creating context")

def destroy_context():
    vgDestroyContextSH()

def get_error():
    return VGError(vgGetError())

def check_error(**error_messages):
    cdef VGErrorCode error_code
    error_code = vgGetError()
    if error_code != VG_NO_ERROR:
        msg = error_messages.get(VGError.error_code_table[error_code], None)
        raise VGError(error_code, msg)

def flush():
    vgFlush()

def finish():
    vgFinish()

def clear(corner, dimensions, color=None):
    if dimensions[0] <= 0.0 or dimensions[1] <= 0.0:
        raise ValueError("width and height must be positive")
    if color is not None:
        old_color = get(VG_CLEAR_COLOR)
        set(VG_CLEAR_COLOR, color)
        vgClear(corner[0], corner[1], dimensions[0], dimensions[1])
        set(VG_CLEAR_COLOR, old_color)
    else:
        vgClear(corner[0], corner[1], dimensions[0], dimensions[1])

    check_error()

FLOAT_PARAMS = (VG_STROKE_LINE_WIDTH, VG_STROKE_MITER_LIMIT,
                VG_STROKE_DASH_PHASE)
VECTOR_PARAMS = (VG_SCISSOR_RECTS, VG_STROKE_DASH_PATTERN,
                 VG_TILE_FILL_COLOR, VG_CLEAR_COLOR)
def get(param_type):
    cdef object value
    if param_type in VECTOR_PARAMS:
        value = _getv(param_type)
    elif param_type in FLOAT_PARAMS:
        value = vgGetf(param_type)
    else:
        value = vgGeti(param_type)
    check_error(VG_ILLEGAL_ARGUMENT_ERROR="param_type %r is not a valid member of VGParamType" % param_type)
    return value

def _getv(param_type):
    cdef VGint *ivalues
    cdef VGfloat *fvalues
    cdef VGint i, count
    cdef object vals
    
    count = vgGetVectorSize(param_type)
    values = []

    if not count:
        return values
    
    if param_type == VG_SCISSOR_RECTS:
        ivalues = <VGint*>malloc(sizeof(VGint) * count)
        vgGetiv(param_type, count, ivalues)
        for i from 0 <= i < count:
            values.append(ivalues[i])
        free(<void*>ivalues)
    else:
        fvalues = <VGfloat*>malloc(sizeof(VGfloat) * count)
        vgGetfv(param_type, count, fvalues)
        for i from 0 <= i < count:
            values.append(fvalues[i])
        free(<void*>fvalues)

    return values

def set(param_type, object value):
    if param_type in VECTOR_PARAMS:
        _setv(param_type, value)
    elif param_type in FLOAT_PARAMS:
        vgSetf(param_type, value)
    else:
        vgSeti(param_type, value)
    check_error(VG_ILLEGAL_ARGUMENT_ERROR="invalid type %r or illegal value %r" % (param_type, value))

    return value

def _setv(param_type, object values):
    cdef VGint *ivalues
    cdef VGfloat *fvalues
    cdef VGint i, count
    
    count = len(values)

    if param_type == VG_SCISSOR_RECTS:
        ivalues = <VGint*>malloc(sizeof(VGint) * count)
        for i from 0 <= i < count:
            ivalues[i] = values[i]
        vgSetiv(param_type, count, ivalues)
        free(<void*>ivalues)
    else:
        fvalues = <VGfloat*>malloc(sizeof(VGfloat) * count)
        for i from 0 <= i < count:
            fvalues[i] = values[i]
        vgSetfv(param_type, count, fvalues)
        free(<void*>fvalues)
    check_error(VG_ILLEGAL_ARGUMENT_ERROR="possible invalid values passed or wrong number of values")
#The structure of matrices is:
#[M[0] M[1] M[2]]
#[M[3] M[4] M[5]]
#[M[6] M[7] M[8]]

#[m11, m12, m13, m21, m22, m23, m31, m32, m33]

def get_matrix():
    cdef VGfloat m[9]

    vgGetMatrix(m)
    check_error()
    
    return [m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8]]

def load_matrix(M):
    cdef VGfloat m[9]
    for i from 0 <= i < 9:
        m[i] = M[i]
        
    vgLoadMatrix(m)
    check_error()

def load_identity():
    vgLoadIdentity()

def mult_matrix(M):
    cdef VGfloat m[9]
    for i from 0 <= i < 9:
        m[i] = M[i]
        
    vgMultMatrix(m)
    check_error()

def translate(tx, ty):
    vgTranslate(tx, ty)

def scale(sx, sy):
    vgScale(sx, sy)

def shear(shx, shy):
    vgShear(shx, shy)

def rotate(angle):
    vgRotate(angle)

##def get_paint(mode):
##    cdef VGPaint handle
##    handle = vgGetPaint(mode)
##    check_error()
##
##    return lookup_paint(handle)

def get_paint(mode):
    #In case you're wondering/forgot why VG_STROKE_PATH | VG_FILL_PATH
    #is not an option, it's because there is no guarantee that
    #the stroke and fill paints are the same, making it impossible
    #to reliably support it.
    
    if mode == VG_STROKE_PATH:
        return Context.singleton.stroke_paint
    elif mode == VG_FILL_PATH:
        return Context.singleton.fill_paint
    else:
        raise ValueError("Either VG_STROKE_PATH or VG_FILL_PATH must be specified")


def set_paint(Paint paint, mode):
    if paint is None:
        vgSetPaint(VG_INVALID_HANDLE, mode)
    else:
        vgSetPaint(paint.handle, mode)
    check_error()
    
    if mode & VG_STROKE_PATH:
        Context.singleton.stroke_paint = paint
    if mode & VG_FILL_PATH:
        Context.singleton.fill_paint = paint

##cdef object lookup_paint(VGPaint handle):
##    cdef Paint paint
##    if (<long>handle) in _paint_table:
##        return _paint_table[<long>handle]
##    else:
##        paint_type = vgGetParameteri(handle, VG_PAINT_TYPE)
##        check_error()
##        if paint_type == VG_PAINT_TYPE_COLOR:
##            paint = Paint.__new__(ColorPaint)
##        elif paint_type == VG_PAINT_TYPE_LINEAR_GRADIENT or \
##             paint_type == VG_PAINT_TYPE_RADIAL_GRADIENT:
##            paint = Paint.__new__(GradientPaint)
##        else:
##            paint = Paint.__new__(PatternPaint)
##            paint._pattern = None
##        paint.handle = handle
##        return paint

def get_string(string_id):
    cdef char *s
    s = <char*>vgGetString(string_id)
    check_error()
    return s

class Context(object):
    def __init__(self, dimensions):
        self.dimensions = dimensions

    def resize(self, dimensions):
        vgResizeSurfaceSH(dimensions[0], dimensions[1])
        check_error()

    def __del__(self):
        if self.__class__.singleton is not None:
            destroy_context()
        self.__class__.singleton = None

    def destroy(self):
        self.__del__()
        
def __new__(cls, dimensions):
    if cls.singleton is None:
        success = vgCreateContextSH(dimensions[0], dimensions[1])
        if not success:
            raise RuntimeError("Unable to create OpenVG context")
        cls.singleton = object.__new__(cls)
        cls.singleton.stroke_paint = None
        cls.singleton.fill_paint = None
    else:
        if dimensions != cls.singleton.dimensions:
            cls.singleton.resize(dimensions)
    return cls.singleton

Context.__new__ = staticmethod(__new__)
del __new__
Context.singleton = None

Context.get_error = staticmethod(get_error)
Context.get = staticmethod(get)
Context.set = staticmethod(set)
Context.get_string = staticmethod(get_string)
Context.get_paint = staticmethod(get_paint)
Context.set_paint = staticmethod(set_paint)
Context.clear = staticmethod(clear)
Context.write_image = staticmethod(write_image)
Context.write_to_image = staticmethod(write_to_image)
Context.write_buffer = staticmethod(write_buffer)
Context.write_to_buffer = staticmethod(write_to_buffer)
Context.copy_pixels = staticmethod(copy_pixels)
Context.flush = staticmethod(flush)
Context.finish = staticmethod(finish)
Context.get_matrix = staticmethod(get_matrix)
Context.load_matrix = staticmethod(load_matrix)
Context.load_identity = staticmethod(load_identity)
Context.mult_matrix = staticmethod(mult_matrix)
Context.translate = staticmethod(translate)
Context.scale = staticmethod(scale)
Context.shear = staticmethod(shear)
Context.rotate = staticmethod(rotate)
Context.interpolate = staticmethod(interpolate)

from constants import param_table
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
            param_type = param_table[name]
            
            self.params[param_type] = value
    
    def enable(self):
        if self.stroke_paint:
            self.old_stroke_paint = get_paint(VG_STROKE_PATH)
            set_paint(self.stroke_paint, VG_STROKE_PATH)

        if self.fill_paint:
            self.old_fill_paint = get_paint(VG_FILL_PATH)
            set_paint(self.fill_paint, VG_FILL_PATH)
            
        for param_type, value in self.params.items():
            self.old_params[param_type] = get(param_type)
            set(param_type, value)

    def disable(self):
        if self.stroke_paint:
            set_paint(self.old_stroke_paint, VG_STROKE_PATH)
            self.old_stroke_paint = None
            
        if self.fill_paint:
            set_paint(self.old_fill_paint, VG_FILL_PATH)
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
        if name not in param_table.values():
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
