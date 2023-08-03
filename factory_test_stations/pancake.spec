# -*- mode: python -*-
# you should run this with your tester name to compile: Eg:
# C:\Python27\scripts\pyinstaller.exe pyinstaller.spec project_station_run.py
import sys
import os
import re
import ntpath
import time
import glob
import UIDep
import pyexceptions
########################################FIGURE OUT WHAT TO BUILD##################
build_target = None
if len(sys.argv) < 3:
    build_target = raw_input("Please specify the build target:")
else:
    build_target =  os.path.basename(sys.argv[2])


if build_target == None:
    print ("You did not specify a build target! Goodbye!")
    time.sleep(1)
    sys.exit(1)

build_target_exe = build_target.split(".")[0] + ".exe"
build_target_run = build_target.split(".")[0]
build_target_station = build_target.split('_run')[0]
block_cipher = None

def getrootdir():
    working_dir = os.getcwd()
    root_dir = working_dir.split("factory_test_omi")[0]
    root_dir += "factory_test_omi\\"
    return root_dir

def get_datas():
     working_dir = os.getcwd()
     datas = [('config\\*%s.py'%build_target_station,'config')]

     if len(glob.glob('shop_floor_interface\\*.py')) > 0:
        datas.append(('shop_floor_interface\\*.py','..\\shop_floor_interface\\'))
     #  file extend name changed to seqxc from version 1.8
     if len(glob.glob('test_station\\test_equipment\\algorithm\\*.seqxc')) > 0:
        datas.append(('test_station\\test_equipment\\algorithm\\*.seqxc',
                '.\\test_station\\test_equipment\\algorithm\\'))
     # json file for mot.
     if len(glob.glob('test_station\\test_equipment\\algorithm\\*.json')) > 0:
        datas.append(('test_station\\test_equipment\\algorithm\\*.json',
                '.\\test_station\\test_equipment\\algorithm\\'))
     datas.append((os.path.join(os.path.dirname(UIDep.__file__), '*.dll'), 'UIDep'))
     datas.append((os.path.join(os.path.dirname(UIDep.__file__), '*.txt'), '.'))
     datas.append((os.path.join(os.path.dirname(UIDep.__file__), '*.png'), '.'))
     datas.append((os.path.join(os.path.dirname(pyexceptions.__file__), 'templates', '*.html'), 'pyexceptions/templates'))
     datas.append(('test_station\\test_equipment\\*.dll','.\\test_station\\test_equipment\\'))

     return datas

########################################Application setup############################
searchpaths = [
    getrootdir(),
    '.'
]

a = Analysis([build_target],
             pathex=searchpaths,
             binaries=[],
             datas= get_datas(),
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['zmq'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=build_target_exe,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon='imo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=build_target_run)
