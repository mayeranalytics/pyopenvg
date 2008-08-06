from __future__ import with_statement

import pygame

from OpenGL.GL import *
from OpenVG import VG
from OpenVG.constants import *

def main():
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 16)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    srf = pygame.display.set_mode((640,480), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Polyline test")
    
    VG.create_context((640, 480))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    polyline = VG.Path()
    stroke_paint = VG.ColorPaint((0.5, 0.2, 0.8, 0.6))
    VG.set_paint(stroke_paint, VG_STROKE_PATH)

    fill_paint = VG.ColorPaint((0.3, 1.0, 0.0, 0.6))
    VG.set_paint(fill_paint, VG_FILL_PATH)

    stroke_style = VG.Style(VG_STROKE_LINE_WIDTH = 4.0,
                            VG_STROKE_JOIN_STYLE = VG_JOIN_MITER,
                            VG_STROKE_CAP_STYLE = VG_CAP_ROUND)

    print "Usage"
    print "Left click: LINE_TO"
    print "Right click: MOVE_TO"
     
    running = True
    first_click = True
    while running:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                    
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1: #left button
                    if first_click:
                        polyline.move_to((e.pos[0], 480-e.pos[1]), rel=False)
                        first_click = False
                    else:
                        polyline.line_to((e.pos[0], 480-e.pos[1]), rel=False)
                elif e.button == 3:#right button
                    polyline.move_to((e.pos[0], 480-e.pos[1]), rel=False)

        VG.clear((0, 0), (640, 480))

#uncomment if no with statement
##        VG.set(VG_STROKE_LINE_WIDTH, 4.0)
##        VG.set(VG_STROKE_JOIN_STYLE, VG_JOIN_MITER)
##        VG.set(VG_STROKE_CAP_STYLE, VG_CAP_ROUND)

        with stroke_style:
            polyline.draw(VG_STROKE_PATH)

        pygame.display.flip()

if __name__ == '__main__':
    main()
