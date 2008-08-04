import pygame
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenVG import VG
from OpenVG.constants import *

def main():
    pygame.init()

    srf = pygame.display.set_mode((640,480), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Pyn test")
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    
    VG.create_context((640, 480))
    VG.set(VG_CLEAR_COLOR, (0.0, 0.0, 0.0, 0.0))
    p = VG.Path()

    stroke_paint = VG.ColorPaint((0.5, 0.2, 0.8, 0.6))
    VG.set_paint(stroke_paint, VG_STROKE_PATH)

    fill_paint = VG.ColorPaint((0.3, 1.0, 0.0, 0.6))
    VG.set_paint(fill_paint, VG_FILL_PATH)

    fps = 30
    dt = 1.0/fps
    running = True
    clock = pygame.time.Clock()
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
                    p.line_to((e.pos[0]-320, 480-e.pos[1]-240), rel=False)
                elif e.button == 3:#right button
                    pass
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    pass
                elif e.button == 3:
                    pass
                elif e.button == 4: #scroll up
                    pass
                elif e.button == 5: #scroll down
                    pass
            elif e.type == pygame.MOUSEMOTION:
                pass

        VG.clear((0, 0), (640, 480))

        VG.set(VG_STROKE_DASH_PATTERN, (5, 10))
        VG.set(VG_STROKE_DASH_PHASE_RESET, True)
        VG.set(VG_STROKE_DASH_PHASE, 0.0)

        VG.set(VG_STROKE_LINE_WIDTH, 5.0)
        VG.set(VG_STROKE_JOIN_STYLE, VG_JOIN_MITER)
        VG.set(VG_STROKE_CAP_STYLE, VG_CAP_SQUARE)

        VG.set(VG_MATRIX_MODE, VG_MATRIX_PATH_USER_TO_SURFACE)

        VG.load_identity()
        VG.translate(320, 240)
##        p.draw(VG_FILL_PATH)
        p.draw(VG_STROKE_PATH)
        
        pygame.display.flip()
        clock.tick(fps)

if __name__ == '__main__':
    main()
