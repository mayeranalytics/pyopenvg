cdef class Path:
    def __cinit__(self, *args, **kwargs):
        self.datafunc = data_py_warn
        self.handle = NULL
        self.datasize = 0
        
    def __init__(self, format=0, datatype=VG_PATH_DATATYPE_F,
                 scale=1.0, bias=0, segment_hint=0,
                 coord_hint=0, capabilities=VG_PATH_CAPABILITY_ALL):
        if scale == 0.0:
            raise ValueError("scale cannot be 0")

        self.handle = vgCreatePath(format, datatype, scale, bias, segment_hint, coord_hint, capabilities)
        self.style = None

        if self.handle == NULL:
            raise VGError(VG_BAD_HANDLE_ERROR, "unable to create path")

        check_error(VG_ILLEGAL_ARGUMENT_ERROR="datatype %r is not a valid path datatype" % datatype,
                    VG_UNSUPPORTED_PATH_FORMAT_ERROR="format %r is unsupported" % format)
        
        if self.datatype == VG_PATH_DATATYPE_F:
            self.datasize = sizeof(VGfloat)
            self.datafunc = data_py_to_float
        elif self.datatype == VG_PATH_DATATYPE_S_8:
            self.datasize = sizeof(VGbyte)
            self.datafunc = data_py_to_byte
        elif self.datatype == VG_PATH_DATATYPE_S_16:
            self.datasize = sizeof(VGshort)
            self.datafunc = data_py_to_short
        elif self.datatype == VG_PATH_DATATYPE_S_32:
            self.datasize = sizeof(VGint)
            self.datafunc = data_py_to_int
        else:
            raise RuntimeError("Unknown path datatype %s" % self.datatype)
    
    def __dealloc__(self):
        vgDestroyPath(self.handle)

    def clear(self, capabilities=None):
        if capabilities is None:
            capabilities = self.capabilities
        vgClearPath(self.handle, capabilities)
        check_error()

    def append(self, segment):
        cdef VGubyte pathSegment
        cdef void *pathData

        command, data = segment

        pathSegment = command
        pathData = malloc(self.datasize * 6)
        if pathData == NULL:
            raise MemoryError("Unable to allocate space for data buffer")
        try:
            self.datafunc(data, 0, pathData)
            vgAppendPathData(self.handle, 1, &pathSegment, pathData)
            check_error(VG_ILLEGAL_ARGUMENT_ERROR="possible invalid command %s" % command)
        finally:
            free(pathData)

    def extend(self, segments):
        cdef VGubyte *pathSegments
        cdef void *pathData
        cdef VGint num_segments, i, j
        
        
        if not isinstance(segments, Path):
            num_segments = len(segments)
            
            pathSegments = <VGubyte*>malloc(sizeof(VGubyte) * num_segments)
            if pathSegments == NULL:
                raise MemoryError("Unable to allocate space for command buffer")
            pathData = malloc(self.datasize * num_segments * 6)
            if pathData == NULL:
                raise MemoryError("Unable to allocate space for data buffer")
            try:
                i = j = 0
                for i from 0 <= i < num_segments:
                    pathSegments[i] = segments[i][0]
                    j = self.datafunc(segments[i][1], j, pathData)
                
                vgAppendPathData(self.handle, num_segments, pathSegments, pathData)
                check_error(VG_ILLEGAL_ARGUMENT_ERROR="no segments or invalid command")
            finally:
                free(<void*>pathSegments)
                free(pathData)
            
        else:
            self.append_path(segments)

    def append_path(self, Path path not None):
        vgAppendPath(self.handle, path.handle)
        check_error(VG_BAD_HANDLE_ERROR="one of the paths is invalid or from a different context",
                    VG_PATH_CAPABILITY_ERROR="either VG_PATH_CAPABILITY_APPEND_FROM or APPEND_TO is disabled")

    def modify(self, index, data):
        cdef void *pathData
        cdef VGint num_segments, i, j

        num_segments = len(data)

        pathData = malloc(self.datasize * 6 * num_segments)
        if pathData == NULL:
            raise MemoryError("Unable to allocate space for data buffer")

        try:
            j = 0
            for i from 0 <= i < num_segments:
                j = self.datafunc(data[i], j, pathData)

            vgModifyPathCoords(self.handle, index, num_segments, pathData)
            check_error()
        finally:
            free(pathData)
    
    def bounds(self):
        cdef VGfloat minX, minY, width, height
        vgPathBounds(self.handle, &minX, &minY, &width, &height)
        check_error()
        return (minX, minY), (width, height)

    def transformed_bounds(self):
        cdef VGfloat minX, minY, width, height
        vgPathTransformedBounds(self.handle, &minX, &minY, &width, &height)
        check_error()
        return (minX, minY), (width, height)

    def length(self, start=0, num_segments=None):
        if not self.capabilities & VG_PATH_CAPABILITY_PATH_LENGTH:
            raise VGError(VG_PATH_CAPABILITY_ERROR, "VG_PATH_CAPABILITY_PATH_LENGTH must be enabled")

        if num_segments is None:
            num_segments = self.num_segments - start

        L = vgPathLength(self.handle, start, num_segments)
        check_error()
        return L

    def get_point(self, distance, start=0, num_segments=None):
        cdef VGfloat x, y, tangentX, tangentY
        if num_segments is None:
            num_segments = self.num_segments - start

        vgPointAlongPath(self.handle, start, num_segments, distance,
                         &x, &y, &tangentX, &tangentY)
        check_error()
        return (x, y), (tangentX, tangentY)

    def draw(self, paint_modes, object style=None):
        if self.style is not None and style is not None:
            style = self.style + style
        elif self.style is not None and style is None:
            style = self.style

        if style is not None:
            style.enable()
            vgDrawPath(self.handle, paint_modes)
            style.disable()
        else:
            vgDrawPath(self.handle, paint_modes)

        check_error()

    def close(self):
        self.append((VG_CLOSE_PATH, ()))

    def move_to(self, p, rel=False):
        self.append((VG_MOVE_TO | rel, p))

    def line_to(self, p, rel=False):
        self.append((VG_LINE_TO | rel, p))

    def hline_to(self, x, rel=False):
        self.append((VG_HLINE_TO | rel, (x,)))

    def vline_to(self, y, rel=False):
        self.append((VG_VLINE_TO | rel, (y,)))

    def quad_to(self, p1, p2, rel=False):
        data = (p1[0],p1[1], p2[0],p2[1])
        self.append((VG_QUAD_TO | rel, data))

    def squad_to(self, p2, rel=False):
        self.append((VG_SQUAD_TO | rel, p2))

    def cubic_to(self, p1, p2, p3, rel=False):
        data = (p1[0],p1[1], p2[0],p2[1], p3[0],p3[1])
        self.append((VG_CUBIC_TO | rel, data))

    def scubic_to(self, p2, p3, rel=False):
        data = (p2[0],p2[1], p3[0],p3[1])
        self.append((VG_SCUBIC_TO | rel, data))

    def arc_to(self, p1, rh, rv, rot, major, CW, rel=False):
        data = (rh,rv,rot,p1[0],p1[1])
        if major and CW:
            command = VG_LCWARC_TO
        elif major and not CW:
            command = VG_LCCWARC_TO
        elif not major and CW:
            command = VG_SCWARC_TO
        else:
            command = VG_SCCWARC_TO
        self.append((command | rel, data))


    def transform(self, Path dest=None):
        capabilities = self.capabilities
        if not capabilities & VG_PATH_CAPABILITY_TRANSFORM_FROM:
            raise VGError(VG_PATH_CAPABILITY_ERROR, "source path must have VG_PATH_CAPABILITY_TRANSFORM_FROM enabled")

        if dest is None:
            capabilities |= VG_PATH_CAPABILITY_TRANSFORM_TO
            dest = Path(self.format, self.datatype, self.scale, self.bias,
                        self.num_segments, self.num_coords, capabilities)
        elif not dest.capabilities & VG_PATH_CAPABILITY_TRANSFORM_TO:
            raise VGError(VG_PATH_CAPABILITY_ERROR, "dest path must have VG_PATH_CAPABILITY_TRANSFORM_TO enabled")
        
        vgTransformPath(dest.handle, self.handle)
        check_error()

        return dest

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
        def __set__(self, value):
            if (value & ~self.capabilities):
                raise ValueError("path capabilities may only be removed, not added")
            vgRemovePathCapabilities(self.handle, self.capabilities & ~value)
            
