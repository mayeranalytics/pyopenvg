cdef class Image:
    def __init__(self, format, dimensions, quality=VG_IMAGE_QUALITY_BETTER):
        self.handle = vgCreateImage(format, dimensions[0], dimensions[1], quality)
        if self.handle == NULL:
            raise VGError(VG_BAD_HANDLE_ERROR, "unable to create image")
        check_error()
        _image_table[<long>self.handle] = self

    def __dealloc__(self):
        del _image_table[<long>self.handle]
        vgDestroyImage(self.handle)

    def sub_data(self, char *data, stride, format, corner, dimensions):
        vgImageSubData(self.handle, <void*>data,
                       stride, format,
                       corner[0], corner[1],
                       dimensions[0], dimensions[1])
        check_error(VG_IMAGE_IN_USE_ERROR="%r is currently a rendering target" % self,
                    VG_UNSUPPORTED_IMAGE_FORMAT_ERROR="invalid format",
                    VG_ILLEGAL_ARGUMENT_ERROR="invalid width/height or data is NULL or data is misaligned")

    def fromiter(self, it, corner, dimensions, alpha=False):
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
                           corner[0], corner[1], width, height)
            check_error()

        finally:
            free(<void*>data)

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
            if (<long>handle) in _image_table:
                return _image_table[<long>handle]
            else:
                image = Image.__new__(Image)
                image.handle = handle
                _image_table[<long>handle] = image
                return image
