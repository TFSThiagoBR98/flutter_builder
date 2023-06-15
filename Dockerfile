FROM docker.io/debian:bookworm

#RUN sed -i 's/htt[p|ps]:\/\/archive.ubuntu.com\/ubuntu\//http:\/\/ubuntu.c3sl.ufpr.br\/ubuntu/g' /etc/apt/sources.list;
RUN DEBIAN_FRONTEND=noninteractive apt-get update; \
    apt-get install -y --no-install-recommends \
    -o APT::Install-Suggests=0 -o APT::Install-Recommends=0 \
    \
    sudo \
    git \
    make \
    wget \
    gcc \
    lld-15 \
    libunwind-15-dev \
    libxml2-dev \
    clang clang-15 clang-tools-15 libclang-common-15-dev libclang-15-dev libclang1-15 clang-format-15 clangd-15 clang-tidy-15 \
    libllvm-15-ocaml-dev libllvm15 llvm-15 llvm-15-dev llvm-15-runtime \
    libc++-15-dev libc++abi-15-dev \
    linux-libc-dev-armel-cross \
    linux-libc-dev-armhf-cross \
    linux-libc-dev-i386-cross \
    libgcc-12-dev-i386-cross \
    libc6-dev-i386 \
    libx32stdc++-11-dev-i386-cross \
    libstdc++-12-dev-i386-cross \
    libstdc++-12-dev-armhf-cross \
    libstdc++6-i386-cross \
    libx32stdc++6-i386-cross \
    lib32stdc++6 \
    libc6-dev-armhf-cross \
    libc6-dev-armel-cross \
    libc6-dev-i386-amd64-cross \
    libgcc-12-dev-armhf-cross \
    libgcc-12-dev-armel-cross \
    lib32gcc-12-dev \
    libgcc-12-dev \
    zlib1g-dev \
    libcurl4-openssl-dev \
    libx32gcc-12-dev \
    gcc \
    g++ \
    gcc-arm-linux-gnueabihf \
    g++-arm-linux-gnueabihf \
    gcc-arm-linux-gnueabi \
    g++-arm-linux-gnueabi \
    gcc-i686-linux-gnu \
    g++-i686-linux-gnu \
    gcc-x86-64-linux-gnux32 \
    g++-x86-64-linux-gnux32 \
    python3 \
    cmake \
    binutils \
    ninja-build \
    pkg-config \
    libgtk-3-dev \
    liblzma-dev \
    curl \
    libzstd-dev \
    build-essential \
    python3-virtualenv \
    python3-httplib2 \
    python3-six \
    pcregrep \
    libfuse-dev \
    libstdc++-12-dev \
    binutils \
    coreutils \
    desktop-file-utils \
    fakeroot \
    fuse \
    zstd \
    libgdk-pixbuf2.0-dev \
    patchelf \
    python3-pip \
    python3-setuptools \
    squashfs-tools \
    strace \
    util-linux \
    zsync \
    file \
    \
    && \
    rm -rf /var/lib/apt/lists/*

RUN dpkg --add-architecture i386; \
    DEBIAN_FRONTEND=noninteractive apt-get update; \
    apt-get install -y --no-install-recommends \
    -o APT::Install-Suggests=0 -o APT::Install-Recommends=0 \
    \
    libstdc++6:i386 \
    libgcc1:i386 \
    libc++-dev:i386 \
 	libstdc++-12-dev:i386 \
    && \
    rm -rf /var/lib/apt/lists/*

RUN dpkg --add-architecture armel; \
    DEBIAN_FRONTEND=noninteractive apt-get update; \
    apt-get install -y --no-install-recommends \
    -o APT::Install-Suggests=0 -o APT::Install-Recommends=0 \
    \
    libstdc++6:armel \
    libgcc1:armel \
    libstdc++-12-dev:armel \
    && \
    rm -rf /var/lib/apt/lists/*

RUN dpkg --add-architecture armhf; \
    DEBIAN_FRONTEND=noninteractive apt-get update; \
    apt-get install -y --no-install-recommends \
    -o APT::Install-Suggests=0 -o APT::Install-Recommends=0 \
    \
    libstdc++6:armhf \
    libgcc1:armhf \
    libstdc++-12-dev:armhf \
    && \
    rm -rf /var/lib/apt/lists/*

ENV VPYTHON_BYPASS='manually managed python not supported by chrome operations'
ENV DEPOT_TOOLS_UPDATE=0
ENV GCLIENT_PY3=1
ENV PATH="$PATH:/opt/depot_tools"

# Install Depot Tools
RUN mkdir /opt/depot_tools; \
    cd /opt/depot_tools; \
    chmod 777 -R /opt/depot_tools/; \
    chown root:1000 -R /opt/depot_tools/; \
    git clone -b main https://chromium.googlesource.com/chromium/tools/depot_tools.git .; \
    gclient --version

# Install GN
RUN mkdir /opt/gn; \
    cd /opt/gn; \
    git clone https://gn.googlesource.com/gn .; \
    git reset --hard 5e19d2fb166fbd4f6f32147fbb2f497091a54ad8; \
    python3 ./build/gen.py --link-lib="-latomic"; \
    ninja -j8 -C out; \
    cp out/gn /usr/local/bin/gn; \
    gn --version

RUN set -eux; \
	addgroup -gid 1000 builder; \
	useradd -u 1000 -s /bin/bash -g builder builder; \
	mkdir --parent /src; \
    mkdir --parent /home/builder; \
	chown builder:builder -R /src; \
    chown builder:builder -R /home/builder;

RUN ln -s /usr/lib/gcc/i686-linux-gnu/12/libstdc++.so /usr/lib/gcc/x86_64-linux-gnu/12/32/libstdc++.so

# Install GN
# RUN mkdir /opt/llvm; \
#     cd /opt/llvm; \
#     git clone https://github.com/llvm/llvm-project.git --depth 3 -b release/16.x src

USER builder
ENV GDK_BACKEND=x11
