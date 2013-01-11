# Copyright 2011,2012 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

include_directories(${Boost_INCLUDE_DIR})
link_directories(${Boost_LIBRARY_DIRS})

add_library(gnuradio-smartnet SHARED smartnet_deinterleave.cc smartnet_crc.cc smartnet_subchannel_framer.cc smartnet_wavsink.cc)
target_link_libraries(gnuradio-smartnet ${Boost_LIBRARIES} ${GRUEL_LIBRARIES} ${GNURADIO_CORE_LIBRARIES})
set_target_properties(gnuradio-smartnet PROPERTIES DEFINE_SYMBOL "gnuradio_smartnet_EXPORTS")

########################################################################
# Install built library files
########################################################################
install(TARGETS gnuradio-smartnet
    LIBRARY DESTINATION lib${LIB_SUFFIX} # .so/.dylib file
    ARCHIVE DESTINATION lib${LIB_SUFFIX} # .lib file
    RUNTIME DESTINATION bin              # .dll file
)

########################################################################
# Build and register unit test
########################################################################
include(GrTest)

include_directories(${CPPUNIT_INCLUDE_DIRS})

#list(APPEND test_smartnet_sources
#  ${CMAKE_CURRENT_SOURCE_DIR}/test_smartnet.cc
#  ${CMAKE_CURRENT_SOURCE_DIR}/qa_smartnet.cc
#  ${CMAKE_CURRENT_SOURCE_DIR}/qa_wavsink.cc
#)

#add_executable(test-smartnet ${test_smartnet_sources})

#target_link_libraries(
#  test-smartnet
#  ${GNURADIO_CORE_LIBRARIES}
#  ${GNURADIO_WAVELET_LIBRARIES}
#  ${Boost_LIBRARIES}
#  ${CPPUNIT_LIBRARIES}
#  gnuradio-smartnet
#)

#GR_ADD_TEST(test_smartnet test-smartnet)
