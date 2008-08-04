import weakref
_paint_table = weakref.WeakValueDictionary()
_image_table = weakref.WeakValueDictionary()

del weakref

include "stdlib.pxi"
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
    
cdef class Path:
    def __init__(self, format=0, datatype=VG_PATH_DATATYPE_F,
                 scale=1.0, bias=0, segment_hint=0,
                 coord_hint=0, capabilities=VG_PATH_CAPABILITY_ALL):
        if scale == 0.0:
            raise ValueError("scale cannot be 0")
        self.handle = vgCreatePath(format, datatype, scale, bias, segment_hint, coord_hint, capabilities)
        if self.handle == NULL:
            raise VGError(VG_BAD_HANDLE_ERROR, "unable to create path")

        check_error(VG_ILLEGAL_ARGUMENT_ERROR="datatype %r is not a valid path datatype" % datatype,
                    VG_UNSUPPORTED_PATH_FORMAT_ERROR="format %r is unsupported" % format)
    
    def __dealloc__(self):
        vgDestroyPath(self.handle)

    def clear(self, capabilities=VG_PATH_CAPABILITY_ALL):
        vgClearPath(self.handle, capabilities)

    def append(self, segment):
        cdef VGubyte pathSegment
        cdef void *pathData
        pathSegment = segment[0]
        n = len(segment[1])
        
        if self.datatype == VG_PATH_DATATYPE_F:
            pathData = malloc(sizeof(VGfloat) * n)
            for i from 0 <= i < n:
                (<VGfloat*>pathData)[i] = segment[1][i]
        elif self.datatype == VG_PATH_DATATYPE_S_8:
            pathData = malloc(sizeof(VGbyte) * n)
            for i from 0 <= i < n:
                (<VGbyte*>pathData)[i] = segment[1][i]
        elif self.datatype == VG_PATH_DATATYPE_S_16:
            pathData = malloc(sizeof(VGshort) * n)
            for i from 0 <= i < n:
                (<VGshort*>pathData)[i] = segment[1][i]
        elif self.datatype == VG_PATH_DATATYPE_S_32:
            pathData = malloc(sizeof(VGint) * n)
            for i from 0 <= i < n:
                (<VGint*>pathData)[i] = segment[1][i]
        else:
            raise NotImplementedError
        vgAppendPathData(self.handle, 1, &pathSegment, pathData)
        free(pathData)
        check_error()

    def extend(self, segments):
        cdef VGint num_segments
        cdef VGubyte *pathSegments
        cdef void *pathData
        pathSegments = NULL
        pathData = NULL
        
        if isinstance(segments, Path):
            vgAppendPath(self.handle, <VGPath>segments)
            check_error(VG_BAD_HANDLE_ERROR="one of the paths is invalid or from a different context",
                        VG_PATH_CAPABILITY_ERROR="either VG_PATH_CAPABILITY_APPEND_FROM or APPEND_TO is disabled")
        else:
            if self.datatype == VG_PATH_DATATYPE_F:
                num_segments = segment_py_to_float(segments, &pathSegments, &pathData)
            elif self.datatype == VG_PATH_DATATYPE_S_8:
                num_segments = segment_py_to_byte(segments, &pathSegments, &pathData)
            elif self.datatype == VG_PATH_DATATYPE_S_16:
                num_segments = segment_py_to_short(segments, &pathSegments, &pathData)
            elif self.datatype == VG_PATH_DATATYPE_S_32:
                num_segments = segment_py_to_int(segments, &pathSegments, &pathData)
            else:
                raise RuntimeError
            vgAppendPathData(self.handle, num_segments, pathSegments, pathData)
            free(<void*>pathSegments)
            free(pathData)
            check_error(VG_ILLEGAL_ARGUMENT_ERROR="no segments or invalid command")
            
    def bounds(self):
        cdef VGfloat minX, minY, width, height
        vgPathBounds(self.handle, &minX, &minY, &width, &height)
        check_error()
        return (minX, minY, width, height)

    def transformed_bounds(self):
        cdef VGfloat minX, minY, width, height
        vgPathTransformedBounds(self.handle, &minX, &minY, &width, &height)
        check_error()
        return (minX, minY, width, height)

    def draw(self, paint_modes):
        vgDrawPath(self.handle, paint_modes)
        check_error()

    def close(self):
        self.append((VG_CLOSE_PATH, ()))

    def move_to(self, p, rel=True):
        self.append((VG_MOVE_TO | rel, p))

    def line_to(self, p, rel=True):
        self.append((VG_LINE_TO | rel, p))

    def hline_to(self, x, rel=True):
        self.append((VG_HLINE_TO | rel, x))

    def vline_to(self, y, rel=True):
        self.append((VG_VLINE_TO | rel, y))

    def quad_to(self, p1, p2, rel=True):
        data = (p1[0],p1[1], p2[0],p2[1])
        self.append((VG_QUAD_TO | rel, data))

    def squad_to(self, p2, rel=True):
        self.append((VG_SQUAD_TO | rel, p2))

    def cubic_to(self, p1, p2, p3, rel=True):
        data = (p1[0],p1[1], p2[0],p2[1], p3[0],p3[1])
        self.append((VG_CUBIC_TO | rel, data))

    def scubic_to(self, p2, p3, rel=True):
        data = (p2[0],p2[1], p3[0],p3[1])
        self.append((VG_SCUBIC_TO | rel, data))

    def arc_from(self, p1, rh, rv, rot, major=True, CCW=False, rel=True):
        data = (rh,rv,rot,p1[0],p1[1])
        if major and CCW:
            command = VG_LCCWARC_TO
        elif major and not CCW:
            command = VG_LCWARC_TO
        elif not major and CCW:
            command = VG_SCCWARC_TO
        else:
            command = VG_SCWARC_TO
        self.append((command | rel, data))

    property format:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_PATH_FORMAT)

    property datatype:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_PATH_DATATYPE)

    property scale:
        def __get__(self):
            return vgGetParameterf(self.handle, VG_PATH_SCALE)

    property bias:
        def __get__(self):
            return vgGetParameterf(self.handle, VG_PATH_BIAS)

    property num_segments:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_PATH_NUM_SEGMENTS)

    property num_coords:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_PATH_NUM_COORDS)

    property capabilities:
        def __get__(self):
            return vgGetPathCapabilities(self.handle)

