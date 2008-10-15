from __future__ import with_statement

import pygame

from OpenVG import VG
from OpenVG.constants import *

def make_mask(start, stop):
    x = 0
    for i in xrange(start, stop):
        x |= 1 << i
    return x

R = make_mask(0, 8)
G = make_mask(8, 16)
B = make_mask(16, 24)
A = ~(R | G | B)

RGBA_masks = (R, G, B, A)

def load_image(path):
    surf = pygame.image.load(path).convert(RGBA_masks)

    data = surf.get_buffer().raw

    im = VG.Image(VG_lRGBA_8888, surf.get_size())
    im.sub_data(data,
                surf.get_pitch(), VG_sRGBA_8888,
                (0,0), surf.get_size(),
                flip=True)

    return im

def main(width, height, path, flags=0):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)

    flags |= pygame.OPENGL | pygame.DOUBLEBUF
    
    screen = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption("Pygame Image Blit Test")
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    im = load_image(path)

    dest_x = (width-im.width)/2.0
    dest_y = (height-im.height)/2.0
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

        VG.blit(im, (dest_x, dest_y))

        pygame.display.flip()

if __name__ == '__main__':
    main(640, 480, "data/donkoose.jpg")