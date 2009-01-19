import math

import pygame
import pymunk

from OpenVG import VG
from OpenVG import VGU
from OpenVG.constants import *

from OpenVG.svg import parse_svg

class MoonWorld(object):
    terrain_data = [
        660.00, 660.00, 660.00, 660.00, 673.21, 688.42, 694.56, 692.55,
        685.40, 676.12, 667.75, 662.45, 658.93, 655.42, 650.17, 641.49,
        627.92, 610.08, 589.01, 565.71, 541.23, 516.58, 492.56, 469.57,
        447.97, 428.13, 410.60, 397.25, 392.66, 394.89, 400.70, 406.82,
        410.93, 413.87, 416.91, 421.30, 428.24, 436.05, 440.41, 437.09,
        421.93, 394.41, 355.57, 308.78, 257.99, 207.18, 160.31, 120.81,
        89.20, 65.17, 48.43, 38.67, 36.68, 45.03, 64.17, 92.26, 128.76,
        173.27, 224.20, 278.84, 334.48, 388.43, 438.31, 483.95, 525.96,
        564.95, 601.54, 633.88, 655.05, 665.87, 667.79, 662.25, 650.01,
        629.92, 604.68, 577.50, 551.55, 529.69, 512.49, 502.04, 500.20,
        502.72, 508.57, 518.31, 531.15, 545.99, 561.70, 577.30, 593.74,
        610.97, 628.13, 644.35, 658.81, 672.13, 684.78, 696.72, 708.00,
        718.65, 728.17, 736.14, 742.62, 747.63, 751.20, 752.58, 750.20,
        743.02, 730.05, 709.98, 682.99, 651.49, 616.61, 579.47, 541.18,
        503.87, 471.12, 444.10, 423.86, 411.44, 407.95, 414.29, 430.28,
        453.64, 482.36, 514.10, 545.66, 577.48, 610.42, 645.32, 682.66,
        719.61, 754.76, 787.26, 816.26, 840.95, 861.10, 876.94, 888.71,
        896.61, 900.84, 900.46, 894.59, 882.69, 864.24, 838.69, 805.77,
        765.56, 718.19, 670.07, 626.07, 586.87, 551.65, 518.20, 484.33,
        447.81, 408.39, 367.51, 324.70, 279.44, 231.25, 181.20, 134.59,
        96.96, 66.40, 40.75, 18.74, 1.97, -8.96, -13.56, -11.33, -2.28,
        11.64, 29.88, 52.04, 78.07, 108.53, 139.94, 171.90, 204.54,
        238.00, 272.25, 305.61, 336.90, 365.19, 389.61, 409.28, 424.38,
        434.79, 438.85, 437.12, 431.08, 422.77, 412.26, 398.92, 382.10,
        361.16, 336.82, 311.06, 285.61, 262.18, 242.50
        ]
    def __init__(self, g=-980.0):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, g)
        
        self.space.resize_static_hash(50.0, 2000)
        self.space.resize_active_hash(50.0, 100)

        self.ground = pymunk.Body(pymunk.inf, pymunk.inf)
        self.ground_path = VG.Path(capabilities=VG_PATH_CAPABILITY_APPEND_TO)
        
        last_point = (0.0, self.terrain_data[0])
        self.ground_path.move_to(last_point)
        for i in xrange(1, len(self.terrain_data)):
            point = (i*75.0, self.terrain_data[i])
            
            segment = pymunk.Segment(self.ground, last_point, point, 0.0)
            segment.friction = 1.0
            self.space.add_static(segment)

            self.ground_path.line_to(point)
            last_point = point

        self.ground_path.vline_to(min(self.terrain_data))
        self.ground_path.hline_to(0.0)
        self.ground_path.close()

        self.ground_path.style = VG.Style(fill_paint=VG.ColorPaint((0.8,0.8,1.0)))

        self.buggy = MoonBuggy(self.space, (100, 800))

    def update(self, substeps=3):
        dt = (1.0/60.0) / substeps

        for i in xrange(substeps):
            self.buggy.reset_forces()
            self.buggy.update(dt)

            self.space.step(dt)

    def draw(self):
        self.ground_path.draw(VG_STROKE_PATH | VG_FILL_PATH)
        self.buggy.draw()

class MoonBuggy(object):
    def __init__(self, space, pos):
        self.input_power = 0.0

        doc = parse_svg("data/openvg.svg")

        svg_logo = doc.find(".//{http://www.w3.org/2000/svg}path")
        
        logo = svg_logo.path
        logo.style = svg_logo.style
        (x, y), (width, height) = logo.bounds()
        self.chassis_path = VG.Path()
        VGU.rect(self.chassis_path, (x-width/2.0, y-height/2.0), (width, height))
        VG.load_matrix([1,  0,      0,
                        0, -1,      0,
                        -width/2.0+x, height/2.0+y, 1])
        logo.transform(self.chassis_path)
        
        del logo
        del svg_logo
        del doc
        
        VG.load_identity()
        
        chassis_mass = 5.0
        vertices = [(width, 0), (width, height),
                    (0,  height), (0, 0)]
