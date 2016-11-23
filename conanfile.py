from conans import ConanFile
from conans.tools import download, unzip, replace_in_file
import os
import shutil
from conans import CMake, ConfigureEnvironment, tools
import os

class ALMixerConan(ConanFile):
    name = "ALmixer"
    version = "0.4.0" # 23.11.2016
    sha = "c2e5b55e4935"
    folder = "ewing-almixer-{}".format(sha)
    requires = "openal-soft/1.17.2@R3v3nX/testing"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]
            , "fPIC": [True, False]
            }
    default_options = '''shared=False
    fPIC=True'''
    generators = "cmake"
    license="LGPL 2.1"

    def config(self):
        del self.settings.compiler.libcxx 

    def source(self):
        zip_name = "{}.zip".format(self.sha)
        download("https://bitbucket.org/ewing/almixer/get/{}".format(zip_name), zip_name)
        unzip(zip_name)
        os.unlink(zip_name) # Remove zip file

    def build(self):
        args = ["-DWANTS_BUILD_FRAMEWORK=OFF", "-DCMAKE_BUILD_WITH_INSTALL_RPATH=0FF",
        "-DALMIXER_USE_CLOCK_GETTIME=ON"] # This option should depend on glibc. before v 2.17 disable this.

        args += ["-DWANTS_BUILD_SHARED_LIBRARY={}".format("ON" if self.options.shared else "OFF")]
        if self.settings.os == "Linux":
            args += ["-DALMIXER_USE_MPG123_DECODER=ON"] # Comment in the cmake file: "Looks like distributions are avoiding bundling [MPEG-support] by default, probably because of patent worries."
                                                        # We do still enable it: mp3 is important (and since linux in contrast to the others isn't providing a system API for that, we need our 
                                                        # inbuild libmpg123.
        tools.replace_in_file("{}/CMakeLists.txt".format(self.folder), "ADD_SUBDIRECTORY(EXAMPLES)", "#ADD_SUBDIRECTORY(EXAMPLES) # Commented by conan. we dont want to build examples")
        tools.replace_in_file("{}/CMakeLists.txt".format(self.folder), "PROJECT(ALmixer)", '''PROJECT(ALmixer)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')
        cmake = CMake(self.settings)
        self.run('cmake {} {} {}'.format(self.folder, cmake.command_line, " ".join(args)))
        self.run("cmake --build . {}".format(cmake.build_config))

    def package(self):
        """ Define your conan structure: headers, libs and data. After building your
            project, this method is called to create a defined structure:
        """
        self.copy(pattern="*.h", dst="include", src="%s/include" % self.folder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.dll*", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", keep_path=False)

    def package_info(self):  
                
        self.cpp_info.libs = ["ALmixer"]
