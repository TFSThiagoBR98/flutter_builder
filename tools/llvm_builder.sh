#!/usr/bin/env bash
cd /opt/llvm/src/;

cmake \
  -B "/opt/llvm/src/_build" \
  -S "/opt/llvm/src/llvm" \
  -G Ninja \
  -D CMAKE_BUILD_TYPE=Release \
  -D LLVM_OPTIMIZED_TABLEGEN=ON \
  -D CMAKE_INSTALL_PREFIX= \
  -D LLVM_HOST_TRIPLE=x86_64-unknown-linux-gnu \
  -D CMAKE_C_COMPILER=/usr/bin/clang \
  -D CMAKE_CXX_COMPILER=/usr/bin/clang++ \
  -D CMAKE_ASM_COMPILER=/usr/bin/clang \
  -D CMAKE_AR=/usr/bin/llvm-ar \
  -D CMAKE_NM=/usr/bin/llvm-nm \
  -D CMAKE_OBJCOPY=/usr/bin/llvm-objcopy \
  -D CMAKE_OBJDUMP=/usr/bin/llvm-objdump \
  -D CMAKE_RANLIB=/usr/bin/llvm-ranlib \
  -D CMAKE_READELF=/usr/bin/llvm-readelf \
  -D CMAKE_STRIP=/usr/bin/llvm-strip \
  -D CMAKE_SYSROOT=/src/build/flutter-engine/src/build/linux/debian_bullseye_amd64-sysroot/ \
  -D LINUX_aarch64-unknown-linux-gnu_SYSROOT=/src/build/flutter-engine/src/build/linux/debian_bullseye_arm64-sysroot/ \
  -D LINUX_armv7-unknown-linux-gnueabihf_SYSROOT=/src/build/flutter-engine/src/build/linux/debian_bullseye_arm-sysroot/ \
  -D LINUX_armv5te-unknown-linux-gnueabi_SYSROOT=/src/build/flutter-engine/src/build/linux/debian_bullseye_armel-sysroot/ \
  -D LINUX_i386-unknown-linux-gnu_SYSROOT=/src/build/flutter-engine/src/build/linux/debian_bullseye_i386-sysroot/ \
  -D LINUX_x86_64-unknown-linux-gnu_SYSROOT=/src/build/flutter-engine/src/build/linux/debian_bullseye_amd64-sysroot/ \
  -D LLVM_BUILD_LLVM_DYLIB=ON \
  -D LLVM_LINK_LLVM_DYLIB=ON \
  -D LLVM_ENABLE_ZLIB=FORCE_ON \
  -D LLVM_ENABLE_ZSTD=FORCE_ON \
  -D LLVM_ENABLE_LIBXML2=FORCE_ON \
  -D LLVM_ENABLE_CURL=FORCE_ON \
  -D LLVM_INSTALL_UTILS=ON \
  -D CMAKE_SHARED_LINKER_FLAGS=-static-libstdc++ \
  -D CMAKE_MODULE_LINKER_FLAGS=-static-libstdc++ \
  -D LLVM_LIT_ARGS="--resultdb-output=r.j -v" \
  -D CROSS_TOOLCHAIN_FLAGS_NATIVE="-DCMAKE_C_COMPILER=/usr/bin/clang;-DCMAKE_CXX_COMPILER=/usr/bin/clang++;-DCMAKE_SYSROOT=/" \
  -D LLVM_ENABLE_LTO=OFF -D LLVM_ENABLE_ASSERTIONS=OFF -D LLVM_ENABLE_BACKTRACES=OFF \
  -D LLVM_BUILD_DOCS=OFF \
  -D LLVM_ENABLE_DOXYGEN=OFF \
  -D LLVM_ENABLE_SPHINX=OFF \
  -D LLVM_LIT_ARGS="-sv --ignore-fail" \
  -C "/src/Fuchsia-stage2.cmake";

DESTDIR="/opt/llvm" ninja -j24 -C _build distribution install-distribution-stripped install/strip install-LLVM-stripped install-clang-libraries;