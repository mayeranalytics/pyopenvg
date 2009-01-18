import sys, os
from distutils.core import setup
from distutils.command.build import build
from distutils.command.build_clib import build_clib
from distutils.errors import *
from distutils.spawn import find_executable, _spawn_posix, _spawn_os2

from distutils import log

#This script will build a copy of libOpenVG from a shiva subversion checkout
#(The official ShivaVG 0.2.0 release is broken; checkout the latest svn version
#and place a copy in lib\ where you can access it. This is only necessary if
#you are building libOpenVG on windows with MinGW. Otherwise you can use Visual
#Studio on windows with the provided project files or just use the makefiles
#on Linux. I happen to use MinGW on windows, so this is mostly for me.

#Usage: python build_shiva.py build_shared

#Oh, and don't forget to set openvg_root to point to your/checkout/here/trunk



def non_quoting_spawn(cmd, search_path=True, verbose=False, dry_run=False):
    if os.name == "posix":
        _spawn_posix(cmd, search_path, verbose, dry_run)
    elif os.name == "nt":
        non_quoting_spawn_nt(cmd, search_path, verbose, dry_run)
    elif os.name == "os2":
        _spawn_os2(cmd, search_path, verbose, dry_run)
    else:
        raise DistutilsPlatformError("don't know how to spawn programs on platform '%s'" % os.name)

def non_quoting_spawn_nt(cmd, search_path, verbose, dry_run):
    if search_path:
        executable = find_executable(cmd[0]) or cmd[0]

    log.info(" ".join([executable] + cmd[1:]))

    if not dry_run:
        try:
            rc = os.spawnv(os.P_WAIT, executable, cmd)
        except OSError, exc:
            raise DistutilsExecError("command '%s' failed: %s" % (cmd[0], exc[-1]))

        if rc != 0:
            raise DistutilsExecError("command '%s' failed with exit status %d" % (cmd[0], rc))

class build_shared(build_clib):
    def build_libraries (self, libraries):
        for (lib_name, build_info) in libraries:
            sources = build_info.get('sources')
            if sources is None or type(sources) not in (list, tuple):
                raise DistutilsSetupError, \
                      ("in 'libraries' option (library '%s'), " +
                       "'sources' must be present and must be " +
                       "a list of source filenames") % lib_name
            sources = list(sources)

            log.info("building '%s' library", lib_name)

            # First, compile the source code to object files in the library
            # directory.  (This should probably change to putting object
            # files in a temporary build directory.)
            macros = build_info.get('macros')
            include_dirs = build_info.get('include_dirs')
            dependencies = build_info.get('dependencies')
            if dependencies:
                dependencies = ["-l%s" % lib for lib in dependencies]
            objects = self.compiler.compile(sources,
                                            output_dir=self.build_temp,
                                            macros=macros,
                                            include_dirs=include_dirs,
                                            debug=self.debug,
                                            extra_preargs=["-fPIC"])

            # Now "link" the object files together into a static library.
            # (On Unix at least, this isn't really linking -- it just
            # builds an archive.  Whatever.)
            self.create_shared_lib(objects, lib_name,
                                   output_dir=self.build_clib,
                                   debug=self.debug,
                                   dependencies=dependencies)

    def create_shared_lib(s, objects, output_libname, output_dir=None, debug=0,
                          target_lang=None, dependencies=None):
        self = s.compiler

        objects, output_dir = self._fix_object_args(objects, output_dir)
        if dependencies is None:
            dependencies = []

        output_filename = os.path.join(output_dir, output_libname)

        if self._need_link(objects, output_filename):
            dll_args = ["-e %s.exp" % output_filename,
                        "-z %s.def" % output_filename,
                        "-l %s.lib" % output_filename,
                        "-D %s.dll" % output_libname]
            non_quoting_spawn(["dlltool"] + dll_args + objects + self.objects)

            non_quoting_spawn(["gcc", "-shared"] + objects + self.objects +
                              ["-o %s.dll" % output_filename] + dependencies)

        else:
            log.debug("skipping %s (up-to-date)", output_filename)


class build(build):
    sub_commands = [('build_py',      build.has_pure_modules),
                    ('build_shared',  build.has_c_libraries),
                    ('build_ext',     build.has_ext_modules),
                    ('build_scripts', build.has_scripts),
                   ]


if __name__ == "__main__":
    openvg_root = r"your/checkout/here/trunk"
    
    shiva_sources = ["shArrays.c", "shContext.c", "shExtensions.c", "shGeometry.c",
                     "shImage.c", "shPaint.c", "shParams.c", "shPath.c",
                     "shPipeline.c", "shVectors.c", "shVgu.c"]
    shiva_sources = [os.path.join(openvg_root, "src", name) for name in shiva_sources]
    shiva_info = {"sources": shiva_sources,
                  "include_dirs": [os.path.join(openvg_root, "include", "vg")],
                  "dependencies": ["GL", "GLU"]}

    if sys.platform == "win32":
        shiva_info["dependencies"] = ["opengl32", "glu32"]


    setup(name="Shivabuildingfakepackage",
          libraries=[("libOpenVG", shiva_info)],
          cmdclass={"build":build,
                    "build_shared":build_shared})