##        vertices = [(x, y), (x, y + height), (x + width, y + height), (x + width, y)]
        print vertices

        chassis_moment = pymunk.moment_for_poly(chassis_mass, vertices, (-x-width/2.0,-y-height/2.0))

        chassis_body = pymunk.Body(chassis_mass, chassis_moment)
        chassis_body.position = pos
        space.add(chassis_body)

        self.wheel_offset_x = width/2.0
        self.wheel_offset_y = height/2.0

        wheel_radius = 15.0
        wheel_mass = 1.0
        wheel_moment = pymunk.moment_for_circle(wheel_mass, wheel_radius, 0.0, (0,0))
        
        wheel1_body = pymunk.Body(wheel_mass, wheel_moment)
        wheel2_body = pymunk.Body(wheel_mass, wheel_moment)
        
        wheel1_body.position = (pos[0]-self.wheel_offset_x, pos[1]-self.wheel_offset_y)
        wheel2_body.position = (pos[0]+self.wheel_offset_x, pos[1]-self.wheel_offset_y)
        space.add(wheel1_body, wheel2_body)

        space.add(pymunk.PinJoint(chassis_body, wheel1_body, (0,0), (0,0)))
        space.add(pymunk.PinJoint(chassis_body, wheel2_body, (0,0), (0,0)))

        self.chassis = pymunk.Poly(chassis_body, vertices, (-x-width/2.0,-y-height/2.0))
        self.chassis.friction = 0.5
        self.chassis.offset = (-x-width/2.0,-y-height/2.0)
        space.add(self.chassis)

        self.wheel1 = pymunk.Circle(wheel1_body, wheel_radius, (0,0))
        self.wheel1.friction = 1.5
        space.add(self.wheel1)

        self.wheel2 = pymunk.Circle(wheel2_body, wheel_radius, (0,0))
        self.wheel2.friction = 1.5
        space.add(self.wheel2)

        self.wheel_path = VG.Path()
        VGU.ellipse(self.wheel_path, (0,0), (wheel_radius/2.0,wheel_radius/2.0))
        VGU.ellipse(self.wheel_path, (0,0), (wheel_radius*2.0,wheel_radius*2.0))
        VGU.ellipse(self.wheel_path, (wheel_radius-wheel_radius/4.0,0.0), (wheel_radius/8.0,wheel_radius/8.0))

        white_paint = VG.ColorPaint((1.0, 1.0, 1.0))
        grey_paint = VG.ColorPaint((0.5, 0.5, 0.5))
        black_paint = VG.ColorPaint((0.0, 0.0, 0.0))
        self.chassis_path.style = VG.Style(fill_paint=black_paint,
                                           stroke_paint=black_paint)

        self.wheel_path.style = VG.Style(fill_paint=grey_paint,
                                         stroke_paint=black_paint)

    def reset_forces(self):
        self.chassis.body.reset_forces()
        self.wheel1.body.reset_forces()
        self.wheel2.body.reset_forces()

    def update(self, dt):
        max_w = -100.0
        torque = 60000.0 * min((self.wheel1.body.angular_velocity - self.input_power*max_w)/max_w, 1.0)

        self.wheel1.body.torque += torque
        self.chassis.body.torque -= torque

        self.chassis.body.damped_spring(self.wheel1.body,
                                        (-self.wheel_offset_x, self.wheel_offset_x), (0,0), 140.0, 400.0, 15.0, dt)
        self.chassis.body.damped_spring(self.wheel2.body,
                                        ( self.wheel_offset_x, self.wheel_offset_x), (0,0), 140.0, 400.0, 15.0, dt)

    def draw(self):
        mat = VG.get_matrix()
        VG.translate(*self.chassis.body.position)
        VG.rotate(math.degrees(self.chassis.body.angle))

##        self.chassis_path.draw(VG_STROKE_PATH | VG_FILL_PATH)

        VG.load_matrix(mat)
        p = VG.Path()
        points = self.chassis.get_points()
        p.move_to(points[0]+self.chassis.offset)
        for point in points[1:]:
            p.move_to(point+self.chassis.offset)
        p.close()

        p.style = VG.Style(fill_paint=VG.ColorPaint((1.0, 0.0,0.0)))
        p.draw(VG_FILL_PATH)

        VG.load_matrix(mat)
        VG.translate(*self.wheel1.body.position)
        VG.rotate(math.degrees(self.wheel1.body.angle))
        self.wheel_path.draw(VG_STROKE_PATH | VG_FILL_PATH)

        VG.load_matrix(mat)
        VG.translate(*self.wheel2.body.position)
        VG.rotate(math.degrees(self.wheel2.body.angle))
        self.wheel_path.draw(VG_STROKE_PATH | VG_FILL_PATH)

        VG.load_matrix(mat)


if __name__ == "__main__":
    pygame.init()
    pymunk.init_pymunk()

    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 2)

    screen = pygame.display.set_mode((640, 480), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("VG Moon Buggy Demo")

    VG.create_context((640, 480))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    world = MoonWorld()
    low_point = min(world.terrain_data)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        left_down, middle_down, right_down = pygame.mouse.get_pressed()
        world.buggy.input_power = 1.0 * (left_down - right_down)

        world.update()

        VG.clear((0,0), (640,480))
        VG.load_identity()
        pos = world.buggy.chassis.body.position
        VG.translate(-pos[0] + 300, min(-pos[1] + 200, -low_point))

        world.draw()
        
        pygame.display.flip()
        clock.tick(60)