cdef int segment_py_to_byte(object segments, VGubyte **p_pathSegments, void **p_pathData) except -1:
    N = len(segments)
    p_pathData[0] = malloc(sizeof(VGbyte) * 6 * N)
    p_pathSegments[0] = <VGubyte*>malloc(sizeof(VGubyte) * N)
    
    j = 0
    for i, (command, data) in enumerate(segments):
        p_pathSegments[0][i] = command
        for coord in data:
            (<VGbyte*>p_pathData[0])[j] = coord
            j += 1
    return N

cdef int segment_py_to_short(object segments, VGubyte **p_pathSegments, void **p_pathData) except -1:
    N = len(segments)
    p_pathData[0] = malloc(sizeof(VGshort) * 6 * N)
    p_pathSegments[0] = <VGubyte*>malloc(sizeof(VGubyte) * N)
    
    j = 0
    for i, (command, data) in enumerate(segments):
        p_pathSegments[0][i] = command
        for coord in data:
            (<VGshort*>p_pathData[0])[j] = coord
            j += 1
    return N

cdef int segment_py_to_int(object segments, VGubyte **p_pathSegments, void **p_pathData) except -1:
    N = len(segments)
    p_pathData[0] = malloc(sizeof(VGint) * 6 * N)
    p_pathSegments[0] = <VGubyte*>malloc(sizeof(VGubyte) * N)
    
    j = 0
    for i, (command, data) in enumerate(segments):
        p_pathSegments[0][i] = command
        for coord in data:
            (<VGint*>p_pathData[0])[j] = coord
            j += 1
    return N

