from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('editor.py', base=base, targetName = 'Kiigame Editor')
]

setup(name='Kiigame - Editor',
      version = '0.3',
      description = '',
      options = dict(build_exe = buildOptions),
      executables = executables)
