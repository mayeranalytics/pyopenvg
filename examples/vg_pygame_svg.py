from __future__ import with_statement

import pygame
import xml.etree.ElementTree as ET

from OpenVG import VG
from OpenVG.constants import *

from svg import group_from_element

def main(width, height, paths):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    srf = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("SVG test")
    
    
    VG.create_context((640, 480))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    g_tag = "{http://www.w3.org/2000/svg}g"
    groups = []
    for svg_path in paths:
        groups.append(group_from_element(ET.parse(svg_path).find(g_tag)))


    dragging = False
    dx = dy = 0
    scale = 0
    
    running = True
    while running:
##        VG.translate(-width/2.0, -height/2.0)
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    dragging = True
                elif e.button == 4: #scroll up
                    mx, my = pygame.mouse.get_pos()
                    mx = (mx - dx) * (1 - 2**(-1))
                    my = (-my - dy + height) * -(1 - 2**(-1))
                    print mx, my
                    VG.translate(-mx, -my)
                    scale += 1
                elif e.button == 5: #scroll down
                    mx, my = pygame.mouse.get_pos()
                    mx = (mx - dx) * (1 - 2**1)
                    my = (-my - dy + height) * -(1 - 2**1)
                    VG.translate(-mx, -my)
                    scale -= 1
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    dragging = False
            elif e.type == pygame.MOUSEMOTION:
                if dragging:
                    dx += e.rel[0]/2**scale
                    dy += e.rel[1]/2**scale

        VG.clear((0, 0), (width, height))

        VG.set(VG_MATRIX_MODE, VG_MATRIX_PATH_USER_TO_SURFACE)
        
        VG.mult_matrix([ 2**scale, 0,         0,
                         0,       -2**scale,  0,
                         0,        0,         1])
        VG.translate(dx, dy-height)
        
        
        for group in groups:
            group.draw()

        VG.load_identity()
        VG.finish()
        pygame.display.flip()

if __name__ == '__main__':
    main(640, 480, ["data/grid2.svg", "data/butterfly.svg"])
