include "vgbase.pyx"
include "VG/shiva.pxi"

def create_context(dimensions):
    return Context(dimensions)

def destroy_context():
    if Context.singleton is not None:
        vgDestroyContextSH()
    Context.singleton = None

def resize_context(dimensions):
    if Context.singleton is not None:
        Context.singleton.resize(dimensions)
    else:
        raise RuntimeError("Cannot resize context before creating context")

class Context(object):
    def __init__(self, dimensions):
        self.dimensions = dimensions

    def resize(self, dimensions):
        vgResizeSurfaceSH(dimensions[0], dimensions[1])
        check_error()

    def __del__(self):
        if self.__class__.singleton is not None:
            vgDestroyContextSH()
        self.__class__.singleton = None

    def destroy(self):
        self.__del__()
        
def context_new(cls, dimensions):
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

Context.__new__ = staticmethod(context_new)
del context_new
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
