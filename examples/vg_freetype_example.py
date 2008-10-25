import pygame

from OpenVG import VG
from OpenVG.font import Font
from OpenVG.constants import *


def rotate_about(p, angle):
    VG.translate(p[0], p[1])
    VG.rotate(angle)
    VG.translate(-p[0], -p[1])

def main(width, height, message, rpm=20):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 2)
    srf = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Freetype Font test")
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    font = Font("data/Vera.ttf", 64)

    red_paint = VG.ColorPaint((1.0, 0.0, 0.0, 1.0))
    text = font.build_path(message)
    (x, y), (w, h) = text.bounds()

    text.style = VG.Style(VG_STROKE_LINE_WIDTH = 1.0,
                          fill_paint = red_paint)

    clock = pygame.time.Clock()
    dt = 0

    cx = width/2.0 - w/2.0
    cy = height/2.0 - h/2.0
    
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
                pos = e.pos
                cx = pos[0]  - w/2.0
                cy = height-pos[1]  - h/2.0

        VG.clear((0, 0), (width, height))
        VG.load_identity()

        VG.translate(cx, cy)
        rotate_about((x+w/2.0, y+h/2.0), dt*360.0*rpm / (60*1000.0))

        text.draw(VG_STROKE_PATH | VG_FILL_PATH)
        
        pygame.display.flip()
        dt += clock.tick(60)
        

if __name__ == '__main__':
    main(640, 480, "Hello, world!")
