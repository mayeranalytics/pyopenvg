from __future__ import with_statement

import pygame

from OpenVG import VG
from OpenVG import VGU
from OpenVG.constants import *


CYCLE_TIME = 4 * 1000

def circle(path, center, radius=16):
    VGU.ellipse(path, center, (radius*2, radius*2))

def main():
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    srf = pygame.display.set_mode((640,480), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Modification test")
    
    
    VG.create_context((640, 480))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    bezier = VG.Path()
    bezier.move_to((200,300))
    bezier.quad_to((400,50),(600,300))
    bezier.squad_to((1000,300))

    control_lines = VG.Path()
    control_circles = VG.Path()

    control_lines.move_to((200,300))
    control_lines.line_to((400,50))
    control_lines.line_to((600,300))
    control_lines.line_to((800,550))
    control_lines.line_to((1000,300))
    
    circle(control_circles, (200,300))
    circle(control_circles, (400,50))
    circle(control_circles, (600,300))
    circle(control_circles, (800,550))
    circle(control_circles, (1000,300))
    
    
    
    control_style = VG.Style(VG_STROKE_LINE_WIDTH = 4.0,
                             stroke_paint = VG.ColorPaint((0.5, 0.5, 0.5, 1.0)),
                             fill_paint = VG.ColorPaint((1.0, 1.0, 1.0, 1.0)))
    bezier.style = VG.Style(VG_STROKE_LINE_WIDTH = 4.0,
                            stroke_paint = VG.ColorPaint((1.0, 0.0, 0.0, 1.0)))

    clock = pygame.time.Clock()

    running = True
    forwards = True
    t = 0
    while running:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        VG.clear((0, 0), (640, 480))
        
        m = t/float(CYCLE_TIME)
        if forwards:
            bezier.modify(1, [(400,50+500*m, 600,300)])
            control_lines.modify(1, [(400,50+500*m)])
            control_circles.modify(4, [(400+16,50+500*m)])
            control_lines.modify(3, [(800,550-500*m)])
            control_circles.modify(12, [(800+16,550-500*m)])
        else:
            bezier.modify(1, [(400,550-500*m, 600,300)])
            control_lines.modify(1, [(400,550-500*m)])
            control_circles.modify(4, [(400+16,550-500*m)])
            control_lines.modify(3, [(800,50+500*m)])
            control_circles.modify(12, [(800+16,50+500*m)])

        VG.set(VG_MATRIX_MODE, VG_MATRIX_PATH_USER_TO_SURFACE)
        VG.load_identity()
        VG.scale(0.5, 0.5)

        bezier.draw(VG_STROKE_PATH)
        with control_style:
            control_lines.draw(VG_STROKE_PATH)
            control_circles.draw(VG_STROKE_PATH | VG_FILL_PATH)
        
        pygame.display.flip()
        
        t += clock.tick(60)
        if t > CYCLE_TIME:
            t -= CYCLE_TIME
            forwards = not forwards

if __name__ == '__main__':
    main()
    VG.destroy_context()
