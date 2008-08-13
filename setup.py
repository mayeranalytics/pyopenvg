from distutils.core import setup, Extension
import Pyrex.Distutils
import os

freetype_root = r"C:\Program Files\Freetype"

libraries = ["freetype"]
library_dirs = [os.path.join(freetype_root, "lib"),
                os.path.join(freetype_root, "bin")]
include_dirs = ["include",
                os.path.join(freetype_root, "include"),
                os.path.join(freetype_root, "include", "freetype2")]

setup(name = "PyFreetype",
      version = "0.0.1",
      packages = ["FT"],
      package_dir = {"FT": "src"},
      py_modules = ["FT.constants"],
      ext_modules = [Extension("FT.freetype",  ["src/freetype.pyx"],
                               libraries=libraries,
                               library_dirs=library_dirs,
                               include_dirs=include_dirs)],
      
      cmdclass = {"build_ext": Pyrex.Distutils.build_ext})

