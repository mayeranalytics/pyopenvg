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

    property opacity:
        def __get__(self):
            cdef VGfloat color[4]
            vgGetParameterfv(self.handle, VG_PAINT_COLOR, 4, color)
            check_error()
            return color[3]
        
        def __set__(self, value):
            cdef VGfloat color[4]
            vgGetParameterfv(self.handle, VG_PAINT_COLOR, 4, color)
            check_error()

            color[4] = value
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
            return ((gradient[0], gradient[1]), (gradient[2], gradient[3]), gradient[4])
        def __set__(self, value):
            cdef VGfloat gradient[5]
            gradient[0] = value[0][0]
            gradient[1] = value[0][1]
            gradient[2] = value[1][0]
            gradient[3] = value[1][1]
            gradient[4] = value[2]
            vgSetParameterfv(self.handle, VG_PAINT_RADIAL_GRADIENT, 5, gradient)
            check_error()

    property spread_mode:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_PAINT_COLOR_RAMP_SPREAD_MODE)
        def __set__(self, value):
            vgSetParameteri(self.handle, VG_PAINT_COLOR_RAMP_SPREAD_MODE, value)

    property stops:
        def __get__(self):
            cdef VGfloat *values
            cdef object stops
            count = vgGetParameterVectorSize(self.handle, VG_PAINT_COLOR_RAMP_STOPS)
            values = <VGfloat*>malloc(sizeof(VGfloat) * count)

            vgGetParameterfv(self.handle, VG_PAINT_COLOR_RAMP_STOPS, count, values)
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
            vgSetParameterfv(self.handle, VG_PAINT_COLOR_RAMP_STOPS, count, values)
            free(<void*>values)
            check_error()

    property premultiplied:
        def __get__(self):
            return vgGetParameteri(self.handle, VG_COLOR_RAMP_PREMULTIPLIED)
        def __set__(self, value):
            vgSetParameteri(self.handle, VG_PAINT_TYPE, value)
            check_error()

cdef class PatternPaint(Paint):
    def __init__(self, pattern, tiling_mode=None):
        Paint.__init__(self, VG_PAINT_TYPE_PATTERN)
        self.pattern = pattern
        if tiling_mode is not None:
            self.tiling_mode = tiling_mode

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
            return vgGetParameteri(self.handle, VG_PAINT_PATTERN_TILING_MODE)
        def __set__(self, value):
            vgSetParameteri(self.handle, VG_PAINT_PATTERN_TILING_MODE, value)
            check_error()
