#!/usr/bin/env python
# -*- coding: utf-8 -*-

import platform
import errno
import functools
import glob
import os
import os.path
import platform
import shutil
import subprocess
import sys
from sysconfig import get_config_vars

from setuptools import Distribution, setup
from setuptools.command.build_clib import build_clib as _build_clib
from setuptools.command.build_ext import build_ext as _build_ext

NAME = "libnacl"
DESC = "Python bindings for libsodium based on ctypes"

# Version info -- read without importing
_locals = {}
with open("libnacl/version.py") as fp:
    exec(fp.read(), None, _locals)
VERSION = _locals["version"]

requirements = []
setup_requirements = ["setuptools"]

def here(*paths):
    return os.path.relpath(os.path.join(*paths))


def abshere(*paths):
    return os.path.abspath(here(*paths))


sodium = functools.partial(here, "src/libsodium/src/libsodium")


sys.path.insert(0, abshere("src"))


def use_system():
    install_type = os.environ.get("SODIUM_INSTALL")

    if install_type == "system":
        # If we are forcing system installs, don't compile the bundled one
        return True
    else:
        # By default we just use the bundled copy
        return False

class Distribution(Distribution):
    def has_c_libraries(self):
        return not use_system()


class build_clib(_build_clib):
    def get_source_files(self):
        files = glob.glob(here("src/libsodium/*"))
        files += glob.glob(here("src/libsodium/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*/*/*/*"))

        return files

    def build_libraries(self, libraries):
        raise Exception("build_libraries")

    def check_library_list(self, libraries):
        raise Exception("check_library_list")

    def get_library_names(self):
        return ["sodium"]

    def run(self):
        if use_system():
            return

        # use Python's build environment variables
        build_env = {
            key: val
            for key, val in get_config_vars().items()
            if key in ("LDFLAGS", "CFLAGS", "CC", "CCSHARED", "LDSHARED")
            and key not in os.environ
        }
        os.environ.update(build_env)

        # Ensure our temporary build directory exists
        build_temp = os.path.abspath(self.build_temp)
        try:
            os.makedirs(build_temp)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        # Ensure all of our executable files have their permission set
        for filename in [
            "src/libsodium/autogen.sh",
            "src/libsodium/compile",
            "src/libsodium/configure",
            "src/libsodium/depcomp",
            "src/libsodium/install-sh",
            "src/libsodium/missing",
            "src/libsodium/msvc-scripts/process.bat",
            "src/libsodium/test/default/wintest.bat",
        ]:
            os.chmod(here(filename), 0o755)

        if not shutil.which("make"):
            raise Exception("ERROR: The 'make' utility is missing from PATH")

        # Locate our configure script
        configure = abshere("src/libsodium/configure")

        # Run ./configure
        configure_flags = [
            "--enable-shared",
            "--enable-static",
            "--disable-debug",
            "--disable-dependency-tracking",
            "--with-pic",
        ]
        if platform.system() == "SunOS":
            # On Solaris, libssp doesn't link statically and causes linker
            # errors during import
            configure_flags.append("--disable-ssp")
        if os.environ.get("SODIUM_INSTALL_MINIMAL"):
            configure_flags.append("--enable-minimal")
        subprocess.check_call(
            [configure]
            + configure_flags
            + ["--prefix", os.path.abspath(self.build_clib)],
            cwd=build_temp,
        )

        make_args = os.environ.get("LIBSODIUM_MAKE_ARGS", "").split()
        # Build the library
        subprocess.check_call(["make"] + make_args, cwd=build_temp)

        # Check the build library
        subprocess.check_call(["make", "check"] + make_args, cwd=build_temp)

        # Install the built library
        subprocess.check_call(["make", "install"] + make_args, cwd=build_temp)


class build_ext(_build_ext):
    def run(self):
        if self.distribution.has_c_libraries():
            build_clib = self.get_finalized_command("build_clib")
            self.include_dirs.append(
                os.path.join(build_clib.build_clib, "include"),
            )
            self.library_dirs.insert(
                0,
                os.path.join(build_clib.build_clib, "lib64"),
            )
            self.library_dirs.insert(
                0,
                os.path.join(build_clib.build_clib, "lib"),
            )

        return _build_ext.run(self)

setup(
    name=NAME,
    version=VERSION,
    description=DESC,
    author="Thomas S Hatch",
    author_email="thatch@saltstack.com",
    url="https://libnacl.readthedocs.org/",
    setup_requires=setup_requirements,
    install_requires=requirements,
    packages=["libnacl"],
    ext_package="libnacl",
    cmdclass={"build_clib": build_clib, "build_ext": build_ext},
    distclass=Distribution,
    zip_safe=False,
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
    ],
)
