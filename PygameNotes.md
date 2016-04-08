# Introduction #

Although OpenVG and SDL are completely unrelated, it's possible to create an OpenGL context in Pygame that ShivaVG will happily render to. There are several important flags and attributes that must be set (otherwise some features will not work with no indication why).


# An example #
```
#Initialize Pygame
pygame.init()

#Set OpenGL attributes
#ShivaVG uses the stencil buffer to tessellate paths, so there must be at least a 1-bit stencil buffer
pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 2)

#Multisampling is needed for antialiasing (things will still look okay without it)
#4 samples is somewhat arbitrary, but it looks decent while 2 samples looks blurry.
pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)

#Now that the desired OpenGL attributes have been set, we can request a window
#The OPENGL flag asks for an OpenGL display and the DOUBLEBUF flag asks for a hardware
#double buffered display, which is helpful because the only way to update the screen
#is by flipping
screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)

VG.create_context((width, height))

#Do some more initialization here, maybe set the caption and continue on.
```

The steps are:

  1. Initialize Pygame
  1. Set OpenGL attributes with [pygame.display.gl\_set\_attribute](http://www.pygame.org/docs/ref/display.html#pygame.display.gl_set_attribute)
    * The `GL_STENCIL_SIZE` attribute should be set to some positive value so that ShivaVG works (otherwise you'll find that everything is a series of colored rectangles)
    * If you want anti-aliasing, set `GL_MULTISAMPLEBUFFERS` and `GL_MULTISAMPLESAMPLES`. Four samples works nicely.
  1. Set the `OPENGL` flag and probably the `DOUBLEBUF` flag
  1. Handle any other initialization (set blend mode, set the caption, etc)

Keep in mind that the attributes set are only requests, and may not actually be possible.