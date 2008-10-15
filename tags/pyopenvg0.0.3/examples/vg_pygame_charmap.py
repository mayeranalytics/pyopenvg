from __future__ import with_statement

import pygame

from OpenVG import VG
from OpenVG.font import Font
from OpenVG.constants import *

def main(width, height, font_path, size):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
    srf = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Freetype Font test")
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    font = Font(font_path, size)
    xmin, ymin, xmax, ymax = [x*font.scale for x in font.face.bbox]

    the_path = VG.Path()

    message = font.build_path("left click and drag to move")
    (x, y), (w, h) = message.bounds()
    VG.translate(width/2.0-w/2.0, height-h)
    message.transform(the_path)

    VG.load_identity()
    VG.translate(0-xmin, height-ymax-h)
    boxes_per_line = int(width/float(xmax-xmin))
    i = 0
    for char_code, glyph in sorted(font.glyph_table.items()):
        font.get_path_for_glyph(glyph).transform(the_path)
        VG.translate(xmax-xmin, 0)
        i += 1
        if i >= boxes_per_line:
            VG.translate((xmax-xmin)*-boxes_per_line, ymin-ymax)
            i = 0
    VG.load_identity()

        
    red_paint = VG.ColorPaint((1.0, 0.0, 0.0, 1.0))
    style = VG.Style(VG_STROKE_LINE_WIDTH = 1.0,
                     fill_paint = red_paint)
    style.enable()

    dragging = False
    
    running = True
    while running:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    dragging = True
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    dragging = False
            elif e.type == pygame.MOUSEMOTION:
                if dragging:
                    VG.translate(e.rel[0], -e.rel[1])

        VG.clear((0, 0), (width, height))
        
        the_path.draw(VG_STROKE_PATH | VG_FILL_PATH)

        
        pygame.display.flip()

if __name__ == '__main__':
    main(640, 480, "data/Vera.ttf", 42)
