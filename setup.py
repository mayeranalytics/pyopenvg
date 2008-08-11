from distutils.core import setup, Extension
import Pyrex.Distutils
import os

libraries = ["libOpenVG"]
library_dirs = ["."]
include_dirs = [".\include"]

#Pyrex cannot detect the change in included files
#so it will not normally regnerate the .c
if os.path.exists(os.path.join("src", "OpenVG", "VG.c")):
    os.remove(os.path.join("src", "OpenVG", "VG.c"))

setup(name = "PyOpenVG",
      version = "0.0.1",
      description = "A Python wrapper for the OpenVG library",
      license = "BSD",
      ext_package = "OpenVG",
      packages = ["OpenVG"],
      package_dir = {"OpenVG":"src/OpenVG"},
      py_modules = ["OpenVG.constants"],
      ext_modules = [Extension("VG",  ["src/OpenVG/VG.pyx"],
                               libraries=libraries,
                               library_dirs=library_dirs,
                               include_dirs=include_dirs),
                     Extension("VGU", ["src/OpenVG/VGU.pyx"],
                               libraries=libraries,
                               library_dirs=library_dirs,
                               include_dirs=include_dirs)],
      cmdclass = {"build_ext": Pyrex.Distutils.build_ext}
)

