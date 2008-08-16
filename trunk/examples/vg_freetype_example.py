from __future__ import with_statement

import pygame

from OpenVG import VG
from OpenVG.font import Font
from OpenVG.constants import *

def main(width, height, message):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 16)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    srf = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Freetype Font test")
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    font = Font("vera.ttf", 64)

    red_paint = VG.ColorPaint((1.0, 0.0, 0.0, 1.0))
    text = font.build_path(message)
    text.style = VG.Style(VG_STROKE_LINE_WIDTH = 1.0,
                          fill_paint = red_paint)
    
    running = True
    while running:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        VG.clear((0, 0), (width, height))
        VG.load_identity()
        VG.translate(100, 300)
        
        text.draw(VG_STROKE_PATH | VG_FILL_PATH)

        
        pygame.display.flip()

if __name__ == '__main__':
    main(640, 480, "Hello, world!")