from distutils.core import setup
from Pyrex.Distutils import build_ext, Extension

import os
import sys


VG_libraries = ["libOpenVG"]
FT_libraries = ["freetype"]

if sys.platform == "win32":
    #Replace this with wherever your copy of the shiva source is.
    #openvg_root = r"path\to\shiva-checkout\trunk"
    openvg_root = r"D:\powerdrop\Devan\shiva-new\trunk"
    
    #This is the default install location with the GnuWin32 installer
    #freetype_root = r"C:\Program Files\GnuWin32\Freetype"
    freetype_root = r"D:\Program Files\Freetype"

    #if you run "build_shiva.py" then you can just use the copy
    #of libOpenVG that ends up in lib/
    #otherwise if you're building with Visual Studio the other directories
    #are the defaults
    VG_library_dirs = ["lib",
                       os.path.join(openvg_root,"projects/visualc7/Release/bin"),
                       os.path.join(openvg_root,"projects/visualc8/Release/bin")]
       
elif sys.platform == "linux2":
    #Need to explicitly link against GL and GLU for some reason on linux
    VG_libraries.extend(["GL", "GLU"])
    openvg_root = "/usr"
    freetype_root = "/usr"

    VG_library_dirs = [os.path.join(openvg_root, "lib")]

VG_include_dirs = ["include",
                   os.path.join(openvg_root, "include")]

FT_library_dirs = [os.path.join(freetype_root, "lib")]
FT_include_dirs = ["include",
                   os.path.join(freetype_root, "include"),
                   os.path.join(freetype_root, "include", "freetype2")]

#Pyrex cannot detect the change in included files
#so it will not normally regenerate the .c
if os.path.exists(os.path.join("src", "OpenVG", "VG.c")):
    os.remove(os.path.join("src", "OpenVG", "VG.c"))

setup(name = "PyOpenVG",
      version = "0.0.3",
      author = "Devan Lai",
      author_email = "devan.lai@gmail.com",
      url = "http://code.google.com/p/pyopenvg/",
      description = "A Python wrapper for the OpenVG library",
      license = "BSD",

      packages = ["OpenVG", "FT"],
      package_dir = {"OpenVG":"src/OpenVG",
                     "FT":"src/FT"},

      package_data = {"OpenVG":["libOpenVG.dll"]},

      py_modules = ["OpenVG.constants", "OpenVG.font", "FT.constants",
                    "OpenVG.svg", "OpenVG.svg_lxml", "OpenVG.descriptors"],
      ext_modules = [Extension("OpenVG.VG",  ["src/OpenVG/VG.pyx"],
                               libraries=VG_libraries,
                               library_dirs=VG_library_dirs,
                               include_dirs=VG_include_dirs),
                     Extension("OpenVG.VGU", ["src/OpenVG/VGU.pyx"],
                               libraries=VG_libraries,
                               library_dirs=VG_library_dirs,
                               include_dirs=VG_include_dirs),
                     Extension("FT.freetype", ["src/FT/freetype.pyx"],
                               libraries=FT_libraries,
                               library_dirs=FT_library_dirs,
                               include_dirs=FT_include_dirs)],

      cmdclass = {"build_ext": build_ext}
)

