__author__ = 'kieranlevin'
#quick test harness to demonstrate usage of adb
import sys
import logging
from adb import *


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

device = adb_device()


print device.list_devices()
print("connect")
device.connect()
print("connected")
for i in range(10):
    device.send_shell_command("ls")

print device.cmd_and_quit("pwd") #run another command while the previous shell session is still active.
device.send_data_as_file("quick brown fox jumped over the lazy dog", "/sdcard/test")
print device.get_file_data( "/sdcard/test")
print("disconnect")
print device.disconnect() # has all shell history here

print device.kill_server()
