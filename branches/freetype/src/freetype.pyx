import weakref
_library_table = weakref.WeakValueDictionary()

del weakref

include "freetype.pxi"

class FreeTypeError(BaseException):
    def __init__(self, code):
        msg = "FreeTypeError[%d]: %s" % (code, self.error_table[code])
        BaseException.__init__(self, msg)
    error_table = {
        0:"no error",
        1:"cannot open resource",
        2:"unknown file format",
        3:"broken file",
        4:"invalid FreeType version",
        5:"module version is too low",
        6:"invalid argument",
        7:"unimplemented feature",
        8:"broken table",
        9:"broken offset within table",
        10:"array allocation size too large",
        16:"invalid glyph index",
        17:"invalid character code",
        18:"unsupported glyph image format",
        19:"cannot render this glyph format",
        20:"invalid outline",
        21:"invalid composite glyph",
        22:"too many hints",
        23:"invalid pixel size",
        32:"invalid object handle",
        33:"invalid library handle",
        34:"invalid module handle",
        35:"invalid face handle",
        36:"invalid size handle",
        37:"invalid glyph slot handle",
        38:"invalid charmap handle",
        39:"invalid cache manager handle",
        40:"invalid stream handle",
        48:"too many modules",
        49:"too many extensions",
        64:"out of memory",
        65:"unlisted object",
        81:"cannot open stream",
        82:"invalid stream seek",
        83:"invalid stream skip",
        84:"invalid stream read",
        85:"invalid stream operation",
        86:"invalid frame operation",
        87:"nested frame access",
        88:"invalid frame read",
        96:"raster uninitialized",
        97:"raster corrupted",
        98:"raster overflow",
        99:"negative height while rastering",
        112:"too many registered caches",
        128:"invalid opcode",
        129:"too few arguments",
        130:"stack overflow",
        131:"code overflow",
        132:"bad argument",
        133:"division by zero",
        134:"invalid reference",
        135:"found debug opcode",
        136:"found ENDF opcode in execution stream",
        137:"nested DEFS",
        138:"invalid code range",
        139:"execution context too long",
        140:"too many function definitions",
        141:"too many instruction definitions",
        142:"SFNT font table missing",
        143:"horizontal header (hhea) table missing",
        144:"locations (loca) table missing",
        145:"name table missing",
        146:"character map (cmap) table missing",
        147:"horizontal metrics (hmtx) table missing",
        148:"PostScript (post) table missing",
        149:"invalid horizontal metrics",
        150:"invalid character map (cmap) format",
        151:"invalid ppem value",
        152:"invalid vertical metrics",
        153:"could not find context",
        154:"invalid PostScript (post) table format",
        155:"invalid PostScript (post) table",
        160:"opcode syntax error",
        161:"argument stack underflow",
        162:"ignore",
        176:"`STARTFONT' field missing",
        177:"`FONT' field missing",
        178:"`SIZE' field missing",
        179:"`CHARS' field missing",
        180:"`STARTCHAR' field missing",
        181:"`ENCODING' field missing",
        182:"`BBX' field missing",
        183:"`BBX' too big",
        184:"Font header corrupted or missing fields",
        185:"Font glyphs corrupted or missing fields"}

cdef class Library:
    cdef object __weakref__
    cdef FT_Library handle

    def __cinit__(self, *args, **kwargs):
        self.handle = NULL
    
    def __init__(self, *args, **kwargs):
        error = FT_Init_FreeType(&self.handle)
        if error:
            raise FreeTypeError(error)
        _library_table[<long>self.handle] = self

    def __dealloc__(self):
        FT_Done_FreeType(self.handle)

    property version:
        def __get__(self):
            cdef FT_Int major, minor, patch
            FT_Library_Version(self.handle, &major, &minor, &patch)
            return (major, minor, patch)

