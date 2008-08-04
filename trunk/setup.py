from distutils.core import setup, Extension
import Pyrex.Distutils

libraries = ["libOpenVG"]
include_dirs = [".\include"]

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
                               library_dirs=["."],
                               include_dirs=include_dirs),
                     Extension("VGU", ["src/OpenVG/VGU.pyx"],
                               libraries=libraries,
                               library_dirs=["."],
                               include_dirs=include_dirs)],
      cmdclass = {"build_ext": Pyrex.Distutils.build_ext}
)

