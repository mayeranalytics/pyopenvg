import os
import sys

import Pyrex.Distutils
import distutils.core
from distutils.command.build import build as distutils_build

class CustomBuild(distutils_build):
    sub_commands = distutils_build.sub_commands[:]
    del sub_commands[2]

    sub_commands.extend([("build_amanith", None),
                         ("build_shiva", None),
                         ("build_freetype", None)])

Extension = Pyrex.Distutils.Extension


def selective_build(name, pattern, extra_inc=None, extra_lib=None):
    class SBC(Pyrex.Distutils.build_ext):
        description = "Build a specific subset of extensions matched by name"
        user_options = (Pyrex.Distutils.build_ext.user_options +
                        [("src-root=", "S",
                          "add include and library directories at src-root"),
                         ("disabled", "d",
                          "disable building this extension")])
        boolean_options = Pyrex.Distutils.build_ext.boolean_options  + ["disabled"]
        def initialize_options(self):
            self.disabled = False
            self.src_root = None
            Pyrex.Distutils.build_ext.initialize_options(self)
        
        def finalize_options(self):
            Pyrex.Distutils.build_ext.finalize_options(self)
            self.extensions = filter(self.owns_extension, self.extensions)
            if self.src_root is not None:
                self.include_dirs.append(os.path.join(self.src_root, "include"))
                if self.extra_includes:
                    for d in self.extra_includes:
                        self.include_dirs.append(os.path.join(self.src_root, d))
                self.library_dirs.append(os.path.join(self.src_root, "lib"))
                if self.extra_library_dirs:
                    for d in self.extra_library_dirs:
                        self.library_dirs.append(os.path.join(self.src_root, d))
        

        def owns_extension(self, ext):
            if isinstance(self.ext_pattern, basestring):         
                return ext.name.startswith(self.ext_pattern)
            else:
                return self.ext_pattern(ext.name)

        def run(self):
            if self.disabled:
                message = "%s aborted (disabled=True)" % self.__class__.__name__
                self.announce(message, 0)
            else:
                Pyrex.Distutils.build_ext.run(self)

    SBC.__name__ = name
    SBC.ext_pattern = pattern
    SBC.extra_includes = extra_inc
    SBC.extra_library_dirs = extra_lib
    return SBC

SH_libraries = ["libOpenVG"]
AM_libraries = ["libAmanithVG"]
FT_libraries = ["freetype"]
   
##if sys.platform == "linux2":
##    #Need to explicitly link against GL and GLU for some reason on linux
##    SH_libraries.extend(["GL", "GLU"])
##    shiva_root = "/usr"
##    freetype_root = "/usr"
##
##    SH_library_dirs = [os.path.join(shiva_root, "lib")]


build_amanith = selective_build("build_amanith", "OpenVG.amanith",
                                extra_lib=[r"bin\win\x86\gle",
                                           r"bin\win\x86\sre"])
build_shiva = selective_build("build_shiva", "OpenVG.shiva")
build_freetype = selective_build("build_freetype", "FT.freetype",
                                 extra_inc=[os.path.join("include", "freetype2")])


distutils.core.setup(
    name = "PyOpenVG",
    version = "0.0.4",
    author = "Devan Lai",
    author_email = "devan.lai@gmail.com",
    url = "http://code.google.com/p/pyopenvg/",
    description = "A Python wrapper for the OpenVG library",
    license = "BSD",

    packages = ["OpenVG", "FT"],
    package_dir = {"OpenVG":"src/OpenVG",
                   "FT":"src/FT"},

    package_data = {"OpenVG":["libOpenVG.dll","libAmanithVG.dll"]},

    py_modules = ["OpenVG.constants", "OpenVG.font", "FT.constants",
                  "OpenVG.svg", "OpenVG.descriptors",
                  "OpenVG.VG", "OpenVG.VGU"],
    ext_modules = [Extension("OpenVG.amanithvg",  ["src/OpenVG/amanithvg.pyx"],
                             libraries=AM_libraries),
                   Extension("OpenVG.amanithvgu", ["src/OpenVG/amanithvgu.pyx"],
                             libraries=AM_libraries),

                   Extension("OpenVG.shivavg",  ["src/OpenVG/shivavg.pyx"],
                             libraries=SH_libraries),
                   Extension("OpenVG.shivavgu", ["src/OpenVG/shivavgu.pyx"],
                             libraries=SH_libraries),

                   Extension("FT.freetype", ["src/FT/freetype.pyx"],
                             libraries=FT_libraries)],

    cmdclass = {"build": CustomBuild,
                "build_amanith": build_amanith,
                "build_shiva": build_shiva,
                "build_freetype": build_freetype}
)

