import pygame
import xml.etree.ElementTree as ET

from OpenVG import VG
from OpenVG.constants import *

from OpenVG.svg import load_svg_element

MORPH_TIME = 1 * 1000

def main(width, height):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    srf = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Interpolation test")
    
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    paths = []
    for element in ET.parse("data/shapes.svg").getroot()[0]:
        svg_path = load_svg_element(element)
        svg_path.path.style = svg_path.style
        paths.append(svg_path.path)

    morph = VG.Path()

    clock = pygame.time.Clock()

    running = True
    dt = 0
    i = 0
    while running:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        VG.clear((0, 0), (width, height))
        morph.clear()

        start = paths[i % len(paths)]
        end = paths[(i+1) % len(paths)]
        
        VG.interpolate(start, end, morph, dt/float(MORPH_TIME))

        morph.style = paths[i % len(paths)].style
        morph.style[VG_STROKE_LINE_WIDTH] = 0.5

        VG.set(VG_MATRIX_MODE, VG_MATRIX_PATH_USER_TO_SURFACE)
        VG.load_identity()
        VG.translate(220, 140)
        VG.scale(10.0, 10.0)

        morph.draw(VG_STROKE_PATH)
        
        pygame.display.flip()
        dt += clock.tick(60)
        if dt >= MORPH_TIME:
            dt -= MORPH_TIME
            i += 1

if __name__ == '__main__':
    main(640, 480)
