import math
import random

import pygame

from OpenVG import VG
from OpenVG.font import Font
from OpenVG.svg import parse_svg
from OpenVG.constants import *



def main(width, height):
    pygame.init()

    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 2)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Flower test")
    
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (0.0, 0.0, 0.0, 1.0))

    vera = Font("data/Vera.ttf", 32)

    message = vera.build_path("Hold down LMB to create flowers")
    message.style = VG.Style(fill_paint=VG.ColorPaint((1.0, 1.0, 1.0, 0.7)))

    doc = parse_svg("data/flower.svg")
    
    flower = doc.getroot()
    (x,y), (w,h) = flower.bounds()
    cx,cy = x+w/2.0, y+h/2.0
    
    particles = []
    to_remove = []

    clock = pygame.time.Clock()
    dt = 0
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        if pygame.mouse.get_pressed()[0]:
            x,y = pygame.mouse.get_pos()
            m = random.randint(-60, 60)
            angle = random.randint(0,359)

            pos = (x-cx, height-y-cy)
            vel = (m*math.cos(math.radians(angle)),
                   m*math.sin(math.radians(angle)))
            rot = random.randint(-30, 30)
            scale = random.randint(8, 12)/10.0
            particles.append([pos, vel, random.randint(0,359), rot, scale])

        VG.clear((0,0), (width, height))
        
        for particle in particles:
            VG.load_identity()
            pos, vel, angle, rot, scale = particle
            VG.translate(pos[0]+cx, pos[1]+cy)
            VG.scale(scale, scale)
            VG.rotate(angle)
            VG.translate(-cx, -cy)
            flower.draw()

            particle[0] = (pos[0]+vel[0]*dt/1000.0,pos[1]+vel[1]*dt/1000.0)
            particle[2] += rot * dt/1000.0
            
            if particle[0][0] + w < 0 or particle[0][1] + h < 0:
                to_remove.append(particle)
            elif particle[0][0] - w > width or particle[0][1] - h > height:
                to_remove.append(particle)

        particles = [particle for particle in particles if particle not in to_remove]
        del to_remove[:]

        VG.load_identity()
        message.draw(VG_FILL_PATH)

        dt = clock.tick(30)
        pygame.display.flip()

if __name__ == "__main__":
    main(640, 480)
