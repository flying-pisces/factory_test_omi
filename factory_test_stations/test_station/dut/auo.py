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
my_ds.display_image("auo_green_33_35_0.png")

print ("ref patter for focus")
my_ds.display_image("check.png")

my_ds.screen_off()
