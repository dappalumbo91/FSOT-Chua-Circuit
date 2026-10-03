# FSOT-Chua-Circuit C++20 layer: Branch L header + golden test + long-window ring tools.
# Depends on the header-only FSOT-2.1-Cpp engine (pin AEB2AD).
#   cmake -S cpp -B cpp/build -G Ninja -DFSOT_CPP_DIR=/path/to/FSOT-2.1-Cpp   (or let it fetch the pinned commit)
cmake_minimum_required(VERSION 3.20)
project(fsot_chua_circuit_cpp CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(FSOT_CPP_DIR "" CACHE PATH "Local FSOT-2.1-Cpp checkout (empty: fetch the pinned commit)")
if(NOT FSOT_CPP_DIR)
  include(FetchContent)
  FetchContent_Declare(fsot_cpp
    GIT_REPOSITORY https://github.com/dappalumbo91/FSOT-2.1-Cpp.git
    GIT_TAG e3e3e230cc6c488f8d8fb4cc3db6ff25c4e2b117)  # AEB2AD engine
  FetchContent_GetProperties(fsot_cpp)
  if(NOT fsot_cpp_POPULATED)
    FetchContent_Populate(fsot_cpp)
  endif()
  set(FSOT_CPP_DIR ${fsot_cpp_SOURCE_DIR})
endif()

# Same interface target as FSOT-2.1-Cpp/CMakeLists.txt (header-only), without importing its test suite.
add_library(fsot INTERFACE)
target_include_directories(fsot INTERFACE ${FSOT_CPP_DIR}/include)
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  target_compile_options(fsot INTERFACE -ffp-contract=off)
endif()
find_package(Boost 1.75 CONFIG QUIET)
if(Boost_FOUND)
  target_link_libraries(fsot INTERFACE Boost::headers)
  target_compile_definitions(fsot INTERFACE FSOT_HAVE_BOOST_MP)
endif()
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU" AND CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
  target_compile_definitions(fsot INTERFACE FSOT_HAVE_FLOAT128)
  target_link_libraries(fsot INTERFACE quadmath)
endif()

add_library(fsot_chua INTERFACE)
target_include_directories(fsot_chua INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(fsot_chua INTERFACE fsot)

add_executable(test_branch_l tests/test_branch_l.cpp)
target_link_libraries(test_branch_l PRIVATE fsot_chua)

add_executable(fsot_chua_sim tools/fsot_chua.cpp)
target_link_libraries(fsot_chua_sim PRIVATE fsot_chua)
target_compile_options(fsot_chua_sim PRIVATE -O3 -Wall -Wextra)

add_executable(fsot_chua_nonideal tools/fsot_chua_nonideal.cpp)
target_link_libraries(fsot_chua_nonideal PRIVATE fsot_chua)
target_compile_options(fsot_chua_nonideal PRIVATE -O3 -Wall -Wextra)

enable_testing()
add_test(NAME branch_l_golden COMMAND test_branch_l ${CMAKE_CURRENT_SOURCE_DIR}/golden/branch_l_AEB2AD.tsv)
add_test(NAME branch_l_derive COMMAND fsot_chua_sim derive kennedy)
set_tests_properties(branch_l_derive PROPERTIES PASS_REGULAR_EXPRESSION "authority_pin\tAEB2AD")
