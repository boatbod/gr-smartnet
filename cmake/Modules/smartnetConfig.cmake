INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_SMARTNET smartnet)

FIND_PATH(
    SMARTNET_INCLUDE_DIRS
    NAMES smartnet/api.h
    HINTS $ENV{SMARTNET_DIR}/include
        ${PC_SMARTNET_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    SMARTNET_LIBRARIES
    NAMES gnuradio-smartnet
    HINTS $ENV{SMARTNET_DIR}/lib
        ${PC_SMARTNET_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(SMARTNET DEFAULT_MSG SMARTNET_LIBRARIES SMARTNET_INCLUDE_DIRS)
MARK_AS_ADVANCED(SMARTNET_LIBRARIES SMARTNET_INCLUDE_DIRS)

