import glob

import pygame
import xml.etree.ElementTree as ET

from OpenVG import VG
from OpenVG.constants import *

from OpenVG.font import Font
from OpenVG.svg import load_svg_element

def main(width, height):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("SVG test")
    
    
    VG.create_context((640, 480))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    vera = Font("data/Vera.ttf", 16)
    text = vera.build_path("Scroll to change svg files. Drag to see more.")

    svg_tag = "{http://www.w3.org/2000/svg}svg"
    drawings = []
    for path in glob.glob("data/*.svg"):
        tree = ET.parse(path)
        element = tree.getroot()
        if element:
            drawings.append(load_svg_element(element))

    dragging = False
    i = 0

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
                if e.button == 1 or e.button == 2 or e.button == 3:
                    dragging = True
                else:
                    if e.button == 4:
                        i += 1
                    else:
                        i -= 1
                    
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1 or e.button == 2 or e.button == 3:
                    dragging = False
            elif e.type == pygame.MOUSEMOTION:
                if dragging:
                    VG.translate(e.rel[0], -e.rel[1])

        VG.clear((0, 0), (width, height))
        drawings[i % len(drawings)].draw()

        VG.translate(10, 10)
        text.draw(VG_FILL_PATH)
        VG.translate(-10, -10)

        pygame.display.flip()

if __name__ == '__main__':
    main(640, 480)
