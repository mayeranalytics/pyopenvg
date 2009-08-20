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

