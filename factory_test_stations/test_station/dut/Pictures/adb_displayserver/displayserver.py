
from adb import adb_device
import re
import numpy as np

class DisplayServer(adb_device):
    def __init__(self, serial=None, custom_adb_path='adb'):
        adb_device.__init__(self, serial=serial, custom_adb_path=custom_adb_path)

        try:
            self.width, self.height, self.framerate = self.get_framebuffer_details()
        except:
            self.width, self.height, self.framerate = 0, 0, 0

    #def connect(self): see parent class

    def get_framebuffer_details(self):
        framebuffer_string,_ = self.get_file_data('/sys/class/graphics/fb0/modes')
        # width, height, framerate
        return [int(item) for item in re.match('^.+:([0-9]+)x([0-9]+).{2}([0-9]+)$', framebuffer_string.split('\n')[0]).groups()]

    def screen_on(self):
        self.send_shell_command('if dumpsys power | grep "Display Power: state=OFF"; then input keyevent KEYCODE_WAKEUP; input keyevent KEYCODE_MENU; echo "wokeup"; fi') #turn on screen if off

    def screen_off(self):
        self.send_shell_command('if dumpsys power | grep "Display Power: state=ON"; then input keyevent KEYCODE_POWER; fi') #toggle screen

    def launch_displayserver(self):
        self.send_shell_command(
            'am start -S -W -n "com.facebook.automation.displayserver/.DisplayServerActivity" -a android.intent.action.MAIN -c android.intent.category.LAUNCHER')
        #self.send_shell_command('am start -n "com.facebook.automation.simpledisplayserver/com.facebook.automation.simpledisplayserver.DisplayServer" --es fileimage white.png')



    def display_image(self, filename):
        self.send_shell_command(
            'am broadcast -n "com.facebook.automation.displayserver/.DisplayImage" --es filename {}'.format(filename))
        #self.send_shell_command('am broadcast -n "com.facebook.automation.simpledisplayserver/com.facebook.automation.simpledisplayserver.ImageBroadcastReceiver" -a android.intent.action.FACTORY_TEST --es fileimage {}'.format(filename))

    def load_fragment_shader(self, filename):
        self.send_shell_command(
            'am broadcast -n "com.facebook.automation.displayserver/.FragShader" --es filename {}'.format(filename))

    def load_vertex_shader(self, filename):
        self.send_shell_command(
            'am broadcast -n "com.facebook.automation.displayserver/.VertShader" --es filename {}'.format(filename))

    def display_color(self, c=(255,255,255)):
        #am broadcast -n "com.facebook.automation.displayserver/.DisplaySolidColor" --es color 255,255,255
        self.send_shell_command(
            'am broadcast -n "com.facebook.automation.displayserver/.DisplaySolidColor" --es color {},{},{}'.format(c[0],c[1],c[2]))

    def checksum_file(self, filename):
        ret, stdout, stderr = self.cmd_and_quit("md5sum /sdcard/Pictures/{}".format(filename))
        checksums = {}
        for i in stdout:
            print i
            checksum, filename, = i.split()
            filename = filename.replace("/sdcard/Pictures/", "")
            checksums[filename] = checksum
        return checksums

    def version(self):
        versioninfo = "UNKNOWN"
        ret, stdout, stderr = self.cmd_and_quit("dumpsys package com.facebook.automation.displayserver | grep versionName")
        for i in stdout:
            vinfo = i.split("=")
            if len(vinfo) > 1:
                versioninfo = vinfo[1]
        return versioninfo

    def get_median_vsync_microseconds(self):
        vsync_timing_script = '''
            echo '' > /data/local/tmp/vsync_log
            `inotifyd - /sys/class/graphics/fb0/vsync_event:-c | while read line; do cat /sys/class/graphics/fb0/vsync_event; done > /data/local/tmp/vsync_log` &
            sleep 1.0
            kill `pidof inotifyd`
            
            cat /data/local/tmp/vsync_log | sed 's/[^0-9]//g'
            rm /data/local/tmp/vsync_log
        '''
        
        response = self.cmd_and_quit(vsync_timing_script)
        vsync_events = np.array(response[1], dtype=np.uint64)
        median_vsync_us = np.median(vsync_events[1:] - vsync_events[:-1]) / 1000.0        
        return median_vsync_us

    def is_ready(self):
        if len(self.list_devices()) == 0:
            return False
        #this should return 1
        code, stdout, stderr = self.cmd_and_quit('getprop sys.boot_completed')  # see if the boot process is done.
        if code is 0 and len(stdout) > 0 and "1" in stdout[0]:
            return True
        return False

    def disable_animations(self):
        self.cmd_and_quit("settings put global window_animation_scale 0")
        self.cmd_and_quit("settings put global transition_animation_scale 0")
        self.cmd_and_quit("settings put global animator_duration_scale 0")

    def set_displayserver_permissions(self):
        self.cmd_and_quit("pm grant com.facebook.automation.displayserver android.permission.WRITE_EXTERNAL_STORAGE")
        self.cmd_and_quit("pm grant com.facebook.automation.displayserver android.permission.READ_EXTERNAL_STORAGE")

    def set_screen_timeout(self, timeout=999000):
        self.cmd_and_quit("settings put system screen_off_timeout {}".format(int(timeout)))