from distutils.core import setup, Extension
import Pyrex.Distutils
import os

libraries = ["libOpenVG"]
library_dirs = ["."]
include_dirs = ["include"]

freetype_root = r"C:\Program Files\Freetype"
FT_libraries = ["freetype"]
FT_library_dirs = [os.path.join(freetype_root, "lib"),
                   os.path.join(freetype_root, "bin")]
FT_include_dirs = ["include",
                   os.path.join(freetype_root, "include"),
                   os.path.join(freetype_root, "include", "freetype2")]

#Pyrex cannot detect the change in included files
#so it will not normally regenerate the .c
if os.path.exists(os.path.join("src", "OpenVG", "VG.c")):
    os.remove(os.path.join("src", "OpenVG", "VG.c"))

setup(name = "PyOpenVG",
      version = "0.0.2",
      description = "A Python wrapper for the OpenVG library",
      license = "BSD",
      packages = ["OpenVG", "FT"],
      package_dir = {"OpenVG":"src/OpenVG",
                     "FT":"src/FT"},
      py_modules = ["OpenVG.constants", "OpenVG.font", "FT.constants"],
      ext_modules = [Extension("OpenVG.VG",  ["src/OpenVG/VG.pyx"],
                               libraries=libraries,
                               library_dirs=library_dirs,
                               include_dirs=include_dirs),
                     Extension("OpenVG.VGU", ["src/OpenVG/VGU.pyx"],
                               libraries=libraries,
                               library_dirs=library_dirs,
                               include_dirs=include_dirs),
                     Extension("FT.freetype", ["src/FT/freetype.pyx"],
                               libraries=FT_libraries,
                               library_dirs=FT_library_dirs,
                               include_dirs=FT_include_dirs)],
      cmdclass = {"build_ext": Pyrex.Distutils.build_ext}
)

