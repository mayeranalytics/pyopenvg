cdef class Path:
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
    
    def __dealloc__(self):
        vgDestroyPath(self.handle)

    def clear(self, capabilities=VG_PATH_CAPABILITY_ALL):
        vgClearPath(self.handle, capabilities)
        check_error()

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

    def length(self, start=0, num_segments=None):
        if not self.capabilities & VG_PATH_CAPABILITY_PATH_LENGTH:
            raise VGError(VG_PATH_CAPABILITY_ERROR, "VG_PATH_CAPABILITY_PATH_LENGTH must be enabled")

        if num_segments is None:
            num_segments = self.num_segments

        L = vgPathLength(self.handle, start, num_segments)
        check_error()
        return L

    def get_point(self, distance, start=0, num_segments=None):
        cdef VGfloat x, y, tangentX, tangentY
        if num_segments is None:
            num_segments = self.num_segments

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
            try:
                style.enable()
                vgDrawPath(self.handle, paint_modes)
                check_error()
            finally:
                style.disable()
        else:
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
