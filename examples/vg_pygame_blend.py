from __future__ import with_statement

import math
import pygame

from OpenVG import VG
from OpenVG import VGU
from OpenVG.font import Font
from OpenVG.constants import *

def center_and_concat(p1, p2):
    (dx, dy), (dw, dh) = p1.bounds()
    (sx, sy), (sw, sh) = p2.bounds()

    dst_cx, dst_cy = (dx+dw/2.0), (dy+dh/2.0)
    src_cx, src_cy = (sx+sw/2.0), (sy+sh/2.0)

    VG.translate(dst_cx-src_cx, dst_cy-src_cy)
    p2.transform(p1)
    VG.load_identity()
    

def main(width, height, radius, count, flags=0):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)

    flags |= pygame.OPENGL | pygame.DOUBLEBUF
    
    srf = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption("Blending test")
    
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    orange_paint = VG.ColorPaint((1.0, 0.5, 0.0, 0.5))
    blue_paint = VG.ColorPaint((0.0, 0.0, 1.0, 0.5))
    black_paint = VG.ColorPaint((0.0, 0.0, 0.0))

    blend_modes = [VG_BLEND_SRC, VG_BLEND_SRC_OVER, VG_BLEND_DST_OVER,
                   VG_BLEND_SRC_IN, VG_BLEND_DST_IN, VG_BLEND_MULTIPLY,
                   VG_BLEND_SCREEN, VG_BLEND_DARKEN, VG_BLEND_LIGHTEN,
                   VG_BLEND_ADDITIVE]

    blend_index = 0
    
    VG.set(VG_BLEND_MODE, blend_modes[0])

    font = Font("data/Vera.ttf", 30)
    src_path = font.build_path("SRC")
    dst_path = font.build_path("DST")
    message = font.build_path("Scroll to change the blend mode")
    
    circle = VG.Path()
    VGU.ellipse(circle, (0, 0), (radius*2, radius*2))
    center_and_concat(circle, dst_path)

    square = VG.Path()
    VGU.rect(square, (-radius, -radius), (radius*2, radius*2))
    center_and_concat(square, src_path)

    circle2 = VG.Path()
    VGU.ellipse(circle2, (0, 0), (radius*2, radius*2))

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
                    blend_index += 1
                    VG.set(VG_BLEND_MODE, blend_modes[blend_index % len(blend_modes)])
                elif e.button == 5:
                    blend_index -= 1
                    VG.set(VG_BLEND_MODE, blend_modes[blend_index % len(blend_modes)])

        VG.clear((0, 0), (width, height))
        
        VG.set(VG_MATRIX_MODE, VG_MATRIX_PATH_USER_TO_SURFACE)
        VG.load_identity()
        VG.translate(width - radius*1.5, radius * 2.5)
        circle.draw(VG_FILL_PATH | VG_STROKE_PATH)
        VG.translate(-radius, -radius)
        VG.set_paint(orange_paint, VG_FILL_PATH)
        square.draw(VG_FILL_PATH | VG_STROKE_PATH)

        VG.set_paint(blue_paint, VG_FILL_PATH)
        for i in xrange(count):
            angle = i*2*math.pi/count
            VG.load_identity()
            VG.translate(width//2, height//2)
            VG.translate(radius*math.cos(angle), radius*math.sin(angle))
            circle2.draw(VG_FILL_PATH)

        VG.load_identity()
        (x,y), (w,h) = message.bounds()
        VG.translate(-x, height-y-h)
        message.draw(VG_STROKE_PATH | VG_FILL_PATH)
        

        
        pygame.display.flip()

if __name__ == '__main__':
    main(640, 480, 64, 6)
