from __future__ import with_statement

import pygame
import xml.etree.ElementTree as ET

from OpenVG import VG
from OpenVG.constants import *

from svg import group_from_element

def main():
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    srf = pygame.display.set_mode((640,480), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Butterfly SVG test")
    
    
    VG.create_context((640, 480))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    g = group_from_element(ET.parse("data/butterfly.svg").getroot()[0])
    
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
        VG.translate(160, 120)
        
        g.draw()
        
        pygame.display.flip()

if __name__ == '__main__':
    main()
    VG.destroy_context()