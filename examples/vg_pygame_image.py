from __future__ import with_statement

import pygame

from OpenVG import VG
from OpenVG.constants import *

def load_image(path):
    surf = pygame.image.load(path).convert_alpha()

    data = surf.get_buffer().raw
    
    im = VG.Image(VG_sRGBA_8888, surf.get_size())
    im.sub_data(data,
                surf.get_pitch(), VG_lARGB_8888,
                (0,0), surf.get_size(),
                flip=True)

    return im

def main(width, height, path, flags=0):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)

    flags |= pygame.OPENGL | pygame.DOUBLEBUF
    
    screen = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption("Pygame Image Test")
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    im = load_image(path)
    
    running = True
    while running:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        VG.clear((0, 0), (width, height))
        
        VG.set(VG_MATRIX_MODE, VG_MATRIX_IMAGE_USER_TO_SURFACE)
        VG.load_identity()
        
        VG.translate((width-im.width)/2.0, (height-im.height)/2.0)

        im.draw()
        
        pygame.display.flip()

if __name__ == '__main__':
    main(640, 480, "data/donkoose.jpg")
