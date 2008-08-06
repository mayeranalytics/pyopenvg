from __future__ import with_statement

from pyglet.gl import *
from pyglet import window

from OpenVG import VG
from OpenVG.constants import *

#Setup pyglet window -- it is crucial that you have a stencil buffer.

screen = window.get_platform().get_default_display().get_default_screen()

template = Config()
template.depth_size = 24
template.double_buffer = True
template.stencil_size = 16

config = screen.get_best_config(template)


# The OpenGL context is created only when you create a window.  Any calls
# to OpenGL before a window is created will fail.
win = window.Window(visible=False, config=config)

# ... perform any OpenGL state initialisation here.
context = VG.create_context((640, 480))

VG.set(VG_CLEAR_COLOR, (0.0, 0.0, 0.0, 1.0))
p = VG.Path()
segments = [(VG_MOVE_TO,     (  0, 50)),
            (VG_LINE_TO_REL, ( 15,-40)),
            (VG_LINE_TO_REL, ( 45,  0)),
            (VG_LINE_TO_REL, (-35,-20)),
            (VG_LINE_TO_REL, ( 15,-40)),
            (VG_LINE_TO_REL, (-40, 30)),
            (VG_LINE_TO_REL, (-40,-30)),
            (VG_LINE_TO_REL, ( 15, 40)),
            (VG_LINE_TO_REL, (-35, 20)),
            (VG_LINE_TO_REL, ( 45,  0)),
            (VG_CLOSE_PATH, ())]
p.extend(segments)
stroke_paint = VG.ColorPaint((0.5, 0.2, 0.8, 0.6))
VG.set_paint(stroke_paint, VG_STROKE_PATH)

fill_paint = VG.ColorPaint((0.3, 1.0, 0.0, 0.6))
VG.set_paint(fill_paint, VG_FILL_PATH)

stroke_style = VG.Style(VG_STROKE_DASH_PATTERN = (5, 10),
                        VG_STROKE_DASH_PHASE_RESET = True,
                        VG_STROKE_DASH_PHASE = 0.0,

                        VG_STROKE_LINE_WIDTH = 5.0,
                        VG_STROKE_JOIN_STYLE = VG_JOIN_MITER,
                        VG_STROKE_CAP_STYLE = VG_CAP_ROUND)

win.set_visible()
while not win.has_exit:
    win.dispatch_events()
    VG.clear((0, 0), (640, 480))

    VG.set(VG_MATRIX_MODE, VG_MATRIX_PATH_USER_TO_SURFACE)
    VG.load_identity()
    VG.translate(320, 240)
    VG.scale(3.0, 3.0)

#uncomment if no with statement support
##    VG.set(VG_STROKE_DASH_PATTERN, (5, 10))
##    VG.set(VG_STROKE_DASH_PHASE_RESET, True)
##    VG.set(VG_STROKE_DASH_PHASE, 0.0)
##
##    VG.set(VG_STROKE_LINE_WIDTH, 5.0)
##    VG.set(VG_STROKE_JOIN_STYLE, VG_JOIN_MITER)
##    VG.set(VG_STROKE_CAP_STYLE, VG_CAP_ROUND)

    with stroke_style:
        p.draw(VG_FILL_PATH)
        p.draw(VG_STROKE_PATH)
    

    win.flip()
