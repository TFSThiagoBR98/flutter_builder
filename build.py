#!/usr/bin/env python3

"""Run Flutter Builder and Apply Required Patches"""

import argparse
import os
from builder.utils import execute, cloneGit, applyPatch
from pathlib import Path
import sys

DART_COMMIT="5b8936496673a285bf8f37472119bc2afb38a295"
FLUTTER_COMMIT="1a65d409c7a1438a34d21b60bf30a6fd5db59314"

REPO_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
BUILD_ROOT = REPO_ROOT / 'build'

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
      "url": "https://github.com/flutter/engine.git@{}".format(FLUTTER_COMMIT),
      "deps_file": "DEPS",
      "managed": False,
      "custom_deps": {
        #'src/third_party/dart/tools/sdks': None,
        #'src/flutter/third_party/gn': None,
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

def buildFlutter(args):
  workDir = BUILD_ROOT / 'flutter-engine'
  gclient = workDir / '.gclient'
  os.makedirs(workDir, exist_ok=True)
  with gclient.open(mode='w'):
    gclient.write_text(creategClientFlutter())
  execute(['gclient', 'sync', '--no-history', '--reset', '--delete_unversioned_trees', '--jobs=8', '--nohooks', '--force'], cwd=workDir)
  execute(['gclient', 'revert', '--jobs=8', '--nohooks'], cwd=workDir)
  execute(['python3', 'src/build/linux/sysroot_scripts/install-sysroot.py', '--arch=armel'], cwd=workDir)
  execute(['python3', 'src/build/linux/sysroot_scripts/install-sysroot.py', '--arch=arm'], cwd=workDir)
  execute(['python3', 'src/build/linux/sysroot_scripts/install-sysroot.py', '--arch=x86'], cwd=workDir)

  patchDir = REPO_ROOT / 'patches' / 'engine'
  for file in patchDir.iterdir():
    if file.suffix == '.patch':
      applyPatch(workDir / 'src', file)

  patchDir = REPO_ROOT / 'patches' / 'flutter_engine'
  for file in patchDir.iterdir():
    if file.suffix == '.patch':
      applyPatch(workDir / 'src' / 'flutter', file)

  execute(['gclient', 'runhooks'], cwd=workDir)

  # Linux Host Debug
  execute(['python3', './flutter/tools/gn', 
           '--no-goma', 
           '--no-prebuilt-dart-sdk',
           '--enable-fontconfig',
           '--build-glfw-shell',
           '--full-dart-sdk',
           '--no-clang',
           '--no-lto',
           '--target-os', 'linux',
           '--linux-cpu', 'arm',
           '--runtime-mode', 'debug',
           '--arm-float-abi', 'softfp',
           '--no-build-embedder-examples', 
           '--cpu', 'cortex-a9',
           '--unoptimized'
           ], cwd=workDir / 'src')
  
  # Linux Host Profile
  execute(['python3', './flutter/tools/gn', 
           '--no-goma', 
           '--no-prebuilt-dart-sdk',
           '--build-glfw-shell',
           '--enable-fontconfig',
           '--full-dart-sdk',
           '--target-os', 'linux',
           '--linux-cpu', 'arm',
           '--runtime-mode', 'profile',
           '--arm-float-abi', 'softfp',
           '--no-build-embedder-examples', 
           '--cpu', 'cortex-a9',
           '--no-clang',
           '--no-lto'
           ], cwd=workDir / 'src')
  
  # Linux Host Release
  execute(['python3', './flutter/tools/gn', 
           '--no-goma', 
           '--no-prebuilt-dart-sdk',
           '--build-glfw-shell',
           '--enable-fontconfig',
           '--full-dart-sdk',
           '--target-os', 'linux',
           '--linux-cpu', 'arm',
           '--runtime-mode', 'release',
           '--arm-float-abi', 'softfp',
           '--no-build-embedder-examples', 
           '--cpu', 'cortex-a9',
           '--no-clang',
           '--no-lto'
           ], cwd=workDir / 'src')
  
  # Linux Build Debug
  execute([
    'autoninja',
    '-C',
    'out/linux_debug_arm',
    'flutter/build/archives:artifacts',
    'flutter/build/archives:dart_sdk_archive',
    'flutter/build/archives:embedder',
    'flutter/build/archives:flutter_patched_sdk',
    'flutter/build/dart:copy_dart_sdk',
    'flutter/shell/platform/linux:flutter_gtk',
    'flutter/shell/platform/linux:flutter_glfw',
    'flutter/tools/font-subset',
    'flutter:unittests',
  ], cwd=workDir / 'src')

  execute([
    'autoninja',
    '-C',
    'out/linux_profile_arm',
    'flutter/tools/path_ops',
    'flutter/build/dart:copy_dart_sdk',
    'flutter/shell/platform/linux:flutter_gtk',
    'flutter/shell/platform/linux:flutter_glfw',
    'flutter/shell/testing',
    'flutter:unittests',
  ], cwd=workDir / 'src')

  execute([
    'autoninja',
    '-C',
    'out/linux_release_arm',
    'flutter/build/archives:flutter_patched_sdk',
    'flutter/build/archives:dart_sdk_archive',
    'flutter/build/archives:embedder',
    'flutter/shell/testing',
    'flutter/tools/path_ops',
    'flutter/shell/platform/linux:flutter_gtk',
    'flutter/shell/platform/linux:flutter_glfw',
    'flutter:unittests',
  ], cwd=workDir / 'src')

  # Debug '--unoptimized',
  # 'flutter/build/archives:artifacts',
  # 'flutter/build/archives:dart_sdk_archive',
  # 'flutter/build/archives:embedder',
  # 'flutter/build/archives:flutter_patched_sdk',
  # 'flutter/build/dart:copy_dart_sdk',
  # 'flutter/tools/font-subset',
  # 'flutter:unittests',

  # Profile '--no-lto',
  # 'flutter/shell/testing',
  # 'flutter/tools/path_ops',
  # 'flutter/build/dart:copy_dart_sdk',
  # 'flutter/shell/platform/linux:flutter_gtk',
  # 'flutter/shell/testing',
  # 'flutter:unittests',

  # Release
  # 'flutter/build/archives:flutter_patched_sdk',
  # 'flutter/build/dart:copy_dart_sdk',
  # 'flutter/display_list:display_list_benchmarks',
  # 'flutter/display_list:display_list_builder_benchmarks',
  # 'flutter/fml:fml_benchmarks',
  # 'flutter/impeller/geometry:geometry_benchmarks',
  # 'flutter/lib/ui:ui_benchmarks',
  # 'flutter/shell/common:shell_benchmarks',
  # 'flutter/shell/testing',
  # 'flutter/third_party/txt:txt_benchmarks',
  # 'flutter/tools/path_ops',
  # 'flutter/shell/platform/linux:flutter_gtk',
  # 'flutter:unittests',

  
  # sdkDir = workDir / 'src' / 'third_party' / 'dart' / 'tools' / 'sdks'
  # sdkOutDir = BUILD_ROOT / 'dart-sdk' / 'sdk' / 'out' / 'ReleaseXARM' / 'dart-sdk'
  # shutil.rmtree(sdkDir, ignore_errors=True)
  # os.makedirs(sdkDir, exist_ok=True)
  # os.symlink(sdkOutDir, sdkDir / 'dart-sdk', target_is_directory=True)

  # gnDir = workDir / 'src' / 'third_party' / 'gn'
  # shutil.rmtree(gnDir, ignore_errors=True)
  # os.makedirs(gnDir, exist_ok=True)
  # os.symlink('/usr/local/bin/gn', gnDir / 'gn')

  return 1

def mountFlutterRelease(args):
  engineDir = BUILD_ROOT / 'flutter'
  workDir = BUILD_ROOT / 'flutter'

def parseArgs(argv):
  parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
  subparsers = parser.add_subparsers(dest='command', help='Commands to run', required=True)

  buildDartSb = subparsers.add_parser('build-dart', description='Compile Dart on Host to Arch')
  buildDartSb.set_defaults(func=buildDart)

  buildFlutterSb = subparsers.add_parser('build-flutter', description='Compile Flutter on Host to Arch')
  buildFlutterSb.set_defaults(func=buildFlutter)

  args = parser.parse_args()
  args_ = vars(args).copy()
  args_.pop('command', None)
  args_.pop('func', None)
  return args.func(args_)
 

def main(argv):
  return parseArgs(argv)

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
