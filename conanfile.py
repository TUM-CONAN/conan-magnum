#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import load, update_conandata, copy, collect_libs, get, replace_in_file
from conan.tools.microsoft.visual import check_min_vs
from conan.tools.system.package_manager import Apt
import os


def sort_libs(correct_order, libs, lib_suffix='', reverse_result=False):
    # Add suffix for correct string matching
    correct_order[:] = [s.__add__(lib_suffix) for s in correct_order]

    result = []
    for expectedLib in correct_order:
        for lib in libs:
            if expectedLib == lib:
                result.append(lib)

    if reverse_result:
        # Linking happens in reversed order
        result.reverse()

    return result


class LibnameConan(ConanFile):
    name = "magnum"
    version = "2020.06"
    description = "Magnum — Lightweight and modular C++11/C++14 \
                   graphics middleware for games and data visualization"
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ("conan", "corrade", "graphics", "rendering", "3d", "2d", "opengl")
    url = "https://github.com/TUM-CONAN/conan-magnum"
    homepage = "https://magnum.graphics"
    author = "ulrich eck (forked on github)"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "build_deprecated": [True, False],
        "build_plugins_static": [True, False],
        "target_gl": [True, False],
        "target_gles": [True, False],
        "with_anyaudioimporter": [True, False],
        "with_anyimageconverter": [True, False],
        "with_anyimageimporter": [True, False],
        "with_anysceneimporter": [True, False],
        "with_audio": [True, False],
        "with_debugtools": [True, False],
        "with_distancefieldconverter": [True, False],
        "with_eglcontext": [True, False],
        "with_fontconverter": [True, False],
        "with_glfwapplication": [True, False],
        "with_glxapplication": [True, False],
        "with_glxcontext": [True, False],
        "with_wglcontext": [True, False],
        "with_gl_info": [True, False],
        "with_imageconverter": [True, False],
        "with_magnumfont": [True, False],
        "with_magnumfontconverter": [True, False],
        "with_meshtools": [True, False],
        "with_objimporter": [True, False],
        "with_opengltester": [True, False],
        "with_primitives": [True, False],
        "with_scenegraph": [True, False],
        "with_sdl2application": [True, False],
        "with_shaders": [True, False],
        "with_text": [True, False],
        "with_tgaimageconverter": [True, False],
        "with_tgaimporter": [True, False],
        "with_vk": [True, False],
        "with_wavaudioimporter": [True, False],
        "with_windowlesswglapplication": [True, False],
        "with_windowlesseglapplication": [True, False],
        "with_windowlesscglapplication": [True, False],
        "with_windowlessglxapplication": [True, False],
        "with_xeglapplication": [True, False],
    }

    default_options = {
        "shared": False, 
        "fPIC": True,
        "build_deprecated": False,
        "build_plugins_static": False,
        "target_gl": True,
        "target_gles": False,
        "with_anyaudioimporter": False,
        "with_anyimageconverter": False,
        "with_anyimageimporter": False,
        "with_anysceneimporter": False,
        "with_audio": False,
        "with_debugtools": True,
        "with_distancefieldconverter": False,
        "with_eglcontext": False,
        "with_fontconverter": False,
        "with_glfwapplication": True,
        "with_glxapplication": False,
        "with_glxcontext": False,
        "with_wglcontext": False,
        "with_gl_info": False,
        "with_imageconverter": False,
        "with_magnumfont": False,
        "with_magnumfontconverter": False,
        "with_meshtools": True,
        "with_objimporter": False,
        "with_opengltester": False,
        "with_primitives": True,
        "with_scenegraph": True,
        "with_sdl2application": False,
        "with_shaders": True,
        "with_text": True,
        "with_tgaimageconverter": False,
        "with_tgaimporter": False,
        "with_vk": False,
        "with_wavaudioimporter": False,
        "with_windowlesswglapplication": False,
        "with_windowlesseglapplication": False,
        "with_windowlesscglapplication": False,
        "with_windowlessglxapplication": False,
        "with_xeglapplication": False,
        "corrade/*:build_deprecated": True,
    }

    def system_requirements(self):
        apt = Apt(self)
        packages = []
        if self.options.target_gl:
            packages.append("libgl1-mesa-dev")
        if self.options.target_gles:
            packages.append("libgles1-mesa-dev")
        missing = apt.check(packages)
        if missing:
            self.output.error("Warning: Missing system packages: {}".format(missing))

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        self.options['corrade']['build_deprecated'] = self.options.build_deprecated

        # To fix issue with resource management, see here:
        # https://github.com/mosra/magnum/issues/304#issuecomment-451768389
        if self.options.shared:
            self.options['corrade']['shared'] = True

    def requirements(self):
        self.requires("corrade/2020.06@camposs/stable")
        self.requires("opengl/system")
        if self.options.with_sdl2application:
            self.requires("sdl/2.26.1")
        if self.options.with_glfwapplication:
            self.requires("glfw/3.3.8")

    def validate(self):
        if self.settings.os == "Windows":
            check_min_vs(self, "141")

    def export(self):
        update_conandata(self, {"sources": {
            "commit": "v{}".format(self.version),
            "url": "https://github.com/mosra/magnum.git"
            }}
            )

    def source(self):
        git = Git(self)
        sources = self.conan_data["sources"]
        git.clone(url=sources["url"], target=self.source_folder)
        git.checkout(commit=sources["commit"])
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
            "find_package(Corrade REQUIRED Utility)",
            "cmake_policy(SET CMP0074 NEW)\nfind_package(Corrade REQUIRED Utility)")

    def generate(self):
        tc = CMakeToolchain(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str 
            tc.variables[var_name] = var_value

        for option, value in self.options.items():
            add_cmake_option(option, value)

        # Corrade uses suffix on the resulting 'lib'-folder when running cmake.install()
        # Set it explicitly to empty, else Corrade might set it implicitly (eg. to "64")
        add_cmake_option("LIB_SUFFIX", "")

        add_cmake_option("BUILD_STATIC", not self.options.shared)
        add_cmake_option("BUILD_STATIC_PIC", not self.options.shared and self.options.get_safe("fPIC"))
        corrade_root = self.dependencies["corrade"].package_folder
        # on windows change to unix style path, as are all other paths
        if self.settings.os == 'Windows':
            corrade_root = corrade_root.replace('\\', '/')        
        tc.variables["Corrade_ROOT"] = corrade_root

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("corrade", "cmake_find_mode", "none")
        deps.set_property("glfw", "cmake_find_mode", "none")
        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="source_subfolder")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst="licenses", src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # See dependency order here: https://doc.magnum.graphics/magnum/custom-buildsystems.html
        all_libs = [
            #1
            "Magnum",
            "MagnumAnimation",
            "MagnumMath",
            #2
            "MagnumAudio",
            "MagnumGL",
            "MagnumSceneGraph",
            "MagnumTrade",
            "MagnumVk",
            #3
            "MagnumMeshTools",
            "MagnumPrimitives",
            "MagnumShaders",
            "MagnumTextureTools",
            "MagnumGlfwApplication",
            "MagnumXEglApplication",
            "MagnumWindowlessEglApplication",
            "MagnumGlxApplication" ,
            "MagnumWindowlessGlxApplication",
            "MagnumSdl2Application",
            "MagnumWindowlessSdl2Application",
            "MagnumWindowlessWglApplication",
            "MagnumWindowlessCglApplication",
            #4
            "MagnumDebugTools",
            "MagnumOpenGLTester",
            "MagnumText",
        ]
        
        # Sort all built libs according to above, and reverse result for correct link order
        suffix = '-d' if self.settings.build_type == "Debug" else ''
        built_libs = collect_libs(self)
        self.cpp_info.libs = sort_libs(correct_order=all_libs, libs=built_libs, lib_suffix=suffix, reverse_result=True)

        if self.settings.os == "Windows":
            if self.settings.compiler == "msvc":
                if not self.options.shared:
                    self.cpp_info.system_libs.append("OpenGL32.lib")
            else:
                self.cpp_info.system_libs.append("opengl32")
        else:
            if self.settings.os == "Macos":
                self.cpp_info.exelinkflags.append("-framework OpenGL")
            elif not self.options.shared:
                self.cpp_info.system_libs.append("GL")