cdef int segment_py_to_float(object segments, VGubyte **p_pathSegments, void **p_pathData) except -1:
    N = len(segments)
    p_pathData[0] = malloc(sizeof(VGfloat) * 6 * N)
    p_pathSegments[0] = <VGubyte*>malloc(sizeof(VGubyte) * N)
    
    j = 0
    for i, (command, data) in enumerate(segments):
        p_pathSegments[0][i] = command
        for coord in data:
            (<VGfloat*>p_pathData[0])[j] = coord
            j += 1
    return N

cdef class Paint:
    def __init__(self, paint_type):
        self.handle = vgCreatePaint()
        if self.handle == NULL:
            raise VGError(VG_BAD_HANDLE_ERROR, "unable to create paint")
        vgSetParameteri(self.handle, VG_PAINT_TYPE, paint_type)
        check_error()
        _paint_table[<long>self.handle] = self
        
    def __dealloc__(self):
        vgDestroyPaint(self.handle)

    property type:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_PAINT_TYPE)
        def __set__(self, value):
            vgSetParameteri(self.handle, VG_PAINT_TYPE, value)
            check_error()


cdef class ColorPaint(Paint):
    def __init__(self, color):
        Paint.__init__(self, VG_PAINT_TYPE_COLOR)
        self.color = color

    property color:
        def __get__(self):
            cdef VGfloat color[4]
            vgGetParameterfv(self.handle, VG_PAINT_COLOR, 4, color)
            check_error()
            return (color[0], color[1], color[2], color[3])
        def __set__(self, value):
            cdef VGfloat color[4]
            color[0] = value[0]
            color[1] = value[1]
            color[2] = value[2]
            if len(value) >= 4:
                color[3] = value[3]
            else:
                color[3] = 1.0
            vgSetParameterfv(self.handle, VG_PAINT_COLOR, 4, color)
            check_error()

