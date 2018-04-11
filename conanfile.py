#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

class MongoCxxConan(ConanFile):
    name = "mongocxx"
    version = "3.2.0"
    url = "http://github.com/DEGoodmanWilson/conan-mongocxx"
    description = "C++ Driver for MongoDB"
    license = "https://github.com/mongodb/mongocxx/blob/{0}/LICENSE".format(version)
    settings =  "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    requires = 'mongo-c-driver/[~=1.9]@DEGoodmanWilson/testing'
    generators = "cmake"

    # def requirements(self):
    #     if tools.os_info.is_windows:
    # Which parts of boost does mongo want?
    #         Boost/1.64.0@conan/stable

    def source(self):
        tools.get("https://github.com/mongodb/mongo-cxx-driver/archive/r{0}.tar.gz".format(self.version))
        extracted_dir = "mongo-cxx-driver-r{0}".format(self.version)
        os.rename(extracted_dir, "sources")

    def build(self):
        conan_magic_lines='''project(MONGO_CXX_DRIVER LANGUAGES CXX)
        include(../conanbuildinfo.cmake)
        conan_basic_setup()
        # include(CheckCXXCompilerFlag)
        # check_cxx_compiler_flag(-std=c++17 HAVE_FLAG_STD_CXX17)
        # if(HAVE_FLAG_STD_CXX17)
        #     message(STATUS USING C++17!)
        #     set(CMAKE_CXX_STANDARD 17)
        #     set(BSONCXX_POLY_USE_MNMLSTC 0)
        #     set(BSONCXX_POLY_USE_STD_EXPERIMENTAL 0)
        #     set(BSONCXX_POLY_USE_BOOST 0)
        #     set(BSONCXX_POLY_USE_STD 1)
        # else()
        #     check_cxx_compiler_flag(-std=c++14 HAVE_FLAG_STD_CXX14)
        #     if(HAVE_FLAG_STD_CXX14)
        #         message(STATUS USING C++14!)
        #         set(CMAKE_CXX_STANDARD 14)
        #         set(BSONCXX_POLY_USE_MNMLSTC 0)
        #         set(BSONCXX_POLY_USE_STD_EXPERIMENTAL 1)
        #         set(BSONCXX_POLY_USE_BOOST 0)
        #         set(BSONCXX_POLY_USE_STD 0)
        #     else()
        #         message(FATAL_ERROR "MongoCXX requires at least C++14")
        #     endif()
        # endif()
        # set(CMAKE_CXX_STANDARD_REQUIRED ON)
        # set(CMAKE_CXX_EXTENSIONS OFF)
        set(BSONCXX_POLY_USE_MNMLSTC 1)
        set(BSONCXX_POLY_USE_STD_EXPERIMENTAL 0)
        set(BSONCXX_POLY_USE_BOOST 0)
        set(BSONCXX_POLY_USE_STD 0)
        '''
        
        cmake_file = "sources/CMakeLists.txt"
        tools.replace_in_file(cmake_file, "project(MONGO_CXX_DRIVER LANGUAGES CXX)", conan_magic_lines)
        content = tools.load(cmake_file)

        cmake = CMake(self)
        if self.settings.compiler == 'Visual Studio':
            cmake.definitions["BSONCXX_POLY_USE_BOOST"] = 1 # required for Windows.
        cmake.configure(source_dir="sources")
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING*", src="sources")
        self.copy(pattern="*.h", dst="include/bson", src="sources/src/libbson/src/bson", keep_path=False)
        self.copy(pattern="*.h", dst="include/jsonsl", src="sources/src/libbson/src/jsonsl", keep_path=False)
        self.copy(pattern="*.h", dst="include/mongoc", src="sources/src/mongoc", keep_path=False)
        # self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="sources", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="sources", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src="sources", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="sources", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['mongoc', 'bson']
        if tools.os_info.is_macos:
            self.cpp_info.exelinkflags = ['-framework CoreFoundation', '-framework Security']
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags


