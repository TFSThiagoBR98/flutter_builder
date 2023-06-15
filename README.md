# Flutter Engine Builder

This manages to build the Flutter SDK to some platforms

## Supported Platforms

* armv5t-unknown-linux-gnueabi (armv5t soft)
* armv7-unknown-linux-gnueabihf (armv7 hardfp)
* aarch64-unknown-linux-gnu (aarch64)
* x86_64-unknown-linux-gnu
* i386-unknown-linux-gnu
* riscv32-unknown-linux-gnu
* riscv64-unknown-linux-gnu

## Build required libraries

- fontconfig
- freetype
- X11
- Xcomposite
- Xcursor
- Xdamage
- Xext
- Xfixes
- Xi
- Xrender
- Xtst
- Xrandr
- Xinerama
- Xxf86vm
- srtp
- GL
- EGL
- GLESv2
- unwind
- atomic
- gcc
- dl
- pthreads
- xcb
- jpeg
- wayland-client
- wayland-egl
- icuuc
- z
- png
- bz2
- harfbuzz
- lua
- webp
- webpdemux
- webpmux
- harfbuzz-subset
- gtk-3
- gdk-3
- pangocairo-1.0
- pango-1.0
- atk-1.0
- cairo-gobject
- cairo
- gdk_pixbuf-2.0
- gio-2.0
- gobject-2.0
- glib-2.0

## Warning
It's required to install qemu-static and qemu-binfmt to run software from other architetures