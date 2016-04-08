# Introduction #
PyOpenVG has three dependencies:
  * [Pyrex](http://www.cosc.canterbury.ac.nz/greg.ewing/python/Pyrex/), which the extension modules depend upon.
  * An OpenVG implementation, your choice of [ShivaVG](http://sourceforge.net/projects/shivavg) (LGPL) or [AmanithVG](http://www.amanith.org/project.html) (commercial, free evaluation version)
  * [FreeType2](http://freetype.sourceforge.net/freetype2/index.html), which is used to read in font outline data.

# Details #
Installing Pyrex itself is fairly straightforward. You can either download it from directly from the Pyrex homepage and run "python setup.py install" or you can use the package manager of your choice.

Building libOpenVG with ShivaVG is straightforward if you are building on Linux with the GNU toolchain or on Windows with Visual Studio 2005 (Express) or newer. Unfortunately, building with MSYS and MinGW doesn't seem to work.

libAmanith binaries are available on an evaluation basis for Win32/x86 from [the AmanithVG download page](http://www.amanith.org/download.html)

FreeType2 binaries can be acquired from [the FreeType download page](http://freetype.sourceforge.net/download.html) or you can build it yourself from source, if you feel so inclined.
Users of 64-bit systems may have to tweak some of the DEFs in `freetype.pxi` to reflect the appropriate type sizes.

To build PyOpenVG, you need to alter the paths in the `setup.cfg`. Specifically, the setup script needs to know where to find the headers and binaries for ShivaVG/AmanithVG and FreeType. If you've already checked out/downloaded the dependencies and compiled them, the easiest way is to just set `src-root` to the proper directory.

For example, this is the setup.cfg that I use to build PyOpenVG:
```
[build]
compiler=mingw32

[build_amanith]
disabled=0
src_root=C:\dropbox\amanithvg
pyrex_include_dirs=include
library_dirs=lib

[build_shiva]
disabled=0
src_root=C:\dropbox\ShivaVG-0.2.1
pyrex_include_dirs=include
library_dirs=lib

[build_freetype]
disabled=0
src_root=C:\Program Files\GnuWin32
pyrex_include_dirs=include
include_dirs=include
```

If your directory structure doesn't exactly mirror the one that the script assumes, then you can always dump the relevant libraries in the `lib` directory and add your own paths to the include list.


From here on, running "python setup.py build" should work correctly and with luck you should have a compiled copy of PyOpenVG.

The examples in the example directories should help clarify the details of getting PyOpenVG working with [Pyglet](http://pyglet.org/) and [Pygame](http://www.pygame.org/)