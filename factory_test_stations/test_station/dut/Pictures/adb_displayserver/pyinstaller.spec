# -*- mode: python -*-
# you should run this with your tester name to compile: Eg:
# K:\Python27\scripts\pyinstaller.exe pyinstaller.spec test_displayserver.py
import sys
import os
import re
import ntpath
import time
from glob import glob
########################################FIGURE OUT WHAT TO BUILD##################
build_target = None
if len(sys.argv) < 3:
    build_target = raw_input("Please specify the build target:")
else:
    build_target =  sys.argv[2]


if build_target == None:
    print ("You did not specify a build target! Goodbye!")
    time.sleep(1)
    sys.exit(1)

build_target_exe = build_target.split(".")[0] + ".exe"

########################################HELPER FUNCTIONS############################
def data_path(paths):
  path_output = []
  for path in paths:
    print ("Appending file %s" % path)
    path_output.append((path, path, 'DATA'))
  return path_output

def getrootdir():
    working_dir = os.getcwd()
    root_dir = working_dir.split("patterns")[0]
    root_dir += "patterns\\"
    return root_dir

def rootdir_path(path_to_glob, relativedir=None):
    from glob import glob
    import ntpath
    path_output = []
    #generate relative path references to the root patterns repo directory
    working_dir = os.getcwd()
    root_dir = working_dir.split("patterns")[0]
    root_dir += "patterns\\"
    globs = glob(root_dir + path_to_glob)
    for path in globs:
      relativepath = path[len(root_dir):]
      store_folder = ntpath.dirname(path)
      if relativedir is None:
        foundrelativedir = store_folder[len(root_dir):]
      else:
        foundrelativedir = relativedir
      print ("Bundling file %s \trelativedir:%s" % (path, foundrelativedir) )
      path_output.append((path,foundrelativedir))
    return path_output

########################################Application setup############################
searchpaths = [
    getrootdir(),
    '.'
]
core_datas = rootdir_path('\\adb_displayserver\\*.dll')
core_datas += rootdir_path('\\adb_displayserver\\*.pyc')
core_datas += rootdir_path('\\adb_displayserver\\*.exe')
core_datas += rootdir_path('\\adb_displayserver\\*.py')

a = Analysis([build_target],
             # add root search paths here, these are any locations you need to include relative hooks to
             pathex=searchpaths,
             # imports from python that are not normally included, currently we find these by running the built exe and see what it misses
             hiddenimports=[],
             hookspath=None,
             datas=core_datas,
             runtime_hooks=None)

binremovelist = []
for d in a.binaries:
    if d[0] in binremovelist:
        a.binaries.remove(d)

for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break


pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=build_target_exe,
          debug=False,
          strip=None,
          upx=True,
          console=True )
