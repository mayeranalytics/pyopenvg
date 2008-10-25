import colorsys
import math

import pygame

from OpenVG import VG
from OpenVG import VGU
from OpenVG.constants import *

def generate_rgb_stops(n):
    stops = []
    for i in xrange(n):
        r,g,b = colorsys.hsv_to_rgb(i/(n-1.0), 1.0, 1.0)
        stops.append((i/(n-1.0), (r, g, b, 1.0)))
    return stops

def main(width, height):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 2)
    srf = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Rainbow Gradient Test")

    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    canvas = VG.Path(capabilities=VG_PATH_CAPABILITY_APPEND_TO)
    VGU.rect(canvas, (0, 0), (width, height))
     
    rgb_gradient = VG.GradientPaint([(0,0), (width,0)], linear=True)
    rgb_gradient.spread_mode = VG_COLOR_RAMP_SPREAD_REFLECT
    rgb_gradient.stops = generate_rgb_stops(7)

    alpha_stops = [(0.0, (0.0, 0.0, 0.0, 0.0)),
                   (1.0, (1.0, 1.0, 1.0, 1.0))]

    alpha_gradient = VG.GradientPaint([(0,0), (0,height)], linear=True)
    alpha_gradient.spread_mode = VG_COLOR_RAMP_SPREAD_REFLECT
    alpha_gradient.stops = alpha_stops

    n = 7

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
                if e.button == 4:
                    n += 1
                    rgb_gradient.stops = generate_rgb_stops(n)
                elif e.button == 5:
                    if n > 2:
                        n -= 1
                        rgb_gradient.stops = generate_rgb_stops(n)

        VG.clear((0, 0), (640, 480))
        VG.set_paint(rgb_gradient, VG_FILL_PATH)
        canvas.draw(VG_FILL_PATH)

        VG.set_paint(alpha_gradient, VG_FILL_PATH)
        canvas.draw(VG_FILL_PATH)
        
        pygame.display.flip()

if __name__ == '__main__':
    main(640, 480)
