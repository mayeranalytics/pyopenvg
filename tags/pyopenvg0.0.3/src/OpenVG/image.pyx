ctypedef struct PyArrayInterface:
    int two              # contains the integer 2 -- simple sanity check
    int nd               # number of dimensions
    char typekind        # kind in array --- character code of typestr
    int itemsize         # size of each element
    int flags            # flags indicating how the data should be interpreted
                         #   must set ARR_HAS_DESCR bit to validate descr
    Py_intptr_t *shape   # A length-nd array of shape information
    Py_intptr_t *strides # A length-nd array of stride information
    void *data           # A pointer to the first element of the array
    void *descr          # NULL or data-description (same as descr key
                         #       of __array_interface__) -- must set ARR_HAS_DESCR
                         #       flag or this will be ignored.

cdef int format_size(format):
    if format < 0 or format > VG_lABGR_8888_PRE:
        raise ValueError("Unknown format %s" % format)

    format &= ~(1 << 6 | 1 << 7) #clear channel order bits
    if VG_sRGBX_8888 <= format <= VG_sRGBA_8888_PRE:
        return 32
    elif VG_sRGB_565 <= format <= VG_sRGBA_4444:
        return 16
    elif VG_lRGBX_8888 <= format <= VG_lRGBA_8888:
        return 32
    elif format == VG_sL_8 or format == VG_lL_8 or format == VG_A_8:
        return 8
    elif format == VG_BW_1:
        return 1
    else:
        raise ValueError("Unknown format")

cdef void* get_read_buffer(object buffer) except NULL:
    cdef void *p
    cdef Py_ssize_t buffer_len

    if PyObject_AsReadBuffer(buffer, &p, &buffer_len) != -1:
        return p

cdef void* get_write_buffer(object buffer, Py_ssize_t min_size) except NULL:
    cdef void *p
    cdef Py_ssize_t buffer_len

    if PyObject_AsWriteBuffer(buffer, <void**>&p, &buffer_len) != -1:
        if buffer_len < min_size:
            raise ValueError("Buffer %r is too small (length %d needed)" % (buffer, min_size))
        return p

cdef class Image:
    def __init__(self, format, dimensions, quality=VG_IMAGE_QUALITY_BETTER):
        self.handle = vgCreateImage(format, dimensions[0], dimensions[1], quality)
        if self.handle == NULL:
            raise VGError(VG_BAD_HANDLE_ERROR, "unable to create image")

        self.width = dimensions[0]
        self.height = dimensions[1]
        self.format = format
        
        check_error()
        _image_table[<long>self.handle] = self

    def __dealloc__(self):
        vgDestroyImage(self.handle)

    def sub_data(self, object data, stride, format, corner, dimensions, flip=False):
        cdef void *p
        p = get_read_buffer(data)
        
        if not flip:
            vgImageSubData(self.handle, p,
                           stride, format,
                           corner[0], corner[1],
                           dimensions[0], dimensions[1])
        else:
            vgImageSubData(self.handle, &((<char*>p)[stride*(dimensions[1]-1)]),
                           -stride, format,
                           corner[0], corner[1],
                           dimensions[0], dimensions[1])
        check_error(VG_IMAGE_IN_USE_ERROR="%r is currently a rendering target" % self,
                    VG_UNSUPPORTED_IMAGE_FORMAT_ERROR="invalid format",
                    VG_ILLEGAL_ARGUMENT_ERROR="invalid width/height or data is NULL or data is misaligned")

    def get_sub_data(self, object buffer, area, format, stride=0):
        cdef void *data
        cdef Py_ssize_t size

        size = format_size(format) * area[1][0]*area[1][1]/8

        data = get_write_buffer(buffer, size)
        vgGetImageSubData(self.handle, data, stride, format,
                          area[0][0], area[0][1],
                          area[1][0], area[1][1])
        check_error()
        

