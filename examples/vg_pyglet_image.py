from pyglet.gl import *
from pyglet import window
import Image
from OpenVG import VG
from OpenVG.constants import *


def load_image(path):
    im = Image.open(path)
##    pixels = reversed([(p[2], p[1], p[0]) for p in im.getdata()])
    pixels = reversed(list(im.getdata()))

    image = VG.Image(VG_lRGBX_8888, im.size)
    image.fromiter(iter(pixels), (0,0), im.size)
    
    return image

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

im = load_image("data/donkoose.jpg")


win.set_visible()
while not win.has_exit:
    win.dispatch_events()
    VG.clear((0, 0), (640, 480))

    VG.set(VG_MATRIX_MODE, VG_MATRIX_IMAGE_USER_TO_SURFACE)
    VG.load_identity()
    VG.translate(160, 120)
    im.draw()
    

    win.flip()