cdef class GradientPaint(Paint):
    def __init__(self, gradient, linear=True):
        if linear:
            paint_type = VG_PAINT_TYPE_LINEAR_GRADIENT
        else:
            paint_type = VG_PAINT_TYPE_RADIAL_GRADIENT
        Paint.__init__(self, paint_type)
        self.gradient = gradient

    property gradient:
        def __get__(self):
            if self.type == VG_PAINT_TYPE_LINEAR_GRADIENT:
                return self.linear_gradient
            elif self.type == VG_PAINT_TYPE_RADIAL_GRADIENT:
                return self.radial_gradient
            else:
                raise ValueError("gradient parameter only makes sense for paint of type VG_PAINT_TYPE_LINEAR_GRADIENT or VG_PAINT_TYPE_RADIAL_GRADIENT")
        def __set__(self, value):
            if self.type == VG_PAINT_TYPE_LINEAR_GRADIENT:
                self.linear_gradient = value
            elif self.type == VG_PAINT_TYPE_RADIAL_GRADIENT:
                self.radial_gradient = value
            else:
                raise ValueError("gradient parameter only makes sense for paint of type VG_PAINT_TYPE_LINEAR_GRADIENT or VG_PAINT_TYPE_RADIAL_GRADIENT")

    property linear_gradient:
        def __get__(self):
            cdef VGfloat gradient[4]
            vgGetParameterfv(self.handle, VG_PAINT_LINEAR_GRADIENT, 4, gradient)
            check_error()
            return ((gradient[0], gradient[1]), (gradient[2], gradient[3]))
        def __set__(self, value):
            cdef VGfloat gradient[4]
            gradient[0] = value[0][0]
            gradient[1] = value[0][1]
            gradient[2] = value[1][0]
            gradient[3] = value[1][1]
            vgSetParameterfv(self.handle, VG_PAINT_LINEAR_GRADIENT, 4, gradient)
            check_error()

    property radial_gradient:
        def __get__(self):
            cdef VGfloat gradient[5]
            vgGetParameterfv(self.handle, VG_PAINT_RADIAL_GRADIENT, 5, gradient)
            check_error()
            return ((gradient[0], gradient[1]), gradient[2], (gradient[3], gradient[4]))
        def __set__(self, value):
            cdef VGfloat gradient[5]
            gradient[0] = value[0][0]
            gradient[1] = value[0][1]
            gradient[2] = value[1]
            gradient[3] = value[2][0]
            gradient[4] = value[2][1]
            vgSetParameterfv(self.handle, VG_PAINT_RADIAL_GRADIENT, 5, gradient)
            check_error()

    property ramp_spread_mode:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_PAINT_COLOR_RAMP_SPREAD_MODE)
        def __set__(self, value):
            vgSetParameteri(self.handle, VG_PAINT_COLOR_RAMP_SPREAD_MODE, value)

    property ramp_stops:
        def __get__(self):
            cdef VGfloat *values
            cdef object stops
            count = vgGetParameterVectorSize(self.handle, VG_PAINT_COLOR_RAMP_STOPS)
            values = <VGfloat*>malloc(sizeof(VGfloat) * count)

            vgGetParameterfv(self.handle, VG_PAINT_COLOR_RAMPS_STOPS, count, values)
            stops = []
            for i from 0 <= i < count/5:
                stop = (values[i*5],
                        (values[i*5+1], values[i*5+2], values[i*5+3], values[i*5+4]))
                stops.append(stop)
            free(<void*>values)
            check_error()
            return stops
        def __set__(self, stops):
            cdef VGfloat *values
            cdef VGint count
            count = len(stops) * 5
            values = <VGfloat*>malloc(sizeof(VGfloat) * count)
            for i from 0 <= i < count/5:
                values[i*5] = stops[i][0]
                values[i*5+1] = stops[i][1][0]
                values[i*5+2] = stops[i][1][1]
                values[i*5+3] = stops[i][1][2]
                values[i*5+4] = stops[i][1][3]
            vgSetParameterfv(self.handle, VG_PAINT_COLOR_RAMPS_STOPS, count, values)
            free(<void*>values)
            check_error()

    property ramp_premultiplied:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_COLOR_RAMP_PREMULTIPLIED)
        def __set__(self, value):
            vgSetParameteri(self.handle, VG_PAINT_TYPE, value)
            check_error()

cdef class PatternPaint(Paint):
    def __init__(self, pattern):
        Paint.__init__(self, VG_PAINT_TYPE_PATTERN)
        self.pattern = pattern

    property pattern:
        def __get__(self):
            return self._pattern
        def __set__(self, value):
            if value is None:
                vgPaintPattern(self.handle, VG_INVALID_HANDLE)
                self._pattern = None
            elif isinstance(value, Image):
                vgPaintPattern(self.handle, (<Image>value).handle)
                self._pattern = value
            else:
                raise TypeError("pattern must of type VG.Image")
            check_error()

    property tiling_mode:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_TILING_MODE)
        def __set__(self, value):
            vgSetParameteri(self.handle, VG_TILING_MODE, value)
            check_error()

