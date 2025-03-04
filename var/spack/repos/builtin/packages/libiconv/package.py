# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import re

from spack.package import *


class Libiconv(AutotoolsPackage, GNUMirrorPackage):
    """GNU libiconv provides an implementation of the iconv() function
    and the iconv program for character set conversion."""

    homepage = "https://www.gnu.org/software/libiconv/"
    gnu_mirror_path = "libiconv/libiconv-1.16.tar.gz"

    version("1.17", sha256="8f74213b56238c85a50a5329f77e06198771e70dd9a739779f4c02f65d971313")
    version("1.16", sha256="e6a1b1b589654277ee790cce3734f07876ac4ccfaecbee8afa0b649cf529cc04")
    version("1.15", sha256="ccf536620a45458d26ba83887a983b96827001e92a13847b45e4925cc8913178")
    version("1.14", sha256="72b24ded17d687193c3366d0ebe7cde1e6b18f0df8c55438ac95be39e8a30613")

    variant(
        "libs",
        default="shared,static",
        values=("shared", "static"),
        multi=True,
        description="Build shared libs, static libs or both",
    )

    # We cannot set up a warning for gets(), since gets() is not part
    # of C11 any more and thus might not exist.
    patch("gets.patch", when="@1.14")
    provides("iconv")

    conflicts("@1.14", when="%gcc@5:")

    # Don't build on Darwin to avoid problems with _iconv vs _libiconv; use native package - see
    # https://stackoverflow.com/questions/57734434/libiconv-or-iconv-undefined-symbol-on-mac-osx
    conflicts("platform=darwin")

    # For spack external find
    executables = ["^iconv$"]

    @classmethod
    def determine_version(cls, exe):
        # We only need to find libiconv on macOS to avoid problems with _iconv vs _libiconv - see
        # https://stackoverflow.com/questions/57734434/libiconv-or-iconv-undefined-symbol-on-mac-osx
        macos_pattern = re.compile("\(GNU libiconv (\w+\.\w+)\)")  # noqa: W605
        version_string = Executable(exe)("--version", output=str, error=str)
        match = macos_pattern.search(version_string)
        version = None
        if match:
            version = match.group(1)
        return version

    def configure_args(self):
        args = ["--enable-extra-encodings"]

        args += self.enable_or_disable("libs")
        args.append("--with-pic")

        # A hack to patch config.guess in the libcharset sub directory
        copy("./build-aux/config.guess", "libcharset/build-aux/config.guess")
        return args

    @property
    def libs(self):
        shared = "libs=shared" in self.spec
        return find_libraries(["libiconv"], root=self.prefix, recursive=True, shared=shared)
