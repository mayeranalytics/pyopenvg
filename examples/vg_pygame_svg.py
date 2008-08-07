from __future__ import with_statement

import pygame

from OpenGL.GL import *
from OpenVG import VG
from OpenVG.constants import *

from svg import parse_path_string

comm_table = {VG_CLOSE_PATH:"VG_CLOSE_PATH",
              VG_MOVE_TO:"VG_MOVE_TO",
              VG_LINE_TO:"VG_LINE_TO",
              VG_HLINE_TO:"VG_HLINE_TO",
              VG_VLINE_TO:"VG_VLINE_TO",
              VG_QUAD_TO:"VG_QUAD_TO",
              VG_CUBIC_TO:"VG_CUBIC_TO",
              VG_SQUAD_TO:"VG_SQUAD_TO",
              VG_SCUBIC_TO:"VG_SCUBIC_TO"}
def pprint_segments(segments):
    for command, args in segments:
        rel = command % 2
        if rel:
            print (comm_table[command - rel] + "_REL"), args
        else:
            print (comm_table[command - rel] + "_ABS"), args

def path_from_string(data):
    segments = parse_path_string(data)
    pprint_segments(segments)
    p = VG.Path()
    p.extend(segments)
    return p

quad_string = "M200 300 Q400 50 600 300 T1000 300"
control_string = "M200 300 L400 50 L600 300 L800 550 L1000 300"

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

    control_style = VG.Style(VG_STROKE_LINE_WIDTH = 5.0,
                             VG_STROKE_JOIN_STYLE = VG_JOIN_MITER,
                             VG_STROKE_CAP_STYLE = VG_CAP_BUTT,
                             VG_STROKE_PATH = grey_paint)
    quad_style = VG.Style(VG_STROKE_LINE_WIDTH = 5.0,
                          VG_STROKE_JOIN_STYLE = VG_JOIN_MITER,
                          VG_STROKE_CAP_STYLE = VG_CAP_BUTT,
                          VG_STROKE_PATH = red_paint)
    
                          
                          

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
        with quad_style:
            quad.draw(VG_STROKE_PATH)
        
        with control_style:
            control.draw(VG_STROKE_PATH)
        
        pygame.display.flip()

if __name__ == '__main__':
    main()
