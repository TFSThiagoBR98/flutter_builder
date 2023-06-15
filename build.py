#!/usr/bin/env python3

"""Run Flutter Builder and Apply Required Patches"""

import argparse
import os
from builder.utils import execute, cloneGit, applyPatch, extract, executeWithFail
from pathlib import Path
import sys
import shutil

FLUTTER_VERSION='3.10.5'
DART_COMMIT="892ba4ae22fad68d7eaf26ccdf05dc9f41619ffe"
FLUTTER_COMMIT="796c8ef79279f9c774545b3771238c3098dbefab"
FLUTTER_ENGINE_COMMIT="45f6e009110df4f34ec2cf99f63cf73b71b7a420"

REPO_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
BUILD_ROOT = REPO_ROOT / 'build'

SYSROOT_ARCH = ('armel', 'armhf', 'arm64', 'i386', 'amd64')

def convertGClientToString(data):
  return "solutions = {}".format(data) 

def creategClientDart():
  return convertGClientToString([
    {
      "name": "sdk",
      "url": "https://dart.googlesource.com/sdk.git@{}".format(DART_COMMIT),
      "deps_file": "DEPS",
      "managed": False,
      "custom_vars": {
        "download_android_deps": False,
        "download_windows_deps": False,
        "download_linux_deps": True
      },
    }
  ])
  # return "solutions = [{\"name\": \"sdk\", \"url\": \"https://dart.googlesource.com/sdk.git@" + DART_COMMIT + "\",\"deps_file\": \"DEPS\",\"managed\": False,\"custom_deps\": {},},]"

def creategClientFlutter():
  return convertGClientToString([
    {
      "name": "src/flutter",
      "url": "https://github.com/flutter/engine.git@{}".format(FLUTTER_ENGINE_COMMIT),
      "deps_file": "DEPS",
      "managed": False,
      "custom_deps": {
        #'src/third_party/dart/tools/sdks': None,
        'src/flutter/third_party/gn': {},
        'src/buildtools/linux-x64/clang': {}
      },
      "custom_vars": {
        "checkout_llvm": True,
        "download_android_deps": False,
        "download_windows_deps": False,
        "download_linux_deps": True
      },
    }
  ])

"""
This method build dart for pre flutter instalation

Clone the SDK to build/dart-sdk
Run fetch
Run 
"""
def buildDart(args):
  workDir = BUILD_ROOT / 'dart-sdk'
  gclient = workDir / '.gclient'
  os.makedirs(workDir, exist_ok=True)
  with gclient.open(mode='w'):
    gclient.write_text(creategClientDart())
  execute(['gclient', 'sync', '--no-history', '--reset', '--delete_unversioned_trees', '--jobs=8'], cwd=workDir)
  #execute(['python3', './tools/build.py', '--no-goma', '-a', 'arm', '-m', 'release', 'create_sdk'], cwd=workDir)
  return 1

