import os
import traceback

import numpy
import pygame

from OpenVG import VG
from OpenVG import VGU
from OpenVG.constants import *

from OpenVG.font import Font, register_font_finder
from OpenVG.svg import parse_svg

def main(width, height, directory):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 2)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("SVG Viewer")
    
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    register_font_finder(pygame.font.match_font)
    @register_font_finder
    def fallback_font(name):
        fname = pygame.font.get_default_font()
        return os.path.join(os.path.dirname(pygame.font.__file__), fname)

    vera = Font("data/fonts/Vera.ttf", 16)
    text = vera.build_path("Scroll to change svg files. Drag to see more.")

    drawings = []

    for root, dirs, files in os.walk(directory):
        for fname in files:
            if not fname.endswith(".svg"):
                continue
            path = os.path.join(root, fname)
            try:
                tree = parse_svg(path)
                name = vera.build_path(fname, 16)
                tree.getroot().fit(width, height)
                drawings.append((tree.getroot(), name))
            except:
                print "Error in loading %s" % path
                traceback.print_exc(0)
    
    dragging = False
    dx = dy = 0
    i = 0
    scale = 1
    
    drawing, name = drawings[0]
    (x,y), (w,h) = drawing.bounds()

    running = True
    while running:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_1:
                    scale = 1
                elif e.key == pygame.K_2:
                    scale = 2
                elif e.key == pygame.K_3:
                    scale = 3
                elif e.key == pygame.K_4:
                    scale = 4
                elif e.key == pygame.K_5:
                    scale = 5
                elif e.key == pygame.K_6:
                    scale = 6
                elif e.key == pygame.K_7:
                    scale = 7
                elif e.key == pygame.K_8:
                    scale = 8
                elif e.key == pygame.K_9:
                    scale = 9

                elif e.key == pygame.K_EQUALS:
                    i += 1
                    drawing, name = drawings[i % len(drawings)]
                    (x,y), (w,h) = drawing.bounds()
                elif e.key == pygame.K_MINUS:
                    i -= 1
                    drawing, name = drawings[i % len(drawings)]
                    (x,y), (w,h) = drawing.bounds()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1 or e.button == 2 or e.button == 3:
                    dragging = True
                else:
                    if e.button == 4:
                        i += 1
                    else:
                        i -= 1
                    drawing, name = drawings[i % len(drawings)]
                    (x,y), (w,h) = drawing.bounds()
                    
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1 or e.button == 2 or e.button == 3:
                    dragging = False
            elif e.type == pygame.MOUSEMOTION:
                if dragging:
                    dx += e.rel[0]/2.0**(scale-1)
                    dy -= e.rel[1]/2.0**(scale-1)

        VG.clear((0, 0), (width, height))

        
        VG.load_identity()

        VG.scale(2**(scale-1),2**(scale-1))
        VG.translate(width/2.0-w/2.0-x+dx, height/2.0-h/2.0-y+dy)

        drawing.draw()

        VG.load_identity()
        VG.translate(10, 10)
        text.draw(VG_FILL_PATH)
        VG.translate(text.bounds()[1][0]+10, 0)
        name.draw(VG_FILL_PATH)

        pygame.display.flip()

if __name__ == '__main__':
    main(800, 640, r"data\svg")
