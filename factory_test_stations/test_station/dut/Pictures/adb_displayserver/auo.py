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

print ("ref patter for focus")
my_ds.display_image("200.png")

print("White 255")
my_ds.display_color((255,255,255))

print("red")
my_ds.display_color((255, 0, 0))

print("green")
my_ds.display_color((0, 255, 0))

print("blue")
my_ds.display_color((0, 0, 255))


my_ds.screen_off()
