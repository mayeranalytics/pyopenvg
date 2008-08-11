from __future__ import with_statement

import math

import pygame
import pymunk as pm

from OpenVG import VG, VGU
from OpenVG.constants import *

def setup(name, width, height, flags=pygame.DOUBLEBUF):
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 16)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)

    screen = pygame.display.set_mode((width, height), pygame.OPENGL | flags)
    pygame.display.set_caption(name)

    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))
    pm.init_pymunk()

    return screen

class StaticL(object):
    style = VG.Style(VG_STROKE_LINE_WIDTH = 2.0)
    def __init__(self, space, position, width, height):
        #    p1*
        #height|
        #      |
        #    p2*____________*___________*p3
        #        (width/2) pos (width/2)

        rotation_center_body = pm.Body(pm.inf, pm.inf) # 1
        rotation_center_body.position = position
        
        self.body = pm.Body(4500, 3 * 10**8)
        self.body.position = position

        rotation_center_joint = pm.PinJoint(self.body, rotation_center_body, (0,0), (0,0))

        p1 = (-width/2.0, height)
        p2 = (-width/2.0, 0.0)
        p3 = ( width/2.0, 0.0)

        self.l1 = pm.Segment(self.body, p2, p3, 2.0)
        self.l1.friction = 0.5
        self.l2 = pm.Segment(self.body, p1, p2, 2.0)
        self.l2.friction = 0.5
        
        space.add(self.l1, self.l2, self.body, rotation_center_joint)

        self.path = VG.Path()
        self.path.move_to((-width/2.0, height), rel=True)
        self.path.line_to((0.0, -height), rel=True)
        self.path.line_to((width, 0.0), rel=True)

    def draw(self):
        with self.style:
            VG.set(VG_MATRIX_MODE, VG_MATRIX_PATH_USER_TO_SURFACE)
            old_matrix = VG.get_matrix()
            
            VG.translate(*self.body.position)
            VG.rotate(math.degrees(self.body.angle))

            self.path.draw(VG_STROKE_PATH)
            VG.load_matrix(old_matrix)
            

class Ball(object):
    path_cache = {}
    smiley_style = VG.Style(
        VG_STROKE_LINE_WIDTH = 2.0,
        VG_STROKE_JOIN_STYLE = VG_JOIN_ROUND,
        VG_STROKE_CAP_STYLE = VG_CAP_ROUND)
    dash_style = smiley_style + VG.Style(
        VG_STROKE_DASH_PATTERN = (4,4),
        VG_STROKE_DASH_PHASE_RESET = True)
    
    def __init__(self, space, position, radius, density=1, smiley=False):
        mass = density * math.pi * radius**2
        inertia = pm.moment_for_circle(mass, 0, radius, (0,0))

        body = pm.Body(mass, inertia)
        body.position = position
        shape = pm.Circle(body, radius, (0,0))
        shape.friction = 0.5

        space.add(body, shape)

        self.body = body
        self.shape = shape
        self.smiley = smiley

    @property
    def path(self):
        r = self.shape.radius
        if (self.smiley, r) in Ball.path_cache:
            return Ball.path_cache[(self.smiley, r)]
        else:
            path = Ball.path_cache[(self.smiley, r)] = VG.Path()
            VGU.ellipse(path, (0, 0), (r*2,r*2))
            if self.smiley:
                VGU.ellipse(path, (-r/2.0, r/4.0), (r/4.0, r/4.0))
                VGU.ellipse(path, (r/2.0, r/4.0), (r/4.0, r/4.0))
                path.move_to((-r/2.0, -r/4.0))
                path.quad_to((0, -r/1.5), (r/2.0, -r/4.0))
                path.line_to((-r/2.0, -r/4.0))
            return path

    @property
    def style(self):
        return Ball.smiley_style if self.smiley else Ball.dash_style

    @property
    def fill_paint(self):
        color = (1.0, 1.0, 0.0, 1.0) if self.smiley else (1.0, 1.0, 1.0, 1.0)
        return VG.ColorPaint(color)

    def draw(self):
        VG.set(VG_MATRIX_MODE, VG_MATRIX_PATH_USER_TO_SURFACE)
        old_matrix = VG.get_matrix()
        
        VG.translate(*self.body.position)
        VG.rotate(math.degrees(self.body.angle))

        old_paint = VG.get_paint(VG_FILL_PATH)
        VG.set_paint(self.fill_paint, VG_FILL_PATH)

        with self.style:
            self.path.draw(VG_STROKE_PATH | VG_FILL_PATH)
            
        VG.set_paint(old_paint, VG_FILL_PATH)

        VG.load_matrix(old_matrix)

def main():
    WIDTH = 640
    HEIGHT = 480
    
    screen = setup("Pymunk + PyOpenVG test", WIDTH, HEIGHT, pygame.DOUBLEBUF | pygame.RESIZABLE)

    black = VG.ColorPaint((0.0, 0.0, 0.0, 1.0))
    white = VG.ColorPaint((1.0, 1.0, 1.0, 1.0))
    red = VG.ColorPaint((1.0, 0.0, 0.0, 1.0))
    yellow = VG.ColorPaint((1.0, 1.0, 0.0, 1.0))

    space = pm.Space()
    space.gravity = (0, -900)

    Ls = [StaticL(space, (300, 300), 200, 25),
          StaticL(space, (250, 150), 200, 25)] 

    balls = []
    running = True
    fps = 60
    multiplier = 1
    
    clock = pygame.time.Clock()

    while running:
        #Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif pygame.K_1 <= event.key <= pygame.K_3:
                    multiplier = event.key - pygame.K_0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = (event.pos[0], HEIGHT-event.pos[1])
                    balls.append(Ball(space, pos, 12*multiplier, smiley=True))
                elif event.button == 3:
                    pos = (event.pos[0], HEIGHT-event.pos[1])
                    balls.append(Ball(space, pos, 12*multiplier, smiley=False))

        #Update world
        space.step(1.0/fps)

        #Redraw
        VG.clear((0,0), (WIDTH, HEIGHT))

        for L in Ls:
            L.draw()

        offscreen = []
        for ball in balls:
            if ball.body.position.y < 0:
                offscreen.append(ball)
            elif ball.body.position.x < 0 or ball.body.position.x > WIDTH:
                offscreen.append(ball)
            else:
                ball.draw()

        for ball in offscreen:
            balls.remove(ball)


        pygame.display.flip()

        clock.tick(fps)
    



if __name__ == "__main__":
    main()

    
