# Install script for directory: /media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm/compiler-rt/lib

# Set the install prefix
IF(NOT DEFINED CMAKE_INSTALL_PREFIX)
  SET(CMAKE_INSTALL_PREFIX "/usr/local")
ENDIF(NOT DEFINED CMAKE_INSTALL_PREFIX)
STRING(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
IF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  IF(BUILD_TYPE)
    STRING(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  ELSE(BUILD_TYPE)
    SET(CMAKE_INSTALL_CONFIG_NAME "Release")
  ENDIF(BUILD_TYPE)
  MESSAGE(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
ENDIF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)

# Set the component getting installed.
IF(NOT CMAKE_INSTALL_COMPONENT)
  IF(COMPONENT)
    MESSAGE(STATUS "Install component: \"${COMPONENT}\"")
    SET(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  ELSE(COMPONENT)
    SET(CMAKE_INSTALL_COMPONENT)
  ENDIF(COMPONENT)
ENDIF(NOT CMAKE_INSTALL_COMPONENT)

# Install shared libraries without execute permission?
IF(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  SET(CMAKE_INSTALL_SO_NO_EXE "1")
ENDIF(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)

IF(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/interception/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/sanitizer_common/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/lsan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/ubsan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/asan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/builtins/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/dfsan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/msan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/profile/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/tsan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/tsan/dd/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/lib/safestack/cmake_install.cmake")

ENDIF(NOT CMAKE_INSTALL_LOCAL_ONLY)

