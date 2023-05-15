set(CMAKE_SYSTEM_NAME               Linux)
set(CMAKE_SYSTEM_PROCESSOR          arm)

# Without this flag CMake is not able to pass the compiler sanity check.
set(CMAKE_TRY_COMPILE_TARGET_TYPE   STATIC_LIBRARY)
set(CMAKE_AR                        llvm-ar${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_ASM_COMPILER              clang${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_C_COMPILER                clang${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_CXX_COMPILER              clang++${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_LINKER                    clang++${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_OBJCOPY                   llvm-objcopy${CMAKE_EXECUTABLE_SUFFIX} CACHE INTERNAL "")
set(CMAKE_RANLIB                    llvm-ranlib${CMAKE_EXECUTABLE_SUFFIX} CACHE INTERNAL "")
set(CMAKE_SIZE                      llvm-size${CMAKE_EXECUTABLE_SUFFIX} CACHE INTERNAL "")
set(CMAKE_STRIP                     llvm-strip${CMAKE_EXECUTABLE_SUFFIX} CACHE INTERNAL "")
set(CMAKE_GCOV                      llvm-cov${CMAKE_EXECUTABLE_SUFFIX} CACHE INTERNAL "")

set(CMAKE_C_FLAGS                   "${APP_C_FLAGS} -target arm-none-linux-gnueabihf -flto -fuse-ld=lld -Wno-unused-command-line-argument --sysroot=${FLUTTER_TARGET_PLATFORM_SYSROOT}" CACHE INTERNAL "")
set(CMAKE_CXX_FLAGS                 "${APP_CXX_FLAGS} ${CMAKE_C_FLAGS}" CACHE INTERNAL "")
set(CMAKE_LD_FLAGS                  "${APP_LD_FLAGS} " CACHE INTERNAL "")

set(CMAKE_C_FLAGS_DEBUG             "-O0 -g" CACHE INTERNAL "")
set(CMAKE_C_FLAGS_RELEASE           "-O3 -DNDEBUG" CACHE INTERNAL "")
set(CMAKE_CXX_FLAGS_DEBUG           "${CMAKE_C_FLAGS_DEBUG}" CACHE INTERNAL "")
set(CMAKE_CXX_FLAGS_RELEASE         "${CMAKE_C_FLAGS_RELEASE}" CACHE INTERNAL "")

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

