
from adb import adb_device
import re
import numpy as np
import socket
import sys
import struct
import cv2
import logging
import time
import subprocess


from tornado.escape import json_encode, json_decode

# A map of operation keywords to method names
ADB_COMMANDS = {
    'DEFAULT_ACCESS_WHITELIST': ['test', 'ui'],
    'connect': {'function': 'connect', 'arguments': []},
    'start': {'function': 'launch_displayserver', 'arguments': []},
    'stop': {'function': 'kill_displayserver', 'arguments': []},
    'on': {'function': 'screen_on', 'arguments': []},
    'off': {'function': 'screen_off', 'arguments': []},
    'color': {'function': 'set_screen_color',
              'arguments': [{'name': 'R', 'type': 'int', 'max': 255, 'min': 0},
                            {'name': 'G', 'type': 'int', 'max': 255, 'min': 0},
                            {'name': 'B', 'type': 'int', 'max': 255, 'min': 0}]},
    'image': {'function': 'display_image',
              'arguments': [{'name': 'filename', 'type': 'filename'}]}
}

class DisplayServer(adb_device):
    HOST = "localhost"
    PORT = 9000
    DISPLAY_IMAGE_FILE = 1
    DISPLAY_IMAGE_RAW = 2
    DISPLAY_SOLID_COLOR = 3
    FRAG_SHADER = 4
    VERT_SHADER = 5
    LOAD_MURA_DATA = 6
    UNLOAD_MURA_DATA = 7


    def __init__(self, serial=None, custom_adb_path='adb'):
        adb_device.__init__(self, serial=serial, custom_adb_path=custom_adb_path)
        self._logger = logging.getLogger(__name__)

        try:
            self.width, self.height, self.framerate = self.get_framebuffer_details()
        except:
            self.width, self.height, self.framerate = 0, 0, 0

    def initialize(self):
        self._hw_id = "adb1"
        self._hw_name = "Display Server"
        self._hw_object_reference = self
        self._hw_operations = ADB_COMMANDS
        self._register_with_hw_server()
        super(DisplayServer, self).initialize()

    def get_framebuffer_details(self):
        framebuffer_string,_ = self.get_file_data('/sys/class/graphics/fb0/modes')
        # width, height, framerate
        return [int(item) for item in re.match('^.+:([0-9]+)x([0-9]+).{2}([0-9]+)$', framebuffer_string.split('\n')[0]).groups()]

    def screen_on(self):
        self.send_shell_command('if dumpsys power | grep "Display Power: state=OFF"; then input keyevent KEYCODE_WAKEUP; input keyevent KEYCODE_MENU; echo "wokeup"; fi') #turn on screen if off

    def screen_off(self):
        self.send_shell_command('if dumpsys power | grep "Display Power: state=ON"; then input keyevent KEYCODE_POWER; fi') #toggle screen

    def launch_displayserver(self):
        #out = subprocess.check_output([custom_adb_path, "forward", "tcp:9000", "tcp:9000"])
        #assert out >= 0, 'adb forward failed.'
        #time.sleep(2)
        self.send_shell_command(
            'am start -S -W -n "com.facebook.automation.displayserver/.DisplayServerActivity" -a android.intent.action.MAIN -c android.intent.category.LAUNCHER')
        #self.send_shell_command('am start -n "com.facebook.automation.simpledisplayserver/com.facebook.automation.simpledisplayserver.DisplayServer" --es fileimage white.png')



    def display_image(self, filename):
        ret,_,err = self.exists(filename)
        if ret:
            raise RuntimeError("Exit because file does not exist in Android device" + err[0])
        self.send_shell_command(
            'am broadcast -n "com.facebook.automation.displayserver/.DisplayImage" --es filename {}'.format(filename))
        #self.send_shell_command('am broadcast -n "com.facebook.automation.simpledisplayserver/com.facebook.automation.simpledisplayserver.ImageBroadcastReceiver" -a android.intent.action.FACTORY_TEST --es fileimage {}'.format(filename))

    def kill_displayserver(self):
        self.send_shell_command('am force-stop com.facebook.automation.displayserver')

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

    def load_mura_data(self, filename):
        ret,_,err = self.exists(filename)
        if ret:
            raise RuntimeError("Exit because file does not exist in Android device" + err[0])
        self.send_shell_command(
            'am broadcast -n "com.facebook.automation.displayserver/.LoadMuraData" --es filename {}'.format(filename))

    def unload_mura_data(self):
        self.send_shell_command(
            'am broadcast -n "com.facebook.automation.displayserver/.UnloadMuraData" ')

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
        # this should return 1
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

    ''' TCP/IP as a faster alternative '''

    def send_displayserver_command(self,commandID,extra=None,data=None):
        entra_bytesize = 0
        data_bytesize = 0
        extra_byteArr = bytearray()
        data_byteArr = bytearray()
        if extra is not None:
            extra_byteArr = bytearray(extra, 'utf8')# equivalent to putExtra in intent, conver the string extra to a bytearray
        if data is not None:
            if isinstance(data,tuple):  # color
                data_byteArr  = bytearray(str(data).strip('()'), 'utf8')
            elif isinstance(data,np.ndarray): # raw image file
                if data.dtype == np.float32:
                    data = (data * 255).round().astype(np.uint8) #convert to uint8
                data_byteArr = bytearray(data, 'utf8')
            else : #isinstance(data,str)
                data_byteArr = bytearray(data)
        command = bytearray()
        command.append(commandID)   # first byte is a byte, indicating command ID
        command += struct.pack('>I',len(extra_byteArr)) #int (4 bytes) indicating extra_byteArr bytesize. ( Big Endien )
        command += struct.pack('>I',len(data_byteArr))  #  int (4 bytes) indicating data_byteArr bytesize ( Big Endien )
        command += extra_byteArr
        command += data_byteArr
        s = socket.socket()
        try:
            num_bytes = len(command)
            s.connect((self.HOST, self.PORT))
            sent = s.send(command)
            if sent == 0:
                raise RuntimeError("Socket failed to send")
            if sent != num_bytes:
                raise RuntimeError("Only" + sent + " of " + num_bytes + " bytes  are sent.")
            reply = s.recv(10)
            if not reply:
                raise RuntimeError("Socket failed to receive")
            if str(commandID) not in reply:
                raise RuntimeError("DisplayServer failed to complete command")
            else:
                msg = "DisplayServer done "
                extras = extra.split(';')
                if commandID == self.DISPLAY_IMAGE_RAW:
                    msg = msg + "displaying raw image of dimension {}x{} ".format(extras[2],extras[3])  + \
                            "  texture unit: {} , sampler: {}".format(extras[1], extras[0])
                elif commandID == self.DISPLAY_IMAGE_FILE:
                    msg = msg + "displaying imgfile: {},".format(data)  + \
                            "  texture unit: {} , sampler: {}".format(extras[1], extras[0])
                elif commandID == self.DISPLAY_SOLID_COLOR:
                    msg = msg + "displaying color {}".format(str(data))  + \
                            "  texture unit: {} , sampler: {}".format(extras[1], extras[0])
                elif commandID == self.VERT_SHADER:
                    msg = msg + "updating vertex shader to " + extra
                elif commandID == self.FRAG_SHADER:
                    msg = msg + "updating fragmen shader to " + extra
                self._logger.info(msg)
            s.close()
            return sent
        except Exception as err:
            self.logger.error(str(err[0]))
            return False

    def display_color_tcpip(self, color=(255,255,255), num_frames = -1, sampler='uTex0',tex=0,retry = 10):
    	''' Display solid color

      Args:
        color: in the format of (R,G,B) each color range is (int)0-255.
        num_frames: specifies the number of frames to display it (default -1 means always) and it will return after that number of frames.
    	'''
        extra = ";".join((sampler ,str(tex),str(num_frames)))
        num_try = 0
        while (self.send_displayserver_command(self.DISPLAY_SOLID_COLOR, extra , tuple(color) ) == False) :
            time.sleep(1)
            num_try += 1
            self._logger.warning("Display server failed {} times. Try again.".format(num_try))
            if num_try >= retry:
                raise RuntimeError("Exit because DisplayServer failed {} times. Check whether it successfully launched".format(num_try) )

    def display_imagefile_tcpip (self, filename, num_frames = -1,sampler='uTex0',tex=0,retry=10):
    	'''Display an image on the display.

        Args:
      filename: name of .png file to put on screen, and should be already pushed in /sdcard/Pictures/
      num_frames: specifies the number of frames to display it (default -1 means always) and it will return after that number of frames.

    	'''
        ret,_,err = self.exists(filename)
        if ret:
            raise RuntimeError("Exit because file does not exist in Android device" + err[0])

        extra = ";".join((sampler ,str(tex),str(num_frames)) )
        num_try = 0
        while (self.send_displayserver_command(self.DISPLAY_IMAGE_FILE, extra , filename) == False):
            time.sleep(1)
            num_try += 1
            self._logger.warning("Display server failed {} times. Try again.".format(num_try))
            if num_try >= retry:
                raise RuntimeError("Exit because DisplayServer failed {} times. Check whether it successfully launched".format(num_try))


    def display_imageraw_tcpip(self, img_npArr, num_frames = -1,sampler='uTex0',tex=0,retry = 10):
    	''' Display raw image data in the format of a numpy array.  No need to adb push image to the device.

      Args:
        img_npArr: img in the format of numpy array. It will be converted to BGRA PNG format with lossless compression
        num_frames: specifies the number of frames to display it (default -1 means always) and it will return after that number of frames.
    	'''
        if isinstance(img_npArr,np.float32):
            img_BGRA = data = (data * 255).round().astype(np.uint8)
        else:
            img_BGRA = img_npArr.astype(np.uint8)
        height,width, channel = img_BGRA.shape
        extra = ";".join((sampler ,str(tex),str(width),str(height),str(num_frames)))# put the width and height of image into extra
        if channel == 3: # If the img_npArr is in RGB format, change  to BGRA format
            r,g,b = cv2.split(img_BGRA)
            alpha = np.ones(b.shape, dtype=b.dtype) * 255               #creating a dummy alpha channel image.
            img_BGRA= cv2.merge((r,g,b,alpha)) # need to be in BGRA format

        compressed_img = bytearray(cv2.imencode('.png',img_BGRA)[1])
        #self._logger.info(("Compressed image from {} btyes to {} bytes ".format(sys.getsizeof(img_BGRA), sys.getsizeof(compressed_img)) ))
        num_try = 0
        while (self.send_displayserver_command(self.DISPLAY_IMAGE_RAW, extra , compressed_img) == False) :
            time.sleep(1)
            num_try += 1
            self._logger.warning("Display server failed {} times. Try again.".format(num_try))
            if num_try >= retry:
                raise RuntimeError("Exit because DisplayServer failed {} times. Check whether it successfully launched".format(num_try))
        return sys.getsizeof(img_BGRA),sys.getsizeof(compressed_img),num_try

    def load_fragment_shader_tcpip(self, shadername,retry = 10):
        extra = shadername
        num_try = 0
        while (self.send_displayserver_command(self.FRAG_SHADER, extra , None)== False) :
            time.sleep(1)
            num_try += 1
            self._logger.warning("Display server failed {} times. Try again.".format(num_try))
            if num_try >= retry:
                raise RuntimeError("Exit because DisplayServer failed {} times. Check whether it successfully launched".format(num_try))

    def load_vertex_shader_tcpip(self, shadername,retry = 10):
        extra = shadername
        num_try = 0
        while (self.send_displayserver_command(self.VERT_SHADER, extra , None)== False) :
            time.sleep(1)
            num_try += 1
            self._logger.warning("Display server failed {} times. Try again.".format(num_try))
            if num_try >= retry:
                raise RuntimeError("Exit because DisplayServer failed {} times. Check whether it successfully launched".format(num_try))

    def load_mura_data_tcpip(self, filename, sampler='uTex0',tex=0,retry = 10):
        '''
            Load Mura scale into the texture. It will display the previous color.
        '''
        ret, _ , err = self.exists(filename)
        if ret:
            raise RuntimeError("Exit because file does not exist in Android device \n" + err[0])

        extra = ";".join((sampler ,str(tex)))
        num_try = 0
        while( self.send_displayserver_command(self.LOAD_MURA_DATA, extra , filename) == False):
            time.sleep(1)
            num_try += 1
            self._logger.warning("Display server failed {} times. Try again.".format(num_try))
            if num_try >= retry:
                raise RuntimeError("Exit because DisplayServer failed {} times. Check whether it successfully launched".format(num_try))



    def unload_mura_data_tcpip(self,retry = 10):
        '''
            Unload Mura texture. It will display the previous color.
        '''
        num_try = 0
        self.send_displayserver_command(self.UNLOAD_MURA_DATA)
