from __future__ import with_statement

import pygame

from OpenVG import VG
from OpenVG import VGU
from OpenVG.constants import *


def main():
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 16)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    srf = pygame.display.set_mode((640,480), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Paint test")
    
    
    VG.create_context((640, 480))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))
    VG.set(VG_STROKE_LINE_WIDTH, 3.0)

    p = VG.Path(capabilities=VG_PATH_CAPABILITY_APPEND_TO)
    VGU.ellipse(p, (0, 0), (64*2,64*2))

    solid_paint = VG.ColorPaint((1.0, 0.0, 1.0))

    stops = [(0.0,(1.0,1.0,1.0,1.0)), (0.333,(1.0,0.0,0.0,1.0)), (0.666,(0.0,1.0,0.0,1.0)), (1.0,(0.0,0.0,1.0,1.0))]

    linear_gradient = [(-60,0), (60,0)]
    linear_paint = VG.GradientPaint(linear_gradient, linear=True)
    linear_paint.spread_mode = VG_COLOR_RAMP_SPREAD_REFLECT
    linear_paint.stops = stops

    radial_gradient = [(0,0), (0,0), 64]
    radial_paint = VG.GradientPaint(radial_gradient, linear=False)
    radial_paint.stops = stops


    running = True
    while running:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        VG.clear((0, 0), (640, 480))
        
        VG.set(VG_MATRIX_MODE, VG_MATRIX_PATH_USER_TO_SURFACE)
        VG.load_identity()

        VG.translate(68, 240-64)
        VG.set_paint(solid_paint, VG_FILL_PATH)
        p.draw(VG_STROKE_PATH | VG_FILL_PATH)

        VG.translate(192, 0)
        VG.set_paint(linear_paint, VG_FILL_PATH)
        p.draw(VG_STROKE_PATH | VG_FILL_PATH)

        VG.translate(192, 0)
        VG.set_paint(radial_paint, VG_FILL_PATH)
        p.draw(VG_STROKE_PATH | VG_FILL_PATH)
        
        pygame.display.flip()

if __name__ == '__main__':
    main()
