# Install script for directory: /media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm/compiler-rt/test

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
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/test/asan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/test/dfsan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/test/lsan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/test/msan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/test/profile/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/test/sanitizer_common/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/test/tsan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/test/ubsan/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/test/cfi/cmake_install.cmake")
  INCLUDE("/media/mengxk/data/sources/chromium-googlecode-origin/src/third_party/llvm-build/compiler-rt/test/safestack/cmake_install.cmake")

ENDIF(NOT CMAKE_INSTALL_LOCAL_ONLY)

