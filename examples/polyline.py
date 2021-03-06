import pygame

from OpenVG import VG
from OpenVG.constants import *

def main(width, height):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 2)
    srf = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Polyline test")
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    polyline = VG.Path()
    stroke_paint = VG.ColorPaint((0.5, 0.2, 0.8, 0.6))
    VG.set_paint(stroke_paint, VG_STROKE_PATH)

    fill_paint = VG.ColorPaint((0.3, 1.0, 0.0, 0.6))
    VG.set_paint(fill_paint, VG_FILL_PATH)

    polyline.style = VG.Style(VG_STROKE_LINE_WIDTH = 4.0,
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
                        polyline.move_to((e.pos[0], height-e.pos[1]), rel=False)
                        first_click = False
                    else:
                        polyline.line_to((e.pos[0], height-e.pos[1]), rel=False)
                elif e.button == 3:#right button
                    polyline.move_to((e.pos[0], height-e.pos[1]), rel=False)

        VG.clear((0, 0), (width, height))

        polyline.draw(VG_STROKE_PATH)

        pygame.display.flip()

if __name__ == '__main__':
    main(640, 480)