##    def load_array(self, array, format, pos, dimensions, padded=False):
##        cdef PyArrayInterface *interface
##        cdef void *data
##        if not hasattr(array, "__array_struct__"):
##            raise ValueError("Array object must implement __array_struct__")
##
##        interface = <PyArrayInterface*>PyCObject_GetDesc(array.__array_struct__)
##        if interface.two != 2:
##            raise ValueError("__array_struct__.two did not equal to 2")
##
##        if interface.nd != 2:
##            raise NotImplementedError("Only 2D arrays are supported")
##
##        if padded or (format & ~(1 << 6 | 1 << 7)) in (VG)):
##            data = interface.data
##        else:
##            count = interface.shapes[0] * interface.shapes[1]
##            size = format_size(format)
##            if size == 1: #Not RGB{A,X} data
##                data = malloc(count)
##            elif size == -1: #B & W bitmap
##                pass
##            else:
##                data = malloc( * count
##
##        vgImageSubData(self.handle, interface.data, interface.strides[0],
##                       format, pos[0], pos[1], dimensions[0], dimensions[1])
##        check_error()

    def fromiter(self, it, pos, dimensions, alpha=False):
        cdef VGubyte *data
        cdef VGImageFormat format
        cdef long i, width, height

        width, height = dimensions
        data = <VGubyte*>malloc(sizeof(VGubyte) * 4 * width * height)
        try:
            if alpha:
                format = VG_lRGBA_8888
                for i from 0 <= i < width*height:
                    obj = it.next()
                    data[i*4] = obj[0]
                    data[i*4+1] = obj[1]
                    data[i*4+2] = obj[2]
                    data[i*4+3] = obj[3]
                    
            else:
                format = VG_lRGBX_8888
                for i from 0 <= i < width*height:
                    obj = it.next()
                    data[i*4] = obj[0]
                    data[i*4+1] = obj[1]
                    data[i*4+2] = obj[2]
            
            vgImageSubData(self.handle, <void*>data, 4 * width, format,
                           pos[0], pos[1], width, height)
            check_error()

        finally:
            free(<void*>data)

    def clear(self, pos, dimensions, color=None):
        if color is not None:
            old_color = get(VG_CLEAR_COLOR)
            vgClearImage(self.handle, pos[0], pos[1], dimensions[0], dimensions[1])
            set(VG_CLEAR_COLOR, color)
        else:
            vgClearImage(self.handle, pos[0], pos[1], dimensions[0], dimensions[1])

        check_error()

    def make_child(self, pos, dimensions):
        cdef VGImage handle
        cdef Image image

        handle = vgChildImage(self.handle, pos[0], pos[1], dimensions[0], dimensions[1])
        check_error()

        image = Image.__new__(Image)
        image.handle = handle
        _image_table[<long>handle] = image
        return image

    def blit(self, Image src not None, dest_pos, area=None, dither=VG_FALSE):
        if area is None:
            area = ((0, 0), (src.width, src.height))
        vgCopyImage(self.handle, dest_pos[0], dest_pos[1],
                    src.handle, area[0][0], area[0][1],
                    area[0][0], area[0][1], dither)
        check_error()

    def draw(self, mode=None):
        if mode is not None:
            old_mode = get(VG_IMAGE_MODE)
            set(VG_IMAGE_MODE, mode)
            vgDrawImage(self.handle)
            set(VG_IMAGE_MODE, old_mode)
        else:
            vgDrawImage(self.handle)

        check_error()
    
##    property format:
##        def __get__(self):
##            return vgGetParameteri(self.handle, VG_IMAGE_FORMAT)
##
##    property width:
##        def __get__(self):
##            return vgGetParameteri(self.handle, VG_IMAGE_WIDTH)
##
##    property height:
##        def __get__(self):
##            return vgGetParameteri(self.handle, VG_IMAGE_HEIGHT)

    property size:
        def __get__(self):
            return (self.width, self.height)

    property parent:
        def __get__(self):
            cdef VGImage handle
            cdef Image image

            handle = vgGetParent(self.handle)
            check_error()

            # Check if it really has a parent
            if handle == self.handle:
                return None

            return lookup_image(handle)

cdef object lookup_image(VGImage handle):
    cdef Image im
    if (<long>handle) in _image_table:
        return _image_table[<long>handle]
    else:
        im = Image.__new__(Image)
        im.handle = handle
        return im

def blit(Image src not None, dest_pos, area=None):
    cdef VGint dest_x, dest_y
    cdef VGint src_x, src_y, width, height

    dest_x, dest_y = dest_pos
    
    if area is None:
        src_x = src_y = 0
        width = src.width
        height = src.height
    else:
        (src_x, src_y), (width, height) = area

    if dest_x < 0:
        src_x -= dest_x
        width += dest_x
        dest_x = 0

    if dest_y < 0:
        src_y -= dest_y
        height += dest_y
        dest_y = 0
        
    vgSetPixels(dest_x, dest_y,
                src.handle, src_x, src_y,
                width, height)
    check_error()

def blit_buffer(object buffer, dest_pos, dimensions, format, stride=0):
    cdef void *data
    
    data = get_read_buffer(buffer)
    vgWritePixels(data, stride, format,
                  dest_pos[0], dest_pos[1],
                  dimensions[0], dimensions[1])
    check_error()

def blit_to_buffer(object buffer, object area, format, stride=0):
    cdef void *data
    cdef Py_ssize_t size

    size = format_size(format) * area[1][0]*area[1][1]/8

    data = get_write_buffer(buffer, size)
    vgReadPixels(data, stride, format,
                 area[0][0], area[0][1],
                 area[1][0], area[1][1])
    check_error()

def blit_to_image(Image dest not None, dest_pos, area):
    vgGetPixels(dest.handle, dest_pos[0], dest_pos[1],
                area[0][0], area[0][1],
                area[1][0], area[1][1])
    check_error()

def copy_pixels(dest_pos, area):
    cdef VGint dest_x, dest_y
    cdef VGint src_x, src_y, width, height

    dest_x, dest_y = dest_pos
    
    if area is None:
        src_x = src_y = 0
        width = src.width
        height = src.height
    else:
        (src_x, src_y), (width, height) = area

    if dest_x < 0:
        src_x -= dest_x
        width += dest_x
        dest_x = 0

    if dest_y < 0:
        src_y -= dest_y
        height += dest_y
        dest_y = 0
    
    vgCopyPixels(dest_x, dest_y,
                 src_x, src_y,
                 width, height)
    check_error()
