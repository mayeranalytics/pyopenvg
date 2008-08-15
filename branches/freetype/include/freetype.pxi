cdef extern from "stdlib.h":
    ctypedef long size_t

cdef extern from "pyfreetype.h":
    #ftconfig.h
    #Some tweaking may be needed on a platform-by-platform basis
    DEF FT_SIZEOF_INT = 4
    DEF FT_SIZEOF_LONG = 4
    
    ctypedef signed short      FT_Int16
    ctypedef unsigned short    FT_UInt16
    IF FT_SIZEOF_INT == 4:
        ctypedef signed int    FT_Int32
        ctypedef unsigned int  FT_UInt32
    ELIF FT_SIZEOF_LONG == 4:
        ctypedef signed long   FT_Int32
        ctypedef unsigned long FT_UInt32

    IF FT_SIZEOF_INT >= 4:
        ctypedef int           FT_Fast
        ctypedef unsigned int  FT_UFast
    ELIF FT_SIZEOF_LONG >= 4:
        ctypedef long          FT_Fast
        ctypedef unsigned long FT_UFast
    
    
    
    #fttypes.h
    ctypedef unsigned char     FT_Bool
    ctypedef signed short      FT_FWord
    ctypedef unsigned short    FT_UFWord
    ctypedef signed char       FT_Char
    ctypedef unsigned char     FT_Byte
    ctypedef FT_Byte*          FT_Bytes
    ctypedef FT_UInt32         FT_Tag
    ctypedef char              FT_String
    ctypedef signed short      FT_Short
    ctypedef unsigned short    FT_UShort
    ctypedef signed int        FT_Int
    ctypedef unsigned int      FT_UInt
    ctypedef signed long       FT_Long
    ctypedef unsigned long     FT_ULong
    ctypedef signed short      FT_F2Dot14
    ctypedef signed long       FT_F26Dot6
    ctypedef signed long       FT_Fixed
    ctypedef int               FT_Error
    ctypedef void*             FT_Pointer
    ctypedef size_t            FT_Offset
    #ctypedef ft_ptrdiff_t      FT_PtrDist
    ctypedef void            (*FT_Generic_Finalizer)(void* object)

    ctypedef struct FT_UnitVector:
        FT_F2Dot14 x,y

    ctypedef struct FT_Matrix:
        FT_Fixed xx, xy, yx, yy

    ctypedef struct FT_Data:
        FT_Bytes pointer
        FT_Int length

    ctypedef struct FT_Generic:
        void *data
        FT_Generic_Finalizer finalizer

    #ftimage.h
    ctypedef signed long       FT_Pos
    ctypedef struct FT_Vector:
        FT_Pos x,y

    ctypedef struct FT_BBox:
        FT_Pos xMin, yMin, xMax, yMax

    ctypedef enum FT_Pixel_Mode:
        FT_PIXEL_MODE_NONE = 0,
        FT_PIXEL_MODE_MONO,
        FT_PIXEL_MODE_GRAY,
        FT_PIXEL_MODE_GRAY2,
        FT_PIXEL_MODE_GRAY4,
        FT_PIXEL_MODE_LCD,
        FT_PIXEL_MODE_LCD_V,

        FT_PIXEL_MODE_MAX

    ctypedef struct FT_Bitmap:
        int            rows, width, pitch
        unsigned char *buffer
        short          num_grays
        char           pixel_mode, palette_mode
        void          *palette

    ctypedef struct FT_Outline:
        short          n_contours, n_points
        FT_Vector     *points
        char          *tags
        short         *contours
        int            flags

    DEF FT_OUTLINE_NONE =            0
    DEF FT_OUTLINE_OWNER =           1 << 0
    DEF FT_OUTLINE_EVEN_ODD_FILL =   1 << 1
    DEF FT_OUTLINE_REVERSE_FILL =    1 << 2
    DEF FT_OUTLINE_IGNORE_DROPOUTS = 1 << 3
    DEF FT_OUTLINE_HIGH_PRECISION =  1 << 8
    DEF FT_OUTLINE_SINGLE_PASS =     1 << 9

    ctypedef int (*FT_Outline_MoveToFunc)(FT_Vector *to, void *user)
    ctypedef int (*FT_Outline_LineToFunc)(FT_Vector *to, void *user)
    ctypedef int (*FT_Outline_ConicToFunc)(FT_Vector *control, FT_Vector *to, void *user)
    ctypedef int (*FT_Outline_CubicToFunc)(FT_Vector *control1, FT_Vector *control2, FT_Vector *to, void *user)

    ctypedef struct FT_Outline_Funcs:
        FT_Outline_MoveToFunc  move_to
        FT_Outline_LineToFunc  line_to
        FT_Outline_ConicToFunc conic_to
        FT_Outline_CubicToFunc cubic_to

        int shift
        FT_Pos delta

    ctypedef enum FT_Glyph_Format:
        FT_GLYPH_FORMAT_NONE = 0
        FT_GLYPH_FORMAT_COMPOSITE = ((<unsigned long>c'c' << 24) |
                                     (<unsigned long>c'o' << 16) |
                                     (<unsigned long>c'm' << 8)  |
                                     (<unsigned long>c'p')),
        FT_GLYPH_FORMAT_BITMAP =    ((<unsigned long>c'b' << 24) |
                                     (<unsigned long>c'i' << 16) |
                                     (<unsigned long>c't' << 8)  |
                                     (<unsigned long>c's')),
        FT_GLYPH_FORMAT_OUTLINE =   ((<unsigned long>c'o' << 24) |
                                     (<unsigned long>c'u' << 16) |
                                     (<unsigned long>c't' << 8)  |
                                     (<unsigned long>c'l')),
        FT_GLYPH_FORMAT_PLOTTER =   ((<unsigned long>c'p' << 24) |
                                     (<unsigned long>c'l' << 16) |
                                     (<unsigned long>c'o' << 8)  |
                                     (<unsigned long>c't'))
    
    

    #freetype.h
    ctypedef struct FT_Glyph_Metrics:
        FT_Pos  width, height
        FT_Pos  horiBearingX, horiBearingY, horiAdvance
        FT_Pos  vertBearingX, vertBearingY, vertAdvance
        
    ctypedef struct FT_Bitmap_Size:
        FT_Short  height, width
        FT_Pos    size
        FT_Pos    x_ppem, y_ppem