def prepareBuild(args):
  workDir = BUILD_ROOT / 'flutter-engine'
  gclient = workDir / '.gclient'
  os.makedirs(workDir, exist_ok=True)
  with gclient.open(mode='w'):
    gclient.write_text(creategClientFlutter())
  executeWithFail(['gclient', 'sync', '--no-history', '--reset', '--delete_unversioned_trees', '--jobs=8', '--nohooks', '--force'], cwd=workDir)
  executeWithFail(['gclient', 'revert', '--jobs=8', '--nohooks'], cwd=workDir)

  patchDir = REPO_ROOT / 'patches' / 'buildroot'
  for file in patchDir.iterdir():
    if file.suffix == '.patch':
      applyPatch(workDir / 'src', file)

  patchDir = REPO_ROOT / 'patches' / 'flutter_engine'
  for file in patchDir.iterdir():
    if file.suffix == '.patch':
      applyPatch(workDir / 'src' / 'flutter', file)

  patchDir = REPO_ROOT / 'patches' / 'third_party' / 'dart'
  for file in patchDir.iterdir():
    if file.suffix == '.patch':
      applyPatch(workDir / 'src' / 'third_party' / 'dart', file)

  patchDir = REPO_ROOT / 'patches' / 'third_party' / 'libpng'
  for file in patchDir.iterdir():
    if file.suffix == '.patch':
      applyPatch(workDir / 'src' / 'third_party' / 'libpng', file)

  clang_dir = workDir / 'src' / 'buildtools' / 'linux-x64'
  shutil.rmtree(clang_dir, ignore_errors=True)
  os.makedirs(clang_dir, exist_ok=True)

  extract(REPO_ROOT / 'prepfiles' / 'clang.tar.zst', clang_dir)

  sysroots = workDir / 'src' / 'build' / 'linux'
  os.makedirs(sysroots, exist_ok=True)

  for arch in SYSROOT_ARCH:
    sysroot_name = 'debian_bullseye_{}-sysroot'.format(arch)
    sysroot_tar = 'debian_bullseye_{}_sysroot.tar.xz'.format(arch)
    sysroot = sysroots / sysroot_name
    os.makedirs(sysroot, exist_ok=True)
    extract(REPO_ROOT / 'prepfiles' / sysroot_tar, sysroot)

  executeWithFail(['gclient', 'runhooks'], cwd=workDir)

  # Special fix for DartTools
  # src/third_party/dart/third_party/pkg/tools
  dartToolsDir = workDir / 'src' / 'third_party' / 'dart' / 'third_party' / 'pkg' / 'tools'
  executeWithFail(['git', 'fetch', 'origin', 'main'], cwd=dartToolsDir)
  executeWithFail(['git', 'checkout', '8d6e8b82e3eef8b2f5e3ec9bdd3dd1a2ad3e13f5'], cwd=dartToolsDir)

  return 1

def prepareTool(args):
  workDir = BUILD_ROOT / 'flutter-tree'
  cloneGit('https://github.com/flutter/flutter.git', workDir, '')

  patchDir = REPO_ROOT / 'patches' / 'flutter'
  for file in patchDir.iterdir():
    if file.suffix == '.patch':
      applyPatch(workDir, file)
  return 1

