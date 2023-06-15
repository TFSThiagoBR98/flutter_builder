import sys
import subprocess
from pathlib import Path

def execute(*popenargs, cwd=None):
  process = subprocess.run(*popenargs,
    stdin =subprocess.PIPE,
    stdout=sys.stdout,
    stderr=sys.stderr,
    universal_newlines=True,
    cwd=cwd,
    bufsize=0)
  return process

def executeWithFail(*popenargs, cwd=None):
  process = subprocess.run(*popenargs,
    stdin =subprocess.PIPE,
    stdout=sys.stdout,
    stderr=sys.stderr,
    universal_newlines=True,
    cwd=cwd,
    bufsize=0)
  
  if (process.returncode != 0):
    raise IOError("Failed to run command")

  return process


def extract(tarball, targetDirectory: Path):
  process = execute(['tar', 'mxf', tarball, '-C', targetDirectory])
  if (process.returncode != 0):
    raise IOError("Failed to extract file {0} in directory {1}: {2}".format(tarball, targetDirectory, process.stderr))

def cloneGit(repo, targetDirectory: Path, refCommit=None):
  if not targetDirectory.exists():
    process = execute([
      'git',
      'clone',
      repo,
      targetDirectory,
    ])

    if (process.returncode != 0):
      raise IOError("Failed to run git {0} in directory {1}: {2}".format(repo, targetDirectory, process.stderr))

  if (refCommit != None):
    process = execute([
      'git',
      'reset',
      '--hard',
      refCommit
    ], cwd=targetDirectory)

    if (process.returncode != 0):
      raise IOError("Failed to run git reset --hard in directory {0}: {1}".format(targetDirectory, process.stderr))

def applyPatch(targetDirectory, patchFile):
  print('Apply patch {} to {}'.format(patchFile, targetDirectory))
  process = execute([
    'patch',
    '-Np1',
    '-i',
    patchFile,
    '-d',
    targetDirectory
  ])
  
  if (process.returncode != 0):
    raise IOError("Failed to run patch file {0} in directory {1}: {2}".format(patchFile, targetDirectory, process.stderr))
