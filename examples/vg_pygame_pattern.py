import pygame
import xml.etree.ElementTree as ET

from OpenVG import VG
from OpenVG.svg import load_svg_element
from OpenVG.constants import *

RGBA_masks = (-16777216, 16711680, 65280, 255)

def load_image(path):
    surf = pygame.image.load(path).convert(RGBA_masks)

    im = VG.Image(VG_sRGBA_8888, surf.get_size())
    im.sub_data(surf.get_buffer(),
                VG_sRGBA_8888, surf.get_pitch(),
                (0,0), surf.get_size(),
                flip=True)

    return im

def main(width, height, path, flags=0):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 2)

    flags |= pygame.OPENGL | pygame.DOUBLEBUF
    
    screen = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption("Pygame Pattern Test")
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    im = load_image(path)
    pattern_paint = VG.PatternPaint(im)
    pattern_paint.tiling_mode = VG_TILE_REPEAT

    tree = ET.parse("data/donkoose.svg")
    shape = load_svg_element(tree.getroot())

    p = shape.children[0].children[0]
    p.paint_mode = VG_STROKE_PATH | VG_FILL_PATH
    p.style.fill_paint = pattern_paint

    (x,y), (w, h) = shape.bounds()

    dest_x = (width-w)/2.0
    dest_y = (height-h)/2.0
    scale = 1.0
    dragging = False
    
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
                if e.button == 1:
                    dragging = True
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    dragging = False
            elif e.type == pygame.MOUSEMOTION:
                if dragging:
                    dest_x += e.rel[0]
                    dest_y -= e.rel[1]

        VG.clear((0, 0), (width, height))
        
        VG.load_identity()
        VG.scale(scale, scale)
        VG.translate(dest_x/scale, dest_y/scale)
        
        shape.draw()

        pygame.display.flip()

if __name__ == '__main__':
    main(640, 480, "data/wood-texture.png")
