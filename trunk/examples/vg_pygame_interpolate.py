import pygame
import xml.etree.ElementTree as ET

from OpenVG import VG
from OpenVG.constants import *

from OpenVG.svg import load_svg_element

MORPH_TIME = 1 * 1000

def main(width, height):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 2)
    srf = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Interpolation test")
    
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    paths = []
    path_tag = "{http://www.w3.org/2000/svg}path"

    VG.set(VG_MATRIX_MODE, VG_MATRIX_PATH_USER_TO_SURFACE)
    VG.scale(5.0, 5.0)
    for element in ET.parse("data/shapes.svg").findall(path_tag):
        svg_path = load_svg_element(element)
        p = svg_path.path.transform()
        p.style = svg_path.style
        if not p.style:
            p.style = VG.Style(VG_STROKE_LINE_WIDTH=5.0)
        else:
            p.style[VG_STROKE_LINE_WIDTH] *= 2
        paths.append(p)

    VG.load_identity()

    morph = VG.Path()
    start = paths[0]
    end = paths[1]
    morph.style = start.style

    VG.set(VG_MATRIX_MODE, VG_MATRIX_PATH_USER_TO_SURFACE)
    VG.translate(220, 140)

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
        VG.interpolate(start, end, morph, dt/float(MORPH_TIME))

        morph.draw(VG_STROKE_PATH)
        
        pygame.display.flip()

        dt += clock.tick(60)
        if dt >= MORPH_TIME:
            dt -= MORPH_TIME
            i += 1
            start = paths[i % len(paths)]
            end = paths[(i+1) % len(paths)]
            morph.style = start.style

if __name__ == '__main__':
    main(640, 480)
