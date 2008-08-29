from OpenVG import VG
from OpenVG.constants import *

from FT.freetype import *
from FT.constants import *

library = Library()

class Font(object):
    def __init__(self, path, size, dpi=72, preload=True):
        self.path = path
        self.size = size
        self.face = Face(library, path)
        self.face.set_char_size(0, size*64, 0, dpi)
        
        self.scale = (size * dpi) / (72.0 * self.face.units_per_EM)

        self.glyph_table = {}
        self.path_table = {}

        if preload:
            flags = FT_LOAD_NO_SCALE | FT_LOAD_LINEAR_DESIGN
            for char_code, glyph in self.face.get_glyphs(flags):
                self.glyph_table[char_code] = glyph

    def build_path(self, text, horizontal=True, do_kerning=True):
        old_matrix = VG.get_matrix()
        VG.load_identity()

        path = VG.Path()

        #Kerning and vertical layouts are mutually exclusive in Freetype
        if do_kerning and horizontal and self.face.has_kerning:
            last_glyph = None
            for char in text:
                glyph = self.get_glyph(char)
                subpath = self.get_path_for_glyph(glyph)
                if last_glyph is not None:
                    kerning = self.face.get_kerning(last_glyph.index,
                                                    glyph.index,
                                                    FT_KERNING_UNSCALED)
                    VG.translate(self.scale*kerning[0], self.scale*kerning[1])
                last_glyph = glyph

                subpath.transform(path)
                VG.translate(self.scale*glyph.advance[0], 0.0)
        else:
            for char in text:
                glyph = self.get_glyph(char)
                subpath = self.get_path_for_glyph(glyph)
                subpath.transform(path)
                VG.translate(self.scale*glyph.advance[0]*horizontal,
                             self.scale*glyph.advance[1]*(not horizontal))

        VG.load_matrix(old_matrix)
        return path

    def get_path_for_glyph(self, glyph):
        if glyph.index in self.path_table:
            return self.path_table[glyph.index]
        else:
            path = self.path_table[glyph.index] = VG.Path(scale=self.scale)
            funcs = (path.move_to, path.line_to, path.quad_to, path.cubic_to)
            glyph.outline.decompose(funcs)
            return path

    def get_path_for_char(self, char):
        return self.get_path_for_glyph(self.get_glyph(char).index)

    def get_glyph(self, char):
        if ord(char) in self.glyph_table:
            return self.glyph_table[ord(char)]
        else:
            flags = FT_LOAD_NO_SCALE | FT_LOAD_LINEAR_DESIGN
            glyph = self.face.load_char(char, flags)
            self.glyph_table[ord(char)] = glyph
            return glyph

    def compile_paths(self):
        for glyph in self.glyph_table.values():
            path = self.path_table[glyph.index] = VG.Path(scale=scale.scale)
            funcs = (path.move_to, path.line_to, path.quad_to, path.cubic_to)
            glyph.outline.decompose(funcs)
            
__all__ = ["Font"]
