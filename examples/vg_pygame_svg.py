from __future__ import with_statement

import pygame
import re

from OpenGL.GL import *
from OpenVG import VG
from OpenVG.constants import *

command_table = dict(M=VG_MOVE_TO_ABS, m=VG_MOVE_TO_REL,
                     Z=VG_CLOSE_PATH, z=VG_CLOSE_PATH,
                     L=VG_LINE_TO_ABS, l=VG_LINE_TO_REL,
                     H=VG_HLINE_TO_ABS, h=VG_HLINE_TO_REL,
                     V=VG_VLINE_TO_ABS, v=VG_VLINE_TO_REL,
                     C=VG_CUBIC_TO_ABS, c=VG_CUBIC_TO_REL,
                     S=VG_SCUBIC_TO_ABS, s=VG_SCUBIC_TO_REL,
                     Q=VG_QUAD_TO_ABS, q=VG_QUAD_TO_REL,
                     T=VG_SQUAD_TO_ABS, t=VG_SQUAD_TO_REL)

quad_string = "M200,300 Q400,50 600,300 T1000,300"
control_string = "M200,300 L400,50 L600,300 L800,550 L1000,300"


svg_pattern = re.compile(r"([MZLHVCSQTA])([^MZLHVCSQTA]+)(?:\s|$)", re.IGNORECASE)
def parse_path_string(data):
    segments = []
    for command, args in svg_pattern.findall(data):
        vg_command = command_table[command]
        coords = map(float, re.split(r"(?:,| )", args))
        segments.append((vg_command, coords))
    return segments

def path_from_string(s):
    segments = parse_path_string(s)

    p = VG.Path()
    p.extend(segments)
    p.close()
    return p

def main():
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 16)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    srf = pygame.display.set_mode((640,480), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Polyline test")
    
    
    VG.create_context((640, 480))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    control = path_from_string(control_string)
    quad = path_from_string(quad_string)

    red_paint = VG.ColorPaint((1.0, 0.0, 0.0, 1.0))
    grey_paint = VG.ColorPaint((0.5, 0.5, 0.5, 1.0))

    svg_style = VG.Style(VG_STROKE_LINE_WIDTH = 5.0,
                         VG_STROKE_JOIN_STYLE = VG_JOIN_MITER,
                         VG_STROKE_CAP_STYLE = VG_CAP_BUTT)
                          
                          

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

        VG.scale(0.4, 0.4)
        VG.translate(320, 240)
        with svg_style:
            quad.draw(VG_STROKE_PATH, red_paint)
            control.draw(VG_STROKE_PATH, grey_paint)
        
        pygame.display.flip()

if __name__ == '__main__':
    main()