def buildFlutterArmv5teGnueabi(args):
  workDir = BUILD_ROOT / 'flutter-engine'
  artifacts = REPO_ROOT / 'artifacts'

  # Linux Host Debug
  executeWithFail(['python3', './flutter/tools/gn', 
           '--no-goma',
           '--no-prebuilt-dart-sdk',
           '--enable-fontconfig',
           '--build-engine-artifacts',
           '--build-glfw-shell',
           '--full-dart-sdk',
           '--target-sysroot', '/src/build/flutter-engine/src/build/linux/debian_bullseye_armel-sysroot',
           '--arm-version', '5',
           '--target-triple', 'arm-linux-gnueabi',
           '--target-os', 'linux',
           '--linux-cpu', 'arm',
           '--runtime-mode', 'debug',
           '--arm-float-abi', 'soft',
           '--no-enable-unittests',
           '--enable-vulkan',
           '--enable-impeller-vulkan',
           '--enable-impeller-opengles',
           '--no-build-embedder-examples',
           '--cpu-arch', 'armv5te',
           '--unoptimized',
           '--no-lto',
           '--clang',
           '--enable-fontconfig',
           ], cwd=workDir / 'src')
  
  # Linux Build Debug
  executeWithFail([
    'autoninja',
    '-C',
    'out/linux_debug_unopt_arm',
    'flutter/build/archives:artifacts',
    'flutter/build/archives:dart_sdk_archive',
    'flutter/build/archives:embedder',
    'flutter/build/archives:flutter_patched_sdk',
    'copy_dart_sdk',
    'flutter/shell/platform/linux:flutter_glfw',
    'flutter/shell/platform/linux:flutter_gtk',
    'flutter/tools/font-subset',
    'flutter:unittests',
  ], cwd=workDir / 'src')

  artifactDest = artifacts / 'flutter-%s-linux-%s-release'.format(FLUTTER_VERSION, 'armv5t')
  os.makedirs(artifactDest, exist_ok=True)

  
  
  # Linux Host Profile
  executeWithFail(['python3', './flutter/tools/gn', 
           '--no-goma', 
           '--no-prebuilt-dart-sdk',
           '--build-engine-artifacts',
           '--build-glfw-shell',
           '--full-dart-sdk',
           '--target-sysroot', '/src/build/flutter-engine/src/build/linux/debian_bullseye_armel-sysroot',
           '--arm-version', '5',
           '--target-triple', 'arm-linux-gnueabi',
           '--target-os', 'linux',
           '--linux-cpu', 'arm',
           '--runtime-mode', 'profile',
           '--arm-float-abi', 'soft',
           '--no-enable-unittests',
           '--enable-vulkan',
           '--enable-impeller-vulkan',
           '--enable-impeller-opengles',
           '--no-build-embedder-examples', 
           '--cpu-arch', 'armv5te',
           '--clang',
           '--no-lto',
           '--enable-fontconfig',
           ], cwd=workDir / 'src')
  
  executeWithFail([
    'autoninja',
    '-C',
    'out/linux_profile_arm',
    'flutter/tools/path_ops',
    'copy_dart_sdk',
    'flutter/shell/platform/linux:flutter_glfw',
    'flutter/shell/platform/linux:flutter_gtk',
    'flutter/shell/testing',
    'flutter:unittests',
  ], cwd=workDir / 'src')
  
  # Linux Host Release
  executeWithFail(['python3', './flutter/tools/gn', 
           '--no-goma', 
           '--no-prebuilt-dart-sdk',
           '--build-glfw-shell',
           '--full-dart-sdk',
           '--build-engine-artifacts',
           '--target-sysroot', '/src/build/flutter-engine/src/build/linux/debian_bullseye_armel-sysroot',
           '--arm-version', '5',
           '--target-triple', 'arm-linux-gnueabi',
           '--target-os', 'linux',
           '--linux-cpu', 'arm',
           '--runtime-mode', 'release',
           '--arm-float-abi', 'soft',
           '--no-enable-unittests',
           '--enable-vulkan',
           '--enable-impeller-vulkan',
           '--enable-impeller-opengles',
           '--no-build-embedder-examples', 
           '--cpu-arch', 'armv5te',
           '--lto',
           '--clang',
           '--enable-fontconfig',
           ], cwd=workDir / 'src')

  executeWithFail([
    'autoninja',
    '-C',
    'out/linux_release_arm',
    'flutter/build/archives:artifacts',
    'flutter/build/archives:flutter_patched_sdk',
    'flutter/build/archives:dart_sdk_archive',
    'flutter/build/archives:embedder',
    'flutter/shell/testing',
    'flutter/tools/path_ops',
    'flutter/shell/platform/linux:flutter_glfw',
    'flutter/shell/platform/linux:flutter_gtk',
    'flutter:unittests',
  ], cwd=workDir / 'src')



  return 1
  

def mountFlutterRelease(args):
  engineDir = BUILD_ROOT / 'flutter'
  workDir = BUILD_ROOT / 'flutter'

def buildFlutter(args):
  if (args['arch'] == 'armv5te'):
    return buildFlutterArmv5teGnueabi(args)
  else:
    raise Exception('This arch is not supported yet.')

def parseArgs(argv):
  parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
  subparsers = parser.add_subparsers(dest='command', help='Commands to run', required=True)

  d1 = subparsers.add_parser('build-dart-only', description='Compile Dart on Host to Arch')
  d1.set_defaults(func=buildDart)
  d2 = subparsers.add_parser('build', description='Compile Flutter on Host to Arch')
  d2.set_defaults(func=buildFlutter)
  d2.add_argument(
      '--arch',
      default='x86-64-v3',
      type=str, choices=['armv5te', 'armv7', 'arm64', 'x86-64', 'x86-64-v3', 'x86-32'],
      help='Define the arch to compile'
  )
  d3 = subparsers.add_parser('prepare', description='Clone and patch Flutter and the Engine')
  d3.set_defaults(func=prepareBuild)

  args = parser.parse_args()
  args_ = vars(args).copy()
  args_.pop('command', None)
  args_.pop('func', None)
  return args.func(args_)
 

def main(argv):
  return parseArgs(argv)

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