##    cdef struct FT_LibraryRec_:
##        pass
##    cdef struct FT_ModuleRec_:
##        pass
##    cdef struct FT_DriverRec_:
##        pass
##    cdef struct FT_RendererRec_:
##        pass

    cdef struct FT_FaceRec_
    cdef struct FT_SizeRec_
    cdef struct FT_GlyphSlotRec_
    cdef struct FT_CharMapRec_

##    ctypedef FT_LibraryRec_*   FT_Library
##    ctypedef FT_ModuleRec_*    FT_Module
##    ctypedef FT_DriverRec_*    FT_Driver
##    ctypedef FT_RendererRec_*  FT_Renderer
    ctypedef void*               FT_Library
    ctypedef void*               FT_Module
    ctypedef void*               FT_Driver
    ctypedef void*               FT_Renderer
    ctypedef FT_FaceRec_*      FT_Face
    ctypedef FT_SizeRec_*      FT_Size
    ctypedef FT_GlyphSlotRec_* FT_GlyphSlot
    ctypedef FT_CharMapRec_*   FT_CharMap

    ctypedef enum FT_Encoding:
        FT_ENCODING_NONE = 0
        FT_ENCODING_MS_SYMBOL =      ((<FT_UInt32>c's' << 24) |
                                      (<FT_UInt32>c'y' << 16) |
                                      (<FT_UInt32>c'm' << 8)  |
                                      (<FT_UInt32>c'b')),
        FT_ENCODING_UNICODE =        ((<FT_UInt32>c'u' << 24) |
                                      (<FT_UInt32>c'n' << 16) |
                                      (<FT_UInt32>c'i' << 8)  |
                                      (<FT_UInt32>c'c')),

        FT_ENCODING_SJIS =           ((<FT_UInt32>c's' << 24) |
                                      (<FT_UInt32>c'j' << 16) |
                                      (<FT_UInt32>c'i' << 8)  |
                                      (<FT_UInt32>c's')),
        FT_ENCODING_GB2312 =         ((<FT_UInt32>c'g' << 24) |
                                      (<FT_UInt32>c'b' << 16) |
                                      (<FT_UInt32>c' ' << 8)  |
                                      (<FT_UInt32>c' ')),
        FT_ENCODING_BIG5 =           ((<FT_UInt32>c'b' << 24) |
                                      (<FT_UInt32>c'i' << 16) |
                                      (<FT_UInt32>c'g' << 8)  |
                                      (<FT_UInt32>c'5')),
        FT_ENCODING_WANSUNG =        ((<FT_UInt32>c'w' << 24) |
                                      (<FT_UInt32>c'a' << 16) |
                                      (<FT_UInt32>c'n' << 8)  |
                                      (<FT_UInt32>c's')),
        FT_ENCODING_JOHAB =          ((<FT_UInt32>c'j' << 24) |
                                      (<FT_UInt32>c'o' << 16) |
                                      (<FT_UInt32>c'h' << 8)  |
                                      (<FT_UInt32>c'a')),

        FT_ENCODING_ADOBE_STANDARD = ((<FT_UInt32>c'A' << 24) |
                                      (<FT_UInt32>c'D' << 16) |
                                      (<FT_UInt32>c'O' << 8)  |
                                      (<FT_UInt32>c'B')),
        FT_ENCODING_ADOBE_EXPERT =   ((<FT_UInt32>c'A' << 24) |
                                      (<FT_UInt32>c'D' << 16) |
                                      (<FT_UInt32>c'B' << 8)  |
                                      (<FT_UInt32>c'E')),
        FT_ENCODING_ADOBE_CUSTOM =   ((<FT_UInt32>c'A' << 24) |
                                      (<FT_UInt32>c'D' << 16) |
                                      (<FT_UInt32>c'B' << 8)  |
                                      (<FT_UInt32>c'C')),
        FT_ENCODING_ADOBE_LATIN_1 =  ((<FT_UInt32>c'l' << 24) |
                                      (<FT_UInt32>c'a' << 16) |
                                      (<FT_UInt32>c't' << 8)  |
                                      (<FT_UInt32>c'1')),

        FT_ENCODING_OLD_LATIN_2 =    ((<FT_UInt32>c'l' << 24) |
                                      (<FT_UInt32>c'a' << 16) |
                                      (<FT_UInt32>c't' << 8)  |
                                      (<FT_UInt32>c'2')),

        FT_ENCODING_APPLE_ROMAN =    ((<FT_UInt32>c'a' << 24) |
                                      (<FT_UInt32>c'r' << 16) |
                                      (<FT_UInt32>c'm' << 8)  |
                                      (<FT_UInt32>c'n'))

    cdef struct FT_CharMapRec_:
        FT_Face     face
        FT_Encoding encoding
        FT_UShort   platform_id
        FT_UShort   encoding_id
    ctypedef FT_CharMapRec_ FT_CharMapRec

    cdef struct FT_FaceRec_:
        FT_Long           num_faces
        FT_Long           face_index

        FT_Long           face_flags
        FT_Long           style_flags

        FT_Long           num_glyphs

        FT_String*        family_name
        FT_String*        style_name

        FT_Int            num_fixed_sizes
        FT_Bitmap_Size*   available_sizes

        FT_Int            num_charmaps
        FT_CharMap*       charmaps

        FT_Generic        generic

        FT_BBox           bbox

        FT_UShort         units_per_EM
        FT_Short          ascender
        FT_Short          descender
        FT_Short          height

        FT_Short          max_advance_width
        FT_Short          max_advance_height

        FT_Short          underline_position
        FT_Short          underline_thickness

        FT_GlyphSlot      glyph
        FT_Size           size
        FT_CharMap        charmap
    ctypedef FT_FaceRec_ FT_FaceRec

    DEF FT_FACE_FLAG_SCALABLE =         1L << 0
    DEF FT_FACE_FLAG_FIXED_SIZES =      1L << 1
    DEF FT_FACE_FLAG_FIXED_WIDTH =      1L << 2
    DEF FT_FACE_FLAG_SFNT =             1L << 3
    DEF FT_FACE_FLAG_HORIZONTAL =       1L << 4
    DEF FT_FACE_FLAG_VERTICAL =         1L << 5
    DEF FT_FACE_FLAG_KERNING =          1L << 6
    DEF FT_FACE_FLAG_FAST_GLYPHS =      1L << 7
    DEF FT_FACE_FLAG_MULTIPLE_MASTERS = 1L << 8
    DEF FT_FACE_FLAG_GLYPH_NAMES =      1L << 9
    DEF FT_FACE_FLAG_EXTERNAL_STREAM =  1L << 10
    DEF FT_FACE_FLAG_HINTER =           1L << 11

    DEF FT_STYLE_FLAG_ITALIC = 1 << 0
    DEF FT_STYLE_FLAG_BOLD =   1 << 1

    ctypedef struct FT_Size_Metrics:
        FT_UShort x_ppem, y_ppem
        FT_Fixed  x_scale, y_scale
        FT_Pos    ascender, descender
        FT_Pos    height
        FT_Pos    max_advance

    cdef struct FT_SizeRec_:
        FT_Face         face
        FT_Generic      generic
        FT_Size_Metrics metrics
    ctypedef FT_SizeRec_ FT_SizeRec

    cdef struct FT_SubGlyphRec_:
        pass
    ctypedef FT_SubGlyphRec_* FT_SubGlyph

    ctypedef struct FT_GlyphSlotRec:
        FT_Library        library
        FT_Face           face
        FT_GlyphSlot      next
        FT_UInt           reserved  
        FT_Generic        generic

        FT_Glyph_Metrics  metrics
        FT_Fixed          linearHoriAdvance, linearVertAdvance
        FT_Vector         advance

        FT_Glyph_Format   format

        FT_Bitmap         bitmap
        FT_Int            bitmap_left, bitmap_top

        FT_Outline        outline

        FT_UInt           num_subglyphs
        FT_SubGlyph       subglyphs

        void*             control_data
        long              control_len

        FT_Pos            lsb_delta, rsb_delta

    FT_Error FT_Init_FreeType(FT_Library *lib)
    FT_Error FT_Done_FreeType(FT_Library lib)

    FT_Error FT_New_Face(FT_Library lib, char *path, FT_Long face_index, FT_Face *face)
    FT_Error FT_Done_Face(FT_Face face)

    ctypedef enum FT_Size_Request_Type:
        FT_SIZE_REQUEST_TYPE_NOMINAL,
        FT_SIZE_REQUEST_TYPE_REAL_DIM,
        FT_SIZE_REQUEST_TYPE_BBOX,
        FT_SIZE_REQUEST_TYPE_CELL,
        FT_SIZE_REQUEST_TYPE_SCALES,

        FT_SIZE_REQUEST_TYPE_MAX
    
    ctypedef struct FT_Size_RequestRec:
        FT_Size_Request_Type type
        FT_Long              width, height
        FT_UInt              horiResolution, vertResolution
    ctypedef FT_Size_RequestRec* FT_Size_Request

    FT_Error FT_Select_Size(FT_Face face, FT_Int strike_index)
    FT_Error FT_Request_Size(FT_Face face, FT_Size_Request req)
    FT_Error FT_Set_Char_Size(FT_Face, FT_F26Dot6 char_width, FT_F26Dot6 char_height, FT_UInt hres, FT_UInt vres)
    FT_Error FT_Set_Pixel_Sizes(FT_Face face, FT_UInt pixel_width, FT_UInt pixel_height)

    FT_Error FT_Load_Glyph(FT_Face face, FT_UInt glyph_index, FT_Int32 flags)
    FT_Error FT_Load_Char(FT_Face face, FT_ULong char_code, FT_Int32 flags)

    DEF FT_LOAD_DEFAULT =                     0
    DEF FT_LOAD_NO_SCALE =                    1 << 0
    DEF FT_LOAD_NO_HINTING =                  1 << 1
    DEF FT_LOAD_RENDER =                      1 << 2
    DEF FT_LOAD_NO_BITMAP =                   1 << 3
    DEF FT_LOAD_VERTICAL_LAYOUT =             1 << 4
    DEF FT_LOAD_FORCE_AUTOHINT =              1 << 5
    DEF FT_LOAD_CROP_BITMAP =                 1 << 6
    DEF FT_LOAD_PEDANTIC =                    1 << 7
    DEF FT_LOAD_IGNORE_GLOBAL_ADVANCE_WIDTH = 1 << 9
    DEF FT_LOAD_NO_RECURSE =                  1 << 10
    DEF FT_LOAD_IGNORE_TRANSFORM =            1 << 11
    DEF FT_LOAD_MONOCHROME =                  1 << 12
    DEF FT_LOAD_LINEAR_DESIGN =               1 << 13
    DEF FT_LOAD_SBITS_ONLY =                  1 << 14
    DEF FT_LOAD_NO_AUTOHINT =                 1 << 15

    void FT_Set_Transform(FT_Face face, FT_Matrix *matrix, FT_Vector *delta)
    
    ctypedef enum FT_Render_Mode:
        FT_RENDER_MODE_NORMAL = 0,
        FT_RENDER_MODE_LIGHT,
        FT_RENDER_MODE_MONO,
        FT_RENDER_MODE_LCD,
        FT_RENDER_MODE_LCD_V,

        FT_RENDER_MODE_MAX

    FT_Error FT_Render_Glyph(FT_GlyphSlot slot, FT_Render_Mode mode)

    ctypedef enum FT_Kerning_Mode:
        FT_KERNING_DEFAULT = 0
        FT_KERNING_UNFITTED,
        FT_KERNING_UNSCALED

    FT_Error FT_Get_Kerning(FT_Face face, FT_UInt left_glyph, FT_UInt right_glyph, FT_UInt mode, FT_Vector *kerning)
    FT_Error FT_Get_Track_Kerning(FT_Face face, FT_Fixed point_size, FT_Int degree, FT_Fixed *kerning)
    FT_Error FT_Get_Glyph_Name(FT_Face face, FT_UInt glyph_index, FT_Pointer buffer, FT_UInt buffer_max)
    char* FT_Get_Postscript_Name(FT_Face face)
    FT_Error FT_Select_Charmap(FT_Face face, FT_Encoding encoding)
    FT_Error FT_Set_Charmap(FT_Face face, FT_CharMap charmap)

    FT_Int FT_Get_Charmap_Index(FT_CharMap charmap)
    FT_UInt FT_Get_Char_Index(FT_Face face, FT_ULong charcode)
    FT_ULong FT_Get_First_Char(FT_Face face, FT_UInt *glyph_index)
    FT_ULong FT_Get_Next_Char(FT_Face face, FT_ULong charcode, FT_UInt *glyph_index)
    FT_UInt FT_Get_Name_Index(FT_Face face, FT_String *glyph_name)

    DEF FT_SUBGLYPH_FLAG_ARGS_ARE_WORDS =      1
    DEF FT_SUBGLYPH_FLAG_ARGS_ARE_XY_VALUES =  2
    DEF FT_SUBGLYPH_FLAG_ROUND_XY_TO_GRID =    4
    DEF FT_SUBGLYPH_FLAG_SCALE =               8
    DEF FT_SUBGLYPH_FLAG_XY_SCALE =           64
    DEF FT_SUBGLYPH_FLAG_2X2 =               128
    DEF FT_SUBGLYPH_FLAG_USE_MY_METRICS =    512

    void FT_Library_Version(FT_Library, FT_Int *major, FT_Int *minor, FT_Int *patch)
    FT_Bool FT_Face_CheckTrueTypePatents(FT_Face face)
    FT_Bool FT_Face_SetUnpatentedHinting(FT_Face face, FT_Bool value)
    


    #ftglyph.h
    ctypedef struct FT_GlyphRec:
        FT_Library      library
        FT_Glyph_Format format
        FT_Vector       advance
    ctypedef FT_GlyphRec* FT_Glyph
    
    ctypedef struct FT_BitmapGlyphRec:
        FT_GlyphRec root
        FT_Int      left, top
        FT_Bitmap   bitmap
    ctypedef FT_BitmapGlyphRec* FT_BitmapGlyph

    ctypedef struct FT_OutlineGlyphRec:
        FT_GlyphRec root
        FT_Outline  outline
    ctypedef FT_OutlineGlyphRec* FT_OutlineGlyph

    FT_Error FT_Get_Glyph(FT_GlyphSlot slot, FT_Glyph *glyph)
    FT_Error FT_Glyph_Copy(FT_Glyph source, FT_Glyph *target)
    FT_Error FT_Glyph_Transform(FT_Glyph glyph, FT_Matrix *matrix, FT_Vector *delta)

    ctypedef enum FT_Glyph_BBox_Mode:
        FT_GLYPH_BBOX_UNSCALED  = 0,
        FT_GLYPH_BBOX_SUBPIXELS = 0,
        FT_GLYPH_BBOX_GRIDFIT   = 1,
        FT_GLYPH_BBOX_TRUNCATE  = 2,
        FT_GLYPH_BBOX_PIXELS    = 3

    void FT_Glyph_Get_CBox(FT_Glyph glyph, FT_UInt bbox_mode, FT_BBox *cbox)
    FT_Error FT_Glyph_To_Bitmap(FT_Glyph *glyph, FT_Render_Mode mode, FT_Vector *origin, FT_Bool destroy)
    void FT_Done_Glyph(FT_Glyph glyph)

    void FT_Matrix_Multiply(FT_Matrix *a, FT_Matrix *b)
    FT_Error FT_Matrix_Invert(FT_Matrix *matrix) 



    #ftoutln.h
    FT_Error FT_Outline_Decompose(FT_Outline *outline, FT_Outline_Funcs *funcs, void *user)
    FT_Error FT_Outline_New(FT_Library lib, FT_UInt n_points, FT_Int n_contours, FT_Outline *outline)
    FT_Error FT_Outline_Done(FT_Library lib, FT_Outline *outline)
    FT_Error FT_Outline_Copy(FT_Outline *source, FT_Outline *target)
    FT_Error FT_Outline_Check(FT_Outline *outline)
    
    void FT_Outline_Get_CBox(FT_Outline *outline, FT_BBox *cbox)
    void FT_Outline_Translate(FT_Outline *outline, FT_Pos xOffset, FT_Pos yOffset)
    void FT_Outline_Transform(FT_Outline *outline, FT_Matrix *matrix)
    FT_Error FT_Outline_Embolden(FT_Outline *outline, FT_Pos strength)
    void FT_Outline_Reverse(FT_Outline *outline)
    FT_Error FT_Outline_Get_Bitmap(FT_Library lib, FT_Outline *outline, FT_Bitmap *bitmap)
    #FT_Error FT_Outline_Render(FT_Library lib, FT_Outline *outline, FT_Raster_params *params)

    ctypedef enum FT_Orientation:
        FT_ORIENTATION_TRUETYPE   = 0,
        FT_ORIENTATION_POSTSCRIPT = 1,
        FT_ORIENTATION_FILL_RIGHT = FT_ORIENTATION_TRUETYPE,
        FT_ORIENTATION_FILL_LEFT  = FT_ORIENTATION_POSTSCRIPT,
        FT_ORIENTATION_NONE

    FT_Orientation FT_Outline_Get_Orientation(FT_Outline *outline)
    