cdef class Image:
    def __init__(self, format, width, height, quality=VG_IMAGE_QUALITY_BETTER):
        self.handle = vgCreateImage(format, width, height, quality)
        if self.handle == NULL:
            raise VGError(VG_BAD_HANDLE_ERROR, "unable to create image")
        check_error()
        _image_table[<long>self.handle] = self

    def __dealloc__(self):
        del _image_table[<long>self.handle]
        vgDestroyImage(self.handle)

    def clear(self, corner, dimensions, color=None):
        if color is not None:
            old_color = get(VG_CLEAR_COLOR)
            try:
                vgClearImage(self.handle, corner[0], corner[1], dimensions[0], dimensions[1])
                check_error()
            finally:
                set(VG_CLEAR_COLOR, color)
        else:
            vgClearImage(self.handle, corner[0], corner[1], dimensions[0], dimensions[1])
            check_error()

    def make_child(self, corner, dimensions):
        cdef VGImage handle
        cdef Image image

        handle = vgChildImage(self.handle, corner[0], corner[1], dimensions[0], dimensions[1])
        check_error()

        image = Image.__new__(Image)
        image.handle = handle
        _image_table[<long>handle] = image
        return image

    def blit(self, dest_pos, Image src not None, src_pos, dim, dither=VG_FALSE):
        vgCopyImage(self.handle, dest_pos[0], dest_pos[1],
                    src.handle, src_pos[0], src_pos[1],
                    dim[0], dim[1], dither)
        check_error()

    def draw(self, mode=None):
        if mode is not None:
            old_mode = get(VG_IMAGE_MODE)
            try:
                set(VG_IMAGE_MODE, mode)
                vgDrawImage(self.handle)
                check_error()
            finally:
                set(VG_IMAGE_MODE, old_mode)
        else:
            vgDrawImage(self.handle)
            check_error()
    
    property format:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_IMAGE_FORMAT)

    property width:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_IMAGE_WIDTH)

    property height:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_IMAGE_HEIGHT)

    property parent:
        def __get__(self):
            cdef VGImage handle
            cdef Image image

            handle = vgGetParent(self.handle)
            check_error()

            # Check if it really has a parent
            if handle == self.handle:
                return None
            if (<long>handle) in _image_table:
                return _image_table[<long>handle]
            else:
                image = Image.__new__(Image)
                image.handle = handle
                _image_table[<long>handle] = image
                return image

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

def clear(corner, dimensions):
    if dimensions[0] <= 0.0 or dimensions[1] <= 0.0:
        raise ValueError("width and height must be positive")
    vgClear(corner[0], corner[1], dimensions[0], dimensions[1])

def blit(src, dest_pos, src_pos, dimensions):
    if isinstance(src, Image):        
        vgSetPixels(dest_pos[0], dest_pos[1],
                    (<Image>src).handle, src_pos[0], src_pos[1],
                    dimensions[0], dimensions[1])
    else:
        raise NotImplementedError
    check_error()

def blit_to(Image dest not None, dest_pos, src_pos, dimensions):
    vgGetPixels(dest.handle, dest_pos[0], dest_pos[1],
                src_pos[0], src_pos[1],
                dimensions[0], dimensions[1])
    check_error()

def copy_pixels(dest_pos, src_pos, dimensions):
    vgCopyPixels(dest_pos[0], dest_pos[1],
                 src_pos[0], src_pos[1],
                 dimensions[0], dimensions[1])
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

#[M11, M12, M13, M21, M22, M23, M31, M32, M33]

def get_matrix():
    cdef VGfloat m[9]
    cdef object M

    vgGetMatrix(m)
    check_error()
    
    M = []
    for i from 0 <= i < 9:
        M.append(m[i])
    return M

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
##    cdef Paint paint
##    cdef VGPaint handle
##    handle = vgGetPaint(mode)
##    check_error()
##
##    if (<long>handle) in _paint_table:
##        return _paint_table[<long>handle]
##    else:
##        paint = Paint.__new__(Paint)
##        paint.handle = handle
##        _paint_table[<long>handle] = paint
##        return paint

def set_paint(Paint paint, mode):
    if paint is None:
        vgSetPaint(VG_INVALID_HANDLE, mode)
    else:
        vgSetPaint((<Paint>paint).handle, mode)
    check_error()
    
    if mode & VG_STROKE_PATH:
        Context.singleton.stroke_paint = paint
    if mode & VG_FILL_PATH:
        Context.singleton.fill_paint = paint
    

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
Context.clear = staticmethod(clear)
Context.blit = staticmethod(blit)
Context.blit_to = staticmethod(blit_to)
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

__all__ = ["Path", "Paint", "ColorPaint", "GradientPaint", "PatternPaint", "Image", "Context", "VGError", "check_error"]
