import os, sys
import time

from displayserver import DisplayServer
custom_adb_path = "adb.exe"
my_ds = DisplayServer(custom_adb_path=custom_adb_path)

print my_ds.is_ready()
my_ds.connect()
my_ds.screen_on()
print ("launch")
my_ds.launch_displayserver()

print("White 255")
my_ds.display_color((255,255,255))

print("gray 180")
my_ds.display_color((180,180,180))

print("gray 127")
my_ds.display_color((127, 127, 127))

print("gray 090")
my_ds.display_color((90, 90, 90))

print("gray 64")
my_ds.display_color((64, 64, 64))

print("gray 35")
my_ds.display_color((35, 35, 35))

print("gray 25")
my_ds.display_color((25, 25, 25))

print("gray 12")
my_ds.display_color((12, 12, 12))

print("red")
my_ds.display_color((255, 0, 0))

print("green")
my_ds.display_color((0, 255, 0))

print("blue")
my_ds.display_color((0, 0, 255))


my_ds.screen_off()
