# (C) Copyright 2022 UCAR
#

cmake_minimum_required( VERSION 3.12 FATAL_ERROR )

find_package( ecbuild 3.6 REQUIRED HINTS ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/../ecbuild)

project( genint-bundle VERSION 1.0.0 LANGUAGES C CXX Fortran )

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

include( ecbuild_bundle )

# Default release mode
set( ECBUILD_DEFAULT_BUILD_TYPE Release )

# Enable OpenMP and MPI
set( ENABLE_MPI ON CACHE BOOL "Compile with MPI" )
set( ENABLE_OMP ON CACHE BOOL "Compile with OpenMP" )

# Define bundle
ecbuild_bundle_initialize()

# add the automatically determined parts of the RPATH
# which point to directories outside the build tree to the install RPATH
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH ON)

# when building, already use the install RPATH
set(CMAKE_BUILD_WITH_INSTALL_RPATH ON)

# Use external jedi-cmake or build in bundle
if(DEFINED ENV{jedi_cmake_ROOT})
  include( $ENV{jedi_cmake_ROOT}/share/jedicmake/Functions/git_functions.cmake )
else()
  ecbuild_bundle( PROJECT jedicmake GIT "https://github.com/jcsda-internal/jedi-cmake.git" BRANCH develop UPDATE RECURSIVE )
  include( jedicmake/cmake/Functions/git_functions.cmake )
endif()

#ecbuild_bundle( PROJECT eckit    GIT "https://github.com/ecmwf/eckit.git" TAG 1.20.2 )
#ecbuild_bundle( PROJECT fckit    GIT "https://github.com/ecmwf/fckit.git" TAG 0.9.5 )
#ecbuild_bundle( PROJECT atlas    GIT "https://github.com/ecmwf/atlas.git" TAG 0.31.1 )

ecbuild_bundle( PROJECT oops     GIT "https://github.com/jcsda-internal/oops.git"        BRANCH develop UPDATE )
ecbuild_bundle( PROJECT vader    GIT "https://github.com/jcsda-internal/vader.git"       BRANCH feature/recipes_hmr_at_ap UPDATE )
ecbuild_bundle( PROJECT saber    GIT "https://github.com/jcsda-internal/saber.git"       BRANCH feature/quench_convergence UPDATE)

ecbuild_bundle( PROJECT crtm     GIT "https://github.com/JCSDA/CRTMv3.git"               BRANCH develop UPDATE )
ecbuild_bundle( PROJECT gsw      GIT "https://github.com/jcsda-internal/GSW-Fortran.git" BRANCH develop UPDATE )
ecbuild_bundle( PROJECT ioda     GIT "https://github.com/jcsda-internal/ioda.git"        BRANCH develop UPDATE )
ecbuild_bundle( PROJECT ufo      GIT "https://github.com/jcsda-internal/ufo.git"         BRANCH develop UPDATE )

ecbuild_bundle( PROJECT quenchxx       GIT "https://github.com/weiwilliam/quenchxx.git"       BRANCH feature/append_constants UPDATE)
ecbuild_bundle( PROJECT quenchxx_test  GIT "https://github.com/benjaminmenetrier/quenchxx_test.git"  BRANCH develop UPDATE)

# ecbuild_bundle( PROJECT genint    GIT "https://github.com/jeromebarre/genint.git"          BRANCH update_wrfchem )

ecbuild_bundle( PROJECT ioda-data      GIT "https://github.com/JCSDA-internal/ioda-data.git"      BRANCH develop UPDATE )
ecbuild_bundle( PROJECT ufo-data       GIT "https://github.com/JCSDA-internal/ufo-data.git"       BRANCH develop UPDATE )


ecbuild_bundle_finalize()
