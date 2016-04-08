# Introduction #

These are a few examples of how to load images for display with OpenVG.
The basic idea is to load the image, convert it to RGBA (because it's straightforward and OpenVG works mostly with 32-bit aligned images), and then pass the data directly to OpenVG for processing.


## Pygame ##

```
RGBA_masks = (-16777216, 16711680, 65280, 255)

def load_image(path):
    surf = pygame.image.load(path).convert(RGBA_masks)

    im = VG.Image(VG_sRGBA_8888, surf.get_size())
    im.sub_data(surf.get_buffer(),
                VG_sRGBA_8888, surf.get_pitch(),
                (0,0), surf.get_size(),
                flip=True)

    return im
```

## PIL ##

```
def load_image(path):
    im = Image.open(path).convert("RGBA")

    image = VG.Image(VG_sRGBA_8888, im.size)
    stride = im.size[0] * 4
    data = im.__array_interface__["data"]
    image.sub_data(data, VG_sABGR_8888, stride, (0,0), im.size, flip=True)
    
    return image
```

## Pyglet ##

```
def load_image(path):
    pic = image.load(path)

    width, height = pic.width, pic.height

    pixels = pic.get_data('RGBA', -4 * pic.width)

    im = VG.Image(VG_sRGBA_8888, (width, height))
    im.sub_data(pixels, VG_sRGBA_8888, pic.width * 4, (0,0), (width, height), flip=True)
    
    return im
```