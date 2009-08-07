import pygame
import Image

from OpenVG import VG
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

mode_table = {
    VG_sRGBX_8888:("RGBX", "XBGR"),
    VG_sRGBA_8888:("RGBA", "ABGR"),
    VG_sRGBA_8888_PRE:None,
    VG_sRGB_565:None,
    VG_sRGBA_5551:None,
    VG_sRGBA_4444:None,
    VG_sL_8:("L", "L"),
    VG_lRGBX_8888:("RGBX", "XBGR"),
    VG_lRGBA_8888:("RGBA", "ABGR"),
    VG_lRGBA_8888_PRE:None,
    VG_lL_8:("L", "L"),
    VG_A_8:("A", "A"),
    VG_BW_1:("1", "1"),
    VG_sXRGB_8888:("RGBX", "RGBX"),
    VG_sARGB_8888:("RGBA", "RGBA"),
    VG_sARGB_8888_PRE:None,
    VG_sARGB_1555:None,
    VG_sARGB_4444:None,
    VG_lXRGB_8888:("RGBX", "RGBX"),
    VG_lARGB_8888:("RGBA", "RGBA"),
    VG_lARGB_8888_PRE:None,
    VG_sBGRX_8888:("RGBX", "XRGB"),
    VG_sBGRA_8888:("RGBA", "ARGB"),
    VG_sBGRA_8888_PRE:None,
    VG_sBGR_565:None,
    VG_sBGRA_5551:None,
    VG_sBGRA_4444:None,
    VG_lBGRX_8888:("RGBX", "XRGB"),
    VG_lBGRA_8888:("RGBA", "ARGB"),
    VG_lBGRA_8888_PRE:None,
    VG_sXBGR_8888:("RGBX", "XBGR"),
    VG_sABGR_8888:("RGBA", "ABGR"),
    VG_sABGR_8888_PRE:("RGBA", "RGBa"),
    VG_sABGR_1555:None,
    VG_sABGR_4444:None,
    VG_lXBGR_8888:("RGBX", "RGBX"),
    VG_lABGR_8888:("RGBA", "RGBA"),
    VG_lABGR_8888_PRE:("RGBA", "RGBa")}

def to_image(im):
    data = im.get_sub_data(None, ((0,0), im.size), im.format, im.stride)
    try:
        mode, raw_mode = mode_table[im.format]
    except TypeError:
        raise NotImplementedError
    return Image.frombuffer(mode, im.size, data, "raw", raw_mode, 0, -1)

def dump_image(im):
    image = to_image(im)
    image.save("out.jpg")

def main(width, height, path, flags=0):
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 2)

    flags |= pygame.OPENGL | pygame.DOUBLEBUF
    
    screen = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption("Pygame Image Draw Test")
    
    VG.create_context((width, height))
    VG.set(VG_CLEAR_COLOR, (1.0, 1.0, 1.0, 1.0))

    im = load_image(path)
    dump_image(im)

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
        
        VG.set(VG_MATRIX_MODE, VG_MATRIX_IMAGE_USER_TO_SURFACE)
        VG.load_identity()
        
        VG.translate(dest_x, dest_y)

        im.draw()
        
        pygame.display.flip()

if __name__ == '__main__':
    main(640, 480, "data/images/donkoose.jpg")