cdef class Face:
    cdef object __weakref__
    cdef Library library
    cdef FT_Face handle

    def __cinit__(self, *args, **kwargs):
        self.handle = NULL
        self.library = None

    def __init__(self, Library library not None, char *path, face_index=0):
        self.library = library
        error = FT_New_Face(library.handle, path, face_index, &self.handle)
        if error:
            raise FreeTypeError(error)

    def __dealloc__(self):
        FT_Done_Face(self.handle)

    def load_glyph(self, index, flags=FT_LOAD_DEFAULT):
        cdef FT_Glyph handle
        error = FT_Load_Glyph(self.handle, index, flags)
        if error:
            raise FreeTypeError(error)
        
        error = FT_Get_Glyph(self.handle[0].glyph, &handle)
        if error:
            raise FreeTypeError(error)
        return Glyph(<long>handle)

    def load_char(self, object s, flags=FT_LOAD_DEFAULT):
        cdef FT_Glyph handle
        error = FT_Load_Char(self.handle, ord(s[0]), flags)
        if error:
            raise FreeTypeError(error)

        error = FT_Get_Glyph(self.handle[0].glyph, &handle)
        if error:
            raise FreeTypeError(error)
        return Glyph(<long>handle)

    def get_glyphs(self, flags=FT_LOAD_DEFAULT):
        cdef FT_ULong char_code
        cdef FT_UInt glyph_index

        glyphs = []

        char_code = FT_Get_First_Char(self.handle, &glyph_index)
        while glyph_index:
            glyph = self.load_glyph(glyph_index, flags)
            glyphs.append((char_code, glyph))
            
            char_code = FT_Get_Next_Char(self.handle, char_code, &glyph_index)

        return glyphs

    def set_char_size(self, width, height, hres=72, vres=72):
        error = FT_Set_Char_Size(self.handle, width, height, hres, vres)
        if error:
            raise FreeTypeError(error)

    property family_name:
        def __get__(self):
            cdef char *name
            name = self.handle[0].family_name
            if name == NULL:
                return ""
            else:
                return name
    
    property style_name:
        def __get__(self):
            cdef char *name
            name = self.handle[0].style_name
            if name == NULL:
                return ""
            else:
                return name

    property units_per_EM:
        def __get__(self):
            return self.handle[0].units_per_EM

cdef class Glyph:
    cdef object __weakref__
    cdef FT_Glyph handle
    cdef Library library
    def __cinit__(self, *args, **kwargs):
        self.handle = NULL
        self.library = None

    def __init__(self, long handle):
        error = FT_Glyph_Copy(<FT_Glyph>handle, &self.handle)
        if error:
            raise FreeTypeError(error)
        self.library = _library_table[<long>(self.handle[0].library)]

    def __dealloc__(self):
        FT_Done_Glyph(self.handle)

    property format:
        def __get__(self):
            return self.handle[0].format

    property outline:
        def __get__(self):
            cdef long handle
            if self.handle[0].format != FT_GLYPH_FORMAT_OUTLINE:
                raise ValueError("Only glyphs of format FT_GLYPH_FORMAT_OUTLINE have an \"outline\" attribute")
            handle = <long>(&(<FT_OutlineGlyph>self.handle)[0].outline)
            return Outline(self.library, handle)

    property advance:
        def __get__(self):
            return (self.handle[0].advance.x, self.handle[0].advance.y)


cdef int call_move_to(FT_Vector *to, void *user):
    (<object>user)[0]((to[0].x, to[0].y))
    return 0

cdef int call_line_to(FT_Vector *to, void *user):
    (<object>user)[1]((to[0].x, to[0].y))
    return 0

cdef int call_conic_to(FT_Vector *control, FT_Vector *to, void *user):
    (<object>user)[2]((control[0].x, control[0].y),(to[0].x, to[0].y))
    return 0

cdef int call_cubic_to(FT_Vector *control1, FT_Vector *control2, FT_Vector *to, void *user):
    (<object>user)[3]((control1[0].x, control1[0].y),(control2[0].x, control2[0].y),(to[0].x, to[0].y))
    return 0

##cdef int print_move_to(FT_Vector *to, void *user):
##    print (to[0].x, to[0].y)
##    print "moo:", <object>user
##    return 0
##
##cdef int print_line_to(FT_Vector *to, void *user):
##    print (to[0].x, to[0].y)
##    return 0
##
##cdef int print_conic_to(FT_Vector *control, FT_Vector *to, void *user):
##    print (control[0].x, control[0].y), (to[0].x, to[0].y)
##    return 0
##
##cdef int print_cubic_to(FT_Vector *control1, FT_Vector *control2, FT_Vector *to, void *user):
##    print (control1[0].x, control1[0].y), (control2[0].x, control2[0].y), (to[0].x, to[0].y)
##    return 0

cdef class Outline:
    cdef object __weakref__
    cdef FT_Outline data
    cdef Library library

    def __init__(self, Library library not None, long handle):
        cdef FT_Outline src
        src = (<FT_Outline*>handle)[0]
        
        error = FT_Outline_New(library.handle, src.n_points, src.n_contours, &self.data)
        if error:
            raise FreeTypeError(error)

        error = FT_Outline_Copy(&src, &self.data)
        if error:
            raise FreeTypeError(error)

        self.library = library

    def __dealloc__(self):
        FT_Outline_Done(self.library.handle, &self.data)

    def translate(self, offset):
        FT_Outline_Translate(&self.data, offset[0], offset[1])
        
    def decompose(self, funcs, shift=0, delta=0):
        cdef FT_Outline_Funcs F
        F.move_to = &call_move_to
        F.line_to = &call_line_to
        F.conic_to = &call_conic_to
        F.cubic_to = &call_cubic_to
        F.shift = shift
        F.delta = delta

        error = FT_Outline_Decompose(&self.data, &F, <void*>funcs)
        if error:
            raise FreeTypeError(error)
