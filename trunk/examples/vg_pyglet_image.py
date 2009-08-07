from pyglet.gl import Config
from pyglet import window
from pyglet import image

import Image

from OpenVG import VG
from OpenVG.constants import *

def load_image(path):
    pic = image.load(path)

    width, height = pic.width, pic.height

    pixels = pic.get_data('RGBA', -4 * pic.width)

    im = VG.Image(VG_sRGBA_8888, (width, height))
    im.sub_data(pixels, VG_sRGBA_8888, pic.width * 4, (0,0), (width, height), flip=True)

    return im

#Setup pyglet window -- it is crucial that you have a stencil buffer.
screen = window.get_platform().get_default_display().get_default_screen()

template = Config()
template.double_buffer = True
template.stencil_size = 2

config = screen.get_best_config(template)


# The OpenGL context is created only when you create a window.  Any calls
# to OpenGL before a window is created will fail.
win = window.Window(visible=False, config=config)

# ... perform any OpenGL state initialisation here.
context = VG.create_context((640, 480))
VG.set(VG_CLEAR_COLOR, (0.0, 0.0, 0.0, 1.0))

im = load_image("data/images/donkoose.jpg")

win.set_visible()
while not win.has_exit:
    win.dispatch_events()
    VG.clear((0, 0), (640, 480))

    VG.set(VG_MATRIX_MODE, VG_MATRIX_IMAGE_USER_TO_SURFACE)
    VG.load_identity()
    VG.translate(160, 120)

    im.draw()

    win.flip()