cdef int data_py_to_byte(object data, int j, void *pathData) except -1:
    for datum in data:
        (<VGbyte*>pathData)[j] = datum
        j += 1
    return j

cdef int data_py_to_short(object data, int j, void *pathData) except -1:
    for datum in data:
        (<VGshort*>pathData)[j] = datum
        j += 1
    return j

cdef int data_py_to_int(object data, int j, void *pathData) except -1:
    for datum in data:
        (<VGint*>pathData)[j] = datum
        j += 1
    return j

cdef int data_py_to_float(object data, int j, void *pathData) except -1:
    for datum in data:
        (<VGfloat*>pathData)[j] = datum
        j += 1
    return j

cdef int data_py_warn(object data, int j, void *pathData) except -1:
    raise ValueError("Uninitialized path wrapper objects should not be used")
    return -1

def interpolate(Path start not None, Path end not None, Path dest, VGfloat amount):
    if not start.capabilities & VG_PATH_CAPABILITY_INTERPOLATE_FROM:
        raise VGError(VG_PATH_CAPABILITY_ERROR, "start path must have VG_PATH_CAPABILITY_INTERPOLATE_FROM enabled")
    elif not end.capabilities & VG_PATH_CAPABILITY_INTERPOLATE_FROM:
        raise VGError(VG_PATH_CAPABILITY_ERROR, "end path must have VG_PATH_CAPABILITY_INTERPOLATE_FROM enabled")

    if dest is None:
        capabilities = start.capabilities | end.capabilities | VG_PATH_CAPABILITY_INTERPOLATE_TO
        dest = Path(format=start.format,
                    datatype=max(start.datatype, end.datatype),
                    capabilties=capabilities)
    elif not dest.capabilities & VG_PATH_CAPABILITY_INTERPOLATE_TO:
        raise VGError(VG_PATH_CAPABILITY_ERROR, "dest path must have VG_PATH_CAPABILITY_INTERPOLATE_TO enabled")

    success = vgInterpolatePath(dest.handle, start.handle, end.handle, amount)
    check_error()

    if not success:
        raise ValueError("Interpolation failed (segment types may have not matched)")
    
    return dest
